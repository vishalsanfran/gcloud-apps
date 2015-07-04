# Notes Application
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import app_identity
from models import Note, CheckListItem

import webapp2
import os
import jinja2
import cloudstorage
import mimetypes

jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class MediaHandler(webapp2.RequestHandler):

    def get(self, file_name):
        user = users.get_current_user()
        bucket_name = app_identity.get_default_gcs_bucket_name
        content_t = mimetypes.guess_type(file_name)[0]

        real_path = os.path.join('/', bucket_name,
                user.user_id(), file_name)

        try:
            # if file found GC Storage 
            with cloudstorage.open(real_path, 'r') as f:
                self.response.headers.add_header('Content-type',
                    content_t)
                self.response.out.write(f.read())
        except:
            cloudstorage.errors.NotFoundError:
                self.abort(404)


class MainHandler(webapp2.RequestHandler):

    def _render_template(self, template_name, context=None):
        if context is None:
            context = {}

        user = users.get_current_user()
        ancestor_key = ndb.Key("User", user.nickname())
        qry = Note.owner_query(ancestor_key)
        context['notes'] = qry.fetch()

        # Boiler plate jinja2 code
        template = jinja_env.get_template(template_name)
        return template.render(context)

    # Transaction to create a note with checklist items
    @ndb.transactional
    def _create_note(self, user, file_name):

        note = Note(parent=ndb.Key("User", user.nickname()),
                    title=self.request.get('title'),
                    content=self.request.get('content'))
        note.put()

        # Retrieve csv representing checklist items
        item_titles = self.request.get('checklist_items').split(',')

        for item_title in item_titles:
            # create a checklist instance
            item = CheckListItem(parent = note.key, title = item_title)
            # store each checklist
            item.put()
            # after storing it, we can access the key to append it to the note
            note.checklist_items.append(item.key)
        if file_name:
            note.files.append(file_name)

        # update the note entity with the checklist items
        note.put()  

    def get(self):

        user = users.get_current_user()
        if user is not None:
            logout_url = users.create_logout_url(self.request.uri)

            template_context = {
                'user': user.nickname(),
                'logout_url': logout_url,
            }

            self.response.out.write(
                self._render_template('main.html', template_context))
        else:
            login_url = users.create_login_url(self.request.uri)
            self.redirect(login_url)

    def post(self):

        user = users.get_current_user()
        if user is None:
            self.error(401)
        
        # create a cloud storage bucket
        # get the default bucket
        bucket_name = app_identity.get_default_gcs_bucket_name()
        # get an instance of FileStorage class
        uploaded_file = self.request.POST.get('uploaded_file')

        file_name = getattr(uploaded_file, 'filename')
        file_content = getattr(uploaded_file, 'file', None)

        real_path = ''
        if file_name and file_content:
            content_t = mimetypes.guess_type(file_name)[0]
            real_path = os.path.join('/', bucket_name,
                user.user_id(), file_name)

        with cloudstorage.open(real_path, 'w', content_type = content_t) as f:
            f.write(file_content.read())

        # create a note
        self._create_note(user, file_name)

        logout_url = users.create_logout_url(self.request.uri)

        template_context = {
            'user': user.nickname(),
            'logout_url': logout_url,
        }

        self.response.out.write(
            self._render_template('main.html', template_context))

# WSGI application constructor
app = webapp2.WSGIApplication([('/', MainHandler), 
    (r'/media/(?P<file_name>[\w.]{0,256})', MediaHandler)],
    debug=True)
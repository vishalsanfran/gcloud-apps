from google.appengine.ext import ndb

# Note entity
class Note(ndb.Model):

    title = ndb.StringProperty()
    content = ndb.TextProperty(required=True)
    data_created = ndb.DateTimeProperty(auto_now_add=True)
    #stores key values CheckListItem, 
    #repeated=True means property can hold more than one value
    checklist_items = ndb.KeyProperty("CheckListItem", repeated=True)
    files = ndb.KeyProperty("NoteFile", repeated=True)

    @classmethod
    def owner_query(cls, parent_key):
        return cls.query(ancestor=parent_key).order(-cls.data_created)

class NoteFile(ndb.Model):
    name = ndb.StringProperty()
    url = ndb.StringProperty()
    thumbnail_url = ndb.StringProperty()
    full_path = ndb.StringProperty()

# Checklist entity
class CheckListItem(ndb.Model):
    title = ndb.StringProperty()
    checked = ndb.BooleanProperty(default=False)
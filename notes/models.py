from google.appengine.ext import ndb

class Note(ndb.Model):
	title = ndb.StringProperty()
	content = ndb.TextProperty(required=True)
	data_created = ndb.DateTimeProperty(auto_now_add=True)
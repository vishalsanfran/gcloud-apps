from google.appengine.ext import ndb

# Note entity
class Note(ndb.Model):

    title = ndb.StringProperty()
    content = ndb.TextProperty(required=True)
    data_created = ndb.DateTimeProperty(auto_now_add=True)
    #stores key values CheckListItem, 
    #repeated=True means property can hold more than one value
    checklist_items = ndb.KeyProperty("CheckListItem", repeated=True)

    @classmethod
    def owner_query(cls, parent_key):
        return cls.query(ancestor=parent_key).order(-cls.data_created)

# Checklist entity
class CheckListItem(ndb.Model):
    title = ndb.StringProperty()
    checked = ndb.BooleanProperty(default=False)
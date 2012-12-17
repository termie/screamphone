from google.appengine.ext import db


class Scream(db.Model):
  id = db.StringProperty()
  url = db.StringProperty()
  duration = db.IntegerProperty()


class Story(db.Model):
  obituary = db.StringProperty()
  body = db.TextProperty()
  ordinal = db.IntegerProperty()

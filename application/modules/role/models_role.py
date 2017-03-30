__author__ = 'wilrona'

from application import db


class Roles(db.Document):
    titre = db.StringField()
    description = db.StringField()
    valeur = db.StringField()
    action = db.IntField()
    active = db.BooleanField(default=True)
    parent = db.ReferenceField("self")




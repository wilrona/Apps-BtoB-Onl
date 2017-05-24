__author__ = 'User'

from ...modules import *


class Cron(db.Document):
    sigle = db.StringField()
    datePassage = db.DateTimeField()
    etat = db.IntField()
    repeat = db.IntField()


class Import_excel(db.Document):
    data = db.DictField()
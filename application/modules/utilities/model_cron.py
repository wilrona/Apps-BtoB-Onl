__author__ = 'User'

from ...modules import *


class Cron(db.Document):
    sigle = db.StringField()
    datePassage = db.DateTimeField()
    etat = db.IntField()
    repeat = db.IntField()


class Import_excel(db.Document):
    data = db.DictField()


class Notification(db.Document):
    title = db.StringField()
    message = db.StringField()
    lu = db.ListField(db.ReferenceField('Users'))
    createDate = db.DateTimeField()
    id_compagnie = db.ReferenceField('Compagnie')

    def save(self, *args, **kwargs):
        if not self.createDate:
            self.createDate = datetime.datetime.now()
        return super(Notification, self).save(*args, **kwargs)

__author__ = 'User'

from ...modules import *


class Paiement(db.Document):
    status = db.IntField()
    iduser_paid = db.ReferenceField('Users')
    iddocument = db.ReferenceField('Document')
    idmoyen_paiement = db.StringField()
    montant = db.FloatField()
    idvendeur = db.ReferenceField('Users')
    createDate = db.DateTimeField()
    updateDate = db.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.createDate:
            self.createDate = datetime.datetime.now()
        self.updateDate = datetime.datetime.now()
        return super(Paiement, self).save(*args, **kwargs)


class Moyen_paiement(db.Document):
    name = db.StringField()
    sigle = db.StringField()
    logo = db.StringField()


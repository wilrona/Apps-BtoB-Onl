__author__ = 'User'

from ...modules import *


class Paiement(db.Document):
    status = db.IntField(default=0)
    iduser_paid = db.ReferenceField('Users')
    iddocument = db.ReferenceField('Document')
    idmoyen_paiement = db.StringField()
    montant = db.FloatField()
    idvendeur = db.ReferenceField('Users')
    createDate = db.DateTimeField()
    validDate = db.DateTimeField()
    updateDate = db.DateTimeField()
    auto = db.BooleanField(default=False)
    souche = db.StringField()
    from_soldier = db.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.createDate:
            self.createDate = datetime.datetime.now()
        self.updateDate = datetime.datetime.now()

        if self.status == 1:
            self.validDate = datetime.datetime.now()

        return super(Paiement, self).save(*args, **kwargs)


class Moyen_paiement(db.Document):
    name = db.StringField()
    sigle = db.StringField()
    logo = db.StringField()


__author__ = 'User'

from ...modules import *


class Paiement(db.Document):
    status = db.IntField(default=0)
    iduser_paid = db.ReferenceField('Users')
    iddocument = db.ReferenceField('Document')
    idmoyen_paiement = db.StringField()
    montant = db.FloatField()
    idvendeur = db.ReferenceField('Users')
    iduser_valid = db.ReferenceField('Users')
    createDate = db.DateTimeField()
    validDate = db.DateTimeField()
    updateDate = db.DateTimeField()
    auto = db.BooleanField(default=False)
    souche = db.StringField()

    def save(self, *args, **kwargs):
        if not self.createDate:
            self.createDate = datetime.datetime.now()
        self.updateDate = datetime.datetime.now()

        if self.status == 1:
            self.validDate = datetime.datetime.now()

        return super(Paiement, self).save(*args, **kwargs)

    def info_paiement(self):

        paid = Moyen_paiement.objects(sigle=self.idmoyen_paiement).get()

        return paid

    def reste(self):

        all_paiement = Paiement.objects(iddocument=self.iddocument).order_by('-createDate')

        reste = self.iddocument.montant - self.montant

        index = len(all_paiement)
        for pay in all_paiement:
            index -= 1
            if pay.id == self.id:
                break

        while index > 0:
            reste = reste - all_paiement[index].montant
            index -= 1

        return reste



class Moyen_paiement(db.Document):
    name = db.StringField()
    sigle = db.StringField()
    logo = db.StringField()


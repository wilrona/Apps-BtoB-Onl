__author__ = 'User'

from ...modules import *
from ..company.models_company import Config_reference


class Document(db.Document):

    ref = db.StringField()
    client_id = db.ReferenceField('Client')
    contact_id = db.ReferenceField('Users')

    createDate = db.DateTimeField()
    updateDate = db.DateTimeField()
    devisDoc = db.BooleanField(default=True)
    status = db.IntField(default=0)
    parent = db.ReferenceField('self')
    montant = db.FloatField()

    vendeur_id = db.ReferenceField('Users')
    opportunite_id = db.ReferenceField('Opportunite')

    def save(self, *args, **kwargs):
        if not self.createDate:
            self.createDate = datetime.datetime.now()
        self.updateDate = datetime.datetime.now()
        return super(Document, self).save(*args, **kwargs)

    def lignedoc(self):
        lignes = LigneDoc.objects(doc_id=self.id)
        return lignes


class LigneDoc(db.Document):
    doc_id = db.ReferenceField('Document')
    prix = db.FloatField()
    qte = db.IntField()
    dateDebut = db.DateTimeField()
    dateFin = db.DateTimeField()
    etat = db.IntField(default=0)
    idcompagnie = db.ReferenceField('Compagnie')
    idpackage = db.ReferenceField('Package')




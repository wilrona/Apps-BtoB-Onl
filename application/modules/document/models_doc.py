__author__ = 'User'

from ...modules import *
from ..company.models_company import Config_reference


class Document(db.Document):

    ref = db.StringField()
    client_id = db.ReferenceField('Compagnie')
    contact_id = db.ReferenceField('Users')

    createDate = db.DateTimeField()
    updateDate = db.DateTimeField()
    devisDoc = db.BooleanField(default=True)
    status = db.IntField(default=0)
    parent = db.ReferenceField('self')
    montant = db.FloatField()

    vendeur_id = db.ReferenceField('Users')
    opportunite_id = db.ReferenceField('Opportunite')
    note = db.StringField()

    exe_ici_cm = db.IntField() # verifier si une facture a deja ete traite, 0 non traite; 1 Traite; 2 Traite partiel

    def save(self, *args, **kwargs):
        if not self.createDate:
            self.createDate = datetime.datetime.now()
        self.updateDate = datetime.datetime.now()
        return super(Document, self).save(*args, **kwargs)

    def lignedoc_devis(self):
        lignes = LigneDoc.objects(iddevis=self.id)
        return lignes

    def lignedoc_facture(self):
        lignes = LigneDoc.objects(iddocument=self.id)
        return lignes

    def factu_devis(self):
        facture = Document.objects(parent=self.id)
        return facture

    def facture_valid(self):

        resp = False
        factures = Document.objects(parent=self.id)

        for facture in factures:
            if facture.status == 1 or facture.status == 2:
                resp = True

        return resp

    def reference(self):
        current_ref = Config_reference.objects().first()
        if not self.devisDoc:
            ref = current_ref.ref_fact+'/'+self.ref
        else:
            ref = current_ref.ref_devis+'/'+self.ref
        return ref

    def reglement_facture(self, status=False):

        from ..paiement.models_paiement import Paiement
        if status:
            paiements = Paiement.objects(Q(iddocument=self.id) & Q(status=1))
        else:
            paiements = Paiement.objects(iddocument=self.id)
        return paiements

    def montant_reglement(self, status=False):

        from ..paiement.models_paiement import Paiement
        if status:
            paiements = Paiement.objects(Q(iddocument=self.id) & Q(status=1))
        else:
            paiements = Paiement.objects(iddocument=self.id)

        montant = 0
        for paiement in paiements:
            montant += paiement.montant
        return montant

    def is_partiel(self):

        from ..paiement.models_paiement import Paiement
        paiements = Paiement.objects(Q(iddocument=self.id) & Q(status=1))
        montant = 0
        for paiement in paiements:
            montant += paiement.montant

        partiel = False
        if montant and montant < self.montant:
            partiel = True

        return partiel

    def package_ici_cm(self):

        lignes = LigneDoc.objects(iddocument=self.id)

        data = []
        for ligne in lignes:
            if ligne.idpackage.idligneService == 'ici_cm' and ligne.etat == 0:
                data.append(ligne)

        return data

    def montant_package_ici_cm(self):

        lignes = LigneDoc.objects(iddocument=self.id)

        montant = 0
        for ligne in lignes:
            if ligne.idpackage.idligneService == 'ici_cm' and ligne.etat == 0:
                montant += ligne.prix

        return montant


class LigneDoc(db.Document):
    iddocument = db.ReferenceField('Document')
    iddevis = db.ReferenceField('Document')
    prix = db.FloatField()
    qte = db.IntField()
    dateDebut = db.DateTimeField()
    dateFin = db.DateTimeField()
    etat = db.IntField(default=0) # 1 : ligne document active
    idcompagnie = db.ReferenceField('Compagnie')
    idpackage = db.ReferenceField('Package')
    desc = db.StringField()
    free = db.IntField(default=0)




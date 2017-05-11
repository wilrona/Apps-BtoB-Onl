from application.modules import *
from ..document.models_doc import Document, LigneDoc
from ..package.models_package import Package
from ..compagnie.models_compagnie import Compagnie
from ..user.models_user import Users
from ..paiement.models_paiement import Paiement


def active_partenaire_facture(current):

    partenaire = Compagnie.objects.get(id=current.id)

    if partenaire.etat_souscription != 1:

        level_pack = Package.objects(Q(idligneService='ici_cm') & Q(hight=True) & Q(sale=0)).get()

        # creation du document facture
        facture = Document()
        facture.client_id = partenaire

        contact = Users.objects(email='support@yoomee.onl').first()
        if contact:
            facture.contact_id = contact
            partenaire.idcontact.append(contact)

            facture.vendeur_id = contact

            count_exist = Document.objects(devisDoc=False).count()
            facture.ref = function.reference(count=count_exist+1, caractere=7, refuser=contact.ref)

        facture.devisDoc = False
        facture.status = 2
        facture.montant = level_pack.prix

        facture = facture.save()

        # Creation des lignes de la facture
        ligne = LigneDoc()
        ligne.iddocument = facture
        ligne.prix = level_pack.prix
        ligne.idpackage = level_pack

        time_zones = tzlocal()
        date_auto_nows = datetime.datetime.now(time_zones).strftime("%m/%d/%y")

        current_date = datetime.datetime.strptime(date_auto_nows, "%m/%d/%y")
        ligne.dateDebut = function.datetime_convert(current_date)
        ligne.dateFin = current_date + relativedelta(months=int(level_pack.duree))
        ligne.qte = level_pack.duree
        ligne.idcompagnie = partenaire
        ligne.etat = 1

        ligne.save()

        # Validation du paiement de la facture
        paiement = Paiement()
        paiement.status = 1
        paiement.montant = level_pack.prix
        paiement.iddocument = facture
        if contact:
            paiement.idvendeur = contact
            paiement.iduser_paid = contact
        paiement.idmoyen_paiement = 'cash'
        paiement.auto = True

        paiement.save()

        partenaire.etat_souscription = 1

        if not partenaire.activated:
            partenaire.activated = True

        partenaire.save()

    return 'True'






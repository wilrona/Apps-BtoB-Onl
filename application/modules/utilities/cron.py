
from ...modules import *
from model_cron import Cron
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger



class Config(object):
    JOBS = [
        # {
        #     'id': 'job1',
        #     'func': 'application.modules.utilities.views:job1',
        #     'args': (1, 2),
        #     'trigger': IntervalTrigger(seconds=60)
        # }
    ]

    SCHEDULER_API_ENABLED = True


# def job1(a, b):
#     print(str(a) + ' ' + str(b))


# Execute tout les 1 minutes.
def active_company_ici():
    from ..document.models_doc import Document

    factures = Document.objects(Q(DevisDoc=False) & Q(exe_ici_cm__exists=0) | Q(exe_ici_cm=0) | Q(exe_ici_cm=2))

    enterprise = []

    for facture in factures:
        if facture.client_id.activated:
            if not facture.is_partiel():
                for ici_cm in facture.package_ici_cm():
                    enterprise.append(ici_cm.idcompagnie)

                    time_zones = tzlocal()
                    date_auto_nows = datetime.datetime.now(time_zones).strftime("%m/%d/%y")

                    current_date = datetime.datetime.strptime(date_auto_nows, "%m/%d/%y")
                    ici_cm.dateDebut = function.datetime_convert(current_date)
                    ici_cm.dateFin = current_date + relativedelta(months=int(ici_cm.qte))

                    ici_cm.etat = 1
                    ici_cm.save()

                facture.exe_ici_cm = 1
                facture.save()

            if facture.is_partiel() and facture.montant_reglement() > 0: # verifie si le paiement n'est pas pas
                # complet et qu'il y'a un versement qui existe
                if facture.montant >= facture.montant_package_ici_cm(): # verifie que le montant existant est
                    # superieur a la valeur du package ici achete
                    for ici_cm in facture.package_ici_cm():
                        enterprise.append(ici_cm.idcompagnie)

                        time_zones = tzlocal()
                        date_auto_nows = datetime.datetime.now(time_zones).strftime("%m/%d/%y")

                        current_date = datetime.datetime.strptime(date_auto_nows, "%m/%d/%y")
                        ici_cm.dateDebut = function.datetime_convert(current_date)
                        ici_cm.dateFin = current_date + relativedelta(months=int(ici_cm.qte))

                        ici_cm.etat = 1
                        ici_cm.save()
                    facture.exe_ici_cm = 2
                    facture.save()

    for entreprise in enterprise:
        entreprise.etat_souscription = 1
        entreprise.save()

    print('activation reussi')


# Execution tous les jours a 07:00 du matin.
def verify_expired_company():

    from ..compagnie.models_compagnie import Compagnie
    from ..workflow.workflow_partenaire import active_partenaire_facture

    time_zones = tzlocal()
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%m/%d/%y")

    current_date = datetime.datetime.strptime(date_auto_nows, "%m/%d/%y")

    entreprises = Compagnie.objects(activated=True)

    for enterprise in entreprises:

        if enterprise.dateExpired().dateFin == function.datetime_convert(current_date):

            enterprise.etat_souscription = 2
            enterprise = enterprise.save()

            no_part = True
            if enterprise.partenaire:
                active_partenaire_facture(enterprise)
                enterprise.etat_souscription = 1
                enterprise = enterprise.save()
                no_part = False

            if no_part:
                ligne = enterprise.dateExpired()
                ligne.etat = 0
                ligne.save()

    print('Entreprise expiree traite')


# Execution tous les jours a 07:30
def send_mail_expired_company():

    from ..compagnie.models_compagnie import Compagnie
    from ..company.models_company import Company
    import time

    time_zones = tzlocal()
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%m/%d/%y")

    current_date = datetime.datetime.strptime(date_auto_nows, "%m/%d/%y")

    entreprises = Compagnie.objects(Q(activated=True) & Q(verify=1))
    info = Company.objects().first()

    count = 0
    sleep = 1
    for enterprise in entreprises:

        # Envoie email de rappel d'expiration pour les entreprises
        if not enterprise.uploaded and enterprise.etat_souscription == 1 and not enterprise.partenaire:

            if enterprise.remaind_day(days=60): # si le temps restant est <= 60 jours avant expiration du package
                if enterprise.remaind_day(days=30): # si le temps restant est <= 30 jours avant expiration du package
                    if enterprise.remaind_day(days=15): # si le temps restant est <= 15 jours avant expiration du
                        # package
                        if enterprise.remaind_day(days=7): # si le temps restant est <= 7 jours avant expiration du
                            # package
                            if enterprise.remaind_day(days=3): # si le temps restant est <= 3 jours avant expiration
                                # du package
                                # envoie de l'email
                                pass
                            else:
                                # envoie de l'email
                                pass
                        else:
                            # envoie de l'email
                            pass
                    else:
                        # envoie de l'email
                        pass
                else:
                    # envoie de l'email
                    pass

        # Envoie email de rappel d'expiration pour les entreprises reclammees
        if enterprise.uploaded and enterprise.claimDate:

            if enterprise.claim_remaind_day(days=60): # si le temps restant est <= 60 jours avant expiration des 3
                # mois fournis
                if enterprise.claim_remaind_day(days=30): # si le temps restant est <= 30 jours avant expiration des
                    # 3 mois fournis
                    if enterprise.claim_remaind_day(days=15): # si le temps restant est <= 15 jours avant expiration
                        # des 3 mois fournis
                        if enterprise.claim_remaind_day(days=7): # si le temps restant est <= 7 jours avant
                            # expiration des 3 mois fournis
                            if enterprise.claim_remaind_day(days=3): # si le temps restant est <= 3 jours avant
                                # expiration des 3 mois fournis
                                if enterprise.claim_remaind_day(days=0): # s'il n'existe plus de temps restant,
                                    # on reinitialise
                                    enterprise.etat_souscription = 2
                                    enterprise = enterprise.save()
                                else:
                                    # envoie de l'email
                                    pass
                            else:
                                # envoie de l'email
                                pass
                        else:
                            # envoie de l'email
                            pass
                    else:
                        # envoie de l'email
                        pass
                else:
                    # envoie de l'email
                    pass

        # Envoie des emails au entreprise qui ont leur package expiree
        if enterprise.etat_souscription == 2:

            if enterprise.dateExpired().dateFin == function.datetime_convert(current_date) and not enterprise.uploaded:

                html = render_template('template_mail/compagnie/expired_mail.html', **locals())

                msg = Message()
                msg.recipients = [enterprise.mainuser.email]
                msg.subject = 'Votre abonnement de l\'entreprise '+str(enterprise.name)+' est arrive a expiration.'
                msg.sender = ('ICI.CM CRM Abonnement Expire', 'no_reply@ici.cm')

                msg.html = html
                mail.send(msg)

            if enterprise.uploaded and enterprise.etat_souscription == 2:
                enterprise.uploaded = False
                enterprise = enterprise.save()

                # envoie de l'email

        count += 1
        if count >= (20 * sleep):
            time.sleep(600)
            sleep += 1

    print('Email envoye')
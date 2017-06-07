# coding=utf-8
from ...modules import *
from model_cron import Cron
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from model_cron import Notification



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

                    if ici_cm.idcompagnie.dateExpired():
                        date_auto_nows = ici_cm.idcompagnie.dateExpired().dateFin.strftime("%m/%d/%y")
                        current_date = datetime.datetime.strptime(date_auto_nows, "%m/%d/%y")

                        old_subcription = ici_cm.idcompagnie.dateExpired()
                        old_subcription.etat = 2
                        old_subcription.save()

                    else:
                        time_zones = tzlocal()
                        date_auto_nows = datetime.datetime.now(time_zones).strftime("%m/%d/%y")
                        current_date = datetime.datetime.strptime(date_auto_nows, "%m/%d/%y")

                    ici_cm.dateDebut = function.datetime_convert(current_date)
                    ici_cm.dateFin = current_date + relativedelta(months=int(ici_cm.qte))

                    ici_cm.etat = 1
                    ici_cm.save()

                facture.exe_ici_cm = 1
                facture.save()

            if facture.is_partiel() and facture.montant_reglement(True) > 0: # verifie si le paiement n'est pas pas
                # complet et qu'il y'a un versement qui existe
                if facture.montant >= facture.montant_package_ici_cm(): # verifie que le montant existant est
                    # superieur a la valeur du package ici achete
                    for ici_cm in facture.package_ici_cm():
                        enterprise.append(ici_cm.idcompagnie)

                        if ici_cm.idcompagnie.dateExpired():
                            date_auto_nows = ici_cm.idcompagnie.dateExpired().dateFin.strftime("%m/%d/%y")
                            current_date = datetime.datetime.strptime(date_auto_nows, "%m/%d/%y")
                            
                            old_subcription = ici_cm.idcompagnie.dateExpired()
                            old_subcription.etat = 2
                            old_subcription.save()

                        else:
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


# Execution tous les jours a 01:00 du matin.
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
                ligne.etat = 2
                ligne.save()

    print('Entreprise expiree traite')


# Execution tous les jours a 06:30
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

            days = None
            if enterprise.remaind_day(days=60): # si le temps restant est <= 60 jours avant expiration du package
                if enterprise.remaind_day(days=30): # si le temps restant est <= 30 jours avant expiration du package
                    if enterprise.remaind_day(days=15): # si le temps restant est <= 15 jours avant expiration du
                        # package
                        if enterprise.remaind_day(days=7): # si le temps restant est <= 7 jours avant expiration du
                            # package
                            if enterprise.remaind_day(days=3): # si le temps restant est <= 3 jours avant expiration
                                # du package
                                # envoie de l'email
                                days = 3
                            else:
                                # envoie de l'email
                                days = 7
                        else:
                            # envoie de l'email
                            days = 15
                    else:
                        # envoie de l'email
                        days = 30
                else:
                    # envoie de l'email
                    days = 60

            if days:

                user_mail = enterprise.mainuser

                msg = Message()
                msg.recipients = [enterprise.mainuser.email]
                html = render_template('template_mail/compagnie/relance.html', **locals())
                msg.subject = 'Renouvellement de vos services'
                msg.sender = (info.senderNotification, 'no_reply@ici.cm')

                msg.html = html
                mail.send(msg)

                for user in enterprise.iduser:

                    user_mail = user
                    msg = Message()
                    msg.recipients = [user.email]
                    html = render_template('template_mail/compagnie/relance.html', **locals())
                    msg.subject = 'Renouvellement de vos services'
                    msg.sender = (info.senderNotification, 'no_reply@ici.cm')

                    msg.html = html
                    mail.send(msg)

                notification = Notification()
                notification.title = 'Renouvellement de vos services'
                notification.message = "Votre souscription pour l'entreprise " + enterprise.name + " expire dans" + days + " jours soit le " + function.format_date(enterprise.dateExpired().dataFin, "%d/%m/%Y") + "."
                notification.id_compagnie = enterprise
                notification.save()

        # Envoie email de rappel d'expiration pour les entreprises reclammees
        if enterprise.uploaded and enterprise.claimDate:

            days = None
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
                                    days = 3
                            else:
                                # envoie de l'email
                                days = 7
                        else:
                            # envoie de l'email
                            days = 15
                    else:
                        # envoie de l'email
                        days = 30
                else:
                    # envoie de l'email
                    days = 60

            if days:

                user_mail = enterprise.mainuser

                msg = Message()
                msg.recipients = [enterprise.mainuser.email]
                html = render_template('template_mail/compagnie/relance.html', **locals())
                msg.subject = 'Renouvellement de vos services'
                msg.sender = (info.senderNotification, 'no_reply@ici.cm')

                msg.html = html
                mail.send(msg)

                for user in enterprise.iduser:

                    user_mail = user
                    msg = Message()
                    msg.recipients = [user.email]
                    html = render_template('template_mail/compagnie/relance.html', **locals())
                    msg.subject = 'Renouvellement de vos services'
                    msg.sender = (info.senderNotification, 'no_reply@ici.cm')

                    msg.html = html
                    mail.send(msg)

                notification = Notification()
                notification.title = 'Renouvellement de vos services'
                notification.message = "Votre souscription pour l'entreprise " + enterprise.name + " expire dans" + str(days) + " jours soit le " + function.format_date(enterprise.dateExpired().dataFin, "%d/%m/%Y") + "."
                notification.id_compagnie = enterprise
                notification.save()


        # Envoie des emails au entreprise qui ont leur package expiree
        if enterprise.etat_souscription == 2:

            send = False

            if enterprise.dateExpired().dateFin == function.datetime_convert(current_date) and not enterprise.uploaded:

                send = True

            if enterprise.uploaded and enterprise.etat_souscription == 2:
                enterprise.uploaded = False
                enterprise = enterprise.save()
                send = True

            if send:

                lien_reactivation = "#"

                user_mail = enterprise.mainuser
                html = render_template('template_mail/compagnie/expired_mail.html', **locals())

                msg = Message()
                msg.recipients = [enterprise.mainuser.email]
                msg.subject = 'Suspension de notre service.'
                msg.sender = (info.senderNotification, 'no_reply@ici.cm')

                msg.html = html
                mail.send(msg)

                for user in enterprise.iduser:

                    user_mail = user
                    html = render_template('template_mail/compagnie/expired_mail.html', **locals())

                    msg = Message()
                    msg.recipients = [user.email]
                    msg.subject = 'Suspension de notre service.'
                    msg.sender = (info.senderNotification, 'no_reply@ici.cm')

                    msg.html = html
                    mail.send(msg)

                notification = Notification()
                notification.title = 'Suspension de notre service.'
                notification.message = 'Notre système de facturation a détecté que ce service est expiré, ' \
                                       'non renouvelé malgré les relances que nous avons envoyées. '
                notification.id_compagnie = enterprise
                notification.save()

                # envoie de l'email

        count += 1
        if count >= (20 * sleep):
            time.sleep(600)
            sleep += 1

    print('Email envoye')
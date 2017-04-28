from application.modules import *


def ckeck_etape(opportunite, etape, devis_create=False):
    """

    :type etape: String
    :type opportunite: objectID
    """
    reponse = False
    from ..document.models_doc import Document
    from ..opportunite.models_opportunite import Suivie

    exist_devis = Document.objects(Q(devisDoc=True) & Q(opportunite_id=opportunite.id) & Q(status__lt=3)).count()

    if (etape == global_etape[0] or etape == global_etape[1]) and not exist_devis:
        opportunite.etape = etape
        opportunite.save()
        reponse = True

    if etape == global_etape[2]:
        if devis_create:
            suivie = Suivie.objects(Q(opportunite_id=opportunite.id) & Q(status=False) & Q(sigle_activite__ne='suivre_devis'))
            for suiv in suivie:
                suiv.status = True
                suiv.save()

            opportunite.etape = etape
            opportunite.save()
            reponse = True

    if etape == global_etape[3]:
        if devis_create:
            suivie = Suivie.objects(Q(opportunite_id=opportunite.id) & Q(status=False))
            for suiv in suivie:
                suiv.status = True
                suiv.save()

            opportunite.etape = etape
            opportunite.save()
            reponse = True

    return reponse


def check_status(document):

    from ..opportunite.models_opportunite import Suivie, Activite, Opportunite

    if document.opportunite_id:

        if document.status == 0:

            suivie_devis = Suivie.objects(Q(opportunite_id=document.opportunite_id.id) & Q(status=False) & Q(sigle_activite='suivre_devis'))

            if not suivie_devis:
                suivie = Suivie()

                suivie.etape = global_etape[2]

                suivie.opportunite_id = document.opportunite_id

                first_activite = Activite.objects(Q(sigle='suivre_devis')).get()
                suivie.activite = first_activite.name
                suivie.sigle_activite = 'suivre_devis'

                time_zones = tzlocal()
                date_auto_nows = datetime.datetime.now(time_zones).strftime("%m/%d/%y")
                current_date = datetime.datetime.strptime(date_auto_nows, "%m/%d/%y")

                suivie.dateNext = current_date + datetime.timedelta(days=first_activite.jour)

                suivie.resume = first_activite.name
                suivie.description = first_activite.description

                suivie.status = False
                suivie = suivie.save()

                opp = Opportunite.objects.get(id=document.opportunite_id.id)
                opp.suivie.append(suivie)
                opp.save()

            # si c'est nouveau, changer l'opportunite en proposal
            ckeck_etape(opportunite=document.opportunite_id, etape=global_etape[2], devis_create=True)

        if document.status == 2:
            # si c'est bon de commande, changer l'opportunite a gagne
            ckeck_etape(opportunite=document.opportunite_id, etape=global_etape[3], devis_create=True)

        if document.status == 3:

            suivie_devis = Suivie.objects(Q(opportunite_id=document.opportunite_id.id) & Q(status=False) & Q(sigle_activite='faire_devis'))

            if suivie_devis:

                suivie = Suivie()

                suivie.etape = global_etape[1]

                suivie.opportunite_id = document.opportunite_id

                first_activite = Activite.objects(Q(sigle='faire_devis')).get()
                suivie.activite = first_activite.name
                suivie.sigle_activite = 'faire_devis'

                time_zones = tzlocal()
                date_auto_nows = datetime.datetime.now(time_zones).strftime("%m/%d/%y")
                current_date = datetime.datetime.strptime(date_auto_nows, "%m/%d/%y")

                suivie.dateNext = current_date + datetime.timedelta(days=first_activite.jour)

                suivie.resume = first_activite.name
                suivie.description = first_activite.description

                suivie.status = False
                suivie = suivie.save()

                opp = Opportunite.objects.get(id=document.opportunite_id.id)
                opp.suivie.append(suivie)
                opp.save()

            suivie = Suivie.objects(Q(opportunite_id=document.opportunite_id.id) & Q(status=False) & Q(sigle_activite__ne='faire_devis'))
            for suiv in suivie:
                suiv.status = True
                suiv.save()

            ckeck_etape(opportunite=document.opportunite_id, etape=global_etape[1])

    return 'True'

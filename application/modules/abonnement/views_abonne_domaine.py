# coding=utf-8
from ...modules import *
from ..compagnie.views_compagnie import Compagnie
from ..document.models_doc import LigneDoc

prefix = Blueprint('domaine', __name__)


@prefix.route('/')
@login_required
@roles_required([('super_admin', 'domaine')])
def index():
    title_page = u'Nom de domaine'

    domaine = True

    datas = []
    lignes = LigneDoc.objects(Q(etat=1) & Q(dateFin=None) & Q(iddocument__ne=None) & Q(free=False)).order_by('-dateFin')
    for ligne in lignes:
        if ligne.idpackage.idligneService == 'domaine':
            datas.append(ligne)

    return render_template('abonnement/hosting.html', **locals())


@prefix.route('/valide', methods=['POST'])
@login_required
def valide():

    data = []
    element = []
    count = 0

    item_index = 0
    for item in request.form.getlist('item_id'):

        info = {}
        item_found = LigneDoc.objects().get(id=item)

        if request.form.getlist('date')[item_index]:

            if item_found.idcompagnie.dateExpired_domaine() and item_found.idcompagnie.dateExpired_domaine().dateFin:
                date_auto_nows = item_found.idcompagnie.dateExpired_domaine().dateFin.strftime("%m/%d/%y")
                current_date = datetime.datetime.strptime(date_auto_nows, "%m/%d/%y")

                old_subcription = item_found.idcompagnie.dateExpired_domaine()
                old_subcription.etat = 2
                old_subcription.save()

            else:
                time_zones = tzlocal()
                date_auto_nows = datetime.datetime.now(time_zones).strftime("%m/%d/%y")
                current_date = datetime.datetime.strptime(date_auto_nows, "%m/%d/%y")

            item_found.dateDebut = function.datetime_convert(current_date)
            item_found.dateFin = current_date + relativedelta(months=int(item_found.qte))

            item_found.etat = 1

            item_found.save()

            element.append(str(item_found.id))
            count += 1
        else:

            info['statut'] = 'NOK'
            info['message'] = u'Le nom de domaine de : "' + item_found.idcompagnie.name + u'" ne contient pas de date ' \
                                                                                       u'de debut'
            data.append(info)

        item_index += 1

    if count:
        info = {}
        info['statut'] = 'OK'
        info['message'] = str(count) + ' élément(s) ont été validé avec success.'
        info['element'] = element
        data.append(info)

    data = json.dumps(data)

    return data


@prefix.route('/abonnee')
@login_required
@roles_required([('super_admin', 'domaine')])
def abonne():
    title_page = u'Nom de domaine Abonnée'

    datas = []
    lignes = LigneDoc.objects(Q(etat=1) & Q(dateFin__ne=None) & Q(iddocument__ne=None)).order_by('-dateFin')
    for ligne in lignes:
        if ligne.idpackage.idligneService == 'domaine':
            datas.append(ligne)

    return render_template('abonnement/domaine_abonne.html', **locals())

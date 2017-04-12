__author__ = 'User'

from ...modules import *
from models_doc import Document, LigneDoc
from forms_doc import FormDevis
from ..user.models_user import Users
from ..compagnie.models_compagnie import Compagnie
from ..opportunite.models_opportunite import Opportunite
from ..company.models_company import Config_reference, Company
from ..workflow import *

prefix = Blueprint('devis', __name__)


@prefix.route('/')
@login_required
def index():

    current_ref = Config_reference.objects().first()
    title_page = 'Devis'

    if current_user.has_roles([('super_admin', 'devis')]):
        datas = Document.objects(devisDoc=True)
    else:
        datas = Document.objects(Q(vendeur_id=current_user.id) & Q(devisDoc=True))

    return render_template('devis/index.html', **locals())


@prefix.route('/view/<objectid:devis_id>', methods=['GET'])
def view(devis_id):

    current_ref = Config_reference.objects().first()

    title_page = 'Devis'

    data = Document.objects.get(id=devis_id)

    check_status(data)

    if not current_user.has_roles([('super_admin', 'devis')]) and data.vendeur_id.id != current_user.id:
        return redirect(url_for('devis.index'))

    form = FormDevis(obj=data)

    form.client_id.data = str(data.client_id.id)
    form.support_id.data = str(data.support_id.id)

    form.contact_id.data = str(data.contact_id.id)

    if data.opportunite_id:
        form.opportunite_id.data = str(data.opportunite_id.id)
        form.opportunite_text.data = data.opportunite_id.name

    all = Client.objects(actif=True)
    form.client_id.choices = [('', ' ')]
    for choice in all:
        form.client_id.choices.append((str(choice.id), choice.name))

    all = Support.objects(actif=True)
    form.support_id.choices = [('', ' ')]
    for choice in all:
        form.support_id.choices.append((str(choice.id), choice.name))

    # list_site = []
    lignes = LigneDoc.objects(doc_id=data.id)

    list_pack = {}
    list_pack['current'] = None
    list_pack['all'] = []

    for ligne in lignes:

        id_packs = []
        if len(list_pack['all']):
            id_packs = [str(data_p['id']) for data_p in list_pack['all']]

        if str(ligne.package.id) not in id_packs:

            pack = {}
            pack['id'] = str(ligne.package.id)
            pack['name'] = str(ligne.package.name)
            pack['qte'] = 0
            pack['total'] = 0
            pack['ville'] = []

            ligne_ville = str(ligne.site_id.local_id.parent.id)
            ville = {}
            ville['id'] = ligne_ville
            ville['site'] = []

            site = {}
            site['id'] = str(ligne.site_id.id)
            site['name'] = ligne.site_id.name
            site['ref'] = str(current_ref.ref_site)+'/'+ligne.site_id.ref
            site['qte'] = ligne.passage
            site['prix'] = ligne.cout_passage
            site['total'] = ligne.passage * ligne.cout_passage

            ville['site'].append(site)

            pack['ville'].append(ville)

            pack['total'] += ligne.passage
            pack['qte'] = pack['total'] / ligne.package.passage

            list_pack['all'].append(pack)

        else:

            index_pack = id_packs.index(str(ligne.package.id))
            pack = list_pack['all'][index_pack]

            id_ville = [data_v['id'] for data_v in pack['ville']]
            ligne_ville = str(ligne.site_id.local_id.parent.id)

            if ligne_ville in id_ville:

                index_ville = id_ville.index(ligne_ville)
                packe_ville = pack['ville'][index_ville]

                site = {}
                site['id'] = str(ligne.site_id.id)
                site['name'] = ligne.site_id.name
                site['ref'] = str(current_ref.ref_site)+'/'+ligne.site_id.ref
                site['qte'] = ligne.passage
                site['prix'] = ligne.cout_passage
                site['total'] = ligne.passage * ligne.cout_passage

                packe_ville['site'].append(site)

                pack['total'] += ligne.passage
                pack['qte'] = pack['total'] / ligne.package.passage

            else:

                ville = {}
                ville['id'] = ligne_ville
                ville['site'] = []

                site = {}
                site['id'] = str(ligne.site_id.id)
                site['name'] = ligne.site_id.name
                site['ref'] = str(current_ref.ref_site)+'/'+ligne.site_id.ref
                site['qte'] = ligne.passage
                site['prix'] = ligne.cout_passage
                site['total'] = ligne.passage * ligne.cout_passage

                ville['site'].append(site)

                pack['ville'].append(ville)

                pack['total'] += ligne.passage
                pack['qte'] = pack['total'] / ligne.package.passage

    list_pack = list_pack['all']

    return render_template('devis/view.html', **locals())


@prefix.route('/edit/<objectid:devis_id>', methods=['GET', 'POST'])
@prefix.route('/edit/', methods=['GET', 'POST'])
@login_required
def edit(devis_id=None):

    current_ref = Config_reference.objects().first()

    title_page = 'Devis'

    if devis_id:
        data = Document.objects.get(id=devis_id)

        check_status(data)

        if not current_user.has_roles([('super_admin', 'devis')], ['edit']) and data.vendeur_id.id != current_user.id:
            return redirect(url_for('devis.view', devis_id=devis_id))

        form = FormDevis(obj=data)

        form.client_id.data = str(data.client_id.id)
        form.support_id.data = str(data.support_id.id)
        form.contact_id.data = str(data.contact_id.id)

        if data.opportunite_id:
            form.opportunite_id.data = str(data.opportunite_id.id)
            form.opportunite_text.data = data.opportunite_id.name

    else:
        data = Document()
        form = FormDevis()

    current_opportunite = None
    if request.args.get('opportunite_id'):
        current_opportunite = Opportunite.objects.get(id=request.args.get('opportunite_id'))
        form.opportunite_id.data = str(current_opportunite.id)
        form.opportunite_text.data = str(current_opportunite.name)

    all = Client.objects(actif=True)
    form.client_id.choices = [('', ' ')]
    for choice in all:
        form.client_id.choices.append((str(choice.id), choice.name))

    all = Support.objects(actif=True)
    form.support_id.choices = [('', ' ')]
    for choice in all:
        form.support_id.choices.append((str(choice.id), choice.name))

    list_pack = []
    if not devis_id:
        if session.get('package'):
            list_pack = session.get('package')['all']

            for pack in list_pack:
                if not len(pack['ville']):
                    list_pack.remove(pack)
    else:
        lignes = LigneDoc.objects(doc_id=data.id)

        list_pack = {}
        list_pack['current'] = None
        list_pack['all'] = []

        for ligne in lignes:

            id_packs = []
            if len(list_pack['all']):
                id_packs = [str(data_p['id']) for data_p in list_pack['all']]

            if str(ligne.package.id) not in id_packs:

                pack = {}
                pack['id'] = str(ligne.package.id)
                pack['name'] = str(ligne.package.name)
                pack['qte'] = 0
                pack['total'] = 0
                pack['ville'] = []

                ligne_ville = str(ligne.site_id.local_id.parent.id)
                ville = {}
                ville['id'] = ligne_ville
                ville['site'] = []

                site = {}
                site['id'] = str(ligne.site_id.id)
                site['name'] = ligne.site_id.name
                site['ref'] = str(current_ref.ref_site)+'/'+ligne.site_id.ref
                site['qte'] = ligne.passage
                site['prix'] = ligne.cout_passage
                site['total'] = ligne.passage * ligne.cout_passage

                ville['site'].append(site)

                pack['ville'].append(ville)

                pack['total'] += ligne.passage
                pack['qte'] = pack['total'] / ligne.package.passage

                list_pack['all'].append(pack)

            else:

                index_pack = id_packs.index(str(ligne.package.id))
                pack = list_pack['all'][index_pack]

                id_ville = [data_v['id'] for data_v in pack['ville']]
                ligne_ville = str(ligne.site_id.local_id.parent.id)

                if ligne_ville in id_ville:

                    index_ville = id_ville.index(ligne_ville)
                    packe_ville = pack['ville'][index_ville]

                    site = {}
                    site['id'] = str(ligne.site_id.id)
                    site['name'] = ligne.site_id.name
                    site['ref'] = str(current_ref.ref_site)+'/'+ligne.site_id.ref
                    site['qte'] = ligne.passage
                    site['prix'] = ligne.cout_passage
                    site['total'] = ligne.passage * ligne.cout_passage

                    packe_ville['site'].append(site)

                    pack['total'] += ligne.passage
                    pack['qte'] = pack['total'] / ligne.package.passage

                else:

                    ville = {}
                    ville['id'] = ligne_ville
                    ville['site'] = []

                    site = {}
                    site['id'] = str(ligne.site_id.id)
                    site['name'] = ligne.site_id.name
                    site['ref'] = str(current_ref.ref_site)+'/'+ligne.site_id.ref
                    site['qte'] = ligne.passage
                    site['prix'] = ligne.cout_passage
                    site['total'] = ligne.passage * ligne.cout_passage

                    ville['site'].append(site)

                    pack['ville'].append(ville)

                    pack['total'] += ligne.passage
                    pack['qte'] = pack['total'] / ligne.package.passage

        list_pack = list_pack['all']

    if form.validate_on_submit():

        client = Client.objects.get(id=form.client_id.data)
        data.client_id = client

        support = Support.objects.get(id=form.support_id.data)
        data.support_id = support

        contact = Users.objects.get(id=form.contact_id.data)
        data.contact_id = contact

        data.apply_tva = False
        data.tva_apply = 0
        if 'apply_tva' in request.form:
            data.apply_tva = True
            data.tva_apply = current_ref.taux_tva

        total = 0
        posit = 0
        for item in request.form.getlist('id'):
            montant = float(request.form.getlist('prix')[posit].replace(',','.')) * int(request.form.getlist('qte')[posit])
            total += montant
            posit += 1

        data.montant = total

        data.have_support = False
        if 'have_support' in request.form:
           data.have_support = True

        vendeur = Users.objects.get(id=current_user.id)
        data.vendeur_id = vendeur

        if form.opportunite_id.data:
            opport = Opportunite.objects.get(id=form.opportunite_id.data)
            data.opportunite_id = opport

        if not devis_id:
            count_exist = Document.objects(devisDoc=True).count()
            data.ref = function.reference(count=count_exist+1, caractere=7, refuser=data.vendeur_id.ref)

        data = data.save()

        ## traitement de recuperation du package
        list_site = []
        for pack in list_pack:
            the_pack = Package.objects.get(id=pack['id'])
            for ville in pack['ville']:
                for site in ville['site']:
                    current_site = {}
                    current_site['id'] = site['id']
                    current_site['package'] = str(the_pack.id)
                    list_site.append(current_site)

        id_list_site = [str(site['id']) for site in list_site]

        if not devis_id:
            position = 0
            for item in request.form.getlist('id'):
                ligne = LigneDoc()
                ligne.passage = int(request.form.getlist('qte')[position])
                ligne.cout_passage = float(request.form.getlist('prix')[position].replace(',','.'))
                ligne.doc_id = data

                index_site = id_list_site.index(item)
                packs = Package.objects.get(id=list_site[index_site]['package'])
                ligne.package = packs

                site = Site.objects.get(id=item)
                ligne.site_id = site

                ligne.save()
                position += 1

            session.pop('package')

        flash('Enregistement effectue avec succes', 'success')

        if request.form['nouveau'] == '1':
            check_status(data)
            return redirect(url_for('devis.edit'))
        else:
            return redirect(url_for('devis.view', devis_id=data.id))

    return render_template('devis/edit.html', **locals())


@prefix.route('/add_package/', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'devis')], ['edit'])
def add_package():

    list_package = Package.objects(actif=True)
    # if request.method == 'GET':
    #     session.pop('package')
    success = False
    if request.method == 'POST':

        list_pack = {}
        list_pack['current'] = None
        list_pack['all'] = []

        if session.get('package'):
            list_pack = session.get('package')

        exist = False
        id_packages = [pack['id'] for pack in list_pack['all']]

        index = None
        if request.form['package_id'] in id_packages:
            index = id_packages.index(request.form['package_id'])
            exist = True

        cuurent_pack = Package.objects.get(id=request.form['package_id'])

        if exist:
            list_pack['all'][index]['qte'] += int(request.form['number_package'])
            list_pack['all'][index]['total'] = list_pack['all'][index]['qte'] * cuurent_pack.passage
        else:
            pack = {}
            pack['id'] = str(cuurent_pack.id)
            pack['name'] = str(cuurent_pack.name)
            pack['qte'] = int(request.form['number_package'])
            pack['total'] = pack['qte'] * cuurent_pack.passage
            pack['ville'] = []
            list_pack['all'].append(pack)

        list_pack['current'] = request.form['package_id']

        session['package'] = list_pack
        success = True

    return render_template('devis/add_package.html', **locals())


@prefix.route('/add_site/', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'devis')], ['edit'])
def add_site():

    if request.args.get('package'):
        current = session.get('package')
        current['current'] = request.args.get('package')
        session['package'] = current

    data_ville = Localisation.objects(Q(parent=None) & Q(actif=True))

    data_secteur = Secteur.objects(actif=True)

    data_ecran = Ecran.objects(actif=True)

    if request.method == 'POST':

        current_ref = Config_reference.objects().first()

        list_pack = session.get('package')

        warning = 'NOK'

        if request.form.getlist('item_id'):

            id_package = [pack['id'] for pack in list_pack['all']]

            index = id_package.index(request.form['package_id'])

            total_pack = list_pack['all'][index]['total']

            total_site = 0
            for vill in list_pack['all'][index]['ville']:
                total_site += len(vill['site'])

            if total_site <= total_pack:

                id_ville = [vil['id'] for vil in list_pack['all'][index]['ville']]

                total_site_add = total_site
                for site in request.form.getlist('item_id'):

                    if total_site_add <= total_pack:

                        current_site = Site.objects.get(id=site)

                        ville_site = current_site.local_id.parent.id

                        site = {}
                        site['id'] = str(current_site.id)
                        site['name'] = current_site.name
                        site['ref'] = str(current_ref.ref_site)+'/'+current_site.ref
                        site['qte'] = None
                        site['prix'] = None
                        site['total'] = None

                    if ville_site in id_ville:

                        index_ville = id_ville.index(ville_site)

                        list_pack['all'][index]['ville'][index_ville]['site'].append(site)

                    else:

                        cur_vil = Localisation.objects.get(id=ville_site)

                        the_ville = {}
                        the_ville['id'] = str(cur_vil.id)
                        the_ville['name'] = cur_vil.name
                        the_ville['site'] = []
                        the_ville['site'].append(site)

                        list_pack['all'][index]['ville'].append(the_ville)

                    total_site_add += 1

            total_site_to_add = total_site + len(request.form.getlist('item_id'))

            if total_site_to_add > total_pack:
                warning = 'OK'


        ## Calcul des quantites, prix et du total

        for pack in list_pack['all']:

            the_pack = Package.objects.get(id=pack['id'])
            nbre_passage = the_pack.passage * pack['qte']

            nbre_ville = len(pack['ville'])
            max = passage_by_ville = nbre_passage / nbre_ville
            reste_ville = nbre_passage % nbre_ville

            start_ville = 1
            for ville in pack['ville']:

                nbre_site = len(ville['site'])

                if start_ville == nbre_ville:
                    passage_by_ville += reste_ville

                passage_by_site = passage_by_ville / nbre_site
                reste_site = passage_by_ville % nbre_site

                start = 1
                for site in ville['site']:

                    if start == nbre_site:
                        passage_by_site += reste_site

                    the_site = Site.objects.get(id=site['id'])

                    prix = the_site.ecran_id.cout_passage

                    if the_site.ecran_id.outdoor and the_pack.prix_outdoor:
                        prix = the_pack.prix_outdoor

                    if not the_site.ecran_id.outdoor and the_pack.prix_indoor:
                        prix = the_pack.prix_indoor

                    site['qte'] = passage_by_site
                    site['prix'] = prix
                    total = passage_by_site*prix
                    site['total'] = total
                    start += 1
                start_ville += 1

        session['package'] = list_pack

        datas = json.dumps({
            'statut': 'OK',
            'data': list_pack['all'],
            'warning': warning
        })

        return datas

    return render_template('devis/add_site.html', **locals())


@prefix.route('/add_site/continuer', methods=['POST'])
@login_required
@roles_required([('super_admin', 'devis')], ['edit'])
def add_site_continuer():

    if request.form.getlist('item_id'):

        current_ref = Config_reference.objects().first()

        list_pack = session.get('package')

        id_package = [pack['id'] for pack in list_pack['all']]

        index = id_package.index(request.form['package_id'])

        total_pack = list_pack['all'][index]['total']

        total_site = 0
        for vill in list_pack['all'][index]['ville']:
            total_site += len(vill['site'])

        if total_site <= total_pack:

            id_ville = [vil['id'] for vil in list_pack['all'][index]['ville']]

            total_site_add = total_site
            for site in request.form.getlist('item_id'):

                if total_site_add <= total_pack:

                    current_site = Site.objects.get(id=site)

                    ville_site = str(current_site.local_id.parent.id)

                    site = {}
                    site['id'] = str(current_site.id)
                    site['name'] = current_site.name
                    site['ref'] = str(current_ref.ref_site)+'/'+current_site.ref
                    site['qte'] = None
                    site['prix'] = None
                    site['total'] = None

                    if ville_site in id_ville:

                        index_ville = id_ville.index(ville_site)

                        list_pack['all'][index]['ville'][index_ville]['site'].append(site)

                    else:
                        cur_vil = Localisation.objects.get(id=ville_site)

                        the_ville = {}
                        the_ville['id'] = str(cur_vil.id)
                        the_ville['name'] = cur_vil.name
                        the_ville['site'] = []

                        the_ville['site'].append(site)

                        list_pack['all'][index]['ville'].append(the_ville)

                    total_site_add += 1

        session['package'] = list_pack

        total_site_to_add = total_site + len(request.form.getlist('item_id'))

        if total_site_to_add > total_pack:
            datas = json.dumps({
                'statut': 'warning'
            })
        else:
            datas = json.dumps({
                'statut': 'OK'
            })
    else:
        datas = json.dumps({
            'statut': 'error'
        })

    return datas


@prefix.route('/find/quartier/', methods=['POST'])
def find_quartier():

    ville_id = str(request.json['ville'])
    quartiers = Localisation.objects(Q(parent=ville_id) & Q(actif=True))

    list = []

    for quartier in quartiers:
        current = {}
        current['id'] = str(quartier.id)
        current['name'] = quartier.name
        list.append(current)

    data = json.dumps({
        'statut': 'OK',
        'data': list
    })

    return data


@prefix.route('/find/offre/', methods=['POST'])
def find_offre():

    ecran_id = str(request.json['ecran'])
    ecran = Ecran.objects.get(id=ecran_id)

    # list = []
    #
    # for data in ecran.package:
    #     if data.actif:
    #         current = {}
    #         current['id'] = str(data.id)
    #         current['name'] = data.name
    #         list.append(current)

    if ecran.multi_choice:
        multi = 1
    else:
        multi = 0

    datas = json.dumps({
        'statut': 'OK',
        'ecran': multi,
        # 'data': list
    })

    return datas


@prefix.route('/find/site/', methods=['POST'])
def find_site():

    ville_id = str(request.json['ville'])
    ecran_id = str(request.json['ecran'])
    quartier_id = str(request.json['quartier'])
    secteur_id = str(request.json['secteur'])

    package_id = str(request.json['package'])

    sites = recherche(ville=ville_id, quartier=quartier_id, secteur=secteur_id, ecran=ecran_id)

    list_pack = session.get('package')
    id_exist = []
    if list_pack['all']:
        id_exist = [str(data['id']) for pack in list_pack['all'] if pack['id'] == package_id for ville in pack['ville'] for data in ville['site'] ]

    list = []

    for data in sites:
        current = {}
        current['id'] = str(data.id)
        current['name'] = data.name
        current['type'] = data.type
        if str(data.id) in id_exist:
            current['check'] = 1
        else:
            current['check'] = 0
        list.append(current)

    datas = json.dumps({
        'statut': 'OK',
        'data': list,
        'test': id_exist
    })

    return datas


@prefix.route('/search/site', methods=['POST'])
def search_site():

    ville_id = str(request.form['ville'])
    ecran_id = str(request.form['ecran'])
    quartier_id = str(request.form['quartier'])
    secteur_id = str(request.form['secteur'])

    current_ref = Config_reference.objects().first()

    datas = []

    sites = recherche(ville=ville_id, quartier=quartier_id, secteur=secteur_id, ecran=ecran_id)

    for site in sites:
        data = {}
        data['id'] = str(site.id)
        data['name'] = site.name
        data['ref'] = str(current_ref.ref_site)+'/'+site.ref
        data['longitude'] = site.longitude
        data['latitude'] = site.latitude
        data['ecran'] = site.ecran_id.name
        data['activite'] = site.secteur_id.name
        data['type'] = site.type
        data['ville'] = site.local_id.name
        data['image'] = None
        datas.append(data)

    datas = json.dumps(datas)

    return datas

@prefix.route('/infos/map', methods=['POST'])
def infobox():

    id = request.form['id']

    site = Site.objects.get(id=id)

    return render_template('devis/infobox.html', **locals())



@prefix.route('/delete/item/<int:pack>/<int:ville>/<int:item>', methods=['GET'])
@prefix.route('/delete/item/<int:pack>/', methods=['GET'])
@prefix.route('/delete/item/', methods=['GET'])
def delete_item(pack=None, ville=None, item=None):

    list_pack = session.get('package')['all']

    if not item and not ville:
        list_pack.pop(pack)
    else:
        list_pack[pack]['ville'][ville]['site'].pop(item)

        if len(list_pack[pack]['ville'][ville]['site']) == 0:
            list_pack[pack]['ville'].pop(ville)

            if len(list_pack[pack]['ville']) == 0:
                list_pack.pop(pack)

    for pack in list_pack:

        the_pack = Package.objects.get(id=pack['id'])
        nbre_passage = the_pack.passage * pack['qte']

        nbre_ville = len(pack['ville'])
        max = passage_by_ville = nbre_passage / nbre_ville
        reste_ville = nbre_passage % nbre_ville

        start_ville = 1
        for ville in pack['ville']:

            nbre_site = len(ville['site'])

            if start_ville == nbre_ville:
                passage_by_ville += reste_ville

            passage_by_site = passage_by_ville / nbre_site
            reste_site = passage_by_ville % nbre_site

            start = 1
            for site in ville['site']:

                if start == nbre_site:
                    passage_by_site += reste_site

                the_site = Site.objects.get(id=site['id'])

                prix = the_site.ecran_id.cout_passage

                if the_site.ecran_id.outdoor and the_pack.prix_outdoor:
                    prix = the_pack.prix_outdoor

                if not the_site.ecran_id.outdoor and the_pack.prix_indoor:
                    prix = the_pack.prix_indoor

                site['qte'] = passage_by_site
                site['prix'] = prix
                total = passage_by_site*prix
                site['total'] = total
                site['max'] = max + reste_ville
                start += 1
            start_ville += 1


    session.get('package')['all'] = list_pack

    datas = json.dumps({
        'statut': 'OK',
        'data': list_pack
    })

    return datas


@prefix.route('/change/<objectid:devis_id>/<int:status>', methods=['GET'])
def change_satus(devis_id, status):

    data = Document.objects.get(id=devis_id)

    if not current_user.has_roles([('super_admin', 'devis')], ['edit']) and data.vendeur_id.id != current_user.id:
        flash('Vous n\'avez pas les droits necessaires sur ce devis', 'success')
        return redirect(url_for('devis.view', devis_id=devis_id))

    data.status = status

    data.save()

    flash('Enregistement effectue avec succes', 'success')
    return redirect(url_for('devis.view', devis_id=devis_id))


@prefix.route('/canceled', methods=['POST'])
@login_required
@roles_required([('super_admin', 'devis')], ['edit'])
def canceled():

    count = 0
    data = []
    element = []
    for item in request.form.getlist('item_id'):

        item_found = Document.objects.get(id=item)
        item_found.status = 3
        item_found.save()

        # element.append(str(item_found.id))
        count += 1

    if count:
        info = {}
        info['statut'] = 'OK'
        info['message'] = str(count)+' element(s) ont ete modifie avec success'
        info['element'] = element
        data.append(info)

    data = json.dumps(data)

    return data


@prefix.route('/notification/support')
def notification_support():

    all_document = Document.objects(Q(have_support=False) & Q(notif_support=False))

    # for document in all_document:

    return 'True'


@prefix.route('/print/<objectid:devis_id>', methods=['GET'])
def print_devis(devis_id):

    current_ref = Config_reference.objects().first()
    compagnie = Company.objects.first()

    data = Document.objects.get(id=devis_id)

    CURRENT_FILE = os.path.abspath(__file__)
    CURRENT_DIR = os.path.dirname(CURRENT_FILE)
    PROJECT_DIR = os.path.dirname(CURRENT_DIR)
    PROJECT_DIR = os.path.dirname(PROJECT_DIR)

    image = PROJECT_DIR+'/static/images/logo.jpeg'

    word = PROJECT_DIR+'/static/images/icon/word.png'
    facebook = PROJECT_DIR+'/static/images/icon/facebook.png'
    twitter = PROJECT_DIR+'/static/images/icon/tweeter.png'

    rendered = render_template('document/document.html', **locals())
    css = [
        PROJECT_DIR+'/static/css/uikit-new.css',
        PROJECT_DIR+'/static/css/lato-font.css',
        PROJECT_DIR+'/static/css/roboto.css',
        PROJECT_DIR+'/static/css/material-icon.css',
        PROJECT_DIR+'/static/css/apps.css',
        PROJECT_DIR+'/static/css/pdf.css',
    ]

    pdfs = pdfkit.from_string(
        rendered, False,
        css=css,
        options={
            'page-size': 'A4',
            # 'margin-top': '0',
            'margin-right': '0',
            'margin-left': '0',
            'margin-bottom': '0',
            'zoom': '0.8',
            'encoding': "UTF-8",

        })

    response = make_response(pdfs)
    response.headers['Content-Type'] = 'application.pdf'
    response.headers['Content-Disposition'] = 'inline; filename='+data.ref+'.pdf'
    # response.headers['Content-Disposition'] = 'attach; filename=output.pdf'

    if data.status == 0:
        data.status = 1
        data.save()

    return response



@prefix.route('/print2/<objectid:devis_id>', methods=['GET'])
def print2_devis(devis_id):

    CURRENT_FILE = os.path.abspath(__file__)
    CURRENT_DIR = os.path.dirname(CURRENT_FILE)
    PROJECT_DIR = os.path.dirname(CURRENT_DIR)
    PROJECT_DIR = os.path.dirname(PROJECT_DIR)

    image = PROJECT_DIR+'/static/images/logo.jpeg'

    word = PROJECT_DIR+'/static/images/icon/word.png'
    facebook = PROJECT_DIR+'/static/images/icon/facebook.png'
    tweeter = PROJECT_DIR+'/static/images/icon/tweeter.png'

    rendered = render_template('document/document2.html', **locals())
    css = [
        PROJECT_DIR+'/static/css/uikit-new.css',
        PROJECT_DIR+'/static/css/lato-font.css',
        PROJECT_DIR+'/static/css/roboto.css',
        PROJECT_DIR+'/static/css/material-icon.css',
        PROJECT_DIR+'/static/css/apps.css',
        PROJECT_DIR+'/static/css/pdf.css',
    ]
    # # pdf = pdfkit.from_file(rendered, 'output.pdf')
    pdfs = pdfkit.from_string(
        rendered, False,
        css=css,
        options={
            'page-size': 'A4',
            # 'margin-top': '0',
            'margin-right': '0',
            'margin-left': '0',
            'margin-bottom': '0',
            # 'zoom': '1.2',
            'encoding': "UTF-8",
            'header-right': '[page]'


        })

    response = make_response(pdfs)
    response.headers['Content-Type'] = 'application.pdf'
    response.headers['Content-Disposition'] = 'inline; filename=output.pdf'
    # response.headers['Content-Disposition'] = 'attach; filename=output.pdf'

    return response


def recherche(ville, quartier, secteur, ecran):

    site_found = []

    if ville:

        if quartier:

            if secteur:
                if ecran:
                    site_found = Site.objects(Q(ecran_id=ecran) & Q(local_id=quartier) & Q(secteur_id=secteur) & Q(actif=True))
                else:
                    site_found = Site.objects(Q(local_id=quartier) & Q(secteur_id=secteur) & Q(actif=True))
            else:
                if ecran:
                    site_found = Site.objects(Q(local_id=quartier) & Q(ecran_id=ecran) & Q(actif=True))
                else:
                    site_found = Site.objects(Q(local_id=quartier) & Q(actif=True))

        else:

            if secteur:
                if ecran:
                    site_found = Site.objects(Q(secteur_id=secteur) & Q(ecran_id=ecran) & Q(actif=True))
                else:
                    site_found = Site.objects(Q(secteur_id=secteur) & Q(actif=True))
            else:
                if ecran:
                    site_found = Site.objects(Q(ecran_id=ecran) & Q(actif=True))
                else:
                    quartiers = Localisation.objects(parent=ville)
                    for quartier in quartiers:
                        current = Site.objects(local_id=quartier)
                        for site in current:
                            if site.actif:
                                site_found.append(site)

    else:

        if secteur:
            if ecran:
                site_found = Site.objects(Q(secteur_id=secteur) & Q(ecran_id=ecran) & Q(actif=True))
            else:
                site_found = Site.objects(Q(secteur_id=secteur) & Q(actif=True))
        else:
            if ecran:
                site_found = Site.objects(Q(ecran_id=ecran) & Q(actif=True))

    return site_found






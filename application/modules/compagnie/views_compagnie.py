__author__ = 'User'

from ...modules import *
from forms_compagnie import FormClient
from models_compagnie import Compagnie, Categorie
from ..user.models_user import Users

prefix = Blueprint('client', __name__)


@prefix.route('/')
@login_required
def index():
    title_page = 'Clients'

    datas = Compagnie.objects(activated=True)

    return render_template('client/index.html', **locals())


@prefix.route('/new')
@login_required
def new():
    title_page = 'Nouveaux Clients'

    news = '1'
    datas = Compagnie.objects(activated=False)

    return render_template('client/index.html', **locals())


@prefix.route('/view/<objectid:client_id>')
@login_required
def view(client_id):

    if request.args.get('news'):
        title_page = 'Nouveaux Client'
    else:
        title_page = 'Clients'

    data = Compagnie.objects.get(id=client_id)
    form = FormClient(obj=data)
    form.id.data = client_id

    return render_template('client/view.html', **locals())


@prefix.route('/edit/<objectid:client_id>', methods=['GET', 'POST'])
@prefix.route('/edit/', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'client')], ['edit'])
def edit(client_id=None):

    if request.args.get('news'):
        title_page = 'Nouveaux Client'
    else:
        title_page = 'Clients'

    if client_id:
        data = Compagnie.objects.get(id=client_id)
        form = FormClient(obj=data)
        form.id.data = client_id

        form.idcategorie.data = [str(cat.id) for cat in data.idcategorie]

        form.maincategorie.choices = [('', 'Faite le choix de la categorie principale')]

        if request.method == 'GET':

            form.maincategorie.data = str(data.maincategorie.id)

            for choice in data.idcategorie:
                form.maincategorie.choices.append((str(choice.id), choice.name))
    else:
        data = Compagnie()
        form = FormClient()

    all = Categorie.objects(Q(activated=True) & Q(parent_idcategorie__ne=None))

    form.idcategorie.choices = [('', '')]
    for choice in all:
        form.idcategorie.choices.append((str(choice.id), choice.name))

    if not client_id:
        form.maincategorie.choices = [('', 'Faite le choix de la categorie principale')]

    for idchoice in request.form.getlist('idcategorie'):
        choice = Categorie.objects.get(id=idchoice)
        form.maincategorie.choices.append((str(choice.id), choice.name))

    if form.validate_on_submit():

        data.raison = form.raison.data
        data.name = form.name.data
        data.ville = form.ville.data
        data.quartier = form.quartier.data
        data.adresse = form.adresse.data
        data.postal_code = form.postal_code.data
        data.repere = form.repere.data

        data.email = form.email.data
        data.phone = form.phone.data
        data.description = form.description.data
        data.urlsite = form.urlsite.data

        data.latitude = form.latitude.data
        data.longitude = form.longitude.data

        data.facebook = form.facebook.data
        data.twitter = form.twitter.data
        data.linkedin = form.linkedin.data
        data.youtube = form.youtube.data

        old_categorie = data.idcategorie
        data.idcategorie = []

        for cat_id in request.form.getlist('idcategorie'):

            the_cat = Categorie.objects.get(id=cat_id)

            data.idcategorie.append(the_cat)

        principale = Categorie.objects.get(id=form.maincategorie.data)
        data.maincategorie = principale

        data = data.save()

        ## verifier que les nouvelles categories ont les informations de l'entreprise cours
        for cat_id in request.form.getlist('idcategorie'):

            the_cat = Categorie.objects.get(id=cat_id)

            if data not in the_cat.idcomapagnie:
                the_cat.idcomapagnie.append(data)
                the_cat.save()

        ## Enlever les informations de l'entreprise dans les anciennes categories qui ne l'appartienne
        for old_cat in old_categorie:
            if old_cat not in data.idcategorie:
                old_c = Categorie.objects(id=old_cat.id)
                old_c.update_one(pull__idcomapagnie=data)

        flash('Enregistement effectue avec succes', 'success')
        return redirect(url_for('client.view', client_id=data.id, news=request.args.get('news')))

    return render_template('client/edit.html', **locals())


@prefix.route('/deleted', methods=['POST'])
@login_required
@roles_required([('super_admin', 'client')], ['delete'])
def deleted():
    from ..opportunite.models_opportunite import Opportunite
    from ..document.models_doc import Document

    data = []
    element = []
    count = 0
    for item in request.form.getlist('item_id'):
        info = {}
        item_found = Compagnie.objects().get(id=item)
        opportunite = Opportunite.objects(client_id=item_found)

        if opportunite:
            info['statut'] = 'NOK'
            info['message'] = 'Le Client "' + item_found.name + '" est utilise par ' + str(
                opportunite.count()) + ' autre(s) opportunite(s)'

        exit_suivie = Document.objects(client_id=item_found)
        if exit_suivie:
            info['statut'] = 'NOK'
            info['message'] = 'Le Client "' + item_found.name + '" est utilise par ' + str(
                exit_suivie.count()) + ' autre(s) Documents(s)'

        if not item_found.uploaded:
            info['statut'] = 'NOK'
            info['message'] = 'Le Client "' + item_found.name + '" ne peut pas etre supprime car il n\'a pas ete ajoute' \
                                                                'manuellement '

        if not opportunite and not exit_suivie and item_found.uploaded:
            item_found.delete()
            element.append(str(item_found.id))
            count += 1
        else:
            data.append(info)

    if count:
        info = {}
        info['statut'] = 'OK'
        info['message'] = str(count) + ' element(s) ont ete supprime avec success'
        info['element'] = element
        data.append(info)

    data = json.dumps(data)

    return data


@prefix.route('/reload/categorie', methods=['POST'])
def reload_categorie():
    list = []

    idcategorie = request.json['data']

    for data in idcategorie:
        current_cat = Categorie.objects.get(id=data)
        current = {}
        current['id'] = str(current_cat.id)
        current['name'] = current_cat.name
        list.append(current)

    datas = json.dumps({
        'statut': 'OK',
        'data': list
    })

    return datas


@prefix.route('/activated', methods=['POST'])
@login_required
@roles_required([('super_admin', 'client')], ['edit'])
def etat_activated():

    data = []
    element = []
    count = 0
    for item in request.form.getlist('item_id'):
        info = {}
        item_found = Compagnie.objects().get(id=item)

        if item_found.activated:
            info['statut'] = 'NOK'
            info['message'] = 'L\'entreprise "'+item_found.name+'" est deja active'

        if not item_found.activated:
            item_found.activated = True
            element.append(str(item_found.id))
            item_found.save()
            count += 1
        else:
            data.append(info)

    if count:
        info = {}
        info['statut'] = 'OK'
        info['message'] = str(count)+' element(s) ont ete active avec success'
        info['element'] = element
        data.append(info)

    data = json.dumps(data)

    return data


@prefix.route('/unactivated', methods=['POST'])
@login_required
@roles_required([('super_admin', 'client')], ['edit'])
def etat_unactivated():

    data = []
    element = []
    count = 0
    for item in request.form.getlist('item_id'):
        info = {}
        item_found = Compagnie.objects().get(id=item)

        if not item_found.activated:
            info['statut'] = 'NOK'
            info['message'] = 'L\'entreprise "'+item_found.name+'" est deja desactive'

        if item_found.activated:
            item_found.activated = False
            element.append(str(item_found.id))
            item_found.save()
            count += 1
        else:
            data.append(info)

    if count:
        info = {}
        info['statut'] = 'OK'
        info['message'] = str(count)+' element(s) ont ete desactive avec success'
        info['element'] = element
        data.append(info)

    data = json.dumps(data)

    return data


@prefix.route('/etat/<objectid:client_id>')
@login_required
@roles_required([('super_admin', 'client')], ['edit'])
def etat(client_id):
    client = Compagnie.objects.get(id=client_id)
    if client.activated:
        client.activated = False
    else:
        client.activated = True

    client.save()

    flash('Les modifications de l\'etat du client ont ete effectue', 'success')
    return redirect(url_for('client.view', client_id=client_id, news=request.args.get('news')))


# @prefix.route('/find/customer/<objectid:customer_id>', methods=['GET','POST'])
@prefix.route('/find/customer/', methods=['POST'])
def find_customer():
    customer_id = str(request.json['client'])

    customer = Compagnie.objects.get(id=customer_id)

    data = json.dumps({
        'id': str(customer.id),
        'name': customer.name,
        'email': customer.email,
        'phone': customer.phone,
        'raison': customer.raison,
        'secteur_id': str(customer.secteur_id.id),
        'statut': 'OK'
    })

    return data


@prefix.route('/find/customer/contact', methods=['POST'])
def find_contact():
    customer_id = str(request.json['client'])

    customer = Compagnie.objects.get(id=customer_id)
    customer = customer.contact

    list = []

    for data in customer:
        current = {}
        current['id'] = str(data.user_id.id)
        # current['civilite'] = str(data.user_id.civilite.id)
        current['first_name'] = data.user_id.first_name
        current['last_name'] = data.user_id.last_name
        current['fonction'] = None
        if data.user_id.fonction:
            current['fonction'] = '(' + data.user_id.fonction + ')'
        # current['email'] = data.user_id.email
        # current['mobile'] = data.user_id.mobile
        # current['telephone'] = data.user_id.telephone
        list.append(current)

    datas = json.dumps({
        'statut': 'OK',
        'data': list
    })

    return datas


@prefix.route('/find/contact/', methods=['POST'])
def find_single_contact():
    customer_id = str(request.json['contact'])

    customer = Users.objects.get(id=customer_id)

    civilite = ''
    if customer.civilite:
        civilite = customer.civilite.id

    data = json.dumps({
        'id': str(customer.id),
        'civilite': str(civilite),
        'first_name': customer.first_name,
        'last_name': customer.last_name,
        'fonction': customer.fonction,
        'email': customer.email,
        'mobile': customer.mobile,
        'telephone': customer.telephone,
        'statut': 'OK'
    })

    return data







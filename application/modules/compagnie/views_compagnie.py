__author__ = 'User'


from ...modules import *
from forms_compagnie import FormClient
from models_compagnie import Compagnie
from ..site.models_site import Secteur
from ..user.forms_user import FormUser


prefix = Blueprint('client', __name__)


@prefix.route('/')
@login_required
def index():

    title_page = 'Clients'

    datas = Compagnie.objects()

    return render_template('client/index.html', **locals())


@prefix.route('/view/<objectid:client_id>')
@login_required
def view(client_id):

    title_page = 'Clients'

    data = Client.objects().get(id=client_id)
    form = FormClient(obj=data)
    form.secteur_id.data = str(data.secteur_id.id)

    all = Secteur.objects(actif=True)
    form.secteur_id.choices = [('', ' ')]
    for choice in all:
        form.secteur_id.choices.append((str(choice.id), choice.name))

    return render_template('client/view.html', **locals())


@prefix.route('/edit/<objectid:client_id>', methods=['GET', 'POST'])
@prefix.route('/edit/', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'client')], ['edit'])
def edit(client_id=None):

    title_page = 'Clients'

    if client_id:
        data = Client.objects.get(id=client_id)
        form = FormClient(obj=data)
        form.id.data = client_id
        form.secteur_id.data = str(data.secteur_id.id)
    else:
        data = Client()
        form = FormClient()

    all = Secteur.objects(actif=True)
    form.secteur_id.choices = [('', ' ')]
    for choice in all:
        form.secteur_id.choices.append((str(choice.id), choice.name))

    if form.validate_on_submit():

        data.raison = form.raison.data
        data.name = form.name.data
        data.email = form.email.data
        data.phone = form.phone.data
        data.ville = form.ville.data
        data.quartier = form.quartier.data
        data.urlsite = form.urlsite.data
        data.client = True
        data.fournisseur = False
        data.adress = form.adress.data
        data.bp = form.bp.data
        data.rue = form.rue.data

        secteur = Secteur.objects.get(id=form.secteur_id.data)
        data.secteur_id = secteur

        data = data.save()

        flash('Enregistement effectue avec succes', 'success')
        return redirect(url_for('client.view', client_id=data.id))

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
        item_found = Client.objects().get(id=item)
        opportunite = Opportunite.objects(client_id=item_found)

        if opportunite:
            info['statut'] = 'NOK'
            info['message'] = 'Le Client "'+item_found.name+'" est utilise par '+str(opportunite.count())+' autre(s) opportunite(s)'

        exit_suivie = Document.objects(client_id=item_found)
        if exit_suivie:
            info['statut'] = 'NOK'
            info['message'] = 'Le Client "'+item_found.name+'" est utilise par '+str(exit_suivie.count())+' autre(s) Documents(s)'

        if not opportunite and not exit_suivie:
            item_found.delete()
            element.append(str(item_found.id))
            count += 1
        else:
            data.append(info)

    if count:
        info = {}
        info['statut'] = 'OK'
        info['message'] = str(count)+' element(s) ont ete supprime avec success'
        info['element'] = element
        data.append(info)

    data = json.dumps(data)

    return data


@prefix.route('/contact/view/<objectid:contact_id>')
@login_required
@roles_required([('super_admin', 'client')])
def contact_view(contact_id):

    title_page = 'Clients'

    data = Users.objects.get(id=contact_id)
    form = FormUser(obj=data)
    form.id.data = str(data.id)
    if data.civilite:
        form.civilite.data = str(data.civilite.id)

    all = Civilite.objects()
    form.civilite.choices = [('', 'Choisir la civilite ')]
    for choice in all:
        form.civilite.choices.append((str(choice.id), choice.name))

    return render_template('contact/view.html', **locals())


@prefix.route('/contact/edit/<objectid:client_id>/<objectid:contact_id>', methods=['GET', 'POST'])
@prefix.route('/contact/edit/<objectid:client_id>', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'client')], ['edit'])
def contact_edit(client_id, contact_id=None):

    title_page = 'Clients'

    if contact_id:
        data = Users.objects.get(id=contact_id)
        form = FormUser(obj=data)
        form.id.data = str(data.id)
        if data.civilite:
            form.civilite.data = str(data.civilite.id)
    else:
        data = Users()
        form = FormUser()

    all = Civilite.objects()
    form.civilite.choices = [('', ' Choisir la civilite ')]
    for choice in all:
        form.civilite.choices.append((str(choice.id), choice.name))

    success = False
    if form.validate_on_submit():

        data.first_name = form.first_name.data
        data.last_name = form.last_name.data
        data.email = form.email.data

        if form.civilite.data:
            civilite = Civilite.objects(id=form.civilite.data).first()
            data.civilite = civilite

        data.fonction = form.fonction.data
        data.mobile = form.mobile.data
        data.telephone = form.telephone.data
        data.note = form.note.data

        data = data.save()

        if not contact_id:
            current_client = Client.objects.get(id=client_id)
            contact_compagnie = CompagniUser()
            contact_compagnie.user_id = data
            current_client.contact.append(contact_compagnie)
            current_client.save()

        success = True

    return render_template('contact/edit.html', **locals())


# @prefix.route('/find/customer/<objectid:customer_id>', methods=['GET','POST'])
@prefix.route('/find/customer/', methods=['POST'])
def find_customer():
    customer_id = str(request.json['client'])

    customer = Client.objects.get(id=customer_id)

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

    customer = Client.objects.get(id=customer_id)
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
            current['fonction'] = '('+data.user_id.fonction+')'
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


@prefix.route('/contact/deleted', methods=['POST'])
@login_required
@roles_required([('super_admin', 'client')], ['delete'])
def contact_deleted():

    from ..opportunite.models_opportunite import Opportunite
    from ..document.models_doc import Document
    from ..user.models_user import Users

    data = []
    element = []
    count = 0
    for item in request.form.getlist('item_id'):
        info = {}
        item_found = Users.objects().get(id=item)
        opportunite = Opportunite.objects(contact_id=item_found)

        if opportunite:
            info['statut'] = 'NOK'
            info['message'] = 'Le contact "'+item_found.first_name+' '+item_found.last_name+'" est utilise par '+str(opportunite.count())+' autre(s) opportunite(s)'

        exit_suivie = Document.objects(contact_id=item_found)
        if exit_suivie:
            info['statut'] = 'NOK'
            info['message'] = 'Le contact "'+item_found.first_name+' '+item_found.last_name+'" est utilise par '+str(exit_suivie.count())+' autre(s) Documents(s)'


        if not opportunite and not exit_suivie:
            item_found.delete()
            element.append(str(item_found.id))
            count += 1
        else:
            data.append(info)

    if count:
        info = {}
        info['statut'] = 'OK'
        info['message'] = str(count)+' element(s) ont ete supprime avec success'
        info['element'] = element
        info['reload'] = 1
        data.append(info)

    data = json.dumps(data)

    return data

@prefix.route('/etat/<objectid:client_id>')
@login_required
@roles_required([('super_admin', 'client')], ['edit'])
def etat(client_id):

    client = Client.objects.get(id=client_id)
    if client.actif:
        client.actif = False
    else:
        client.actif = True

    client.save()

    flash('Les modifications de l\'etat du client ont ete effectue', 'success')
    return redirect(url_for('client.edit', client_id=client_id))
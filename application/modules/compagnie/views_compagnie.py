__author__ = 'User'

from ...modules import *
from forms_compagnie import FormClient
from models_compagnie import Compagnie, Categorie
from ..user.models_user import Users

prefix = Blueprint('client', __name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@prefix.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER_CLIENT'],
                               filename, as_attachment=True)


@prefix.route('/')
@login_required
def index():
    title_page = 'Clients'

    for newer in Compagnie.objects():
        if not newer.partenaire:
            newer.partenaire = False
            newer.save()

    datas = Compagnie.objects(verify=True)

    return render_template('client/index.html', **locals())


@prefix.route('/new')
@login_required
def new():
    title_page = 'Nouveaux Clients'

    news = '1'
    datas = Compagnie.objects(verify=False)

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

        old_name = None
        if client_id:
            old_name = data.name

        data.raison = form.raison.data
        data.name = form.name.data
        data.ville = form.ville.data
        data.quartier = form.quartier.data
        data.adresse = form.adresse.data
        data.postal_code = form.postal_code.data
        data.repere = form.repere.data
        data.region = form.region.data

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

        if not client_id:
            data.source = "creation CRM"
            data.verify = False
            data.activated = False

        old_categorie = data.idcategorie
        data.idcategorie = []

        for cat_id in request.form.getlist('idcategorie'):
            the_cat = Categorie.objects.get(id=cat_id)

            data.idcategorie.append(the_cat)

        principale = Categorie.objects.get(id=form.maincategorie.data)
        data.maincategorie = principale

        error_file = False
        file = request.files['file']

        if file:

            if old_name:
                old_rename = function._slugify(old_name)
            else:
                old_rename = function._slugify(data.name)

            if not data.imagedir:
                import calendar
                time_zones = tzlocal()
                date_auto_nows = datetime.datetime.now(time_zones)

                current_date = date_auto_nows
                current_date = calendar.timegm(current_date.utctimetuple())
                current_date = str(current_date).encode('base64').rstrip()
                os.makedirs(os.path.join(app.config['UPLOAD_FOLDER_CLIENT'], current_date))
                data.imagedir = current_date

            url_dossier = os.path.join(app.config['UPLOAD_FOLDER_CLIENT'], data.imagedir)

            if allowed_file(file.filename):

                if data.logo and request.form['url_image_change'] == '1' and client_id:
                    os.remove(os.path.join(url_dossier, data.url_image))

                filename = secure_filename(file.filename)
                file.save(os.path.join(url_dossier, filename))

                extension = filename.split(".")
                extension = extension[1]

                source = os.path.join(url_dossier, filename)
                destination = url_dossier + "/logo-" + old_rename + "." + extension

                os.rename(source, destination)

                link_save_file = "/logo-" + old_rename + "." + extension
                data.logo = data.imagedir + link_save_file

            else:
                flash('Le systeme n\'accepte que les images au format .png, .jpg ou .jpeg', 'warning')
                error_file = True

        if not error_file:

            data = data.save()

            ## verifier que les nouvelles categories ont les informations de l'entreprise cours
            for cat_id in request.form.getlist('idcategorie'):

                the_cat = Categorie.objects.get(id=cat_id)

                if data not in the_cat.compagnie:
                    the_cat.compagnie.append(data)
                    the_cat.save()

            ## Enlever les informations de l'entreprise dans les anciennes categories qui ne l'appartienne
            for old_cat in old_categorie:
                if old_cat not in data.idcategorie:
                    old_c = Categorie.objects(id=old_cat.id)
                    old_c.update_one(pull__compagnie=data)

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
            info['message'] = 'L\'entreprise "' + item_found.name + '" est deja active'

        if not item_found.activated:
            item_found.activated = True
            if not item_found.verify:
                item_found.verify = True
            element.append(str(item_found.id))
            item_found.save()
            count += 1
        else:
            data.append(info)

    if count:
        info = {}
        info['statut'] = 'OK'
        info['message'] = str(count) + ' element(s) ont ete active avec success'
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
            info['message'] = 'L\'entreprise "' + item_found.name + '" est deja desactive'

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
        info['message'] = str(count) + ' element(s) ont ete desactive avec success'
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
        if not client.verify:
            client.verify = True

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
        'ville': customer.ville,
        'quartier': customer.quartier,
        'statut': 'OK'
    })

    return data


@prefix.route('/find/customer/contact', methods=['POST'])
def find_contact():
    customer_id = str(request.json['client'])

    customer = Compagnie.objects.get(id=customer_id)

    list = []

    for data in customer.relation():
        current = {}
        current['id'] = str(data.id)
        current['first_name'] = data.first_name
        current['last_name'] = data.last_name
        current['fonction'] = ''
        if data.fonction:
            current['fonction'] = '(' + data.fonction + ')'
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

    data = json.dumps({
        'id': str(customer.id),
        'first_name': customer.first_name,
        'last_name': customer.last_name,
        'fonction': customer.fonction,
        'email': customer.email,
        'phone': customer.phone,
        'statut': 'OK'
    })

    return data


@prefix.route('/edit/special', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'client')], ['edit'])
def edit_special():
    title_page = 'Clients'

    if request.args.get('partenaire'):
        datas = Compagnie.objects(Q(partenaire__exists=0) | Q(partenaire=0) | Q(partenaire=1) & Q(verify=True) & Q(activated=True))
        title_page += '- Partenaires'
    else:
        datas = Compagnie.objects(Q(partenaire__exists=0) | Q(partenaire__gte=0) & Q(verify=True) & Q(activated=True))
        title_page += '- Institutions'

    if request.method == 'POST':

        if request.form.getlist('item_id'):
            error = False
            for id_compagnie in request.form.getlist('item_id'):
                current = Compagnie.objects.get(id=id_compagnie)
                if request.args.get('partenaire'):
                    current.partenaire = 1
                else:
                    current.partenaire = 2
                current = current.save()

                from ..workflow.workflow_partenaire import active_partenaire_facture
                active_partenaire_facture(current)

            if not error:
                if request.args.get('partenaire'):
                    flash('Ajout des partenaires reussis avec success', 'success')
                else:
                    flash('Ajout des institutions reussis avec success', 'success')

            datas = json.dumps({
                'statut': 'OK'
            })

        else:

            datas = json.dumps({
                'statut': 'NOK'
            })

        return datas

    return render_template('client/edit_exist.html', **locals())


@prefix.route('/remove/special', methods=['POST'])
@login_required
@roles_required([('super_admin', 'client')], ['edit'])
def remove_special():

    if request.form.getlist('item_id'):
        error = False
        for id_compagnie in request.form.getlist('item_id'):

            current = Compagnie.objects.get(id=id_compagnie)
            if request.args.get('partenaire'):
                current.partenaire = 0
            else:
                if current.partenaire == 2:
                    current.partenaire = 0
                else:
                    error = True

            current.save()
        if request.args.get('partenaire'):
            flash('Les clients selectionnes ne sont plus des partenaires. Ils sont acquis une relation de client', 'success')
        else:
            flash('Les clients selectionnes ne sont plus des institutions. Ils sont acquis une relation de client', 'success')

        if error:
            flash('Certaines entreprises sont des partenaires. ils ne peuvent etre enlever institution', 'warning')

        datas = json.dumps({
            'statut': 'OK'
        })

    else:

        datas = json.dumps({
            'statut': 'NOK'
        })

    return datas


@prefix.route('/all_activated')
def all_activated():
    compagnie = Compagnie.objects(uploaded=True)

    count = 0
    for com in compagnie:
        if not com.partenaire:
            com.partenaire = int(0)
            com.save()
            count += 1

    return str(count)

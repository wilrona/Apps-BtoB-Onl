__author__ = 'User'

from ...modules import *
from forms_compagnie import FormClient
from models_compagnie import Compagnie, Categorie, Media, Raison
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

    datas = Compagnie.objects(verify=1)

    return render_template('client/index.html', **locals())


@prefix.route('/new')
@login_required
def new():
    title_page = 'Nouveaux Clients'

    news = '1'
    datas = Compagnie.objects(verify=0)

    return render_template('client/index.html', **locals())


@prefix.route('/view/<objectid:client_id>')
@login_required
def view(client_id):

    if request.args.get('news'):
        if request.args.get('news') == "2":
            title_page = 'Client Abonnement ICI'
        else:
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
        if request.args.get('news') == "2":
            title_page = 'Client Abonnement ICI'
        else:
            title_page = 'Nouveaux Client'
    else:
        title_page = 'Clients'

    if client_id:
        data = Compagnie.objects.get(id=client_id)
        form = FormClient(obj=data)
        form.id.data = client_id

        form.idcategorie.data = [str(cat.id) for cat in data.idcategorie]

        form.maincategorie.choices = [('', 'Faite le choix de la categorie principale')]

        if request.method == "GET":
            form.maincategorie.data = str(data.maincategorie.id)

        for choice in data.idcategorie:
            form.maincategorie.choices.append((str(choice.id), choice.name))

        if request.method == "POST":
            principale = Categorie.objects.get(id=form.maincategorie.data)
            form.maincategorie.data = str(principale.id)
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
            data.verify = 0
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
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER_CLIENT'], data.logo))

                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['FOLDER_APPS']+'/static/uploads', filename))

                extension = filename.split(".")
                extension = extension[1]

                source = os.path.join(app.config['FOLDER_APPS']+'/static/uploads', filename)
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


@prefix.route('/uploader/<objectid:client_id>', methods=['POST'])
def uploader(client_id):

    from ..workflow.workflow_user import id_generator

    data = Compagnie.objects.get(id=client_id)

    if not data.imagedir:
        import calendar
        time_zones = tzlocal()
        date_auto_nows = datetime.datetime.now(time_zones)

        current_date = date_auto_nows
        current_date = calendar.timegm(current_date.utctimetuple())
        current_date = str(current_date).encode('base64').rstrip()
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER_CLIENT'], current_date))
        data.imagedir = current_date

        data.save()

    url_dossier = os.path.join(app.config['UPLOAD_FOLDER_CLIENT'], data.imagedir)

    saved_file = None
    for key, file in request.files.items():
        if file: # and allowed_file(fie.filename):

            filename = secure_filename(file.filename)

            file.save(os.path.join(app.config['FOLDER_APPS']+'/static/uploads', filename))

            source = os.path.join(app.config['FOLDER_APPS']+'/static/uploads', filename)

            destination = url_dossier + "/" + filename

            url_save = data.imagedir+"/"+filename

            count_image = Media.objects(Q(type='image') & Q(url=url_save) & Q(idcompagnie=data.id)).count()

            if count_image:
                extension = filename.split(".")
                rename = extension[0]+'-'+str(id_generator(size=7))
                filename = rename+'.'+extension[1]
                destination = url_dossier + "/"+filename

            os.rename(source, destination)

            url_save = data.imagedir+"/"+filename

            nbr_img_une = Media.objects(Q(type='image') & Q(idcompagnie=data.id) & Q(une=True)).count()

            media = Media()
            media.url = url_save
            media.idcompagnie = data
            media.type = 'image'

            if not nbr_img_une:
                media.une = True
            else:
                media.une = False

            saved_file = media.save()

    return render_template('client/image.html', **locals())


@prefix.route('/deleted/image/<objectid:image_id>', methods=['GET'])
def delete_image(image_id):

    media = Media.objects.get(id=image_id)

    companie_id = media.idcompagnie.id
    une = media.une

    os.remove(os.path.join(app.config['UPLOAD_FOLDER_CLIENT'], media.url))
    media.delete()

    new_une = ""
    if une:
        reste_image = Media.objects(Q(type='image') & Q(idcompagnie=companie_id))
        if reste_image.count():
            reste_image = reste_image.first()
            reste_image.une = True
            reste_image = reste_image.save()
            new_une = reste_image.id

    data = json.dumps({
        "image_id": str(image_id),
        "image_news_une": str(new_une)
    })
    return data


@prefix.route('/une/image/<objectid:image_id>', methods=['GET'])
def une_image(image_id):

    media = Media.objects.get(id=image_id)

    reste_image = Media.objects(Q(type='image') & Q(idcompagnie=media.idcompagnie.id) & Q(une=True))
    prev_une = ""
    if reste_image.count():
        reste_image = reste_image.first()
        reste_image.une = False
        reste_image = reste_image.save()
        prev_une = reste_image.id

    media.une = True
    media.save()

    data = json.dumps({
        "image_id": str(image_id),
        "image_prev_act": str(prev_une)
    })
    return data


@prefix.route('/edit/video/<objectid:client_id>')
@prefix.route('/edit/video/<objectid:client_id>/<video_link>')
def edit_video(client_id, video_link=None):

    company = Compagnie.objects.get(id=client_id)
    video = Media.objects(Q(idcompagnie=client_id) & Q(type="video")).first()

    if video_link:
        if not video:
            media_v = Media()
            media_v.type = "video"
            media_v.url = "https://www.youtube.com/watch?v="+video_link
            media_v.une = False
            media_v.idcompagnie = company
            media_v.save()
        else:
            video.url = "https://www.youtube.com/watch?v="+video_link
            video.save()

    return redirect(url_for('client.edit', client_id=client_id))


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

        if not item_found.mainuser:
            info['statut'] = 'NOK'
            info['message'] = 'Le Client "' + item_found.name + '" ne peut pas etre supprime car il est gere par un ' \
                                                                'utilisateur '

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

    from ..company.models_company import Company

    infos = Company.objects.first()

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
                item_found.verify = 1

                url_presence = "#"
                html = render_template('template_mail/compagnie/accept_info.html', **locals())

                msg = Message()
                msg.recipients = [item_found.mainuser.email]
                msg.add_recipient(infos.emailNotification)
                msg.subject = 'Statut demande d\'enregistrement de votre entreprise'
                msg.sender = (infos.senderNotification, 'no_reply@ici.cm')

                msg.html = html
                mail.send(msg)

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
    from ..company.models_company import Company

    info = Company.objects.first()

    client = Compagnie.objects.get(id=client_id)

    if client.activated:
        client.activated = False
    else:
        client.activated = True
        if not client.verify:
            client.verify = 1

            url_presence = "#"
            html = render_template('template_mail/compagnie/accept_info.html', **locals())

            msg = Message()
            msg.recipients = [client.mainuser.email]
            msg.add_recipient(info.emailNotification)
            msg.subject = 'Statut demande d\'enregistrement de votre entreprise'
            msg.sender = (info.senderNotification, 'no_reply@ici.cm')

            msg.html = html
            mail.send(msg)

    client.save()

    flash('Les modifications de l\'etat du client ont ete effectue', 'success')
    return redirect(url_for('client.view', client_id=client_id, news=request.args.get('news')))


@prefix.route('/refuse/<objectid:client_id>', methods=['GET', 'POST'])
def refuse_client(client_id):

    from ..company.models_company import Company

    info = Company.objects.first()

    client = Compagnie.objects.get(id=client_id)

    success = False
    if request.method == 'POST' and request.form['raison']:

        prev_raison = Raison.objects(Q(status=True) & Q(name_entity="client") & Q(id_entity=str(client.id))).first()
        if prev_raison:
            prev_raison.status = False
            prev_raison.save()

        next_raison = Raison()
        next_raison.status = True
        next_raison.name_entity = "client"
        next_raison.id_entity = str(client.id)
        next_raison.raison = request.form['raison']

        user = Users.objects.get(id=current_user.id)
        next_raison.user_reply = user

        next_raison = next_raison.save()

        client.verify = 2
        client.save()

        numero_call_center = "+237 600 00 00 00"

        html = render_template('template_mail/compagnie/refus_info.html', **locals())

        msg = Message()
        msg.recipients = [client.mainuser.email]
        msg.add_recipient(info.emailNotification)
        msg.subject = 'Statut demande d\'enregistrement de votre entreprise'
        msg.sender = (info.senderNotification, 'no_reply@ici.cm')

        msg.html = html
        mail.send(msg)

        # Envoyer un email au mainuser du client que son entreprise n'a pas ete valide

        flash('Refus de validation effectue avec succes', 'success')
        success = True

    return render_template('client/raison_refus.html', **locals())


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
        datas = Compagnie.objects(Q(partenaire__exists=0) | Q(partenaire=0) | Q(partenaire=1) & Q(verify=1) & Q(activated=True))
        title_page += '- Partenaires'
    else:
        datas = Compagnie.objects(Q(partenaire__exists=0) | Q(partenaire__gte=0) & Q(verify=1) & Q(activated=True))
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


@prefix.route('/import/excel', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'client')], ['edit'])
def import_excel():

    title_page = 'Clients - Import'

    from ..utilities.imports import ExcelParser
    from ..utilities.model_cron import Import_excel

    importation = Import_excel.objects()

    datas = []

    for import_e in importation:
        datas.append(import_e.data)

    if request.method == "POST":
        file = request.files['file']
        if file:
            excel_parser = ExcelParser()

            filename = secure_filename(file.filename)
            source_save = os.path.join(app.config['FOLDER_APPS']+'/static/uploads', filename)
            file.save(source_save)

            items = excel_parser.read_excel(source_save)
            os.remove(source_save)

            for item in items:
                data = Import_excel()
                data.data = item
                data.save()

            flash('Traitement des donnees reussis', 'success')
            return redirect(url_for('client.import_excel'))

    return render_template('client/importation.html', **locals())


@prefix.route('/traitement/import', methods=['POST'])
@login_required
def traitement_import():

    from ..utilities.model_cron import Import_excel

    importation = Import_excel.objects()

    if importation:

        for importa in importation:
            data = importa.data

            if data.categorie:

                categorie = Categorie.objects(name=data.categorie).first()

                if categorie:

                    entreprise = Compagnie()
                    entreprise.name = data.nom
                    entreprise.uploaded = True
                    entreprise.email = data.email
                    entreprise.phone = data.phone
                    entreprise.region = data.region
                    entreprise.activated = True
                    entreprise.verify = True
                    entreprise.repere = data.reperage
                    entreprise.ville = data.ville
                    entreprise.quartier = data.quartier
                    entreprise.urlsite = data.website
                    entreprise.imagedir = data.dossier
                    entreprise.logo = data.logo
                    entreprise.adresse = data.rue
                    entreprise.description = data.description
                    entreprise.facebook = data.facebook
                    entreprise.maincategorie = categorie
                    entreprise.idcategorie.append(categorie)
                    entreprise.save()

        datas = json.dumps({
            'statut': 'OK'
        })

    else:

        datas = json.dumps({
            'statut': 'NOK'
        })

    return datas


@prefix.route('/add/slide', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'client')], ['edit'])
def add_slide():
    title_page = 'Clients'

    datas = Compagnie.objects(Q(verify=1) & Q(activated=True))

    if request.method == 'POST':

        if request.form.getlist('item_id'):
            for id_compagnie in request.form.getlist('item_id'):
                current = Compagnie.objects.get(id=id_compagnie)
                current.slide = True
                current.save()

            flash('Entreprise ajoute sur le slide avec success', 'success')

            datas = json.dumps({
                'statut': 'OK'
            })

        else:

            datas = json.dumps({
                'statut': 'NOK'
            })

        return datas

    return render_template('client/add_slide.html', **locals())


@prefix.route('/remove/slide', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'client')], ['edit'])
def remove_slide():
    title_page = 'Clients'

    datas = Compagnie.objects(Q(verify=1) & Q(activated=True))

    if request.method == 'POST':

        if request.form.getlist('item_id'):
            for id_compagnie in request.form.getlist('item_id'):
                current = Compagnie.objects.get(id=id_compagnie)
                current.slide = False
                current.save()

            flash('Entreprise enleve du slide avec success', 'success')

            datas = json.dumps({
                'statut': 'OK'
            })

        else:

            datas = json.dumps({
                'statut': 'NOK'
            })

        return datas

    return render_template('client/add_slide.html', **locals())


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

    compagnie = Compagnie.objects(uploaded=True).update(verify=1)

    count = 0
    # for com in compagnie:
    #     count += 1

    return str(count)


@prefix.route('/contact/administrateur/<objectid:client_id>', methods=['GET', 'POST'])
def contact_to_admin(client_id):

    client = Compagnie.objects.get(id=client_id)

    success = False
    if request.method == 'POST':

        count = 0
        for item in request.form.getlist('item_id'):

            data = Users.objects.get(id=item)

            client.iduser.append(data)

            index = client.idcontact.index(data)

            client.idcontact.pop(index)

            if not client.mainuser:
                client.mainuser = data

            client.save()

            # Envoyer un emails au main user existant qu'un nouvel utilisateur est ajoute
            # Envoyer un mail au nouveau main user s'il y'en avait pas qu'il est un nouveau main user
            # Envoyer un email a l'utilisateur qui vient d'etre ajoute comme administrateur de la page.

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('client/contact_to_admin.html', **locals())


@prefix.route('/add/administrateur/<objectid:client_id>', methods=['GET', 'POST'])
def add_admin(client_id):

    datas = Users.objects(user=0)

    client = Compagnie.objects.get(id=client_id)

    success = False
    if request.method == 'POST':

        count = 0
        for item in request.form.getlist('item_id'):

            data = Users.objects.get(id=item)

            if data not in client.iduser:
                client.iduser.append(data)

            if data in client.idcontact:
                index = client.idcontact.index(data)

                client.idcontact.pop(index)

            if not client.mainuser:
                client.mainuser = data

            client.save()

            # Envoyer un emails au main user existant qu'un nouvel utilisateur est ajoute
            # Envoyer un mail au nouveau main user s'il y'en avait pas qu'il est un nouveau main user
            # Envoyer un email a l'utilisateur qui vient d'etre ajoute comme administrateur de la page.

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('client/add_admin.html', **locals())


@prefix.route('/delete/administrateur/<objectid:client_id>', methods=['GET', 'POST'])
def delete_admin(client_id):

    client = Compagnie.objects.get(id=client_id)

    success = False
    if request.method == 'POST':

        count = 0
        for item in request.form.getlist('item_id'):

            data = Users.objects.get(id=item)

            if data in client.iduser:
                index = client.iduser.index(data)

                client.iduser.pop(index)

            if data not in client.idcontact:
                client.idcontact.append(data)

            client.save()

            # Envoyer un email au main user que certain utilisateur ont ete enleve comme administrateur
            # Envoyer un email au utilisateur qu'ils ont ete enleve comme administrateur

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('client/delete_admin.html', **locals())


@prefix.route('/change/maineuser/<objectid:client_id>', methods=['GET', 'POST'])
def change_mainuser(client_id):

    client = Compagnie.objects.get(id=client_id)

    success = False
    if request.method == 'POST' and request.form['item_id']:

        item = request.form['item_id']
        data = Users.objects.get(id=item)

        if not client.mainuser:
            client.mainuser = data

        client.save()

        # Envoyer un emails au nouveau main user que c'est lui maintenant
        # Envoyer un email a l'ancien main user qu'il ne l'est plus

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('client/change_mainuser.html', **locals())

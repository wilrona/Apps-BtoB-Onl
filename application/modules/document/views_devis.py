__author__ = 'User'

from ...modules import *
from models_doc import Document, LigneDoc
from forms_doc import FormDevis
from ..user.models_user import Users
from ..compagnie.models_compagnie import Compagnie
from ..package.models_package import LigneService, Package
from ..opportunite.models_opportunite import Opportunite
from ..company.models_company import Config_reference, Company
from ..compagnie.forms_compagnie import FormClient
from ..user.forms_user import FormUser
from ..workflow import *

prefix = Blueprint('devis', __name__)


@prefix.route('/')
@login_required
def index():

    current_ref = Config_reference.objects().first()
    title_page = 'Devis'

    if current_user.has_roles([('super_admin', 'devis')]):
        datas = Document.objects(Q(devisDoc=True)& Q(status__lt=2))
    else:
        datas = Document.objects(Q(vendeur_id=current_user.id) & Q(devisDoc=True) & Q(status__lt=2))

    return render_template('devis/index.html', **locals())


@prefix.route('/view/<objectid:devis_id>', methods=['GET'])
def view(devis_id):

    current_ref = Config_reference.objects().first()

    title_page = 'Devis'

    data = Document.objects.get(id=devis_id)

    if not current_user.has_roles([('super_admin', 'devis')], ['edit']) and data.vendeur_id.id != current_user.id:
        flash('Vous n\'avez pas les droits necessaires sur ce devis', 'warning')
        return redirect(url_for('devis.index'))

    form = FormDevis(obj=data)

    if data.opportunite_id:
        form.opportunite_id.data = str(data.opportunite_id.id)
        form.opportunite_text.data = data.opportunite_id.name

    check_status(data)

    ligne_doc = LigneDoc.objects(iddevis=data.id)

    customer = Compagnie.objects.get(id=data.client_id.id)
    form_client = FormClient(prefix="client", obj=customer)

    contact = Users.objects.get(id=data.contact_id.id)
    form_contact = FormUser(obj=contact)

    services = LigneService.objects()

    return render_template('devis/view.html', **locals())


@prefix.route('/edit/<objectid:devis_id>', methods=['GET', 'POST'])
@prefix.route('/edit/', methods=['GET', 'POST'])
@login_required
def edit(devis_id=None):

    current_ref = Config_reference.objects().first()

    title_page = 'Devis'

    # if devis_id:
    #     data = Document.objects.get(id=devis_id)
    #
    #     check_status(data)
    #
    #     if not current_user.has_roles([('super_admin', 'devis')], ['edit']) and data.vendeur_id.id != current_user.id:
    #         return redirect(url_for('devis.view', devis_id=devis_id))
    #
    #     form = FormDevis(obj=data)
    #
    #     if data.opportunite_id:
    #         form.opportunite_id.data = str(data.opportunite_id.id)
    #         form.opportunite_text.data = data.opportunite_id.name
    #         current_opportunite = data.opportunite_id
    #
    #     customer = Compagnie.objects.get(id=data.client_id.id)
    #     form_client = FormClient(prefix="client", obj=customer)
    #
    #     contact = Users.objects.get(id=data.contact_id.id)
    #     form_contact = FormUser(obj=contact)
    #
    #     form_client.id.data = str(customer.id)
    #
    # else:

    data = Document()
    form = FormDevis()

    customer = Compagnie()
    form_client = FormClient(prefix="client")

    contact = Users()
    form_contact = FormUser()

    if 'contact_exist' in request.form and request.form['contact_exist']:
        form_contact.id.data = request.form['contact_exist']

    if 'client_exist' in request.form and request.form['client_exist']:
        form_client.id.data = request.form['client_exist']
        cur_client = Compagnie.objects.get(id=request.form['client_exist'])

        contact_list = []
        for cont in cur_client.idcontact:
            contact_list.append(cont)

        for cont in cur_client.iduser:
            if cont not in contact_list:
                contact_list.append(cont)

    services = LigneService.objects()

    if 'package' not in session:
        session['package'] = []

    current_client = None
    if request.method == 'POST' and 'client_exist' in request.form and request.form['client_exist']:

        current_client = Compagnie.objects.get(id=request.form['client_exist'])

        form_client.name.data = current_client.name
        form_client.email.data = current_client.email
        form_client.raison.data = current_client.raison
        form_client.phone.data = current_client.phone
        form_client.ville.data = current_client.ville
        form_client.quartier.data = current_client.quartier

    current_contact = None
    if request.method == 'POST' and 'contact_exist' in request.form and request.form['contact_exist']:

        current_contact = Users.objects.get(id=request.form['contact_exist'])

        form_contact.id.data = current_contact.id
        form_contact.email.data = current_contact.email
        form_contact.first_name.data = current_contact.first_name
        form_contact.last_name.data = current_contact.last_name
        form_contact.fonction.data = current_contact.fonction
        form_contact.phone.data = current_contact.phone

    current_opportunite = None
    if request.args.get('opportunite_id'):
        current_opportunite = Opportunite.objects.get(id=request.args.get('opportunite_id'))
        form.opportunite_id.data = str(current_opportunite.id)
        form.opportunite_text.data = str(current_opportunite.name)
        form_client = FormClient(prefix="client", obj=current_opportunite.client_id)

        contact_list = []
        for cont in current_opportunite.client_id.idcontact:
            contact_list.append(cont)

        for cont in current_opportunite.client_id.iduser:
            if cont not in contact_list:
                contact_list.append(cont)

    form_client.notCat.data = '1'

    form_client.idcategorie.data = ''
    form_client.idcategorie.choices = [('', '')]
    form_client.maincategorie.data = ''
    form_client.maincategorie.choices = [('', 'Faite le choix de la categorie principale')]

    client_list = Compagnie.objects(activated=True)

    if form.validate_on_submit() and form_client.validate_on_submit() and form_contact.validate_on_submit():

        if 'client_exist' in request.form and request.form['client_exist']:
            data.client_id = current_client
        else:
            if not devis_id:
                if not form.opportunite_id.data:
                    customer.raison = form_client.raison.data
                    customer.name = form_client.name.data
                    customer.ville = form_client.ville.data
                    customer.quartier = form_client.quartier.data

                    customer.email = form_client.email.data
                    customer.phone = form_client.phone.data
                    customer.activated = False
                    customer.verify = 0
                    customer.source = "devis"

                    current_client = customer.save()

                    data.client_id = current_client
                else:
                    current_client = current_opportunite.client_id
                    data.client_id = current_client

        if 'contact_exist' in request.form and request.form['contact_exist']:
            data.contact_id = current_contact
            data.status = 0
        else:
            if not devis_id:

                contact.email = form_contact.email.data
                contact.first_name = form_contact.first_name.data
                contact.last_name = form_contact.last_name.data
                if form_contact.fonction.data:
                    contact.fonction = form_contact.fonction.data
                contact.phone = form_contact.phone.data
                contact.activated = False
                contact.source = "devis"
                contact.user = 0
                contact = contact.save()

                data.contact_id = contact
                data.status = 0

                # Sauvegarde du contact dans l'entreprise en cours.
                contact_compagnie = data.client_id.idcontact
                user_compagnie = data.client_id.iduser
                if contact not in contact_compagnie and contact not in user_compagnie:
                    cli = Compagnie.objects.get(id=data.client_id.id)
                    cli.idcontact.append(contact)
                    cli.save()

        total = 0
        for item in session.get('package')['data']:
            total += item['st']

        data.montant = total

        vendeur = Users.objects.get(id=current_user.id)
        data.vendeur_id = vendeur

        if form.opportunite_id.data:
            opport = Opportunite.objects.get(id=form.opportunite_id.data)
            data.opportunite_id = opport

        if not devis_id:
            count_exist = Document.objects(devisDoc=True).count()
            data.ref = function.reference(count=count_exist+1, caractere=7, refuser=data.vendeur_id.ref)

        data = data.save()

        position = 0
        if not devis_id:
            for item in session.get('package')['data']:
                ligne = LigneDoc()

                ligne.iddevis = data
                ligne.prix = float(item['st'])
                ligne.qte = item['qte']

                ligne.idcompagnie = current_client
                package = Package.objects.get(id=item['package'])
                ligne.idpackage = package

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


@prefix.route('/ligne/commande', methods=['POST'])
def ligne_commande():

    from ..package.models_package import Package

    session['package'] = []

    data = []

    services = request.form.getlist('services')
    package = request.form.getlist('package')
    qte = request.form.getlist('qte')
    st = request.form.getlist('st')
    prix = request.form.getlist('prix')
    exist_ici = ''
    size = len(services)
    if size:
        packs = Package.objects(idligneService=services[0])
        similaire = []
        for pack in packs:
            ligsimilaire = {}
            ligsimilaire['id'] = str(pack.id)
            ligsimilaire['name'] = pack.name
            similaire.append(ligsimilaire)

        for x in range(0, size):
            if services[0]:
                ligne = {}
                if services[0] == 'ici_cm':
                    exist_ici = '1'
                ligne['service'] = services[0]
                ligne['package'] = str(package[0])
                ligne['similaire'] = similaire
                ligne['qte'] = int(qte[0])
                ligne['prix'] = float(prix[0])
                ligne['st'] = float(st[0])

                data.append(ligne)

    session['package'] = {
        'exist_ici': exist_ici,
        'data': data
    }

    data = json.dumps(data)

    return data


@prefix.route('/change/<objectid:devis_id>/<int:status>', methods=['GET'])
def change_satus(devis_id, status):

    data = Document.objects.get(id=devis_id)

    if not current_user.has_roles([('super_admin', 'devis')], ['edit']) and data.vendeur_id.id != current_user.id:
        flash('Vous n\'avez pas les droits necessaires sur ce devis', 'warning')
        return redirect(url_for('devis.view', devis_id=devis_id))

    if int(status) == 3:
        if data.facture_valid():
            flash('Le devis "'+data.ref+'" contient '+str(data.factu_devis().count())+' Facture(s) validee(s). il ne peut etre annule.', 'warning')
            return redirect(url_for('devis.view', devis_id=devis_id))

    data.status = status

    data.save()

    flash('Enregistement effectue avec succes', 'success')
    return redirect(url_for('devis.view', devis_id=devis_id))


@prefix.route('/devis/<objectid:devis_id>')
@login_required
def facture(devis_id):

    title_page = 'Factures'

    current = Document.objects.get(id=devis_id)

    current_ref = Config_reference.objects().first()
    datas = Document.objects(Q(parent=current) & Q(devisDoc=False))

    return render_template('facture/index.html', **locals())


@prefix.route('/canceled', methods=['POST'])
@login_required
@roles_required([('super_admin', 'devis')], ['edit'])
def canceled():

    count = 0
    data = []
    element = []
    for item in request.form.getlist('item_id'):
        info = {}
        item_found = Document.objects.get(id=item)

        if item_found.facture_valid():
            info['statut'] = 'NOK'
            info['message'] = 'Le devis "'+item_found.ref+'" contient '+str(item_found.factu_devis().count())+' Facture(s) validee(s).'

        if not item_found.facture_valid():
            item_found.status = 3
            item_found.save()
            element.append(str(item_found.id))
            count += 1
        else:
            data.append(info)

    if count:
        info = {}
        info['statut'] = 'OK'
        info['message'] = str(count)+' element(s) ont ete modifie avec success'
        info['element'] = element
        data.append(info)

    data = json.dumps(data)

    return data


@prefix.route('/print/<objectid:devis_id>', methods=['GET'])
def print_devis(devis_id):

    current_ref = Config_reference.objects().first()
    compagnie = Company.objects.first()

    data = Document.objects.get(id=devis_id)

    services = LigneService.objects()

    PROJECT_DIR = app.config['FOLDER_APPS']

    config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')

    image = PROJECT_DIR+'/static/images/icicm.png'

    word = PROJECT_DIR+'/static/images/icon/word.png'
    facebook = PROJECT_DIR+'/static/images/icon/facebook.png'
    twitter = PROJECT_DIR+'/static/images/icon/tweeter.png'


    css = [
        PROJECT_DIR+'/static/css/uikit-new.css',
        PROJECT_DIR+'/static/css/lato-font.css',
        PROJECT_DIR+'/static/css/apps.css',
        PROJECT_DIR+'/static/css/pdf.css',
    ]

    rendered = render_template('document/document.html', **locals())

    pdfs = pdfkit.from_string(
        rendered, False,
        css=css,
        options={
            'page-size': 'A4',
            # 'margin-top': '0',
            'margin-right': '0',
            'margin-left': '0',
            'margin-bottom': '0',
            'zoom': '0.65',
            'dpi': '400',
            'encoding': "UTF-8"

        },
        configuration=config
    )

    response = make_response(pdfs)
    response.headers['Content-Type'] = 'application.pdf'
    response.headers['Content-Disposition'] = 'inline; filename='+data.reference()+'.pdf'
    # response.headers['Content-Disposition'] = 'attach; filename=output.pdf'

    if data.status == 0:
        data.status = 1
        data.save()

    return response


# @prefix.route('/print2/<objectid:devis_id>', methods=['GET'])
# def print2_devis(devis_id):
#
#     PROJECT_DIR = app.config['FOLDER_APPS']
#
#     config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
#
#     image = PROJECT_DIR+'/static/images/logo.jpeg'
#
#     word = PROJECT_DIR+'/static/images/icon/word.png'
#     facebook = PROJECT_DIR+'/static/images/icon/facebook.png'
#     tweeter = PROJECT_DIR+'/static/images/icon/tweeter.png'
#
#     rendered = render_template('document/document2.html', **locals())
#     css = [
#         PROJECT_DIR+'/static/css/uikit-new.css',
#         PROJECT_DIR+'/static/css/lato-font.css',
#         PROJECT_DIR+'/static/css/roboto.css',
#         PROJECT_DIR+'/static/css/material-icon.css',
#         PROJECT_DIR+'/static/css/apps.css',
#         PROJECT_DIR+'/static/css/pdf.css',
#     ]
#     # # pdf = pdfkit.from_file(rendered, 'output.pdf')
#     pdfs = pdfkit.from_string(
#         rendered, False,
#         css=css,
#         options={
#             'page-size': 'A4',
#             # 'margin-top': '0',
#             'margin-right': '0',
#             'margin-left': '0',
#             'margin-bottom': '0',
#             # 'zoom': '1.2',
#             'encoding': "UTF-8",
#             'header-right': '[page]'
#
#
#         },
#         configuration=config
#     )
#
#     response = make_response(pdfs)
#     response.headers['Content-Type'] = 'application.pdf'
#     response.headers['Content-Disposition'] = 'inline; filename=output.pdf'
#     # response.headers['Content-Disposition'] = 'attach; filename=output.pdf'
#
#     return response







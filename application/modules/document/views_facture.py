__author__ = 'User'


from ...modules import *
from models_doc import Document, LigneDoc
from forms_doc import FormFacture
from ..user.models_user import Users
from ..compagnie.models_compagnie import Compagnie
from ..package.models_package import LigneService, Package
from ..opportunite.models_opportunite import Opportunite
from ..company.models_company import Config_reference, Company
from ..compagnie.forms_compagnie import FormClient
from ..user.forms_user import FormUser
from ..workflow import *


prefix = Blueprint('facture', __name__)


@prefix.route('/')
@login_required
def index():

    current_ref = Config_reference.objects().first()
    title_page = 'Facture'

    if current_user.has_roles([('super_admin', 'facture')]):
        datas = Document.objects(devisDoc=False)
    else:
        datas = Document.objects(Q(vendeur_id=current_user.id) & Q(devisDoc=False))

    return render_template('facture/index.html', **locals())


@prefix.route('/solde')
@login_required
def solde():

    current_ref = Config_reference.objects().first()
    title_page = 'Facture Non solde'

    solde = '1'

    if current_user.has_roles([('super_admin', 'facture')]):
        data = Document.objects(devisDoc=False)
    else:
        data = Document.objects(Q(vendeur_id=current_user.id) & Q(devisDoc=False))

    datas = []

    for facture in data:
        if facture.is_partiel():
            datas.append(facture)

    return render_template('facture/solde.html', **locals())


@prefix.route('/view/<objectid:facture_id>', methods=['GET'])
def view(facture_id):

    current_ref = Config_reference.objects().first()

    title_page = 'Facture'

    data = Document.objects.get(id=facture_id)

    if not current_user.has_roles([('super_admin', 'devis')], ['edit']) and data.vendeur_id.id != current_user.id:
        return redirect(url_for('devis.index'))

    form = FormFacture(obj=data)

    if data.parent:
        form.devis_id.data = str(data.parent.id)
        form.devis_text.data = data.parent.reference()

    # check_status(data)

    ligne_doc = LigneDoc.objects(iddocument=data.id)

    customer = Compagnie.objects.get(id=data.client_id.id)
    form_client = FormClient(prefix="client", obj=customer)

    contact = Users.objects.get(id=data.contact_id.id)
    form_contact = FormUser(obj=contact)

    services = LigneService.objects()

    return render_template('facture/view.html', **locals())


@prefix.route('/edit/<objectid:facture_id>', methods=['GET', 'POST'])
@prefix.route('/edit/', methods=['GET', 'POST'])
@login_required
def edit(facture_id=None):

    current_ref = Config_reference.objects().first()

    title_page = 'Facture'

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
    form = FormFacture()

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
        for cont in cur_client.relation():
            contact_list.append(cont)

    services = LigneService.objects()

    if 'package_fact' not in session:
        session['package_fact'] = []

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

    current_devis = None
    if request.args.get('devis_id'):

        current_devis = Document.objects.get(id=request.args.get('devis_id'))
        form.devis_id.data = str(current_devis.id)
        form.devis_text.data = str(current_devis.ref)
        form_client = FormClient(prefix="client", obj=current_devis.client_id)

        contact_list = []
        for cont in current_devis.client_id.relation():
            contact_list.append(cont)

        ligne_doc = LigneDoc.objects(iddevis=current_devis.id)

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
            if not facture_id:
                if not form.devis_id.data:
                    customer.raison = form_client.raison.data
                    customer.name = form_client.name.data
                    customer.ville = form_client.ville.data
                    customer.quartier = form_client.quartier.data

                    customer.email = form_client.email.data
                    customer.phone = form_client.phone.data
                    customer.activated = False
                    customer.source = "facture"
                    customer.verify = False

                    current_client = customer.save()

                    data.client_id = current_client
                else:
                    current_client = current_devis.client_id
                    data.client_id = current_client

        if 'contact_exist' in request.form and request.form['contact_exist']:
            data.contact_id = current_contact
            data.status = 0
        else:
            if not facture_id:

                contact.email = form_contact.email.data
                contact.first_name = form_contact.first_name.data
                contact.last_name = form_contact.last_name.data
                if form_contact.fonction.data:
                    contact.fonction = form_contact.fonction.data
                contact.phone = form_contact.phone.data
                contact.activated = False
                contact.source = "facture"
                contact.user = 0
                contact = contact.save()

                data.contact_id = contact
                data.status = 0

                # Sauvegarde du contact dans l'entreprise en cours.
                contact_compagnie = data.client_id.idcontact
                if contact not in contact_compagnie:
                    cli = Compagnie.objects.get(id=data.client_id.id)
                    cli.idcontact.append(contact)
                    cli.save()

        data.devisDoc = False

        total = 0
        if current_devis:
            ligne_doc = LigneDoc.objects(iddevis=current_devis.id)
            for ligne in ligne_doc:
                total += ligne.prix
        else:
            for item in session.get('package_fact')['data']:
                total += item['st']

        data.montant = total

        vendeur = Users.objects.get(id=current_user.id)
        data.vendeur_id = vendeur

        if form.devis_id.data:
            devis = Document.objects.get(id=form.devis_id.data)
            data.parent = devis

        if not facture_id:
            count_exist = Document.objects(devisDoc=False).count()
            data.ref = function.reference(count=count_exist+1, caractere=7, refuser=data.vendeur_id.ref)

        data = data.save()

        position = 0
        if not facture_id:
            if current_devis:
                ligne_doc = LigneDoc.objects(iddevis=current_devis.id)
                for ligne in ligne_doc:
                    ligne.iddocument = data
                    ligne.save()
            else:
                for item in session.get('package_fact')['data']:
                    ligne = LigneDoc()

                    ligne.iddocument = data
                    ligne.prix = float(item['st'])
                    ligne.qte = item['qte']

                    ligne.idcompagnie = current_client
                    package = Package.objects.get(id=item['package'])
                    ligne.idpackage = package

                    ligne.save()
                    position += 1

            session.pop('package_fact')

        flash('Enregistement effectue avec succes', 'success')

        if request.form['nouveau'] == '1':
            # check_status(data)
            return redirect(url_for('facture.edit'))
        else:
            return redirect(url_for('facture.view', facture_id=data.id))

    return render_template('facture/edit.html', **locals())


@prefix.route('/ligne/commande', methods=['POST'])
def ligne_commande():

    from ..package.models_package import Package

    session['package_fact'] = []

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

    session['package_fact'] = {
        'exist_ici': exist_ici,
        'data': data
    }

    data = json.dumps(data)

    return data


@prefix.route('/reglement/<objectid:facture_id>', methods=['GET', 'POST'])
@login_required
def reglement(facture_id):

    from ..paiement.models_paiement import Paiement

    data = Document.objects.get(id=facture_id)

    contacts = data.client_id.relation()

    list = []

    for user in contacts:
        current = {}
        current['id'] = str(user.id)
        current['name'] = user.full_name()
        current['fonction'] = ''
        if user.fonction:
            current['fonction'] = '(' + user.fonction + ')'
        list.append(current)

    success = False
    if request.method == 'POST':

        reglement = Paiement()

        if 'montant_partiel' in request.form:
            reglement.montant = float(request.form['montant_partiel'])
        else:
            reglement.montant = data.montant

        user = Users.objects.get(id=request.form['user_paid'])
        reglement.iduser_paid = user

        reglement.iddocument = data

        vendeur = Users.objects.get(id=current_user.id)
        reglement.idvendeur = vendeur

        reglement.idmoyen_paiement = 'cash'

        # Modification du status du document facture.
        data.status = 2
        data.save()

        reglement.save()

        success = True

    return render_template('facture/reglement.html', **locals())


@prefix.route('/change/<objectid:facture_id>/<int:status>', methods=['GET'])
def change_satus(facture_id, status):

    data = Document.objects.get(id=facture_id)

    if not current_user.has_roles([('super_admin', 'facture')], ['edit']) and data.vendeur_id.id != current_user.id:
        flash('Vous n\'avez pas les droits necessaires sur cette facture', 'success')
        return redirect(url_for('facture.view', facture_id=facture_id))

    data.status = status

    data.save()

    flash('Enregistement effectue avec succes', 'success')
    return redirect(url_for('facture.view', facture_id=facture_id))


@prefix.route('/canceled', methods=['POST'])
@login_required
@roles_required([('super_admin', 'facture')], ['edit'])
def canceled():

    count = 0
    data = []
    element = []
    for item in request.form.getlist('item_id'):
        info = {}
        item_found = Document.objects.get(id=item)

        if item_found.status == 2:
            info['statut'] = 'NOK'
            info['message'] = 'La facture "'+item_found.ref+'" ne peut plus etre supprimee car elle a deja des paiements en cours.'

        if not item_found.facture_valid():
            item_found.status = 0
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


@prefix.route('/print/<objectid:facture_id>', methods=['GET'])
def print_facture(facture_id):

    current_ref = Config_reference.objects().first()
    compagnie = Company.objects.first()

    data = Document.objects.get(id=facture_id)

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


@prefix.route('/print2/<objectid:facture_id>', methods=['GET'])
def print2_facture(facture_id):

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
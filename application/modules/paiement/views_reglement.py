# coding=utf-8
from ...modules import *
from models_paiement import Paiement
from ..document.models_doc import Document
from ..user.models_user import Users

prefix = Blueprint('reglement', __name__)


@prefix.route('/')
@login_required
@roles_required([('super_admin', 'reglement')])
def index():
    title_page = 'Reglement Facture'

    datas = Paiement.objects(Q(status=0) & Q(idmoyen_paiement='cash')).order_by('-createDate')

    return render_template('paiement/reglement/index.html', **locals())


@prefix.route('/transaction')
@login_required
@roles_required([('super_admin', 'reglement')])
def transaction():
    title_page = 'Transactions Financieres'

    datas = Paiement.objects().order_by('-createDate')

    return render_template('paiement/reglement/transaction.html', **locals())


@prefix.route('/edit/', methods=['GET', 'POST'])
@login_required
def edit():

    factures = Document.objects(Q(devisDoc=False) & Q(status__ne=3)).order_by('-createDate')

    datas = []

    for facture in factures:
        if facture.is_partiel():
            datas.append(facture)

    success = False
    if request.method == 'POST':

        count = 0
        for item in request.form.getlist('item_id'):

            data = Document.objects.get(id=item)

            reglement = Paiement()

            reglement.montant = float(request.form.getlist('montant')[count])

            user = Users.objects.get(id=request.form.getlist('contact')[count])
            reglement.iduser_paid = user

            reglement.iddocument = data

            vendeur = Users.objects.get(id=current_user.id)
            reglement.idvendeur = vendeur

            reglement.idmoyen_paiement = 'cash'

            # Modification du status du document facture.
            data.status = 2
            data.save()

            reglement.save()

        flash('Enregistement effectué avec succes', 'success')
        success = True

    return render_template('paiement/reglement/edit.html', **locals())


@prefix.route('/valide', methods=['POST'])
@login_required
@roles_required([('super_admin', 'reglement')], ['delete'])
def valide():

    from ..company.models_company import Company
    from ..utilities.model_cron import Notification

    infos = Company.objects.first()

    data = []
    element = []
    count = 0

    item_index = 0
    for item in request.form.getlist('item_id'):

        info = {}
        item_found = Paiement.objects().get(id=item)

        if request.form.getlist('souche')[item_index]:
            item_found.status = 1
            item_found.souche = request.form.getlist('souche')[item_index]

            user = Users.objects.get(id=current_user.id)
            item_found.iduser_valid = user

            if item_found.iddocument.package_ici_cm():

                html = render_template('template_mail/compagnie/accept_reglement.html', **locals())

                msg = Message()
                msg.recipients = [item_found.iduser_paid.email]
                msg.add_recipient(infos.emailNotification)
                msg.subject = 'Confirmation de paiement'
                msg.sender = (infos.senderNotification, 'no_reply@ici.cm')

                msg.html = html
                mail.send(msg)

                notification = Notification()
                notification.title = 'Confirmation de paiement'
                notification.message = 'Votre paiement a été validé avec succes. Vous pouvez consulter les ' \
                                       'informations de votre entreprise sur ICI. '
                notification.id_compagnie = item_found.iddocument.client_id
                notification.save()

            facture = item_found.iddocument

            ligne_doc = facture.lignedoc_facture()

            for ligne in ligne_doc:
                if ligne.idpackage.idligneService == 'hosting':
                    ligne.etat = 1
                    ligne.save()

                if ligne.idpackage.idligneService == 'domaine':
                    ligne.etat = 1
                    ligne.save()

            item_found.save()

            element.append(str(item_found.id))
            count += 1
        else:

            info['statut'] = 'NOK'
            info['message'] = u'La facture No: "' + item_found.iddocument.reference() + u'" ne contient pas de souche ' \
                                                                                       u'renseigné. '
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


@prefix.route('/print/<objectid:paiement_id>', methods=['GET'])
def print_paiement(paiement_id):

    from ..company.models_company import Config_reference, Company

    current_ref = Config_reference.objects().first()
    compagnie = Company.objects.first()

    paiement = Paiement.objects.get(id=paiement_id)

    data = Document.objects.get(id=paiement.iddocument.id)

    PROJECT_DIR = app.config['FOLDER_APPS']

    config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')

    image = PROJECT_DIR+'/static/images/icicm.jpg'

    word = PROJECT_DIR+'/static/images/icon/word.png'
    facebook = PROJECT_DIR+'/static/images/icon/facebook.png'
    twitter = PROJECT_DIR+'/static/images/icon/tweeter.png'


    css = [
        PROJECT_DIR+'/static/css/uikit-new.css',
        PROJECT_DIR+'/static/css/lato-font.css',
        PROJECT_DIR+'/static/css/apps.css',
        PROJECT_DIR+'/static/css/pdf.css',
        ]

    rendered = render_template('document/document_paiement.html', **locals())

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

    return response

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

    factures = Document.objects(devisDoc=False)

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

            html = render_template('template_mail/compagnie/accept_reglement.html', **locals())

            msg = Message()
            msg.recipients = [item_found.iduser_paid.email]
            msg.add_recipient(infos.emailNotification)
            msg.subject = 'Confirmation de paiement'
            msg.attach()
            msg.sender = (infos.senderNotification, 'no_reply@ici.cm')

            msg.html = html
            mail.send(msg)

            notification = Notification()
            notification.title = 'Confirmation de paiement'
            notification.message = 'Votre paiement a été validé avec succes. Vous pouvez consulter les informations ' \
                                   'de votre entreprise sur ICI. '
            notification.id_compagnie = item_found.compagnie
            notification.save()

            item_found.save()

            element.append(str(item_found.id))
            count += 1
        else:

            info['statut'] = 'NOK'
            info['message'] = 'La facture No: "' + item_found.iddocument.reference() + '" ne contient pas de souche ' \
                                                                                       'renseigné. '
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

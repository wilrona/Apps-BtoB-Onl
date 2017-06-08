# coding=utf-8
from ...modules import *
from models_compagnie import Claim, Compagnie
from ..user.models_user import Users
from forms_compagnie import FormClient


prefix_claim = Blueprint('claim', __name__)


@prefix_claim.route('/')
@login_required
@roles_required([('super_admin', 'claim')])
def index():

    title_page = 'Reclamation Entreprise'

    datas = Claim.objects(Q(statut=1) | Q(statut=0)).order_by('-createDate')

    return render_template('client/claim/index.html', **locals())


@prefix_claim.route('/view/<objectid:claim_id>')
@login_required
@roles_required([('super_admin', 'claim')])
def view(claim_id):

    title_page = 'Reclamation Entreprise'

    claim = Claim.objects.get(id=claim_id)

    data = Compagnie.objects.get(id=claim.idcompagnie.id)
    form = FormClient(obj=data)
    form.id.data = str(data.id)

    return render_template('client/claim/view.html', **locals())


@prefix_claim.route('/accepter/<objectid:claim_id>')
@prefix_claim.route('/accepter')
@login_required
@roles_required([('super_admin', 'claim')], ['edit'])
def accepte(claim_id=None):

    from ..company.models_company import Company
    from ..utilities.model_cron import Notification
    infos = Company.objects.first()

    if claim_id:
        data = Claim.objects.get(id=claim_id)

        data.statut = 0

        compagnie = Compagnie.objects.get(id=data.idcompagnie.id)

        user = Users.objects.get(id=data.iduser.id)

        compagnie.mainuser = user
        compagnie.claimDate = datetime.datetime.now()
        compagnie = compagnie.save()

        if compagnie.id not in user.idcompagnie:
            user.idcompagnie.append(compagnie)
            user.save()

        html = render_template('template_mail/compagnie/accept_reclamation.html', **locals())

        msg = Message()
        msg.recipients = [data.iduser.email]
        msg.add_recipient(infos.emailNotification)
        msg.subject = 'Statut demande de revendication'
        msg.sender = (infos.senderNotification, 'no_reply@ici.cm')

        msg.html = html
        mail.send(msg)

        notification = Notification()
        notification.title = 'Statut demande de revendication'
        notification.message = 'Nous avons le plaisir de confirmer la validation de votre demande de revendication.'
        notification.id_compagnie = data.idcompagnie
        notification.save()

        data.save()

        flash('Demande accepté avec success', 'success')
        return redirect(url_for('claim.view', claim_id=claim_id))
    else:
        datas = []
        element = []
        count = 0
        for item in request.form.getlist('item_id'):

            data = Claim.objects().get(id=item)

            data.statut = 0

            compagnie = Compagnie.objects.get(id=data.idcompagnie.id)

            user = Users.objects.get(id=data.iduser.id)

            compagnie.mainuser = user
            compagnie.claimDate = datetime.datetime.now()
            compagnie.save()

            if compagnie.id not in user.idcompagnie:
                user.idcompagnie.append(compagnie)
                user.save()

            url_presence = "#"
            html = render_template('template_mail/compagnie/accept_reclamation.html', **locals())

            msg = Message()
            msg.recipients = [data.iduser.email]
            msg.add_recipient(infos.emailNotification)
            msg.subject = 'Statut demande de revendication'
            msg.sender = (infos.senderNotification, 'no_reply@ici.cm')

            msg.html = html
            mail.send(msg)

            notification = Notification()
            notification.title = 'Statut demande de revendication'
            notification.message = 'Nous avons le plaisir de confirmer la validation de votre demande de ' \
                                   'revendication. '
            notification.id_compagnie = data.idcompagnie
            notification.save()

            element.append(str(data.id))
            data.save()
            count += 1

        if count:
            info = {}
            info['statut'] = 'OK'
            info['message'] = str(count)+' reclammation(s) ont ete validé avec success'
            info['element'] = element
            datas.append(info)

        datas = json.dumps(datas)

        return datas


@prefix_claim.route('/refuser/<objectid:claim_id>', methods=['GET', 'POST'])
def refuser(claim_id):

    from ..company.models_company import Company
    from ..compagnie.models_compagnie import Raison
    from ..utilities.model_cron import Notification

    info = Company.objects.first()

    client = Claim.objects.get(id=claim_id)

    success = False
    if request.method == 'POST' and request.form['raison']:

        prev_raison = Raison.objects(Q(status=True) & Q(name_entity="claim") & Q(id_entity=str(client.id))).first()
        if prev_raison:
            prev_raison.status = False
            prev_raison.save()

        next_raison = Raison()
        next_raison.status = True
        next_raison.name_entity = "claim"
        next_raison.id_entity = str(client.id)
        next_raison.raison = request.form['raison']

        user = Users.objects.get(id=current_user.id)
        next_raison.user_reply = user

        next_raison = next_raison.save()

        client.verify = 2
        client.save()

        numero_call_center = "+237 600 00 00 00"
        html = render_template('template_mail/compagnie/refus_reclamation.html', **locals())

        msg = Message()
        msg.recipients = [client.mainuser.email]
        msg.add_recipient(info.emailNotification)
        msg.subject = 'Statut demande de revendication'
        msg.sender = (info.senderNotification, 'no_reply@ici.cm')

        msg.html = html
        mail.send(msg)

        notification = Notification()
        notification.title = 'Statut demande de revendication'
        notification.message = 'Nous vous informons que votre demande n’a pas été validé.'
        notification.id_compagnie = client.idcompagnie
        notification.save()

        # Envoyer un email au mainuser du client que son entreprise n'a pas ete valide

        flash('Refus de la demande de relation effectué avec succes', 'success')
        success = True

    return render_template('client/claim/raison_refus.html', **locals())


@prefix_claim.route('/refuser/<objectid:claim_id>')
@prefix_claim.route('/refuser')
@login_required
@roles_required([('super_admin', 'claim')], ['edit'])
def refuse(claim_id=None):

    if claim_id:
        data = Claim.objects.get(id=claim_id)

        data.statut = 2

        html = render_template('template_mail/compagnie/refus_reclamation.html', **locals())

        msg = Message()
        msg.recipients = [data.iduser.email]
        msg.subject = 'Reponse a votre reclamation'
        msg.sender = ('ICI.CM service client', 'no_reply@ici.cm')

        msg.html = html
        mail.send(msg)

        data.save()

        flash('Demande Refuse avec success', 'success')
        return redirect(url_for('claim.view', claim_id=claim_id))
    else:
        datas = []
        element = []
        count = 0
        for item in request.form.getlist('item_id'):

            data = Claim.objects().get(id=item)

            data.statut = 2
            element.append(str(data.id))

            html = render_template('template_mail/compagnie/refus_reclamation.html', **locals())

            msg = Message()
            msg.recipients = [data.iduser.email]
            msg.subject = 'Reponse a votre reclamation'
            msg.sender = ('ICI.CM service client', 'no_reply@ici.cm')

            msg.html = html
            mail.send(msg)

            data.save()
            count += 1

        if count:
            info = {}
            info['statut'] = 'OK'
            info['message'] = str(count)+' reclamation(s) ont ete refuse avec success'
            info['element'] = element
            datas.append(info)

        datas = json.dumps(datas)

        return datas
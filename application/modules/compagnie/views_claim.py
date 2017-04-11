
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

    datas = Claim.objects(Q(statut=1) | Q(statut=0))

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

    if claim_id:
        data = Claim.objects.get(id=claim_id)

        data.statut = 0

        compagnie = Compagnie.objects.get(id=data.idcompagnie.id)

        user = Users.objects.get(id=data.iduser.id)

        compagnie.mainuser = user
        compagnie = compagnie.save()

        if compagnie.id not in user.idcompagnie:
            user.idcompagnie.append(compagnie)
            user.save()

        html = render_template('template_mail/compagnie/reponse_reclamation.html', **locals())

        msg = Message()
        msg.recipients = [data.iduser.email]
        msg.subject = 'Reponse a votre reclamation'
        msg.sender = ('ICI.CM service reclamation d\'entreprise', 'no_reply@ici.cm')

        msg.html = html
        mail.send(msg)

        data.save()

        flash('Demande Accepte avec success', 'success')
        return redirect(url_for('claim.view', claim_id=claim_id))
    else:
        data = []
        element = []
        count = 0
        for item in request.form.getlist('item_id'):

            item_found = Claim.objects().get(id=item)

            item_found.statut = 0

            compagnie = Compagnie.objects.get(id=item_found.idcompagnie.id)

            user = Users.objects.get(id=item_found.iduser.id)

            compagnie.mainuser = user
            compagnie.save()

            html = render_template('template_mail/compagnie/reponse_reclamation.html', **locals())

            msg = Message()
            msg.recipients = [item_found.iduser.email]
            msg.subject = 'Reponse a votre reclamation'
            msg.sender = ('ICI.CM service reclamation d\'entreprise', 'no_reply@ici.cm')

            msg.html = html
            mail.send(msg)

            element.append(str(item_found.id))
            item_found.save()
            count += 1

        if count:
            info = {}
            info['statut'] = 'OK'
            info['message'] = str(count)+' reclammation(s) ont ete valide avec success'
            info['element'] = element
            data.append(info)

        data = json.dumps(data)

        return data


@prefix_claim.route('/refuser/<objectid:claim_id>')
@prefix_claim.route('/refuser')
@login_required
@roles_required([('super_admin', 'claim')], ['edit'])
def refuse(claim_id=None):

    if claim_id:
        data = Claim.objects.get(id=claim_id)

        data.statut = 2

        html = render_template('template_mail/compagnie/reponse_reclamation.html', **locals())

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
        data = []
        element = []
        count = 0
        for item in request.form.getlist('item_id'):

            item_found = Claim.objects().get(id=item)

            item_found.statut = 2
            element.append(str(item_found.id))

            html = render_template('template_mail/compagnie/reponse_reclamation.html', **locals())

            msg = Message()
            msg.recipients = [item_found.iduser.email]
            msg.subject = 'Reponse a votre reclamation'
            msg.sender = ('ICI.CM service client', 'no_reply@ici.cm')

            msg.html = html
            mail.send(msg)

            item_found.save()
            count += 1

        if count:
            info = {}
            info['statut'] = 'OK'
            info['message'] = str(count)+' reclamation(s) ont ete refuse avec success'
            info['element'] = element
            data.append(info)

        data = json.dumps(data)

        return data
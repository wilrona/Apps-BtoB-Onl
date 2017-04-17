from ...modules import *
from models_compagnie import Relation, Compagnie
from ..user.models_user import Users
from forms_compagnie import FormClient


prefix_relation = Blueprint('relation', __name__)


@prefix_relation.route('/')
@login_required
@roles_required([('super_admin', 'relation')])
def index():

    title_page = 'Demande Relation'

    datas = Relation.objects(Q(statut=1) | Q(statut=0))

    return render_template('client/relation/index.html', **locals())


@prefix_relation.route('/view/<objectid:relation_id>')
@login_required
@roles_required([('super_admin', 'relation')])
def view(relation_id):

    title_page = 'Reclamation Entreprise'

    relation = Relation.objects.get(id=relation_id)

    data = Compagnie.objects.get(id=relation.idagence.id)
    form = FormClient(obj=data)
    form.id.data = str(data.id)

    data_parent = Compagnie.objects.get(id=relation.idparent.id)
    form_parent = FormClient(obj=data_parent)
    form_parent.id.data = str(data_parent.id)

    return render_template('client/relation/view.html', **locals())


@prefix_relation.route('/accepter/<objectid:relation_id>')
@prefix_relation.route('/accepter')
@login_required
@roles_required([('super_admin', 'relation')], ['edit'])
def accepte(relation_id=None):

    if relation_id:
        data = Relation.objects.get(id=relation_id)

        data.statut = 0

        agence = Compagnie.objects.get(id=data.idagence.id)

        parent = Compagnie.objects.get(id=data.idparent.id)
        agence.parent_idcompagnie = parent
        agence.save()

        html = render_template('template_mail/compagnie/reponse_relation.html', **locals())

        msg = Message()
        msg.recipients = [data.iduser.email]
        msg.subject = 'Reponse a votre demande de relation'
        msg.sender = ('ICI.CM service client', 'no_reply@ici.cm')

        msg.html = html
        mail.send(msg)

        data.save()

        flash('Demande Accepte avec success', 'success')
        return redirect(url_for('relation.view', relation_id=relation_id))
    else:
        data = []
        element = []
        count = 0
        for item in request.form.getlist('item_id'):

            item_found = Relation.objects().get(id=item)

            item_found.statut = 0

            agence = Compagnie.objects.get(id=data.idagence.id)

            parent = Compagnie.objects.get(id=data.idparent.id)
            agence.parent_idcompagnie = parent
            agence.save()

            html = render_template('template_mail/compagnie/reponse_relation.html', **locals())

            msg = Message()
            msg.recipients = [item_found.iduser.email]
            msg.subject = 'Reponse a votre demande de relation'
            msg.sender = ('ICI.CM service client', 'no_reply@ici.cm')

            msg.html = html
            mail.send(msg)

            element.append(str(item_found.id))
            item_found.save()
            count += 1

        if count:
            info = {}
            info['statut'] = 'OK'
            info['message'] = str(count)+' demande(s) de relation ont ete valide avec success'
            info['element'] = element
            data.append(info)

        data = json.dumps(data)

        return data


@prefix_relation.route('/refuser/<objectid:relation_id>')
@prefix_relation.route('/refuser')
@login_required
@roles_required([('super_admin', 'relation')], ['edit'])
def refuse(relation_id=None):

    if relation_id:
        data = Relation.objects.get(id=relation_id)

        data.statut = 2

        html = render_template('template_mail/compagnie/reponse_relation.html', **locals())

        msg = Message()
        msg.recipients = [data.iduser.email]
        msg.subject = 'Reponse a votre demande de relation'
        msg.sender = ('ICI.CM service client', 'no_reply@ici.cm')

        msg.html = html
        mail.send(msg)

        data.save()

        flash('Demande Refuse avec success', 'success')
        return redirect(url_for('claim.view', relation_id=relation_id))

    else:
        data = []
        element = []
        count = 0
        for item in request.form.getlist('item_id'):

            item_found = Relation.objects().get(id=item)

            item_found.statut = 2
            element.append(str(item_found.id))

            html = render_template('template_mail/compagnie/reponse_relation.html', **locals())

            msg = Message()
            msg.recipients = [item_found.iduser.email]
            msg.subject = 'Reponse a votre demande de relation'
            msg.sender = ('ICI.CM service client', 'no_reply@ici.cm')

            msg.html = html
            mail.send(msg)

            item_found.save()
            count += 1

        if count:
            info = {}
            info['statut'] = 'OK'
            info['message'] = str(count)+' demande(s) de relation ont ete refuse avec success'
            info['element'] = element
            data.append(info)

        data = json.dumps(data)

        return data

from ...modules import *
from models_paiement import Paiement
from ..user.models_user import Users

prefix = Blueprint('reglement', __name__)


@prefix.route('/')
@login_required
@roles_required([('super_admin', 'reglement')])
def index():

    title_page = 'Reglement Facture'

    datas = Paiement.objects(Q(status=0) & Q(idmoyen_paiement='cash')).order_by('-createDate')

    return render_template('paiement/reglement/index.html', **locals())


@prefix.route('/valide', methods=['POST'])
@login_required
@roles_required([('super_admin', 'reglement')], ['delete'])
def valide():

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

            item_found.save()

            element.append(str(item_found.id))
            count += 1
        else:

            info['statut'] = 'NOK'
            info['message'] = 'La facture No: "'+item_found.iddocument.reference()+'" ne contient pas de souche ' \
                                                                                  'renseigne. '
            data.append(info)

        item_index += 1

    if count:
        info = {}
        info['statut'] = 'OK'
        info['message'] = str(count)+' element(s) ont ete valide avec success.'
        info['element'] = element
        data.append(info)

    data = json.dumps(data)

    return data
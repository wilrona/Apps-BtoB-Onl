__author__ = 'User'


from ...modules import *
from models_doc import Document, LigneDoc
from forms_doc import FormDevis
from ..user.models_user import Users
from ..compagnie.models_compagnie import Compagnie
from ..company.models_company import Config_reference
from ..compagnie.forms_compagnie import FormClient
from ..user.forms_user import FormUser
from ..package.models_package import LigneService

prefix = Blueprint('commande', __name__)


@prefix.route('/')
@login_required
def index():

    current_ref = Config_reference.objects().first()
    title_page = 'Commande'

    if current_user.has_roles([('super_admin', 'commande')]):
        datas = Document.objects(Q(devisDoc=True) & Q(status=2))
    else:
        datas = Document.objects(Q(vendeur_id=current_user.id) & Q(devisDoc=True) & Q(status=2))

    return render_template('commande/index.html', **locals())


@prefix.route('/view/<objectid:devis_id>', methods=['GET'])
def view(devis_id):

    current_ref = Config_reference.objects().first()

    title_page = 'Commande'

    data = Document.objects.get(id=devis_id)

    if not current_user.has_roles([('super_admin', 'commande')], ['edit']) and data.vendeur_id.id != current_user.id:
        return redirect(url_for('devis.index'))

    form = FormDevis(obj=data)

    if data.opportunite_id:
        form.opportunite_id.data = str(data.opportunite_id.id)
        form.opportunite_text.data = data.opportunite_id.name

    ligne_doc = LigneDoc.objects(iddevis=data.id)

    customer = Compagnie.objects.get(id=data.client_id.id)
    form_client = FormClient(prefix="client", obj=customer)

    contact = Users.objects.get(id=data.contact_id.id)
    form_contact = FormUser(obj=contact)

    services = LigneService.objects()

    return render_template('devis/view.html', **locals())



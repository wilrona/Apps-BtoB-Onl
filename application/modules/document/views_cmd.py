__author__ = 'User'


from ...modules import *
from models_doc import Document, LigneDoc
from forms_doc import FormDevis
from ..user.models_user import Users
from ..compagnie.models_compagnie import Compagnie
from ..opportunite.models_opportunite import Opportunite
from ..site.models_site import Support, Horaire, Site
from ..site.models_site import Localisation, Ecran, Package
from ..company.models_company import Config_reference

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

    if not current_user.has_roles([('super_admin', 'commande')]) and data.vendeur_id.id != current_user.id:
        return redirect(url_for('commande.index'))

    form = FormDevis(obj=data)

    form.client_id.data = str(data.client_id.id)
    form.support_id.data = str(data.support_id.id)

    all = Client.objects()
    form.client_id.choices = [('', ' ')]
    for choice in all:
        form.client_id.choices.append((str(choice.id), choice.name))

    all = Support.objects()
    form.support_id.choices = [('', ' ')]
    for choice in all:
        form.support_id.choices.append((str(choice.id), choice.name))

    list_site = []
    lignes = LigneDoc.objects(doc_id=data.id)
    for ligne in lignes:
        site = {}
        site['id'] = str(ligne.id)
        site['name'] = ligne.site_id.name
        site['ref'] = str(current_ref.ref_site)+'/'+ligne.site_id.ref
        site['qte'] = ligne.passage
        site['prix'] = ligne.cout_passage
        site['total'] = ligne.passage * ligne.cout_passage
        list_site.append(site)

    return render_template('commande/view.html', **locals())



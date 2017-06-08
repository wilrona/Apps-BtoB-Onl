
from ...modules import *
from ..compagnie.views_compagnie import Compagnie


prefix = Blueprint('abonnement', __name__)


@prefix.route('/ici')
@login_required
@roles_required([('super_admin', 'abonnement_ici')])
def index():

    title_page = 'Abonnement ICI.CM'

    news = '2'
    datas = Compagnie.objects(Q(etat_souscription=1) | Q(etat_souscription=2) & Q(activated=True)).order_by('-updateDate')

    return render_template('abonnement/ici.html', **locals())
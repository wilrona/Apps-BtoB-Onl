
from ...modules import *
from models_paiement import Moyen_paiement
from form_paiement import FormMoyenPaiement

prefix = Blueprint('reglement', __name__)


@prefix.route('/')
@login_required
@roles_required([('super_admin', 'reglement')])
def index():

    title_page = 'Reglement Facture'

    datas = Moyen_paiement.objects()

    return render_template('paiement/index.html', **locals())
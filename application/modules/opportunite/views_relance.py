__author__ = 'User'

from ...modules import *
from models_opportunite import Suivie, Opportunite


prefix_relance = Blueprint('relance', __name__)


@prefix_relance.route('/')
@login_required
def index():

    title_page = 'Activite Suivante'
    single = False

    if not current_user.has_roles([('super_admin', 'opportunite')]):
        ids_opportunity = [opportunite.id for opportunite in Opportunite.objects(vendeur_id__ne=current_user.id).order_by('-createDate')]
    else:
        ids_opportunity = []

    datas = Suivie.objects(status=False).order_by('-dateNext')

    return render_template('relance/index.html', **locals())




from ...modules import *
from models_package import Package

prefix = Blueprint('package', __name__)


@prefix.route('/')
@login_required
@roles_required([('super_admin', 'package')])
def index():

    title_page = 'Services/Packages'

    datas = Package.objects()

    return render_template('package/index.html', **locals())


@prefix.route('/view/<objectid:package_id>', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'package')], ['edit'])
def view(package_id):

    return render_template('package/view.html', **locals())


@prefix.route('/edit/<objectid:package_id>', methods=['GET', 'POST'])
@prefix.route('/edit/', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'package')], ['edit'])
def edit(package_id=None):

    return render_template('package/edit.html', **locals())
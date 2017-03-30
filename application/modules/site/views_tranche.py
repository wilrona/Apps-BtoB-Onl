__author__ = 'User'


from ...modules import *
from models_site import Horaire
from forms_site import FormTranche

prefix_tranche = Blueprint('tranche', __name__)


@prefix_tranche.route('/')
@login_required
@roles_required([('super_admin', 'tranche')])
def index():

    title_page = 'Tranche Horaire'
    datas = Horaire.objects()

    return render_template('site/horaire/index.html', **locals())


@prefix_tranche.route('/view/<objectid:tranche_id>')
@login_required
@roles_required([('super_admin', 'tranche')])
def view(tranche_id):

    title_page = 'Tranche Horaire'

    data = Horaire.objects().get(id=tranche_id)
    form = FormTranche(obj=data)

    return render_template('site/horaire/view.html', **locals())


@prefix_tranche.route('/edit/<objectid:tranche_id>', methods=['GET', 'POST'])
@prefix_tranche.route('/edit/', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'tranche')], ['edit'])
def edit(tranche_id=None):

    title_page = 'Tranche Horaire'

    if tranche_id:
        data = Horaire.objects.get(id=tranche_id)
        form = FormTranche(obj=data)
        form.id.data = tranche_id
    else:
        data = Horaire()
        form = FormTranche()


    if form.validate_on_submit():

        data.name = form.name.data

        data = data.save()

        flash('Enregistement effectue avec succes', 'success')
        return redirect(url_for('tranche.view', tranche_id=data.id))

    return render_template('site/horaire/edit.html', **locals())
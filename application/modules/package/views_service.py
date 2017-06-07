from ...modules import *
from models_package import LigneService, Attribut
from form_package import FormService, FormAttribut

prefix_service = Blueprint('service', __name__)


@prefix_service.route('/')
@login_required
@roles_required([('super_admin', 'service')])
def index():

    title_page = 'Ligne de service'

    datas = LigneService.objects()

    return render_template('package/service/index.html', **locals())


@prefix_service.route('/view/<objectid:service_id>')
@login_required
@roles_required([('super_admin', 'service')])
def view(service_id):

    title_page = 'Ligne de service'

    data = LigneService.objects.get(id=service_id)
    form = FormService(obj=data)
    form.id.data = service_id

    attribut = Attribut.objects(idligneService=data.sigle)

    return render_template('package/service/view.html', **locals())


@prefix_service.route('/edit/<objectid:service_id>', methods=['GET', 'POST'])
@prefix_service.route('/edit/', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'service')], ['edit'])
def edit(service_id=None):

    title_page = 'Ligne de service'

    if service_id:
        data = LigneService.objects.get(id=service_id)
        form = FormService(obj=data)
        form.id.data = service_id

        attribut = Attribut.objects(idligneService=data.sigle)

    else:
        data = LigneService()
        form = FormService()

    if form.validate_on_submit():

        data.name = form.name.data

        if current_user.has_roles([('super_admin')]) and form.sigle.data:
            data.sigle = form.sigle.data

        if form.package.data:
            data.package = True
        else:
            data.package = False

        data.unite = form.unite.data

        data = data.save()

        flash('Enregistement effectue avec succes', 'success')

        if request.form['nouveau'] == '1':
            return redirect(url_for('service.edit'))
        else:
            return redirect(url_for('service.view', service_id=data.id))

    return render_template('package/service/edit.html', **locals())


@prefix_service.route('/attribut/view/<objectid:attribut_id>')
@login_required
@roles_required([('super_admin', 'service')])
def attribut_view(attribut_id):

    data = Attribut.objects.get(id=attribut_id)
    form = FormAttribut(obj=data)
    form.id.data = str(data.id)

    return render_template('attribut/view.html', **locals())


@prefix_service.route('/attibut/edit/<objectid:service_id>/<objectid:attribut_id>', methods=['GET', 'POST'])
@prefix_service.route('/attibut/edit/<objectid:service_id>', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'service')], ['edit'])
def attribut_edit(service_id, attribut_id=None):

    title_page = 'Clients'

    if attribut_id:
        data = Attribut.objects.get(id=attribut_id)
        form = FormAttribut(obj=data)
        form.id.data = str(data.id)
    else:
        data = Attribut()
        form = FormAttribut()

    success = False
    if form.validate_on_submit():

        service = LigneService.objects.get(id=service_id)
        data.idligneService = service.sigle

        if current_user.has_roles([('super_admin')]) and form.name.data:
            data.name = form.name.data

        data.libelle = form.libelle.data

        data.desc = form.desc.data

        data = data.save()
        success = True

    return render_template('attribut/edit.html', **locals())
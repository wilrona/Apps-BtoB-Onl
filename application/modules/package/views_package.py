
from ...modules import *
from models_package import Package, LigneService, Attribut
from form_package import FormPackage

prefix = Blueprint('package', __name__)


@prefix.route('/')
@login_required
@roles_required([('super_admin', 'package')])
def index():

    title_page = 'Packages/Offres'

    datas = Package.objects()

    return render_template('package/index.html', **locals())


@prefix.route('/view/<objectid:package_id>', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'package')], ['edit'])
def view(package_id):

    title_page = 'Packages/Offres'

    data = Package.objects.get(id=package_id)
    form = FormPackage(obj=data)
    form.id.data = package_id
    form.idligneService.data = data.idligneService

    all = LigneService.objects()
    form.idligneService.choices = [('', ' ')]
    for choice in all:
        form.idligneService.choices.append((str(choice.sigle), choice.name))

    if data.is_package:
        attr = Attribut.objects(idligneService=data.idligneService)

    return render_template('package/view.html', **locals())


@prefix.route('/edit/<objectid:package_id>', methods=['GET', 'POST'])
@prefix.route('/edit/', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'package')], ['edit'])
def edit(package_id=None):

    title_page = 'Packages/Offres'

    if package_id:
        data = Package.objects.get(id=package_id)
        form = FormPackage(obj=data)
        form.id.data = package_id
        form.idligneService.data = data.idligneService

    else:
        data = Package()
        form = FormPackage()

    all = LigneService.objects()
    form.idligneService.choices = [('', ' ')]
    for choice in all:
        form.idligneService.choices.append((str(choice.sigle), choice.name))

    if data.is_package and package_id:
        attr = Attribut.objects(idligneService=data.idligneService)

    if form.validate_on_submit():

        data.name = form.name.data
        data.idligneService = form.idligneService.data
        data.description = form.description.data
        data.prix = float(form.prix.data)
        data.duree = int(form.duree.data)

        ligne = LigneService.objects.get(sigle=form.idligneService.data)
        if ligne.package:
            data.is_package = True
        else:
            data.is_package = False

        if form.sale.data:
            data.sale = True
        else:
            data.sale = False

        if form.prix_promo.data:
            data.prix_promo = float(form.prix_promo.data)

        if form.promo.data:
            data.promo = True
        else:
            data.promo = False

        if ligne.package and not package_id:
            count = Package.objects(idligneService=form.idligneService.data).count()
            data.level = (count + 1)

        data.attribut = []
        for attr in request.form.getlist('attr'):
            data.attribut.append(attr)

        data = data.save()

        flash('Enregistement effectue avec succes', 'success')

        if not data.is_package:
            if request.form['nouveau'] == '1':
                return redirect(url_for('package.edit'))
            else:
                return redirect(url_for('package.view', package_id=data.id))
        else:
            if not package_id:
                flash('Proceder a la definition des attributs de votre package', 'success')
                return redirect(url_for('package.edit', package_id=data.id))
            else:
                return redirect(url_for('package.view', package_id=data.id))

    return render_template('package/edit.html', **locals())


@prefix.route('/etat/<objectid:package_id>')
@login_required
@roles_required([('super_admin', 'package')], ['edit'])
def etat(package_id):

    pack = Package.objects.get(id=package_id)
    if pack.status:
        pack.status = False
    else:
        pack.status = True

    pack.save()

    flash('Les modifications de l\'etat du package ont ete effectue', 'success')
    return redirect(url_for('package.view', package_id=package_id))


@prefix.route('/up/<objectid:package_id>')
@login_required
@roles_required([('super_admin', 'package')], ['edit'])
def up(package_id):
    current_etape = Package.objects.get(id=package_id)

    prev = current_etape.level - 1
    precedent = Package.objects(Q(level=prev) & Q(idligneService=current_etape.idligneService)).first()
    if precedent:
        precedent.level = current_etape.level
        precedent.save()

        current_etape.level = prev
        current_etape.save()

    return redirect(url_for('package.index'))


@prefix.route('/down/<objectid:package_id>')
@login_required
@roles_required([('super_admin', 'package')], ['edit'])
def down(package_id):
    current_etape = Package.objects.get(id=package_id)

    prev = current_etape.level + 1
    precedent = Package.objects(Q(level=prev) & Q(idligneService=current_etape.idligneService)).first()
    if precedent:
        precedent.level = current_etape.level
        precedent.save()

        current_etape.level = prev
        current_etape.save()

    return redirect(url_for('package.index'))
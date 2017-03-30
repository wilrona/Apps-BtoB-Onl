__author__ = 'User'

from ...modules import *
from models_site import Package, Ecran
from forms_site import FormPackage


prefix_package = Blueprint('package', __name__)


@prefix_package.route('/')
@login_required
@roles_required([('super_admin', 'package')])
def index():

    title_page = 'Packages'
    datas = Package.objects()
    return render_template('site/package/index.html', **locals())


@prefix_package.route('/view/<objectid:package_id>')
@login_required
@roles_required([('super_admin', 'package')])
def view(package_id):

    title_page = 'Packages'

    data = Package.objects().get(id=package_id)
    form = FormPackage(obj=data)
    form.id.data = str(package_id)

    return render_template('site/package/view.html', **locals())


@prefix_package.route('/edit/<objectid:package_id>', methods=['GET', 'POST'])
@prefix_package.route('/edit/', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'package')], ['edit'])
def edit(package_id=None):

    title_page = 'Packages'

    if package_id:
        data = Package.objects.get(id=package_id)
        form = FormPackage(obj=data)
        form.id.data = str(package_id)

    else:
        data = Package()
        form = FormPackage()


    if form.validate_on_submit():

        data.name = form.name.data

        # ecrant = None
        # old_ecrant = None
        # if package_id:
        #     old_ecrant = data.ecran_id


        data.prix_indoor = float(form.prix_indoor.data)
        data.prix_outdoor = float(form.prix_outdoor.data)
        data.passage = int(form.passage.data)

        data = data.save()

        # if ecrant:
        #     if old_ecrant:
        #         if old_ecrant != ecrant:
        #             old_site = [i.id for i in old_ecrant.site]
        #             if data.id in old_site:
        #                 current = Ecran.objects(id=old_ecrant.id)
        #                 current.update_one(pull__package=data)
        #
        #             site = [i.id for i in ecrant.site]
        #             if data.id not in site:
        #                 current = Ecran.objects(id=ecrant.id)
        #                 current.update_one(push__package=data)
        #     else:
        #         if data not in ecrant.site:
        #             current = Ecran.objects(id=ecrant.id)
        #             current.update_one(push__package=data)

        flash('Enregistement effectue avec succes', 'success')

        if request.form['nouveau'] == '1':
            return redirect(url_for('package.edit'))
        else:
            return redirect(url_for('package.view', package_id=data.id))

    return render_template('site/package/edit.html', **locals())


@prefix_package.route('/deleted', methods=['POST'])
@login_required
@roles_required([('super_admin', 'package')], ['delete'])
def deleted():

    from ..document.models_doc import LigneDoc

    data = []
    element = []
    count = 0
    for item in request.form.getlist('item_id'):
        info = {}
        item_found = Package.objects().get(id=item)
        pack = LigneDoc.objects(package=item_found)

        if pack:
            info['statut'] = 'NOK'
            info['message'] = 'Le package "'+item_found.name+'" est utilise comme information dans une ou plusieurs autre(s) document(s) Facture et/ou Devis'

        if not pack:
            item_found.delete()
            element.append(str(item_found.id))
            count += 1
        else:
            data.append(info)

    if count:
        info = {}
        info['statut'] = 'OK'
        info['message'] = str(count)+' element(s) ont ete supprime avec success'
        info['element'] = element
        data.append(info)

    data = json.dumps(data)

    return data

@prefix_package.route('/etat/<objectid:package_id>')
@login_required
@roles_required([('super_admin', 'package')], ['edit'])
def etat(package_id):

    data = Package.objects.get(id=package_id)
    if data.actif:
        data.actif = False
    else:
        data.actif = True

    data.save()

    flash('Les modifications de l\'etat du package ont ete effectues', 'success')
    return redirect(url_for('package.edit', package_id=package_id))

__author__ = 'User'

from ...modules import *
from models_site import Ecran
from forms_site import FormEcran


prefix_ecran = Blueprint('ecran', __name__)


@prefix_ecran.route('/')
@login_required
@roles_required([('super_admin', 'ecran')])
def index():

    title_page = 'Type d\'ecran'

    datas = Ecran.objects()


    return render_template('site/ecran/index.html', **locals())


@prefix_ecran.route('/view/<objectid:ecran_id>')
@login_required
@roles_required([('super_admin', 'ecran')])
def view(ecran_id):

    title_page = 'Type d\'ecran'

    data = Ecran.objects().get(id=ecran_id)
    form = FormEcran(obj=data)

    return render_template('site/ecran/view.html', **locals())


@prefix_ecran.route('/edit/<objectid:ecran_id>', methods=['GET', 'POST'])
@prefix_ecran.route('/edit/', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'ecran')], ['edit'])
def edit(ecran_id=None):

    title_page = 'Type d\'ecran'

    if ecran_id:
        data = Ecran.objects.get(id=ecran_id)
        form = FormEcran(obj=data)
        form.id.data = ecran_id
    else:
        data = Ecran()
        form = FormEcran()

    if form.validate_on_submit():

        data.name = form.name.data

        # if form.multi_choice.data:
        #     data.multi_choice = True
        # else:
        #     data.multi_choice = False

        if form.outdoor.data:
            data.outdoor = True
        else:
            data.outdoor = False

        data.cout_passage = float(form.cout_passage.data)

        data = data.save()

        flash('Enregistement effectue avec succes', 'success')

        if request.form['nouveau'] == '1':
            return redirect(url_for('ecran.edit'))
        else:
            return redirect(url_for('ecran.view', ecran_id=data.id))

    return render_template('site/ecran/edit.html', **locals())



@prefix_ecran.route('/deleted', methods=['POST'])
@login_required
@roles_required([('super_admin', 'ecran')], ['delete'])
def deleted():

    from models_site import Site

    data = []
    element = []
    count = 0
    for item in request.form.getlist('item_id'):
        info = {}
        item_found = Ecran.objects().get(id=item)
        site = Site.objects(ecran_id=item_found)

        if site:
            info['statut'] = 'NOK'
            info['message'] = 'L\'ecrant "'+item_found.name+'" est utilise par '+str(site.count())+' autre(s) site(s)'

        if not site:
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


@prefix_ecran.route('/etat/<objectid:ecran_id>')
@login_required
@roles_required([('super_admin', 'ecran')], ['edit'])
def etat(ecran_id):

    data = Ecran.objects.get(id=ecran_id)
    if data.actif:
        data.actif = False
    else:
        data.actif = True

    data.save()

    flash('Les modifications de l\'etat du type d\'ecran ont ete effectues', 'success')
    return redirect(url_for('ecran.edit', ecran_id=ecran_id))
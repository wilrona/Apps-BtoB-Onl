from ...modules import *
from models_opportunite import Libelle_Opportunite
from form_opportunite import FormLibelle

prefix_libelle = Blueprint('libelle_opportunite', __name__)


@prefix_libelle.route('/')
@login_required
def index():

    title_page = 'Libelle des opportunites'

    datas = Libelle_Opportunite.objects()

    return render_template('opportunite/libelle/index.html', **locals())


@prefix_libelle.route('/view/<objectid:libelle_id>')
@login_required
@roles_required([('super_admin', 'libelle_opportunite')])
def view(libelle_id):

    title_page = 'Secteur d\'activite'

    data = Libelle_Opportunite.objects().get(id=libelle_id)
    form = FormLibelle(obj=data)

    return render_template('opportunite/libelle/view.html', **locals())


@prefix_libelle.route('/edit/<objectid:libelle_id>', methods=['GET', 'POST'])
@prefix_libelle.route('/edit/', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'libelle_opportunite')], ['edit'])
def edit(libelle_id=None):

    title_page = 'Libelle des opportunites'

    if libelle_id:
        data = Libelle_Opportunite.objects.get(id=libelle_id)
        form = FormLibelle(obj=data)
        form.id.data = libelle_id
    else:
        data = Libelle_Opportunite()
        form = FormLibelle()

    if form.validate_on_submit():

        data.name = form.name.data

        data = data.save()

        flash('Enregistement effectue avec succes', 'success')

        if request.form['nouveau'] == '1':
            return redirect(url_for('libelle_opportunite.edit'))
        else:
            return redirect(url_for('libelle_opportunite.view', libelle_id=data.id))

    return render_template('opportunite/libelle/edit.html', **locals())


@prefix_libelle.route('/deleted', methods=['POST'])
@login_required
@roles_required([('super_admin', 'libelle_opportunite')], ['delete'])
def deleted():

    data = []
    element = []
    count = 0
    for item in request.form.getlist('item_id'):
        item_found = Libelle_Opportunite.objects().get(id=item)
        item_found.delete()
        element.append(str(item_found.id))
        count += 1

    if count:
        info = {}
        info['statut'] = 'OK'
        info['message'] = str(count)+' element(s) ont ete supprime avec success'
        info['element'] = element
        data.append(info)

    data = json.dumps(data)

    return data


@prefix_libelle.route('/etat/<objectid:libelle_id>')
@login_required
@roles_required([('super_admin', 'secteur')], ['edit'])
def etat(libelle_id):

    data = Libelle_Opportunite.objects.get(id=libelle_id)
    if data.actif:
        data.actif = False
    else:
        data.actif = True

    data.save()
    flash('Les modifications de l\'etat du libelle ont ete effectues', 'success')
    return redirect(url_for('libelle_opportunite.edit', libelle_id=libelle_id))
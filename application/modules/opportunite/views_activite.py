__author__ = 'User'

from ...modules import *
from models_opportunite import Activite
from form_opportunite import FormActivite


prefix_activite = Blueprint('activite', __name__)


@prefix_activite.route('/')
@login_required
@roles_required([('super_admin', 'activite')])
def index():

    title_page = 'Activite'

    datas = Activite.objects()

    return render_template('opportunite/activite/index.html', **locals())


@prefix_activite.route('/view/<objectid:activite_id>')
@login_required
@roles_required([('super_admin', 'activite')])
def view(activite_id):

    title_page = 'Activite'

    data = Activite.objects().get(id=activite_id)
    form = FormActivite(obj=data)
    if data.next:
        form.next.data = str(data.next.id)

    all = Activite.objects(id__ne=data.id)
    form.next.choices = [('', ' ')]
    for choice in all:
        form.next.choices.append((str(choice.id), choice.name))

    return render_template('opportunite/activite/view.html', **locals())


@prefix_activite.route('/edit/<objectid:activite_id>', methods=['GET', 'POST'])
@prefix_activite.route('/edit/', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'activite')], ['edit'])
def edit(activite_id=None):
    title_page = 'Activite'

    if activite_id:
        data = Activite.objects.get(id=activite_id)
        form = FormActivite(obj=data)
        form.id.data = activite_id

        if data.next and request.method == 'GET':
            form.next.data = str(data.next.id)

        all = Activite.objects(id__ne=data.id)
    else:
        data = Activite()
        form = FormActivite()
        all = Activite.objects()

    form.next.choices = [('', ' ')]
    for choice in all:
        form.next.choices.append((str(choice.id), choice.name))

    if form.validate_on_submit():

        data.description = form.description.data
        data.name = form.name.data
        data.jour = int(form.jour.data)
        if form.default.data:
            data.default = True
        else:
            data.default = False

        if form.next.data:
            current_next = Activite.objects(id=form.next.data).first()
            data.next = current_next

        if form.sigle.data:
            data.sigle = form.sigle.data

        data = data.save()

        flash('Enregistement effectue avec succes', 'success')

        if request.form['nouveau'] == '1':
            return redirect(url_for('activite.edit'))
        else:
            return redirect(url_for('activite.view', activite_id=data.id))

    return render_template('opportunite/activite/edit.html', **locals())


@prefix_activite.route('/deleted', methods=['POST'])
@login_required
@roles_required([('super_admin', 'activite')], ['delete'])
def deleted():

    data = []
    element = []
    count = 0
    for item in request.form.getlist('item_id'):
        info = {}
        item_found = Activite.objects().get(id=item)
        next_activite = Activite.objects(next=item_found)

        if next_activite:
            info['statut'] = 'NOK'
            info['message'] = 'L\'activite "'+item_found.name+'" est utilise par '+str(next_activite.count())+' autre(s) activite(s) en recommandation'

        if item_found.sigle:
            info['statut'] = 'NOK'
            info['message'] = 'L\'activite "'+item_found.name+'" ne peut etre supprimer'

        if not next_activite and not item_found.sigle:
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


@prefix_activite.route('/etat/<objectid:activite_id>')
@login_required
@roles_required([('super_admin', 'activite')], ['edit'])
def etat(activite_id):

    data = Activite.objects.get(id=activite_id)

    if not data.sigle:
        if data.actif:
            data.actif = False
        else:
            data.actif = True

        data.save()

        flash('Les modifications de l\'etat de l\'activite ont ete effectue', 'success')
    else:
        flash('Cette etat ne peut etre desactivee', 'warning')

    return redirect(url_for('activite.edit', activite_id=activite_id))





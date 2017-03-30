__author__ = 'User'

from ...modules import *
from models_site import Localisation
from forms_site import FormLocal

prefix_localisation = Blueprint('localisation', __name__)


@prefix_localisation.route('/')
@login_required
@roles_required([('super_admin', 'localisation')])
def index():

    title_page = 'Localisation'

    datas = Localisation.objects()

    return render_template('site/localisation/index.html', **locals())


@prefix_localisation.route('/view/<objectid:localisation_id>')
@login_required
@roles_required([('super_admin', 'localisation')])
def view(localisation_id):

    title_page = 'Localisation'

    data = Localisation.objects().get(id=localisation_id)
    form = FormLocal(obj=data)

    form.parent.choices = [('', 'Choix de la ville')]

    if data.parent:
        all = Localisation.objects(Q(parent=None) & Q(actif=True))
        form.parent.data = str(data.parent.id)
        for choice in all:
            form.parent.choices.append((str(choice.id), choice.name))

    return render_template('site/localisation/view.html', **locals())


@prefix_localisation.route('/edit/<objectid:localisation_id>', methods=['GET', 'POST'])
@prefix_localisation.route('/edit/', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'localisation')], ['edit'])
def edit(localisation_id=None):

    title_page = 'Localisation'

    if localisation_id:
        data = Localisation.objects.get(id=localisation_id)
        form = FormLocal(obj=data)
        form.id.data = localisation_id
        if data.parent and request.method == 'GET':
            form.parent.data = str(data.parent.id)
    else:
        data = Localisation()
        form = FormLocal()


    form.parent.choices = [('', 'Choix de la ville')]

    all = Localisation.objects(Q(parent=None) & Q(actif=True))
    for choice in all:
        form.parent.choices.append((str(choice.id), choice.name))

    if not request.args.get('quartier'):
        form.parent.data = ''

    form.quartier.data = 0
    if request.args.get('quartier') or data.parent:
        form.quartier.data = 1

    if form.validate_on_submit():

        data.name = form.name.data

        if form.parent.data:
            ville = Localisation.objects(id=form.parent.data).first()
            data.parent = ville

        data = data.save()

        flash('Enregistement effectue avec succes', 'success')

        if request.form['nouveau'] == '1':
            return redirect(url_for('localisation.edit', quartier=request.args.get('quartier')))
        else:
            return redirect(url_for('localisation.view', localisation_id=data.id))

    return render_template('site/localisation/edit.html', **locals())



@prefix_localisation.route('/deleted', methods=['POST'])
@login_required
@roles_required([('super_admin', 'localisation')], ['delete'])
def deleted():

    from ..site.models_site import Site

    data = []
    element = []
    count = 0
    for item in request.form.getlist('item_id'):
        info = {}
        item_found = Localisation.objects().get(id=item)
        site = Site.objects(local_id=item_found)

        if site:
            info['statut'] = 'NOK'
            info['message'] = 'La localisation "'+item_found.name+'" est utilise par '+str(site.count())+' autre(s) site(s)'

        exit_ville = Localisation.objects(parent=item_found)
        if exit_ville:
            info['statut'] = 'NOK'
            info['message'] = 'La localisation "'+item_found.name+'" est utilise par '+str(exit_ville.count())+' autre(s) quartier(s)'

        if not site and not exit_ville:
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


@prefix_localisation.route('/etat/<objectid:localisation_id>')
@login_required
@roles_required([('super_admin', 'localisation')], ['edit'])
def etat(localisation_id):

    data = Localisation.objects.get(id=localisation_id)
    if data.actif:
        data.actif = False
    else:
        data.actif = True

    data.save()

    flash('Les modifications de l\'etat de la localisation ont ete effectues', 'success')
    return redirect(url_for('localisation.edit', localisation_id=localisation_id))
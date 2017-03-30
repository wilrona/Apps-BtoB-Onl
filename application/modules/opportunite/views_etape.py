__author__ = 'User'

from ...modules import *
from models_opportunite import Etape
from form_opportunite import FormEtape


prefix_etape = Blueprint('etape', __name__)


@prefix_etape.route('/')
@login_required
@roles_required([('super_admin', 'etape')])
def index():

    title_page = 'Etape'
    datas = Etape.objects().order_by('order')

    return render_template('opportunite/etape/index.html', **locals())


@prefix_etape.route('/view/<objectid:etape_id>')
@login_required
@roles_required([('super_admin', 'etape')])
def view(etape_id):
    title_page = 'Etape'

    data = Etape.objects().get(id=etape_id)
    form = FormEtape(obj=data)

    return render_template('opportunite/etape/view.html', **locals())


@prefix_etape.route('/edit/<objectid:etape_id>', methods=['GET', 'POST'])
@prefix_etape.route('/edit/', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'etape')], ['edit'])
def edit(etape_id=None):

    title_page = 'Etape'

    if etape_id:
        data = Etape.objects.get(id=etape_id)
        form = FormEtape(obj=data)
        form.id.data = etape_id
    else:
        data = Etape()
        form = FormEtape()

    if form.validate_on_submit():

        data.proba = float(form.proba.data)
        data.name = form.name.data

        if not etape_id:
            exist = False
            position = 1
            while not exist:
                etap = Etape.objects(order=position).get()
                if not etap:
                    exist = True
                    data.order = position
                position += 1

        if form.sigle.data:
            data.sigle = form.sigle.data

        etape = data.save()

        flash('Enregistement effectue avec succes', 'success')

        if request.form['nouveau'] == '1':
            return redirect(url_for('etape.edit'))
        else:
            return redirect(url_for('etape.view', etape_id=etape.id))

    return render_template('opportunite/etape/edit.html', **locals())


@prefix_etape.route('/up/<objectid:etape_id>')
@login_required
@roles_required([('super_admin', 'etape')], ['edit'])
def up(etape_id):
    current_etape = Etape.objects.get(id=etape_id)

    prev = current_etape.order - 1
    precedent = Etape.objects(order=prev).first()
    if precedent:
        precedent.order = current_etape.order
        precedent.save()

        current_etape.order = prev
        current_etape.save()

    return redirect(url_for('etape.index'))


@prefix_etape.route('/down/<objectid:etape_id>')
@login_required
@roles_required([('super_admin', 'etape')], ['edit'])
def down(etape_id):
    current_etape = Etape.objects.get(id=etape_id)

    prev = current_etape.order + 1
    precedent = Etape.objects(order=prev).first()
    if precedent:
        precedent.order = current_etape.order
        precedent.save()

        current_etape.order = prev
        current_etape.save()

    return redirect(url_for('etape.index'))


@prefix_etape.route('/deleted', methods=['POST'])
@login_required
@roles_required([('super_admin', 'etape')], ['delete'])
def deleted():

    # from ..opportunite.models_opportunite import Suivie, Opportunite

    data = []
    element = []
    count = 0
    for item in request.form.getlist('item_id'):
        info = {}
        item_found = Etape.objects().get(id=item)

        # opportunite = Opportunite.objects(etape_id=item_found)

        # if opportunite:
        #     info['statut'] = 'NOK'
        #     info['message'] = 'L\'etape "'+item_found.name+'" est utilise par '+str(opportunite.count())+' autre(s) opportunite(s)'
        #
        # exit_suivie = Suivie.objects(etape_id=item_found)
        # if exit_suivie:
        #     info['statut'] = 'NOK'
        #     info['message'] = 'L\'etape "'+item_found.name+'" est utilise par '+str(exit_suivie.count())+' autre(s) suivie(s)'

        if item_found.sigle:
            info['statut'] = 'NOK'
            info['message'] = 'L\'etape "'+item_found.name+'" ne peut etre supprimer'

        # if not opportunite and not exit_suivie:
        if not item_found.sigle:
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


@prefix_etape.route('/etat/<objectid:etape_id>')
@login_required
@roles_required([('super_admin', 'etape')], ['edit'])
def etat(etape_id):

    data = Etape.objects.get(id=etape_id)
    if data.actif:
        data.actif = False
    else:
        data.actif = True

    data.save()

    flash('Les modifications de l\'etat de l\'etape ont ete effectues', 'success')
    return redirect(url_for('etape.edit', etape_id=etape_id))


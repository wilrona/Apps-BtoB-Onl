__author__ = 'User'

from ...modules import *
from models_site import Support
from forms_site import FormSupport


prefix_support = Blueprint('support', __name__)


@prefix_support.route('/')
@login_required
@roles_required([('super_admin', 'support')])
def index():

    title_page = 'Format de contenu'
    datas = Support.objects()


    return render_template('site/support/index.html', **locals())


@prefix_support.route('/view/<objectid:support_id>')
@login_required
@roles_required([('super_admin', 'support')])
def view(support_id):

    title_page = 'Format de contenu'

    data = Support.objects().get(id=support_id)
    form = FormSupport(obj=data)

    return render_template('site/support/view.html', **locals())


@prefix_support.route('/edit/<objectid:support_id>', methods=['GET', 'POST'])
@prefix_support.route('/edit/', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'support')], ['edit'])
def edit(support_id=None):

    title_page = 'Format de contenu'

    if support_id:
        data = Support.objects.get(id=support_id)
        form = FormSupport(obj=data)
        form.id.data = support_id
    else:
        data = Support()
        form = FormSupport()


    if form.validate_on_submit():

        data.name = form.name.data

        data = data.save()

        flash('Enregistement effectue avec succes', 'success')

        if request.form['nouveau'] == '1':
            return redirect(url_for('support.edit'))
        else:
            return redirect(url_for('support.view', support_id=data.id))

    return render_template('site/support/edit.html', **locals())



@prefix_support.route('/deleted', methods=['POST'])
@login_required
@roles_required([('super_admin', 'support')], ['delete'])
def deleted():

    from ..document.models_doc import Document

    data = []
    element = []
    count = 0
    for item in request.form.getlist('item_id'):
        info = {}
        item_found = Support.objects().get(id=item)
        document = Document.objects(support_id=item_found)

        if document:
            info['statut'] = 'NOK'
            info['message'] = 'Le format de contenu "'+item_found.name+'" est utilise par '+str(document.count())+' autre(s) document(s) facture et/ou devis'

        if not document:
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


@prefix_support.route('/etat/<objectid:support_id>')
@login_required
@roles_required([('super_admin', 'support')], ['edit'])
def etat(support_id):

    data = Support.objects.get(id=support_id)
    if data.actif:
        data.actif = False
    else:
        data.actif = True

    data.save()

    flash('Les modifications de l\'etat du support ont ete effectues', 'success')
    return redirect(url_for('support.edit', support_id=support_id))

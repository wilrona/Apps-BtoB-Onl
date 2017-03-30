__author__ = 'User'

from ...modules import *
from models_site import Secteur
from forms_site import FormSecteur


prefix_secteur = Blueprint('secteur', __name__)


@prefix_secteur.route('/')
@login_required
@roles_required([('super_admin', 'secteur')])
def index():

    title_page = 'Secteur d\'activite'

    datas = Secteur.objects()

    return render_template('site/secteur/index.html', **locals())


@prefix_secteur.route('/view/<objectid:secteur_id>')
@login_required
@roles_required([('super_admin', 'secteur')])
def view(secteur_id):

    title_page = 'Secteur d\'activite'

    data = Secteur.objects().get(id=secteur_id)
    form = FormSecteur(obj=data)

    return render_template('site/secteur/view.html', **locals())


@prefix_secteur.route('/edit/<objectid:secteur_id>', methods=['GET', 'POST'])
@prefix_secteur.route('/edit/', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'secteur')], ['edit'])
def edit(secteur_id=None):

    title_page = 'Secteur d\'activite'

    if secteur_id:
        data = Secteur.objects.get(id=secteur_id)
        form = FormSecteur(obj=data)
        form.id.data = secteur_id
    else:
        data = Secteur()
        form = FormSecteur()


    if form.validate_on_submit():

        data.name = form.name.data

        data = data.save()

        flash('Enregistement effectue avec succes', 'success')

        if request.form['nouveau'] == '1':
            return redirect(url_for('secteur.edit'))
        else:
            return redirect(url_for('secteur.view', secteur_id=data.id))

    return render_template('site/secteur/edit.html', **locals())


@prefix_secteur.route('/deleted', methods=['POST'])
@login_required
@roles_required([('super_admin', 'secteur')], ['delete'])
def deleted():

    from models_site import Site

    data = []
    element = []
    count = 0
    for item in request.form.getlist('item_id'):
        info = {}
        item_found = Secteur.objects().get(id=item)
        site = Site.objects(secteur_id=item_found)

        if site:
            info['statut'] = 'NOK'
            info['message'] = 'Le secteur "'+item_found.name+'" est utilise par '+str(site.count())+' autre(s) Site(s)'

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


@prefix_secteur.route('/etat/<objectid:secteur_id>')
@login_required
@roles_required([('super_admin', 'secteur')], ['edit'])
def etat(secteur_id):

    data = Secteur.objects.get(id=secteur_id)
    if data.actif:
        data.actif = False
    else:
        data.actif = True

    data.save()

    flash('Les modifications de l\'etat du secteur ont ete effectues', 'success')
    return redirect(url_for('secteur.edit', secteur_id=secteur_id))

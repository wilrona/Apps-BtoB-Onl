

from ...modules import *


from models_compagnie import Categorie
from forms_compagnie import FormCategorie


prefix_categorie = Blueprint('categorie', __name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@prefix_categorie.route('/')
@login_required
@roles_required([('super_admin', 'categorie')])
def index():

    title_page = 'Categories'

    datas = Categorie.objects()

    return render_template('compagnie/categorie/index.html', **locals())


@prefix_categorie.route('/view/<objectid:categorie_id>')
@login_required
@roles_required([('super_admin', 'categorie')])
def view(categorie_id):

    title_page = 'Categories'

    data = Categorie.objects().get(id=categorie_id)
    form = FormCategorie(obj=data)

    form.parent_idcategorie.choices = [('', 'Choix de la categorie')]

    if data.parent_idcategorie:
        all = Categorie.objects(Q(parent_idcategorie=None) & Q(activated=True))
        form.parent_idcategorie.data = str(data.parent_idcategorie.id)
        for choice in all:
            form.parent_idcategorie.choices.append((str(choice.id), choice.name))

    return render_template('compagnie/categorie/view.html', **locals())


@prefix_categorie.route('/edit/<objectid:categorie_id>', methods=['GET', 'POST'])
@prefix_categorie.route('/edit/', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'categorie')], ['edit'])
def edit(categorie_id=None):

    title_page = 'Categories'

    if categorie_id:
        data = Categorie.objects.get(id=categorie_id)
        form = FormCategorie(obj=data)
        form.id.data = categorie_id
        if data.parent_idcategorie and request.method == 'GET':
            form.parent_idcategorie.data = str(data.parent_idcategorie.id)
    else:
        data = Categorie()
        form = FormCategorie()

    form.parent_idcategorie.choices = [('', 'Choix de la categorie')]

    all = Categorie.objects(Q(parent_idcategorie=None) & Q(activated=True))
    for choice in all:
        form.parent_idcategorie.choices.append((str(choice.id), choice.name))

    if not request.args.get('categorie'):
        form.parent_idcategorie.data = ''

    form.enfant.data = 0
    if request.args.get('categorie') or data.parent_idcategorie:
        form.enfant.data = 1

    if request.method == 'POST':

        file = request.files['file']
        file_icone = request.files['file_icone']

        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            link_save_file = '/static/uploads/'+filename
            form.url_image.data = link_save_file
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            flash('Le systeme n\'accepte que les images au format .png, .jpg ou .jpeg', 'warning')

        if allowed_file(file_icone.filename):
            filename = secure_filename(file_icone.filename)
            link_save_file_icone = '/static/uploads/'+filename
            form.icone.data = link_save_file_icone
            file_icone.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            flash('Le systeme n\'accepte que les images au format .png, .jpg ou .jpeg pour les icones', 'warning')

    if form.validate_on_submit():

        data.name = form.name.data
        data.slug = function._slugify(form.name.data)

        if form.parent_idcategorie.data:
            categorie = Categorie.objects(id=form.parent_idcategorie.data).first()
            data.parent_idcategorie = categorie

        data.url_image = form.url_image.data
        data.icone = form.icone.data

        data = data.save()

        flash('Enregistement effectue avec succes', 'success')

        if request.form['nouveau'] == '1':
            return redirect(url_for('categorie.edit', categorie=request.args.get('categorie')))
        else:
            return redirect(url_for('categorie.view', categorie_id=data.id))

    return render_template('compagnie/categorie/edit.html', **locals())


@prefix_categorie.route('/deleted', methods=['POST'])
@login_required
@roles_required([('super_admin', 'categorie')], ['delete'])
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


@prefix_categorie.route('/etat/<objectid:categorie_id>')
@login_required
@roles_required([('super_admin', 'categorie')], ['edit'])
def etat(categorie_id):

    data = Localisation.objects.get(id=categorie_id)
    if data.actif:
        data.actif = False
    else:
        data.actif = True

    data.save()

    flash('Les modifications de l\'etat de la localisation ont ete effectues', 'success')
    return redirect(url_for('categorie.edit', categorie_id=categorie_id))
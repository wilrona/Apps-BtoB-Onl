

from ...modules import *


from models_compagnie import Categorie, Compagnie
from forms_compagnie import FormCategorie


prefix_categorie = Blueprint('categorie', __name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER_CATEGORIE'],
                               filename, as_attachment=True)


@prefix_categorie.route('/')
@login_required
@roles_required([('super_admin', 'categorie')])
def index():

    title_page = 'Categories'

    datas = Categorie.objects()

    return render_template('client/categorie/index.html', **locals())


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

    return render_template('client/categorie/view.html', **locals())


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

    if not request.args.get('categorie') and not categorie_id:
        form.parent_idcategorie.data = ''

    if not form.parent_idcategorie.data or not data.parent_idcategorie:
        form.parent_idcategorie.data = ''

    form.enfant.data = 0
    if request.args.get('categorie') or data.parent_idcategorie:
        form.enfant.data = 1

    if form.validate_on_submit():

        old_name = None
        if categorie_id:
            old_name = data.name

        data.name = form.name.data
        data.slug = function._slugify(form.name.data)

        if form.parent_idcategorie.data:
            categorie = Categorie.objects().get(id=form.parent_idcategorie.data)
            data.parent_idcategorie = categorie

        error_file = False
        if not form.parent_idcategorie.data:

            file = request.files['file']
            file_icone = request.files['file_icone']

            if old_name:
                old_rename = function._slugify(old_name)
            else:
                old_rename = function._slugify(data.name)

            if file:

                if allowed_file(file.filename):

                    if data.url_image:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER_CATEGORIE'], data.url_image))

                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER_CATEGORIE'], filename))

                    extension = filename.split(".")
                    extension = extension[1]

                    source = os.path.join(app.config['UPLOAD_FOLDER_CATEGORIE'], filename)
                    destination = app.config['UPLOAD_FOLDER_CATEGORIE']+"/image-"+old_rename+"."+extension

                    os.rename(source, destination)

                    link_save_file = "image-"+old_rename+"."+extension
                    form.url_image.data = link_save_file

                else:
                    flash('Le systeme n\'accepte que les images au format .png, .jpg ou .jpeg', 'warning')
                    error_file = True

            if file_icone:

                if allowed_file(file_icone.filename):

                    if data.icone:
                        os.remove(os.path.join(app.config['UPLOAD_FOLDER_CATEGORIE'], data.icone))

                    filename = secure_filename(file_icone.filename)

                    filename = secure_filename(file_icone.filename)
                    file_icone.save(os.path.join(app.config['UPLOAD_FOLDER_CATEGORIE'], filename))

                    extension = filename.split(".")
                    extension = extension[1]

                    source = os.path.join(app.config['UPLOAD_FOLDER_CATEGORIE'], filename)
                    destination = app.config['UPLOAD_FOLDER_CATEGORIE']+"/icone-"+old_rename+"."+extension

                    os.rename(source, destination)

                    link_save_file_icone = "icone-"+old_rename+"."+extension
                    form.icone.data = link_save_file_icone

                else:
                    flash('Le systeme n\'accepte que les images au format .png, .jpg ou .jpeg pour les icones', 'warning')
                    error_file = True

        if form.url_image.data:
            data.url_image = form.url_image.data

        if form.icone.data:
            data.icone = form.icone.data

        if form.description.data:
            data.description = form.description.data

        if not error_file:
            data = data.save()

            flash('Enregistement effectue avec succes', 'success')

            if request.form['nouveau'] == '1':
                return redirect(url_for('categorie.edit', categorie=request.args.get('categorie')))
            else:
                return redirect(url_for('categorie.view', categorie_id=data.id))

    return render_template('client/categorie/edit.html', **locals())


@prefix_categorie.route('/deleted', methods=['POST'])
@login_required
@roles_required([('super_admin', 'categorie')], ['delete'])
def deleted():

    data = []
    element = []
    count = 0
    for item in request.form.getlist('item_id'):
        info = {}
        item_found = Categorie.objects().get(id=item)
        entreprise = Compagnie.objects(idcategorie=item_found)

        if entreprise:
            info['statut'] = 'NOK'
            info['message'] = 'La categorie "'+item_found.name+'" est utilise par '+str(entreprise.count())+' autre(s) entreprise(s)'

        if not entreprise:
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

    data = Categorie.objects.get(id=categorie_id)

    if data.activated:
        data.activated = False
    else:
        data.activated = True

    data.save()

    flash('Les modifications d\'etat des categories ont ete effectues', 'success')
    return redirect(url_for('categorie.edit', categorie_id=categorie_id))


@prefix_categorie.route('/activated', methods=['POST'])
@login_required
@roles_required([('super_admin', 'categorie')], ['edit'])
def etat_activated():

    data = []
    element = []
    count = 0
    for item in request.form.getlist('item_id'):
        info = {}
        item_found = Categorie.objects().get(id=item)

        if item_found.parent_idcategorie and item_found.activated:
            info['statut'] = 'NOK'
            info['message'] = 'La categorie "'+item_found.name+'" est deja active'

        if not item_found.activated and item_found.parent_idcategorie:
            item_found.activated = True
            element.append(str(item_found.id))
            item_found.save()
            count += 1
        else:
            data.append(info)

    if count:
        info = {}
        info['statut'] = 'OK'
        info['message'] = str(count)+' element(s) ont ete active avec success'
        info['element'] = element
        data.append(info)

    data = json.dumps(data)

    return data


@prefix_categorie.route('/unactivated', methods=['POST'])
@login_required
@roles_required([('super_admin', 'categorie')], ['edit'])
def etat_unactivated():

    data = []
    element = []
    count = 0
    for item in request.form.getlist('item_id'):
        info = {}
        item_found = Categorie.objects().get(id=item)

        if not item_found.activated and item_found.parent_idcategorie:
            info['statut'] = 'NOK'
            info['message'] = 'La categorie "'+item_found.name+'" est deja desactive'

        if item_found.activated and item_found.parent_idcategorie:
            item_found.activated = False
            element.append(str(item_found.id))
            item_found.save()
            count += 1
        else:
            data.append(info)

    if count:
        info = {}
        info['statut'] = 'OK'
        info['message'] = str(count)+' element(s) ont ete desactive avec success'
        info['element'] = element
        data.append(info)

    data = json.dumps(data)

    return data


@prefix_categorie.route('/all_activated')
def all_activated():

    for cat in Categorie.objects():
        cat.save()

    return 'True'
__author__ = 'User'


from ...modules import *
from models_site import Site, Ecran, Localisation, Secteur
from forms_site import FormSite
from ..company.models_company import Config_reference

prefix_site = Blueprint('site', __name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@prefix_site.route('/')
@login_required
@roles_required([('super_admin', 'site')])
def index():

    current_ref = Config_reference.objects().first()

    title_page = 'Sites'

    datas = Site.objects()

    return render_template('site/index.html', **locals())



@prefix_site.route('/view/<objectid:site_id>')
@login_required
@roles_required([('super_admin', 'site')])
def view(site_id):

    current_ref = Config_reference.objects().first()

    title_page = 'Sites'

    data = Site.objects().get(id=site_id)
    form = FormSite(obj=data)

    if data.ecran_id:
        form.ecrant.data = str(data.ecran_id.id)

    if data.local_id:
        form.local.data = str(data.local_id.id)

    if data.secteur_id:
        form.secteur.data = str(data.secteur_id.id)

    form.ecrant.choices = [('', 'Type d\'ecran')]
    all = Ecran.objects(actif=True)
    for choice in all:
        form.ecrant.choices.append((str(choice.id), choice.name))

    form.local.choices = [('', 'Quartier du site')]
    all = Localisation.objects(Q(actif=True) & Q(parent__ne=None))
    for choice in all:
        form.local.choices.append((str(choice.id), choice.name))

    form.secteur.choices = [('', 'Secteur d\'activite')]
    all = Secteur.objects(actif=True)
    for choice in all:
        form.secteur.choices.append((str(choice.id), choice.name))

    return render_template('site/view.html', **locals())


@prefix_site.route('/edit/<objectid:site_id>', methods=['GET', 'POST'])
@prefix_site.route('/edit/', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'site')], ['edit'])
def edit(site_id=None):

    current_ref = Config_reference.objects().first()

    title_page = 'Sites'

    if site_id:
        data = Site.objects.get(id=site_id)
        form = FormSite(obj=data)
        form.id.data = site_id

        if data.ecran_id and request.method == 'GET':
            form.ecrant.data = str(data.ecran_id.id)

        if data.local_id and request.method == 'GET':
            form.local.data = str(data.local_id.id)

        if data.secteur_id and request.method == 'GET':
            form.secteur.data = str(data.secteur_id.id)
    else:
        data = Site()
        form = FormSite()

    form.ecrant.choices = [('', 'Type d\'ecran')]
    all_ecran = Ecran.objects(actif=True)
    for choice in all_ecran:
        form.ecrant.choices.append((str(choice.id), choice.name))

    form.local.choices = [('', 'Quartier du site')]
    all_local = Localisation.objects(Q(actif=True) & Q(parent__ne=None))
    for choice in all_local:
        form.local.choices.append((str(choice.id), choice.name))

    form.secteur.choices = [('', 'Secteur d\'activite')]
    all = Secteur.objects(actif=True)
    for choice in all:
        form.secteur.choices.append((str(choice.id), choice.name))

    file = None
    if request.method == 'POST':
        file = request.files['file']

    if form.validate_on_submit():

        data.name = form.name.data

        ecrant = None
        old_ecrant = None
        if site_id:
            old_ecrant = data.ecran_id

        if form.ecrant.data:
            ecrant = Ecran.objects().get(id=form.ecrant.data)
            data.ecran_id = ecrant

        local = None
        old_local = None
        if site_id:
            old_local = data.local_id

        if form.local.data:
            local = Localisation.objects().get(id=form.local.data)
            data.local_id = local

        if form.secteur.data:
            secteur = Secteur.objects().get(id=form.secteur.data)
            data.secteur_id = secteur

        data.type = form.type.data

        if form.latitude.data:
            data.latitude = float(form.latitude.data)

        if form.longitude.data:
            data.longitude = float(form.longitude.data)

        if not site_id:
            count_exist = Site.objects().count()
            reference = function.reference(count_exist+1, 4)
            data.ref = reference

        if file:
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                link_save = '/static/uploads/'+filename
                data.image = link_save
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            else:
                flash('Le systeme n\'accepte que les images au format .png, .jpg ou .jpeg', 'warning')




        data = data.save()

        # if local:
        #     if old_local:
        #         if old_local != local:
        #             old_site = [i.id for i in old_local.site]
        #             if data.id in old_site:
        #                 current = Localisation.objects(id=old_local.id)
        #                 current.update_one(pull__site=data)
        #
        #             site = [i.id for i in local.site]
        #             if data.id not in site:
        #                 current = Localisation.objects(id=local.id)
        #                 current.update_one(push__site=data)
        #     else:
        #         if data not in local.site:
        #             current = Localisation.objects(id=local.id)
        #             current.update_one(push__site=data)
        #
        # if ecrant:
        #     if old_ecrant:
        #         if old_ecrant != ecrant:
        #             old_site = [i.id for i in old_ecrant.site]
        #             if data.id in old_site:
        #                 current = Ecran.objects(id=old_ecrant.id)
        #                 current.update_one(pull__site=data)
        #
        #             site = [i.id for i in ecrant.site]
        #             if data.id not in site:
        #                 current = Ecran.objects(id=ecrant.id)
        #                 current.update_one(push__site=data)
        #     else:
        #         if data not in ecrant.site:
        #             current = Ecran.objects(id=ecrant.id)
        #             current.update_one(push__site=data)


        flash('Enregistement effectue avec succes', 'success')

        if request.form['nouveau'] == '1':
            return redirect(url_for('site.edit'))
        else:
            return redirect(url_for('site.view', site_id=data.id))

    return render_template('site/edit.html', **locals())



@prefix_site.route('/deleted', methods=['POST'])
@login_required
@roles_required([('super_admin', 'site')], ['delete'])
def deleted():

    from models_site import Ecran
    from ..document.models_doc import LigneDoc

    data = []
    element = []
    count = 0
    for item in request.form.getlist('item_id'):
        info = {}
        item_found = Site.objects().get(id=item)
        # ecran = Ecran.objects(site=item_found)

        exit_ldoc = LigneDoc.objects(site_id=item_found)
        if exit_ldoc:
            info['statut'] = 'NOK'
            info['message'] = 'Le site "'+item_found.name+'" est utilise dans des informations de documents facture et/ou devis'

        if not exit_ldoc:

            # ecran.update(pull__site=item_found)

            item_found.delete()
            element.append(str(item_found.id))
            count += 1
        else:
            data.append(info)

    if count:
        info = {}
        info['statut'] = 'OK'
        info['message'] = str(count)+' element(s) supprime(s) avec success'
        info['element'] = element
        data.append(info)

    data = json.dumps(data)

    return data


@prefix_site.route('/etat/<objectid:site_id>')
@login_required
@roles_required([('super_admin', 'site')], ['edit'])
def etat(site_id):

    data = Site.objects.get(id=site_id)
    if data.actif:
        data.actif = False
    else:
        data.actif = True

    data.save()

    flash('Les modifications de l\'etat du site ont ete effectues', 'success')
    return redirect(url_for('site.edit', site_id=site_id))


@prefix_site.route('/correction')
@login_required
@roles_required([('super_admin', 'site')])
def correction():

    all_site = Site.objects()

    for site in all_site:
        if site.longitude and site.latitude:
            memory_lg = site.longitude
            memory_lt = site.latitude
            site.latitude = memory_lg
            site.longitude = memory_lt
            site.save()

    return 'True'


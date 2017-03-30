__author__ = 'wilrona'

from ...modules import *

from models_profil import Profil, ProfilRole, Roles
from forms_profil import FormProfil

# Flask-Cache (configured to use App Engine Memcache API)
prefix = Blueprint('profil', __name__)


@prefix.route('/profil')
@login_required
@roles_required([('super_admin', 'profil')])
def index():
    title_parent = 'Configuration'
    title_page = 'Profils'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    offset = 0
    limit = 10
    if page > 1:
        offset = ((page - 1) * 10)

    count = Profil.objects().count()
    datas = Profil.objects().skip(offset).limit(limit)

    pagination = Pagination(css_framework='uikit', page=page, total=count, search=search, record_name='Profils')

    return render_template('profil/index.html', **locals())


@prefix.route('/profil/edit',  methods=['GET', 'POST'])
@prefix.route('/profil/edit/<objectid:profil_id>',  methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'grade')], ['edit'])
def edit(profil_id=None):

    if profil_id:
        profils = Profil.objects.get(id=profil_id)
        form = FormProfil(obj=profils)
        form.id.data = profil_id
    else:
        profils = Profil()
        form = FormProfil()

    success = False
    if form.validate_on_submit():

        profils.name = form.name.data
        profils.description = form.description.data
        profils.active = form.active.data
        profils.save()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('profil/edit.html', **locals())


@prefix.route('/profil/delete/<objectid:profil_id>')
@login_required
@roles_required([('super_admin', 'grade')], ['delete'])
def delete(profil_id):
    profils = Profil.objects.get(id=profil_id)

    profil_role_exist = ProfilRole.objects(
        profil_id = profils.id
    )

    if len(profil_role_exist):
        flash('Impossible de supprimer de profil car il contient des roles', 'warning')
    else:
        profils.delete()
        flash('Suppression reussie', 'success')
    return redirect(url_for('profil.index'))


@prefix.route('/profil/role/<objectid:profil_id>',  methods=['GET', 'POST'])
def list(profil_id):

    profil = Profil.objects.get(id=profil_id)

    # liste des roles lie au profil en cours
    attrib = ProfilRole.objects(profil_id = profil.id)

    attrib_list = [role.role_id.id for role in attrib]

    # liste des roles lie au profil en cours avec le droit d'edition
    edit = ProfilRole.objects(Q(profil_id=profil.id) & Q(edit=True))

    edit_list = [role.role_id.id for role in edit]

    # liste des roles lie au profil en cours avec le droit de modification
    delete = ProfilRole.objects(Q(profil_id=profil.id) & Q(deleted=True))
    delete_list = [role.role_id.id for role in delete]

    liste_role = []
    data_role = Roles.objects(
        valeur__ne='super_admin'
    )

    for role in data_role:
        if not role.parent:
            module = {}
            module['titre'] = role.titre
            enfants = Roles.objects(
                parent = role.id
            )
            module['role'] = []
            for enfant in enfants:
                rol = {}
                rol['id'] = enfant.id
                rol['titre'] = enfant.titre
                rol['action'] = enfant.action
                module['role'].append(rol)
            liste_role.append(module)

    success = False
    if request.method == 'POST':

        form_attrib = request.form.getlist('attrib')
        form_edit = request.form.getlist('edit')
        form_delete = request.form.getlist('delete')
        
        # liste des roles lie au profil et supprimer ce qui ne sont plus attribue
        current_profil_role = ProfilRole.objects(profil_id=profil.id)
        for current in current_profil_role:
            if current.role_id.id not in form_attrib:
                current.delete()

        # Insertion des roles et authorisation en provenance du formulaire
        for attrib in form_attrib:

            role_form = Roles.objects.get(id=attrib)

            profil_role_exist = ProfilRole.objects(Q(role_id=role_form.id) & Q(profil_id=profil.id)).first()

            if profil_role_exist:
                if attrib in form_edit:
                    profil_role_exist.edit = True
                else:
                    profil_role_exist.edit = False

                if attrib in form_delete:
                    profil_role_exist.deleted = True
                else:
                    profil_role_exist.deleted = False

                profil_role_exist.save()
            else:
                profil_role_create = ProfilRole()
                profil_role_create.role_id = role_form
                profil_role_create.profil_id = profil
                if attrib in form_edit:
                    profil_role_create.edit = True
                else:
                    profil_role_create.edit = False

                if attrib in form_delete:
                    profil_role_create.deleted = True
                else:
                    profil_role_create.deleted = False

                profil_role_create.save()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('profil/list.html', **locals())




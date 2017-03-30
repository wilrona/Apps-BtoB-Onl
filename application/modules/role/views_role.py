__author__ = 'wilrona'

from ...modules import *
from ..role.models_role import Roles
from forms_role import FormRole


# Flask-Cache (configured to use App Engine Memcache API)
prefix = Blueprint('role', __name__)


@prefix.route('/', methods=['GET', 'POST'])
@login_required
def index():
    title_parent = 'Configuration'
    title_page = 'Roles'

    datas = Roles.objects(Q(valeur__ne='super_admin') & Q(parent=None))

    return render_template('role/index.html', **locals())


@prefix.route('/edit/<objectid:role_id>',  methods=['GET', 'POST'])
@login_required
def edit(role_id):

    roles = Roles.objects.get(id=role_id)
    form = FormRole(obj=roles)

    success = False
    if form.validate_on_submit():

        roles.description = form.description.data
        roles.active = form.active.data
        roles.save()

        success = True

    return render_template('role/edit.html', **locals())


@prefix.route('/list/<objectid:role_id>',  methods=['GET', 'POST'])
@login_required
def list(role_id):

    module = Roles.objects.get(id=role_id)
    roles = Roles.objects(
        parent = module.id
    )

    return render_template('role/list.html', **locals())


@prefix.route('/generate')
def generate():

    for mod in global_role:

        module_exite = Roles.objects(
            valeur=mod['valeur']
        )

        if not len(module_exite):
            module = Roles()
            module.titre = mod['module']
            module.valeur = mod['valeur']
            save = module.save()
        else:
            module = module_exite.first()
            module.titre = mod['module']
            module.valeur = mod['valeur']
            save = module.save()

        for rol in mod['role']:

            role_exist = Roles.objects(
                valeur=rol['valeur']
            )

            if not role_exist.count():
                role = Roles()
                role.titre = rol['titre']
                role.valeur = rol['valeur']
                role.action = rol['action']
                role.parent = save
                role.save()
            else:
                role = role_exist.first()
                role.titre = rol['titre']
                role.valeur = rol['valeur']
                role.action = rol['action']
                role.parent = save
                role.save()

    flash(u' All Role generated.', 'success')
    return redirect(url_for('role.index'))


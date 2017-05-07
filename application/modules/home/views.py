__author__ = 'wilrona'

from ...modules import *
from application import login_manager
from ..user.models_user import UserRole, Roles, Users
from ..user.forms_user import FormRegisterUserAdmin, FormLogin
from  ..company.models_company import Company
from ..company.forms_company import FormCompany


prefix = Blueprint('home', __name__)

# @app.route('/set_session')
# def set_session():
#     session.permanent = True
#     return json.dumps({
#         'statut': True
#     })


@prefix.route('/')
def index():

    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    admin_role = Roles.objects(valeur='super_admin').first()
    company = Company.objects().first()

    exist_super_admin = None
    if admin_role:
        exist_super_admin = Users.objects(roles__role_id=admin_role).first()

    exist_company = None
    if company:
        exist_company = True

    exist = False
    if exist_super_admin and exist_company:
        exist = True

    form = FormLogin()

    return render_template('user/login.html', **locals())


@prefix.route('/config', methods=['GET', 'POST'])
def setting():

    admin_role = Roles.objects(valeur='super_admin').first()
    company = Company.objects().first()

    if admin_role and company:
        return redirect(url_for('home.index'))

    if not admin_role:

        if request.method == 'POST':
            form = FormRegisterUserAdmin(request.form)
        else:
            form = FormRegisterUserAdmin()

        if request.method == 'POST' and form.validate_on_submit():

            try:
                password = hashlib.sha256(form.password.data).hexdigest()
            except UnicodeEncodeError:
                flash('Mots de passe invalide', 'danger')
                return redirect(url_for('home.setting'))

            time_zones = tzlocal()
            date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

            Role = Roles()
            Role.valeur = 'super_admin'
            role_id = Role.save()

            User_Role = UserRole()
            User_Role.role_id = role_id

            User = Users()
            User.first_name = form.first_name.data
            User.last_name = form.last_name.data
            User.email = form.email.data
            User.password = password
            User.activated = True
            User.user = 2
            User.roles.append(User_Role)
            count_user = Users.objects(user__gte=1).count()
            User.ref = function.reference(count=count_user+1, caractere=4, user=True, refuser=None)
            user_id = User.save()

            return redirect(url_for('home.setting'))

        return render_template('user/edit_setting.html', **locals())

    else:

        if request.method == 'POST':
            form = FormCompany(request.form)
        else:
            form = FormCompany()

        if request.method == 'POST' and form.validate_on_submit():

            com = Company()
            com.name = form.name.data
            com.bp = form.bp.data
            com.adress = form.adress.data
            com.ville = form.ville.data
            com.pays = form.pays.data
            com.phone = form.phone.data
            com.capital = form.capital.data
            com.numcontr = form.numcontr.data
            com.registcom = form.registcom.data
            com.email = form.email.data
            com.siteweb = form.siteweb.data
            com.slogan = form.slogan.data
            com.typEnt = form.typEnt.data
            com.quartier = form.quartier.data
            com.facebook = form.facebook.data
            com.twitter = form.twitter.data
            com.save()

            return redirect(url_for('home.index'))

        return render_template('company/edit_setting.html', **locals())
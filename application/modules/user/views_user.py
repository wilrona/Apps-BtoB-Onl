__author__ = 'wilrona'

from ...modules import *
from ..workflow.workflow_user import generate_confirmation_token, confirm_token, id_generator
from application import login_manager
from models_user import Users, UserRole, Roles
from forms_user import FormLogin, FormUser, FormPassword
from ..company.models_company import Company

prefix = Blueprint('user', __name__)
prefix_param = Blueprint('user_param', __name__)


@login_manager.user_loader
def load_user(userid):
    return Users.objects(id=userid).first()


@prefix.route('/oauth2callback', methods=['POST'])
def login():

    form = FormLogin(request.form)

    if form.validate_on_submit():

        try:
            password = hashlib.sha256(form.password.data).hexdigest()
        except UnicodeEncodeError:
            flash('Adresse email ou mot de passe incorrect' 'danger')
            return redirect(url_for('home.index'))

        user_login = Users.objects(
            Q(email=form.email.data) & Q(password=password)
        ).first()

        if user_login is None:
            flash('Adresse email ou mot de passe incorrect', 'danger')
            return redirect(url_for('home.index'))
        else:
            if not user_login.is_active():
                flash('Votre compte est desactive. Contactez l\'administrateur', 'danger')
                return redirect(url_for('home.index'))

            if user_login.user == 1 or user_login.user == 0:
                flash('Vous ne pouvez pas vous connecter sur cette interface', 'warning')
                return redirect(url_for('user.logout'))

            #implementation de l'heure local
            time_zones = tzlocal()
            date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

            session['user_id'] = str(user_login.id)
            user_login.logged = True
            user_login.lastLogin = function.datetime_convert(date_auto_nows)
            user_login.save()

            session['company_name'] = Company.objects().first().name

            return redirect(url_for('dashboard.index'))
    else:
        flash('Adresse email ou mot de passe incorrect ICI', 'danger')
        return redirect(url_for('home.index'))


@prefix.route('/logout')
def logout():
    change = None

    if 'user_id' in session:
        UserLogout = Users.objects.get(id=session.get('user_id'))
        UserLogout.logged = False
        change = UserLogout.save()

    if change:
        session.pop('user_id')
        session.pop('company_name')

        flash('Deconnexion reussie avec success', 'success')

        # if 'package' in session:
        #     session.pop('package');
        # session.pop('site')

    return redirect(url_for('home.index'))


@prefix_param.route('/')
@login_required
@roles_required([('super_admin', 'user')])
def index():
    title_page = 'Utilisateurs'

    admin_role = Roles.objects(valeur='super_admin').first()

    datas = Users.objects(Q(user__gte=1) & Q(roles__role_id__ne=admin_role))

    return render_template('user/index.html', **locals())


@prefix_param.route('/view/<objectid:user_id>', methods=['GET'])
def view(user_id):

    title_page = 'Utilisateurs'

    data = Users.objects.get(id=user_id)
    form = FormUser(obj=data)

    # liste des roles lie a l'utiliasteur en cours
    attrib_list = [role.role_id.id for role in data.roles]

    # liste des roles lie a l'utiliasteur en cours avec le droit d'edition
    edit_list = [role.role_id.id for role in data.roles if role.edit == True]

    # liste des roles lie a l'utiliasteur en cours avec le droit de suppression
    delete_list = [role.role_id.id for role in data.roles if role.deleted == True]

    liste_role = []
    data_role = Roles.objects(
        valeur__ne='super_admin'
    )

    for role in data_role:
        if not role.parent:
            module = {}
            module['titre'] = role.titre
            module['id'] = role.id
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

    return render_template('user/view.html', **locals())


@prefix_param.route('/choice')
def choice():
    return render_template('user/choice_admin.html', **locals())


@prefix_param.route('/choice/soldier')
def choice_soldier():
    return render_template('user/choice_soldier.html', **locals())


@prefix_param.route('/edit/password/<objectid:user_id>')
def edit_password(user_id):

    user = Users.objects.get(id=user_id)

    flash('Un mail avec votre mot de passe genere a ete envoye.', 'success')
    password = id_generator(size=7)
    user.password = hashlib.sha256(password).hexdigest()

    html = render_template('template_mail/user/password_mail_reset.html', **locals())

    msg = Message()
    msg.recipients = [user.email]
    msg.subject = 'Votre nouveau mot de passe sur ici.cm'
    msg.sender = ('ICI.CM CRM', 'no_reply@ici.cm')

    msg.html = html
    mail.send(msg)

    return redirect(url_for('user_param.view', user_id=user_id))


@prefix_param.route('/edit/existant', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'user')], ['edit'])
def edit_exist():

    title_page = 'Utilisateurs'

    admin_role = Roles.objects(valeur='super_admin').first()

    if request.args.get('field_soldier'):
        datas = Users.objects(Q(user__lt=1) & Q(activated=True) & Q(roles__role_id__ne=admin_role))
    else:
        datas = Users.objects(Q(user__lt=2) & Q(activated=True) & Q(roles__role_id__ne=admin_role))

    if request.method == 'POST':

        if request.form.getlist('item_id'):

            for id_user in request.form.getlist('item_id'):
                current = Users.objects.get(id=id_user)
                if request.args.get('field_soldier'):
                    current.user = 1
                else:
                    current.user = 2

                if not current.ref:
                    count_user = Users.objects(user__gte=1).count()
                    current.ref = function.reference(count=count_user+1, caractere=4, user=True, refuser=None)

                current.save()

            flash('Ajout des administrateurs/Commerciaux reussis avec success', 'success')

            datas = json.dumps({
                'statut': 'OK'
            })

        else:

            datas = json.dumps({
                'statut': 'NOK'
            })

        return datas

    return render_template('user/edit_exist.html', **locals())


@prefix_param.route('/edit/<objectid:user_id>', methods=['GET', 'POST'])
@prefix_param.route('/edit/', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'user')], ['edit'])
def edit(user_id=None):

    title_page = 'Utilisateurs'

    if user_id:

        data = Users.objects.get(id=user_id)

        if current_user.has_roles([('super_admin', 'user')], ['edit']) and data.id == current_user.id:
            return redirect(url_for('user.view', user_id=user_id))

        form = FormUser(obj=data)
        form.id.data = str(data.id)

        # liste des roles lie a l'utiliasteur en cours
        attrib_list = [role.role_id.id for role in data.roles]

        # liste des roles lie a l'utiliasteur en cours avec le droit d'edition
        edit_list = [role.role_id.id for role in data.roles if role.edit == True]

        # liste des roles lie a l'utiliasteur en cours avec le droit de suppression
        delete_list = [role.role_id.id for role in data.roles if role.deleted == True]

        liste_role = []
        data_role = Roles.objects(
            valeur__ne='super_admin'
        )

        for role in data_role:
            if not role.parent:
                module = {}
                module['titre'] = role.titre
                module['id'] = role.id
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

    else:
        data = Users()
        form = FormUser()
        if request.args.get('field_soldier'):
            form.user.data = 1
        else:
            form.user.data = 2

    if form.validate_on_submit() and request.method == 'POST' and current_user.has_roles([('super_admin', 'user')], ['edit']) and current_user.id != data.id:

        data.first_name = form.first_name.data
        data.last_name = form.last_name.data

        if form.email.data != data.email and user_id:
            flash('L\'adresse email ne peut etre modifier dans cette action.', 'warning')

        if not user_id:
            data.email = form.email.data
            data.user = int(form.user.data)
            count_user = Users.objects(user__gte=1).count()
            data.ref = function.reference(count=count_user+1, caractere=4, user=True, refuser=None)

        data.fonction = form.fonction.data
        data.phone = form.phone.data
        data.note = form.note.data

        if not user_id:
            data.activated = False

        data = data.save()

        if not user_id:

            token = generate_confirmation_token(data.email)
            confirm_url = url_for('user_param.confirm_email', user_id=data.id, token=token, _external=True)
            html = render_template('template_mail/user/activate.html', **locals())

            msg = Message()
            msg.recipients = [data.email]
            msg.subject = 'Confirmation de votre compte email'
            msg.sender = ('ICI.CM CRM', 'no_reply@ici.cm')

            msg.html = html
            mail.send(msg)

            flash('Un mail de confirmation a ete envoye dans l\'adresse email fournit lors de la creation.', 'success')

        if user_id:
            form_attrib = request.form.getlist('attrib')

            form_edit = request.form.getlist('edit')
            form_delete = request.form.getlist('delete')

            # Insertion des roles et authorisation en provenance du formulaire
            for attrib in form_attrib:

                role_form = Roles.objects.get(id=attrib)
                profil_role_exist = Users.objects(Q(roles__role_id=role_form.id) & Q(id=data.id))

                if profil_role_exist:
                    if attrib in form_edit:
                        profil_role_exist.update_one(set__roles__S__edit=True)
                    else:
                        profil_role_exist.update_one(set__roles__S__edit=False)

                    if attrib in form_delete:
                        profil_role_exist.update_one(set__roles__S__deleted=True)
                    else:
                        profil_role_exist.update_one(set__roles__S__deleted=False)
                else:
                    profil_role_create = UserRole()
                    profil_role_create.role_id = role_form
                    if attrib in form_edit:
                        profil_role_create.edit = True
                    else:
                        profil_role_create.edit = False

                    if attrib in form_delete:
                        profil_role_create.deleted = True
                    else:
                        profil_role_create.deleted = False

                    data = Users.objects.get(id=user_id)
                    data.roles.append(profil_role_create)
                    data.save()

            for role in data.roles:
                if str(role.role_id.id) not in form_attrib:
                    profil_role_exist = Users.objects(id=data.id).update_one(pull__roles__role_id=role.role_id)

        flash('Enregistement effectue avec succes', 'success')

        if request.form['nouveau'] == '1':
            return redirect(url_for('user_param.edit'))
        else:

            return redirect(url_for('user_param.view', user_id=data.id))

    return render_template('user/edit.html', **locals())


@prefix_param.route('/deleted', methods=['POST'])
@login_required
@roles_required([('super_admin', 'user')], ['delete'])
def deleted():

    from ..opportunite.models_opportunite import Opportunite
    from ..document.models_doc import Document

    data = []
    element = []
    count = 0
    for item in request.form.getlist('item_id'):
        info = {}
        item_found = Users.objects().get(id=item)
        opportunite = Opportunite.objects(vendeur_id=item_found)

        if opportunite:
            info['statut'] = 'NOK'
            info['message'] = 'L\'utilisateur "'+item_found.first_name+' '+item_found.last_name+'" est utilise par '+str(opportunite.count())+' autre(s) opportunite(s)'

        exit_document = Document.objects(vendeur_id=item_found)
        if exit_document:
            info['statut'] = 'NOK'
            info['message'] = 'L\'utilisateur "'+item_found.name+'" est utilise par '+str(exit_document.count())+' autre(s) Documents(s)'

        if not opportunite and not exit_document:
            item_found.delete()
            element.append(str(item_found.id))
            count += 1
        else:
            data.append(info)

    if count:
        info = {}
        info['statut'] = 'OK'
        info['message'] = str(count)+' utilisateur(s) supprime(s) avec success'
        info['element'] = element
        data.append(info)

    data = json.dumps(data)

    return data


@prefix_param.route('/removed', methods=['POST'])
@login_required
@roles_required([('super_admin', 'user')], ['delete'])
def removed():

    data = []
    element = []
    count = 0
    for item in request.form.getlist('item_id'):
        info = {}
        item_found = Users.objects().get(id=item)

        if item_found.user > 1:
            info['statut'] = 'NOK'
            if len(item_found.roles):
                info['message'] = 'L\'utilisateur "'+item_found.full_name()+'" est un Administrateur. IL ne peut etre ' \
                                                                            'enlever comme Field Soldier. '
            else:
                info['message'] = 'L\'utilisateur "'+item_found.full_name()+'" est un Commercial. IL ne peut etre ' \
                                                                            'enlever comme Field Soldier. '

            data.append(info)
        else:
            item_found.user = 0
            element.append(str(item_found.id))
            count += 1

            item_found.save()

    if count:
        info = {}
        info['statut'] = 'OK'
        info['message'] = str(count)+' utilisateur(s) enleve(s) comme Field Soldier avec success'
        info['element'] = element
        data.append(info)

    data = json.dumps(data)

    return data


@prefix_param.route('/removed_cam', methods=['POST'])
@login_required
@roles_required([('super_admin', 'user')], ['delete'])
def removed_cam():

    data = []
    element = []
    count = 0
    for item in request.form.getlist('item_id'):
        info = {}
        item_found = Users.objects().get(id=item)

        if item_found.user == 1 or len(item_found.roles):
            info['statut'] = 'NOK'
            if len(item_found.roles):
                info['message'] = 'L\'utilisateur "'+item_found.full_name()+'" est un Administrateur. IL ne peut etre ' \
                                                                            'enlever comme Commercial. '
            else:
                info['message'] = 'L\'utilisateur "'+item_found.full_name()+'" est un Field Soldier. IL ne peut etre ' \
                                                                            'enlever comme Commercial. '
            data.append(info)
        else:
            item_found.roles = []
            item_found.user = 0
            element.append(str(item_found.id))
            count += 1

            item_found.save()

    if count:
        info = {}
        info['statut'] = 'OK'
        info['message'] = str(count)+' utilisateur(s) enleve(s) comme Commercial avec success. ils sont redevenu des ' \
                                     'simples utilisateurs '
        info['element'] = element
        data.append(info)

    data = json.dumps(data)

    return data


@prefix_param.route('/removed_admin', methods=['POST'])
@login_required
@roles_required([('super_admin', 'user')], ['delete'])
def removed_admin():

    data = []
    element = []
    count = 0
    for item in request.form.getlist('item_id'):
        info = {}
        item_found = Users.objects().get(id=item)

        if not len(item_found.roles):
            info['statut'] = 'NOK'
            info['message'] = 'L\'utilisateur "'+item_found.full_name()+'" n\' est plus Administrateur.'

            data.append(info)
        else:
            item_found.roles = []
            item_found.user = 0
            element.append(str(item_found.id))
            count += 1

            item_found.save()

    if count:
        info = {}
        info['statut'] = 'OK'
        info['message'] = str(count)+' utilisateur(s) enleve(s) comme Admnistrateur avec success. ils sont redevenu ' \
                                     'des commerciaux '
        info['element'] = element
        data.append(info)

    data = json.dumps(data)

    return data


@prefix_param.route('/etat/<objectid:user_id>')
@login_required
@roles_required([('super_admin', 'user')], ['edit'])
def etat(user_id):

    data = Users.objects.get(id=user_id)
    if data.activated:
        data.activated = False
    else:
        data.activated = True

    data.save()

    flash('Les modifications de l\'etat de l\'utilisateur ont ete effectues', 'success')
    return redirect(url_for('user_param.edit', user_id=user_id))


@prefix_param.route('/confirm/<objectid:user_id>/<token>')
def confirm_email(user_id, token):

    token_email = confirm_token(token)
    user = Users.objects.get(id=user_id)

    if user.activated:
        flash('Votre compte est deja confirme. SVP connectez vous.', 'success')
    else:
        if user.email == token_email:
            user.activated = True

            flash('Vous avez confirmee votre compte. Merci!', 'success')
            if not user.password:
                flash('Un mail avec votre mot de passe genere a ete envoye.', 'success')
                password = id_generator(size=7)
                user.password = hashlib.sha256(password).hexdigest()

                html = render_template('template_mail/user/password_mail.html', **locals())

                msg = Message()
                msg.recipients = [user.email]
                msg.subject = 'Votre mot de passe sur ici.cm'
                msg.sender = ('ICI.CM CRM', 'no_reply@ici.cm')

                msg.html = html
                mail.send(msg)

            user.save()
        else:
            flash('Le lien de confirmation est invalide ou est expiree.', 'danger')

    if user.is_authenticated():
        return redirect(url_for('user_param.unconfirmed'))
    else:
        return redirect(url_for('home.index'))


@prefix_param.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.is_active():
        return redirect('dashboard.index')

    flash('SVP confirmez votre adresse email!', 'warning')
    return render_template('user/unconfirmed.html', **locals())


@prefix_param.route('/resend_confirmation')
@login_required
def resend_confirmation():

    token = generate_confirmation_token(current_user.email)
    reset = True
    confirm_url = url_for('user_param.confirm_email', user_id=current_user.id, token=token, _external=True)
    html = render_template('template_mail/user/activate.html', **locals())

    msg = Message()
    msg.recipients = [current_user.email]
    msg.subject = 'Confirmation de votre compte email'
    msg.sender = ('ICI.CM CRM confirmer votre compte', 'no_reply@ici.cm')

    msg.html = html
    mail.send(msg)

    flash('Un nouveau message de confirmation a ete envoye.', 'success')
    return redirect(url_for('user_param.unconfirmed'))





# @prefix_param.route('/set_ref')
# def set_ref():
#
#     count_user = Users.objects(user=True).order_by('createDate')
#     count = 1
#     for user in count_user:
#         user.ref = function.reference(count=count, caractere=4, user=True, refuser=None)
#         user.save()
#         count += 1
#
#     return 'True'


# @prefix_param.route('/permission/<objectid:user_id>', methods=['GET', 'POST'])
# @login_required
# @roles_required([('super_admin', 'user_permission')])
# def permission(user_id):
#     menu = 'user'
#     submenu = 'users'
#     context = 'permission'
#     title_page = 'Parametre - Utilisateurs'
#
#     user = Users.objects.get(id=user_id)
#
#     # liste des roles lie a l'utiliasteur en cours
#     attrib = UserRole.objects(
#         user_id = user.id
#     )
#     attrib_list = [role.role_id.id for role in attrib]
#
#     # liste des roles lie a l'utiliasteur en cours avec le droit d'edition
#     edit = UserRole.objects(Q(user_id=user.id) & Q(edit=True))
#     edit_list = [role.role_id.id for role in edit]
#
#     # liste des roles lie a l'utiliasteur en cours avec le droit de suppression
#     delete = UserRole.objects(Q(user_id=user.id) & Q(deleted=True))
#     delete_list = [role.role_id.id for role in delete]
#
#
#     liste_role = []
#     data_role = Roles.objects(
#         valeur__ne='super_admin'
#     )
#
#     for role in data_role:
#         if not role.parent:
#             module = {}
#             module['titre'] = role.titre
#             module['id'] = role.id
#             enfants = Roles.objects(
#                 parent = role.id
#             )
#             module['role'] = []
#             for enfant in enfants:
#                 rol = {}
#                 rol['id'] = enfant.id
#                 rol['titre'] = enfant.titre
#                 rol['action'] = enfant.action
#                 module['role'].append(rol)
#             liste_role.append(module)
#
#     # liste des profils de l'application
#     list_profil = Profil.objects(
#         active=True
#     )
#
#     profil_select = None
#     if request.args.get('profil') and request.method == 'GET':
#
#         profil_select = int(request.args.get('profil'))
#         profil_request = Profil.objects.get(id=request.args.get('profil'))
#
#         attrib = ProfilRole.objects(
#             profil_id= profil_request.id
#         )
#
#         attrib_list = [role.role_id.id for role in attrib]
#
#         # liste des roles lie a l'utiliasteur en cours avec le droit d'edition
#         edit = ProfilRole.objects(Q(profil_id=profil_request) & Q(edit=True))
#         edit_list = [role.role_id.id for role in edit]
#
#         # liste des roles lie a l'utiliasteur en cours avec le droit de suppression
#         delete = ProfilRole.objects(Q(profil_id=profil_request.id) & Q(deleted=True))
#         delete_list = [role.role_id.id for role in delete]
#
#
#     if request.method == 'POST' and current_user.has_roles([('super_admin', 'user_permission')], ['edit']):
#
#         form_attrib = request.form.getlist('attrib')
#
#         # if not form_attrib and attrib_list:
#         #     flash('Les utilisateurs ne doivent pas exister sans permission dans l\'application', 'warning')
#         #     return redirect(url_for('user_param.permission', user_id=user_id))
#         # elif form_attrib:
#         #     user.is_enabled = True
#         #     user.put()
#
#         form_edit = request.form.getlist('edit')
#         form_delete = request.form.getlist('delete')
#
#         # liste des roles lie au profil et supprimer ce qui ne sont plus attribue
#         current_profil_role = UserRole.objects(
#             user_id = user.id
#         )
#         for current in current_profil_role:
#             if current.role_id.id not in form_attrib:
#                 current.delete()
#
#         # Insertion des roles et authorisation en provenance du formulaire
#         for attrib in form_attrib:
#
#             role_form = Roles.objects.get(id=attrib)
#
#             profil_role_exist = UserRole.objects(Q(role_id=role_form.id) & Q(user_id=user.id)).first()
#
#             if profil_role_exist:
#                 if attrib in form_edit:
#                     profil_role_exist.edit = True
#                 else:
#                     profil_role_exist.edit = False
#
#                 if attrib in form_delete:
#                     profil_role_exist.deleted = True
#                 else:
#                     profil_role_exist.deleted = False
#
#                 profil_role_exist.save()
#             else:
#                 profil_role_create = UserRole()
#                 profil_role_create.role_id = role_form
#                 profil_role_create.user_id = user
#                 if attrib in form_edit:
#                     profil_role_create.edit = True
#                 else:
#                     profil_role_create.edit = False
#
#                 if attrib in form_delete:
#                     profil_role_create.deleted = True
#                 else:
#                     profil_role_create.deleted = False
#
#                 profil_role_create.save()
#
#         flash('Enregistement effectue avec succes', 'success')
#         return redirect(url_for('user_param.permission', user_id=user_id))
#
#     return render_template('user/permission.html', **locals())













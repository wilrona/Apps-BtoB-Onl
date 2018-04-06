__author__ = 'wilrona'

from ...modules import *
from ..role.models_role import Roles


class UserRole(db.EmbeddedDocument):
    role_id = db.ReferenceField('Roles')
    edit = db.BooleanField(default=False)
    deleted = db.BooleanField(default=False)


class Users(db.Document):

    ref = db.StringField()

    first_name = db.StringField()
    last_name = db.StringField()
    email = db.StringField()

    password = db.StringField()
    fonction = db.StringField()
    phone = db.StringField()

    registerDate = db.DateTimeField()
    token_confirmation = db.StringField()
    activated = db.BooleanField()

    logged = db.BooleanField()
    lastLogin = db.DateTimeField()
    user = db.IntField() # 0 simple user; 1 field soldier; 2 administrateur/cam
    note = db.StringField()
    ville = db.StringField()
    sex = db.StringField()
    dateNaiss = db.DateTimeField()
    picture = db.StringField()

    source = db.StringField()
    list_id = db.ListField(db.StringField())

    roles = db.ListField(db.EmbeddedDocumentField(UserRole))
    idcompagnie = db.ListField(db.ReferenceField('Compagnie'))

    favorite = db.ListField(db.ReferenceField('Compagnie'))

    def save(self, *args, **kwargs):
        if not self.registerDate:
            self.registerDate = datetime.datetime.now()
        return super(Users, self).save(*args, **kwargs)

    def is_active(self):
        return self.activated

    def is_authenticated(self):
        return self.logged

    def is_anonymous(self):
        return False

    def full_name(self):
        full_name = u''+self.first_name+u' '+self.last_name+u''
        return full_name

    def has_roles(self, requirements, accesibles=None):

        user_role = self.roles
        user_roles = [role.role_id.valeur for role in user_role]

        # has_role() accepts a list of requirements
        for requirement in requirements:
            if isinstance(requirement, (list, tuple)):
                # this is a tuple_of_role_names requirement
                tuple_of_role_names = requirement
                authorized = False
                for role_name in tuple_of_role_names:
                    if role_name in user_roles:
                        # tuple_of_role_names requirement was met: break out of loop
                        authorized = True

                        if accesibles and role_name != 'super_admin':

                            edit = False
                            delete = False

                            for role in user_role:
                                if role.edit and role.role_id.valeur == role_name:
                                    edit = True
                                if role.edit and role.role_id.valeur == role_name:
                                    delete = True

                            # role = Roles.objects(valeur=role_name).first()
                            #
                            # role_user = UserRole.objects(Q(user_id=self.id) & Q(role_id=role.id)).first()

                            for accesible in accesibles:
                                if accesible == 'edit' and not edit:
                                    authorized = False
                                    break
                                if accesible == 'delete' and not delete:
                                    authorized = False
                                    break
                        else:
                            break
                if not authorized:
                    return False                    # tuple_of_role_names requirement failed: return False
                else:
                    return True
            else:
                # this is a role_name requirement
                role_name = requirement

                # the user must have this role
                if not role_name in user_roles:
                    return False                    # role_name requirement failed: return False
                else:
                    if accesibles and role_name != 'super_admin':

                        edit = False
                        delete = False

                        for role_user in user_role:
                            if role_user.edit and role_user.role_id.valeur == role_name:
                                edit = True
                            if role_user.edit and role_user.role_id.valeur == role_name:
                                delete = True

                        for accesible in accesibles:
                            if accesible == 'edit' and not edit:
                                return False
                            if accesible == 'delete' and not delete:
                                return False

        # All requirements have been met: return True
        return True

    def nbre_prospection(self, date_start=None, date_end=None):

        from ..document.models_doc import Document

        if date_start is None and date_end is None:
            date_start = datetime.date.today()
            date_end = datetime.date.today()

        nbre = Document.objects(Q(vendeur_id=self.id) & Q(createDate__gte=date_start) & Q(createDate__lte=date_end)).count()

        return nbre

    def nbre_activation(self, date_start=None, date_end=None):

        from ..document.models_doc import Document
        if date_start is None and date_end is None:
            date_start = datetime.date.today()
            date_end = datetime.date.today()

        nbre = Document.objects(Q(vendeur_id=self.id) & Q(montant__ne=0) & Q(createDate__gte=date_start) & Q(createDate__lte=date_end)).count()

        return nbre









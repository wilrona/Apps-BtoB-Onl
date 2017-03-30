__author__ = 'wilrona'

from application import db
from ..role.models_role import Roles


class Profil(db.Document):
    name = db.StringField()
    description = db.StringField()
    active = db.BooleanField()

    def count_role(self):
        profil_role_exist = ProfilRole.objects(id=self.id)
        return len(profil_role_exist)


class ProfilRole(db.Document):
    role_id = db.ReferenceField(Roles)
    profil_id = db.ReferenceField(Profil)
    edit = db.BooleanField()
    deleted = db.BooleanField()
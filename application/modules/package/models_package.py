__author__ = 'User'

from ...modules import *


class Package(db.Document):
    name = db.StringField()
    description = db.StringField()
    duree = db.IntField()
    prix = db.FloatField()
    prix_promo = db.FloatField(default=0)
    promo = db.BooleanField()
    level = db.IntField()
    idligneService = db.StringField()
    is_package = db.BooleanField()
    status = db.BooleanField(default=True)
    attribut = db.ListField(db.StringField())
    sale = db.IntField()
    hight = db.BooleanField()

    def similar(self):

        pack = Package.objects(Q(idligneService=self.idligneService) & Q(sale=0))

        return pack

    def level_first(self):

        packs = Package.objects(Q(idligneService=self.idligneService) & Q(sale=0))

        id = None
        level = None
        count = 0
        for pack in packs:

             if count:
                 if pack.level < level:
                     level = pack.level
                     id = pack.id
             else:
                 level = pack.level
                 id = pack.id

             count += 1

        return id

    def level_last(self):
        pack = Package.objects(Q(idligneService=self.idligneService) & Q(hight=True) & Q(sale=0)).first()
        return pack


class LigneService(db.Document):
    name = db.StringField()
    package = db.BooleanField()
    sigle = db.StringField()

    def packages(self):
        pack = Package.objects(idligneService=self.sigle)
        return pack


class Attribut(db.Document):
    name = db.StringField()
    desc = db.StringField()
    libelle = db.StringField()
    idligneService = db.StringField()
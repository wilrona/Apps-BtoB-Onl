__author__ = 'User'

from ...modules import *


class Package(db.Document):
    name = db.StringField()
    description = db.StringField()
    duree = db.IntField()
    prix = db.FloatField()
    prix_promo = db.FloatField()
    promo = db.BooleanField()
    level = db.IntField()
    idligneService = db.StringField()
    is_package = db.BooleanField()
    proposal = db.BooleanField()
    status = db.BooleanField()
    attribut = db.ListField(db.StringField())
    sale = db.IntField()


class LigneService(db.Document):
    name = db.StringField()
    package = db.BooleanField()
    sigle = db.StringField()


class Attribut(db.Document):
    name = db.StringField()
    desc = db.StringField()
    libelle = db.StringField()
    idligneService = db.StringField()
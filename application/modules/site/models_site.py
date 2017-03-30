__author__ = 'User'


from ...modules import *


class Localisation(db.Document):
    name = db.StringField()
    parent = db.ReferenceField('self')
    site = db.ListField(db.ReferenceField('Site'))
    actif = db.BooleanField(default=True)


class Ecran(db.Document):
    name = db.StringField()
    multi_choice = db.BooleanField()
    cout_passage = db.FloatField()

    updateDate = db.DateTimeField()
    createDate = db.DateTimeField()

    site = db.ListField(db.ReferenceField('Site'))
    package = db.ListField(db.ReferenceField('Package'))
    outdoor = db.BooleanField()

    actif = db.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.createDate:
            self.createDate = datetime.datetime.now()
        self.updateDate = datetime.datetime.now()
        return super(Ecran, self).save(*args, **kwargs)


class Site(db.Document):
    ref = db.StringField()
    name = db.StringField()
    type = db.StringField()
    longitude = db.FloatField()
    latitude = db.FloatField()
    ecran_id = db.ReferenceField('Ecran')
    local_id = db.ReferenceField('Localisation')

    secteur_id = db.ReferenceField('Secteur')
    ligne_doc = db.ListField(db.ReferenceField('LigneDoc'))
    image = db.StringField()
    actif = db.BooleanField(default=True)


class Package(db.Document):
    name = db.StringField()
    prix_outdoor = db.FloatField()
    prix_indoor = db.FloatField()
    passage = db.IntField()

    updateDate = db.DateTimeField()
    createDate = db.DateTimeField()
    actif = db.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.createDate:
            self.createDate = datetime.datetime.now()
        self.updateDate = datetime.datetime.now()
        return super(Package, self).save(*args, **kwargs)


class Horaire(db.Document):
    name = db.StringField()
    actif = db.BooleanField(default=True)


class Support(db.Document):
    name = db.StringField()
    actif = db.BooleanField(default=True)


class Secteur(db.Document):
    name = db.StringField()
    actif = db.BooleanField(default=True)

__author__ = 'User'

from ...modules import *


class Compagnie(db.Document):

    name = db.StringField()
    raison = db.StringField()
    adresse = db.StringField()
    ville = db.StringField()
    quartier = db.StringField()
    repere = db.StringField()

    latitude = db.StringField()
    longitude = db.StringField()

    email = db.StringField()
    phone = db.StringField()
    description = db.StringField()
    urlsite = db.StringField()

    postal_code = db.StringField()
    activated = db.BooleanField()

    imagedir = db.StringField()
    logo = db.StringField()

    facebook = db.StringField()
    twitter = db.StringField()
    linkedin = db.StringField()
    youtube = db.StringField()

    mainuser = db.ReferenceField('Users')
    parent_idcompagnie = db.ReferenceField('self')
    maincategorie = db.ReferenceField('Categorie')
    idcategorie = db.ListField(db.ReferenceField('Categorie'))

    createDate = db.DateTimeField()
    updateDate = db.DateTimeField()

    etat_souscription = db.IntField()
    uploaded = db.BooleanField()
    partenaire = db.BooleanField()

    iduser = db.ListField(db.ReferenceField('Users'))

    owner = db.BooleanField(default=False)
    idagent = db.ReferenceField('Users')

    def save(self, *args, **kwargs):
        if not self.createDate:
            self.createDate = datetime.datetime.now()
        self.updateDate = datetime.datetime.now()
        return super(Compagnie, self).save(*args, **kwargs)


class Media(db.Document):
    type = db.StringField()
    une = db.BooleanField(default=False)
    url = db.StringField()
    idcompagnie = db.ReferenceField('Compagnie')


class Categorie(db.Document):
    name = db.StringField()
    description = db.StringField()
    slug = db.StringField()
    url_image = db.StringField()
    icone = db.StringField()
    idcomapagnie = db.ListField(db.ReferenceField('Compagnie'))
    parent_idcategorie = db.ReferenceField('self')
    activated = db.BooleanField(default=True)


class Claim(db.Document):
    idcompagnie = db.ReferenceField('Compagnie')
    iduser = db.ReferenceField('Users')
    statut = db.IntField()
    dateclaim = db.DateTimeField()
    updateclaim = db.DateTimeField()

    def save(self, *args, **kwargs):
        self.updateclaim = datetime.datetime.now()
        return super(Claim, self).save(*args, **kwargs)

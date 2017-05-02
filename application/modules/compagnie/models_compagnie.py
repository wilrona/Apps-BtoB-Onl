__author__ = 'User'

from ...modules import *


class Compagnie(db.Document):

    name = db.StringField()
    raison = db.StringField()
    adresse = db.StringField()
    ville = db.StringField()
    quartier = db.StringField()
    repere = db.StringField()
    region = db.StringField()

    latitude = db.StringField()
    longitude = db.StringField()

    email = db.StringField()
    phone = db.StringField()
    description = db.StringField()
    urlsite = db.StringField()

    postal_code = db.StringField()
    activated = db.BooleanField()
    verify = db.BooleanField()

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

    etat_souscription = db.IntField() #0 non paye; 1 paye; 2 expiree
    uploaded = db.BooleanField()
    partenaire = db.IntField(default=0) # 1 partenaire et institution; 2 institution

    iduser = db.ListField(db.ReferenceField('Users'))
    idagent = db.ReferenceField('Users')
    idcontact = db.ListField(db.ReferenceField('Users'))

    def save(self, *args, **kwargs):
        if not self.createDate:
            self.createDate = datetime.datetime.now()
        self.updateDate = datetime.datetime.now()
        return super(Compagnie, self).save(*args, **kwargs)

    def relation(self):

        list = []

        for user in self.iduser:
            list.append(user)

        for contact in self.idcontact:
            if contact not in list:
                list.append(contact)

        return list

    def dateExpired(self):
        from ..document.models_doc import LigneDoc

        lignes = LigneDoc.objects(Q(idcompagnie=self.id) & Q(etat=1) & Q(dateFin__ne=None)).order_by('-dateFin')

        ligne = None

        for lign in lignes:
            if lign.idpackage.idligneService == 'ici_cm':
                ligne = lign
                break

        return ligne


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
    compagnie = db.ListField(db.ReferenceField('Compagnie'))
    parent_idcategorie = db.ReferenceField('self')
    activated = db.BooleanField(default=True)


class Claim(db.Document):
    idcompagnie = db.ReferenceField('Compagnie')
    iduser = db.ReferenceField('Users')
    statut = db.IntField()
    dateclaim = db.DateTimeField()
    updateDate = db.DateTimeField()

    def save(self, *args, **kwargs):
        self.updateDate = datetime.datetime.now()
        return super(Claim, self).save(*args, **kwargs)


class Relation(db.Document):
    idagence = db.ReferenceField('Compagnie')
    idparent = db.ReferenceField('Compagnie')
    iduser = db.ReferenceField('Users')
    statut = db.IntField()
    createDate = db.DateTimeField()
    updateDate = db.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.createDate:
            self.createDate = datetime.datetime.now()
        self.updateDate = datetime.datetime.now()
        return super(Relation, self).save(*args, **kwargs)

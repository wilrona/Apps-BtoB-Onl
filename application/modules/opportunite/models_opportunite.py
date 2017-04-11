__author__ = 'User'


from ...modules import *


class Libelle_Opportunite(db.Document):
    name = db.StringField()
    actif = db.BooleanField(default=True)


class Etape(db.Document):
    name = db.StringField()
    proba = db.FloatField()
    actif = db.BooleanField(default=True)
    order = db.IntField()
    sigle = db.StringField()


class Activite(db.Document):
    name = db.StringField()
    description = db.StringField()
    jour = db.IntField()
    default = db.BooleanField(default=False)
    next = db.ReferenceField("self", reverse_delete_rule=NULLIFY)
    actif = db.BooleanField(default=True)
    sigle = db.StringField()


class Opportunite(db.Document):
    name = db.StringField()
    etape = db.StringField()
    vendeur_id = db.ReferenceField('Users')
    contact_id = db.ReferenceField('Users')
    client_id = db.ReferenceField('Compagnie')
    note = db.StringField()

    updateDate = db.DateTimeField()
    createDate = db.DateTimeField()
    suivie = db.ListField(db.ReferenceField('Suivie'))

    def save(self, *args, **kwargs):
        if not self.createDate:
            self.createDate = datetime.datetime.now()
        self.updateDate = datetime.datetime.now()
        return super(Opportunite, self).save(*args, **kwargs)


class Suivie(db.Document):
    activite = db.StringField()
    sigle_activite = db.StringField()
    etape = db.StringField()
    resume = db.StringField()
    description = db.StringField()

    updateDate = db.DateTimeField()
    createDate = db.DateTimeField()
    dateNext = db.DateTimeField()
    status = db.BooleanField()
    opportunite_id = db.ReferenceField('Opportunite')

    def save(self, *args, **kwargs):
        if not self.createDate:
            self.createDate = datetime.datetime.now()
        self.updateDate = datetime.datetime.now()
        return super(Suivie, self).save(*args, **kwargs)





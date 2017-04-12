__author__ = 'User'


from application import db


class Company(db.Document):
    name = db.StringField()
    bp = db.StringField()
    adress = db.StringField()
    quartier = db.StringField()
    ville = db.StringField()
    pays = db.StringField()
    phone = db.StringField()
    capital = db.StringField()
    numcontr = db.StringField()
    registcom = db.StringField()
    email = db.StringField()
    siteweb = db.StringField()
    slogan = db.StringField()
    typEnt = db.StringField()
    facebook = db.StringField()
    twitter = db.StringField()


class Config_reference(db.Document):
    ref_fact = db.StringField()
    ref_devis = db.StringField()
    email_service = db.StringField()
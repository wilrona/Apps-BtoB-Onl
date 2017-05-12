__author__ = 'User'


from flaskext import wtf
from flaskext.wtf import validators


class FormCompany(wtf.Form):
    name = wtf.StringField(label='Nom de la societe :', validators=[validators.Required(message='Champs Obligatoire')])
    bp = wtf.StringField(label='Boite Postal :')
    adress = wtf.StringField(label='Adresse :', validators=[validators.Required(message='Champs Obligatoire')])
    ville = wtf.StringField(label='Ville :', validators=[validators.Required(message='Champs Obligatoire')])
    pays = wtf.StringField(label='Pays :')
    phone = wtf.StringField(label='Numero Telephone :', validators=[validators.Required(message='Champs Obligatoire')])
    capital = wtf.StringField(label='Capital social :')
    numcontr = wtf.StringField(label='Numero du contribuable', validators=[validators.Required(message='Champs Obligatoire')])
    registcom = wtf.StringField(label='Registre du commerce', validators=[validators.Required(message='Champs Obligatoire')])
    email = wtf.StringField(label='Adresse mail', validators=[validators.Required(message='Champs Obligatoire'), validators.Email('Email invalide')])
    siteweb = wtf.StringField(label='Site Web', validators=[validators.Required(message='Champs Obligatoire')])
    slogan = wtf.StringField(label='Slogan/Breve description :')
    typEnt = wtf.StringField(label='Selectionnez le type :', validators=[validators.Required(message='Champs Obligatoire')])
    facebook = wtf.StringField(label='Lien facebook :', validators=[validators.Required(message='Champs Obligatoire')])
    twitter = wtf.StringField(label='Lien twitter :', validators=[validators.Required(message='Champs Obligatoire')])
    quartier = wtf.StringField(label='Quartier :', validators=[validators.Required(message='Champs Obligatoire')])
    emailNotification = wtf.StringField(label='Email Notification :')
    senderNotification = wtf.StringField(label='Sender Notification :')

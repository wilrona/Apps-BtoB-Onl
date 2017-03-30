__author__ = 'User'


from flaskext import wtf
from flaskext.wtf import validators


class FormClient(wtf.Form):
    id = wtf.HiddenField()
    raison = wtf.StringField(label='Forme juridique :')
    name = wtf.StringField(label='Nom de l\'entreprise :', validators=[validators.Required(message='Champ obligatoire')])
    email = wtf.StringField(label='Adresse Email :', validators=[validators.Required(message='Champ obligatoire')])
    phone = wtf.StringField(label='Numero de telephone :', validators=[validators.Required(message='Champ obligatoire')])
    ville = wtf.StringField(label='Ville :', validators=[validators.Required(message='Champ obligatoire')])
    quartier = wtf.StringField(label='Quartier :', validators=[validators.Required(message='Champ obligatoire')])
    bp = wtf.StringField(label='Boite postal :')
    rue = wtf.StringField(label='Rue :')
    numcontr = wtf.StringField(label='Numero contribuable :')
    registcom = wtf.StringField(label='Registre Commerce :')
    adress = wtf.TextAreaField(label='Localisation :')
    urlsite = wtf.StringField(label='Url du site web :')
    secteur_id = wtf.SelectField(label='Activite du client :', coerce=str, validators=[validators.Required(message='Champ obligatoire')])

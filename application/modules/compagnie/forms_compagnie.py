__author__ = 'User'


from flaskext import wtf
from flaskext.wtf import validators


class FormClient(wtf.Form):

    id = wtf.HiddenField()

    raison = wtf.StringField(label='Forme juridique :')
    name = wtf.StringField(label='Nom de l\'entreprise :', validators=[validators.Required(message='Champ obligatoire')])
    ville = wtf.StringField(label='Ville :', validators=[validators.Required(message='Champ obligatoire')])
    quartier = wtf.StringField(label='Quartier :', validators=[validators.Required(message='Champ obligatoire')])
    adresse = wtf.StringField(label='Adresse :')
    postal_code = wtf.StringField(label='Code postal :')
    repere = wtf.StringField(label='Reperage :')

    email = wtf.StringField(label='Adresse Email :', validators=[validators.Required(message='Champ obligatoire')])
    phone = wtf.StringField(label='Numero de telephone :')
    description = wtf.StringField(label='Description :')
    urlsite = wtf.StringField(label='Site web :')

    latitude = wtf.StringField(label='Latitude :')
    longitude = wtf.StringField(label='Longitude :')

    facebook = wtf.StringField(label='Lien facebook :')
    twitter = wtf.StringField(label='Lien twitter :')
    linkedin = wtf.StringField(label='Lien linkedin :')
    youtube = wtf.StringField(label='Lien youtube :')

    maincategorie = wtf.SelectField(label='Categorie Principale :', coerce=str, validators=[validators.Required(message='Champ obligatoire')])


def check_enfant(form, field):
    if form.enfant.data and not field.data:
        raise wtf.ValidationError('Selection obligatoire')


def check_enfant_media(form, field):
    if not form.enfant.data and not field.data:
        raise wtf.ValidationError('Ajout du Media Obligatoire')


class FormCategorie(wtf.Form):

    id = wtf.HiddenField()
    enfant = wtf.HiddenField()

    name = wtf.StringField(label='Nom de la categorie :', validators=[validators.Required(message='Champ obligatoire')])
    description = wtf.TextAreaField(label='Description de la categorie :')
    url_image = wtf.StringField(label='Image de la categorie :', validators=[check_enfant_media])
    icone = wtf.StringField(label='Icone de la categorie', validators=[check_enfant_media])
    parent_idcategorie = wtf.SelectField(label='Categorie Parente :', coerce=str, validators=[check_enfant])


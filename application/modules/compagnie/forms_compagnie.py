__author__ = 'User'


from flaskext import wtf
from flaskext.wtf import validators
from models_compagnie import Compagnie, Q, Categorie


def unique_email_validator(form, field):
    """ email must be unique"""
    user_manager = Compagnie.objects(
        Q(email=field.data)
    ).count()
    if user_manager >= 1 and not form.id:
        raise wtf.ValidationError('Email deja utilise par un autre utilisateur')


def check_not_cat(form, field):
    if not form.notCat.data and not field.data:
        raise wtf.ValidationError('Champ obligatoire')


class FormClient(wtf.Form):

    id = wtf.HiddenField()
    notCat = wtf.HiddenField()

    raison = wtf.StringField(label='Forme juridique :')
    name = wtf.StringField(label='Nom de l\'entreprise :', validators=[validators.Required(message='Champ obligatoire')])
    ville = wtf.StringField(label='Ville :', validators=[validators.Required(message='Champ obligatoire')])
    quartier = wtf.StringField(label='Quartier :')
    adresse = wtf.StringField(label='Adresse :')
    postal_code = wtf.StringField(label='Code postal :')
    repere = wtf.StringField(label='Reperage :')
    region = wtf.StringField(label='Region :')

    email = wtf.StringField(label='Adresse Email :', validators=[unique_email_validator])
    phone = wtf.StringField(label='Numero de telephone :')
    description = wtf.TextAreaField(label='Description :')
    urlsite = wtf.StringField(label='Site web :')

    latitude = wtf.StringField(label='Latitude :')
    longitude = wtf.StringField(label='Longitude :')

    facebook = wtf.StringField(label='Lien facebook :')
    twitter = wtf.StringField(label='Lien twitter :')
    linkedin = wtf.StringField(label='Lien linkedin :')
    youtube = wtf.StringField(label='Lien youtube :')

    idcategorie = wtf.SelectMultipleField(label='Categorie de l\'entreprise :', coerce=str, validators=[validators.Required(message='Champ obligatoire')])
    maincategorie = wtf.SelectField(label='Categorie Principale :', coerce=str, validators=[validators.Required(message='Champ obligatoire')])

    logo = wtf.StringField(label='Logo entreprise :')
    imageslide = wtf.StringField(label='Image du slide :')


def check_enfant(form, field):
    if form.enfant.data and not field.data:
        raise wtf.ValidationError('Selection obligatoire')


def check_enfant_media(form, field):
    if not form.enfant.data and not field.data:
        raise wtf.ValidationError('Ajout du Media Obligatoire')


def unique_code_validator(form, field):
    code_unique = Categorie.objects(
        name = field.data
    ).count()
    if code_unique:
        if not form.id.data:
            raise wtf.ValidationError('Ce nom est deja utilise.')
        else:
            code = Categorie.objects.get(id=form.id.data)
            if code.name != field.data:
                raise wtf.ValidationError('Ce nom est deja utilise.')


class FormCategorie(wtf.Form):

    id = wtf.HiddenField()
    enfant = wtf.HiddenField()

    name = wtf.StringField(label='Nom de la categorie :', validators=[validators.Required(message='Champ obligatoire'), unique_code_validator])
    description = wtf.TextAreaField(label='Description de la categorie :')
    url_image = wtf.StringField(label='Image de la categorie :')
    icone = wtf.StringField(label='Icone de la categorie :')
    parent_idcategorie = wtf.SelectField(label='Categorie Parente :', coerce=str, validators=[check_enfant])


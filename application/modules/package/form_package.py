# coding=utf-8
__author__ = 'User'


from flaskext import wtf
from flaskext.wtf import validators
from flaskext.wtf.html5 import NumberInput
from models_package import LigneService, Attribut


def valid_promo(form, field):
    if form.promo.data and not field.data:
        raise wtf.ValidationError('Definir le prix promotionnel.')


class FormPackage(wtf.Form):
    id = wtf.HiddenField()
    name = wtf.StringField(label='Nom du package :', validators=[validators.Required(message='Champ obligatoire')])
    description = wtf.TextAreaField(label='Description :')
    duree = wtf.StringField(label=u'Durée/Période :', widget=NumberInput(), validators=[validators.Required(message='Champ obligatoire')])
    prix = wtf.StringField(label='Prix :', widget=NumberInput(), validators=[validators.Required(message='Champ obligatoire')])
    prix_promo = wtf.StringField(label='Prix promotionnel :', widget=NumberInput(), validators=[valid_promo])
    promo = wtf.BooleanField()
    sale = wtf.BooleanField()
    idligneService = wtf.SelectField(label='Ligne de service :', coerce=str, validators=[validators.Required('Information Obligatoire')])


def unique_code_validator(form, field):
    code_unique = LigneService.objects(
        sigle = field.data
    ).count()
    if code_unique:
        if not form.id.data:
            raise wtf.ValidationError(u'Ce sigle est déja utilisé')
        else:
            code = LigneService.objects.get(id=form.id.data)
            if code.sigle != field.data:
                raise wtf.ValidationError(u'Ce sigle est déja utilisé.')


class FormService(wtf.Form):
    id = wtf.HiddenField()
    name = wtf.StringField(label='Nom du service :', validators=[validators.Required(message='Champ obligatoire')])
    package = wtf.BooleanField()
    sigle = wtf.StringField(label='Sigle :', validators=[unique_code_validator])
    unite = wtf.StringField(label=u'Unité des offres/packages :')


def unique_code_validator_attr(form, field):
    code_unique = Attribut.objects(
        name = field.data
    ).count()
    if code_unique:
        if not form.id.data:
            raise wtf.ValidationError(u'Ce sigle est déja utilisé.')
        else:
            code = Attribut.objects.get(id=form.id.data)
            if code.name != field.data:
                raise wtf.ValidationError(u'Ce sigle est déja utilisé.')


class FormAttribut(wtf.Form):
    id = wtf.HiddenField()
    name = wtf.StringField(label='Sigle :',validators=[unique_code_validator_attr])
    desc = wtf.TextAreaField(label='Description :')
    libelle = wtf.StringField(label='Nom de l\'attribut :', validators=[validators.Required(message='Champ obligatoire')])
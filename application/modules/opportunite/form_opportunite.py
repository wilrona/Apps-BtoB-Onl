__author__ = 'User'


from flaskext import wtf
from flaskext.wtf import validators
from flaskext.wtf.html5 import NumberInput
from models_opportunite import Activite, Etape, Libelle_Opportunite


def unique_code_validator(form, field):
    code_unique = Activite.objects(
        name=field.data
    ).count()
    if code_unique:
        if not form.id.data:
            raise wtf.ValidationError('Ce nom est deja utilise.')
        else:
            code = Activite.objects.get(id=form.id.data)
            if code.name != field.data:
                raise wtf.ValidationError('Ce nom est deja utilise.')


class FormActivite(wtf.Form):
    id = wtf.HiddenField()
    name = wtf.StringField(label='Type de message :', validators=[validators.Required(message='Champ obligatoire'), validators.length(max=50), unique_code_validator])
    description = wtf.TextAreaField(label='Description :')
    jour = wtf.StringField(label='Nombre de jour:', widget=NumberInput(), default=0)
    next = wtf.SelectField(label='Activite suivante recommande :', coerce=str)
    default = wtf.BooleanField(label='Default :')
    sigle = wtf.StringField()




def unique_code_validator_etape(form, field):
    code_unique = Etape.objects(
        name = field.data
    ).count()
    if code_unique:
        if not form.id.data:
            raise wtf.ValidationError('Ce nom est deja utilise.')
        else:
            code = Etape.objects.get(id=form.id.data)
            if code.name != field.data:
                raise wtf.ValidationError('Ce nom est deja utilise.')


class FormEtape(wtf.Form):
    id = wtf.HiddenField()
    name = wtf.StringField(label='Nom de l\'etape :', validators=[validators.Required(message='Champ obligatoire'), validators.length(max=50), unique_code_validator_etape])
    sigle = wtf.StringField()
    proba = wtf.StringField(label='Changer automatiquement la probabilite a (%) :', widget=NumberInput(), validators=[validators.Required(message='Champ obligatoire')])


class FormOpportunite(wtf.Form):
    id = wtf.HiddenField()
    etape = wtf.HiddenField()
    name = wtf.StringField(label='Objet de l\'opportunite :',  validators=[validators.Required(message='Champ obligatoire')])
    vendeur_id = wtf.SelectField(label='Vendeur :', coerce=str, validators=[validators.Required(message='Champ obligatoire')])
    note = wtf.TextAreaField(label='Note interne :')


class FormRelance(wtf.Form):
    id = wtf.HiddenField()
    activite_id = wtf.SelectField(label='Activite :', coerce=str, validators=[validators.Required(message='Champ obligatoire')])
    resume = wtf.StringField(label='Resume :',  validators=[validators.Required(message='Champ obligatoire')])
    dateNext = wtf.DateField(label='Date Fermeture :', format="%d/%m/%Y", validators=[validators.Required('Champ Obligatoire')])
    description = wtf.TextAreaField(label='Description :')


def unique_code_validator_lib(form, field):
    code_unique = Libelle_Opportunite.objects(
        name = field.data
    ).count()
    if code_unique:
        if not form.id.data:
            raise wtf.ValidationError('Ce nom est deja utilise.')
        else:
            code = Libelle_Opportunite.objects.get(id=form.id.data)
            if code.name != field.data:
                raise wtf.ValidationError('Ce nom est deja utilise.')

class FormLibelle(wtf.Form):
    id = wtf.HiddenField()
    name = wtf.StringField(label='Libelle opportunite :', validators=[validators.Required(message='Champ obligatoire'), validators.length(max=50), unique_code_validator_lib])




__author__ = 'wilrona'


from flaskext import wtf
from flaskext.wtf import validators
from models_profil import Profil


def unique_code_validator(form, field):
    code_unique = Profil.objects(
        name = field.data
    ).count()
    if code_unique:
        if not form.id.data:
            raise wtf.ValidationError('Ce nom est deja utilise dans les profils.')
        else:
            code = Profil.objects.get(id=form.id.data)
            if code.name != field.data:
                raise wtf.ValidationError('Ce nom est deja utilise dans les profils.')


class FormProfil(wtf.Form):
    id = wtf.HiddenField()
    name = wtf.StringField(label='Nom profil', validators=[validators.Required(message='Champ obligatoire'), validators.length(max=50), unique_code_validator])
    description = wtf.TextAreaField(label='Description du profil')
    active = wtf.BooleanField(default=True)

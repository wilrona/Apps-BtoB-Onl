
from flaskext import wtf
from flaskext.wtf import validators
from models_paiement import Moyen_paiement


def unique_code_validator(form, field):
    code_unique = Moyen_paiement.objects(
        sigle = field.data
    ).count()
    if code_unique:
        if not form.id.data:
            raise wtf.ValidationError('Ce sigle est deja utilise.')
        else:
            code = Moyen_paiement.objects.get(id=form.id.data)
            if code.sigle != field.data:
                raise wtf.ValidationError('Ce sigle est deja utilise.')


class FormMoyenPaiement(wtf.Form):
    id = wtf.HiddenField()
    name = wtf.StringField(label='Nom du moyen de paiement :', validators=[validators.Required(message='Champ obligatoire')])
    sigle = wtf.StringField(label='Sigle :', validators=[unique_code_validator])
    logo = wtf.StringField(label='Image du moyen de paiement :')
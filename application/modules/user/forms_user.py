__author__ = 'wilrona'

from flaskext import wtf
from flaskext.wtf import validators
from application import function
from ...modules import *
import datetime
from models_user import Users


def unique_email_validator(form, field):
    """ email must be unique"""
    user_manager = Users.objects(
        Q(email=field.data)
    ).count()
    if user_manager >= 1 and not form.id:
        raise wtf.ValidationError('Email deja utilise par un autre utilisateur')


def password_validator(form, field):
        """ Password must have one lowercase letter, one uppercase letter and one digit."""
        # Convert string to list of characters
        password = list(field.data)
        password_length = len(password)

        # Count lowercase, uppercase and numbers
        lowers = uppers = digits = 0
        for ch in password:
            if ch.islower(): lowers+=1
            if ch.isupper(): uppers+=1
            if ch.isdigit(): digits+=1

        # Password must have one lowercase letter, one uppercase letter and one digit
        is_valid = password_length>=6 and lowers and uppers and digits
        if not is_valid:
            raise wtf.ValidationError('Le mot de passe doit avoir plus de 6 caracteres avec une lettre minuscule, une lettre majuscule et un chiffre.')


class FormRegisterUserAdmin(wtf.Form):
    first_name = wtf.StringField(label='Prenom', validators=[validators.Required('Information obligatoire')])
    last_name = wtf.StringField(label='Nom', validators=[validators.Required('Information obligatoire')])
    email = wtf.StringField(label='Adresse Email', validators=[validators.Email('Email non valid'), validators.Required('Information obligatoire'), unique_email_validator])
    password = wtf.PasswordField(label='Mot de passe', validators=[validators.Required('Information obligatoire'), password_validator])
    retype_password = wtf.PasswordField(label='Confirmation du mot de passe', validators=[validators.EqualTo('password', message='Les deux mots de passe sont differents')])


class FormPassword(wtf.Form):
    password = wtf.PasswordField(label='Mot de passe', validators=[validators.Required('Information obligatoire'), password_validator])
    retype_password = wtf.PasswordField(label='Confirmation du mot de passe', validators=[validators.EqualTo('password', message='Les deux mots de passe sont differents')])


class FormLogin(wtf.Form):
    email = wtf.StringField(label='Adresse Email :', validators=[validators.Email('Email non valid'), validators.Required('Information obligatoire')])
    password = wtf.PasswordField(label='Mot de passe :', validators=[validators.Required('Information obligatoire'), password_validator])


def error_phone(form, field):
    if not form.mobile.data and not field.data:
        raise wtf.ValidationError('Le telephone ou le mobile, l\'un deux doit etre renseigne')


class FormUser(wtf.Form):
    id = wtf.HiddenField()
    first_name = wtf.StringField(label='Prenom', validators=[validators.Required('Information obligatoire')])
    last_name = wtf.StringField(label='Nom', validators=[validators.Required('Information obligatoire')])
    email = wtf.StringField(label='Adresse Email', validators=[validators.Email('Email non valid'), validators.Required('Information obligatoire'), unique_email_validator])
    fonction = wtf.StringField(label='Fonction :')
    phone = wtf.StringField(label='Telephone Mobile :')
    note = wtf.TextAreaField(label='Note interne :')

# formulaire pour le taux horaire
# def control_pass_date(form, field):
#     date = function.datetime_convert(field.data)
#     if datetime.datetime.today() > date:
#         raise wtf.ValidationError('Appliquez les taux horaires sur une date futur ou actuelle.')



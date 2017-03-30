__author__ = 'User'


from flaskext import wtf
from flaskext.wtf import validators
from flaskext.wtf.html5 import NumberInput


class FormDevis(wtf.Form):
    iddoc = wtf.HiddenField()
    client_id = wtf.SelectField(label='Information du client', validators=[validators.Required('Information Obligatoire')])
    contact_id = wtf.StringField(label='Information du contact', validators=[validators.Required('Information Obligatoire')])
    support_id = wtf.SelectField(label='Format de contenu utilise', validators=[validators.Required('Information Obligatoire')])
    opportunite_text = wtf.StringField(label='Opportunite associee au devis')
    opportunite_id = wtf.HiddenField()
    have_support = wtf.BooleanField()
    apply_tva = wtf.BooleanField()

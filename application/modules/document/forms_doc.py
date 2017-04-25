__author__ = 'User'


from flaskext import wtf
from flaskext.wtf import validators
from flaskext.wtf.html5 import NumberInput


class FormDevis(wtf.Form):
    iddoc = wtf.HiddenField()
    opportunite_text = wtf.StringField(label='Opportunite associee au devis')
    opportunite_id = wtf.HiddenField()


class FormFacture(wtf.Form):
    iddoc = wtf.HiddenField()
    devis_text = wtf.StringField(label='Reference du devis')
    devis_id = wtf.HiddenField()

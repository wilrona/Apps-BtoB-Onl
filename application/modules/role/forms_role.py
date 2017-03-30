__author__ = 'wilrona'

from flaskext import wtf


class FormRole(wtf.Form):
    description = wtf.TextAreaField(label='Description :')
    active = wtf.BooleanField(label='Active ?')
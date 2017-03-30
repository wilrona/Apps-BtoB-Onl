__author__ = 'wilrona'

from ...modules import app
from views import prefix

app.register_blueprint(prefix) # pas de url prefix pour la page d'accueil
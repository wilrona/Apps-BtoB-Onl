__author__ = 'wilrona'

from views_profil import app, prefix

app.register_blueprint(prefix, url_prefix='/configuration')
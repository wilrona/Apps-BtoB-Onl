__author__ = 'User'


from ...modules import app
from views_compagnie import prefix

app.register_blueprint(prefix, url_prefix='/client')

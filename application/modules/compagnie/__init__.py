__author__ = 'User'


from ...modules import app
from views_compagnie import prefix
from views_categorie import prefix_categorie


app.register_blueprint(prefix, url_prefix='/client')
app.register_blueprint(prefix_categorie, url_prefix='/configuration/categorie')

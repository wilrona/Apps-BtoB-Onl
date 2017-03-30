__author__ = 'User'


from ...modules import app
from views_devis import prefix
from views_cmd import prefix as prefix_commande

app.register_blueprint(prefix, url_prefix='/vente/devis')
app.register_blueprint(prefix_commande, url_prefix='/vente/commande')
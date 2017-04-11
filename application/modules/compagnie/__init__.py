__author__ = 'User'


from ...modules import app
from views_compagnie import prefix
from views_categorie import prefix_categorie
from views_claim import prefix_claim
from views_relation import prefix_relation


app.register_blueprint(prefix, url_prefix='/client')
app.register_blueprint(prefix_claim, url_prefix='/reclammation')
app.register_blueprint(prefix_relation, url_prefix='/relation')
app.register_blueprint(prefix_categorie, url_prefix='/configuration/categorie')

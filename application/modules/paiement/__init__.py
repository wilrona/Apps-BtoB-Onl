
from ...modules import app

from views_paiement import prefix
from views_reglement import prefix as prefix_reglement

app.register_blueprint(prefix, url_prefix='/configuration/moyen_paiement')
app.register_blueprint(prefix_reglement, url_prefix='/vente/reglement')



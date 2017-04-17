
from ...modules import app

from views_paiement import prefix

app.register_blueprint(prefix, url_prefix='/configuration/moyen_paiement')
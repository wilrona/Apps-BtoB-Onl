__author__ = 'User'

from ...modules import app
from views_support import prefix_support
from views_tranche import prefix_tranche
from views_localisation import prefix_localisation
from views_ecran import prefix_ecran
from views_site import prefix_site
# from views_package import prefix_package
from views_secteur import prefix_secteur


app.register_blueprint(prefix_support, url_prefix='/configuration/support')
app.register_blueprint(prefix_tranche, url_prefix='/configuration/tranche')
app.register_blueprint(prefix_localisation, url_prefix='/configuration/localisation')
app.register_blueprint(prefix_ecran, url_prefix='/configuration/ecran')
app.register_blueprint(prefix_site, url_prefix='/configuration/site')
# app.register_blueprint(prefix_package, url_prefix='/configuration/package')
app.register_blueprint(prefix_secteur, url_prefix='/configuration/secteur')
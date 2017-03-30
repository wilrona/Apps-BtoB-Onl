__author__ = 'User'

from ...modules import app
from views_opportunite import prefix_opportunite
from views_activite import prefix_activite
from views_etape import prefix_etape
from views_relance import prefix_relance
from views_libelle import prefix_libelle

app.register_blueprint(prefix_activite, url_prefix='/configuration/activite')
app.register_blueprint(prefix_etape, url_prefix='/configuration/etape')
app.register_blueprint(prefix_libelle, url_prefix='/configuration/libelle')
app.register_blueprint(prefix_opportunite, url_prefix='/relance/opportunite')
app.register_blueprint(prefix_relance, url_prefix='/relance/activite')
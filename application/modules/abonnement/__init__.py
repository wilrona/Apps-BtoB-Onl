
from ...modules import app
from views_abonne_ici import prefix
from views_abonne_hosting import prefix as prefix_hosting
from views_abonne_domaine import prefix as prefix_domaine

app.register_blueprint(prefix, url_prefix='/relance/abonnement')
app.register_blueprint(prefix_hosting, url_prefix='/relance/hosting')
app.register_blueprint(prefix_domaine, url_prefix='/relance/domaine')
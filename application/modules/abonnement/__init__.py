
from ...modules import app
from views_abonne_ici import prefix

app.register_blueprint(prefix, url_prefix='/relance/abonnement')
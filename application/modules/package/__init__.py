
from ...modules import app
from views_service import prefix_service
from views_package import prefix


app.register_blueprint(prefix, url_prefix='/configuration/package')
app.register_blueprint(prefix_service, url_prefix='/configuration/service')
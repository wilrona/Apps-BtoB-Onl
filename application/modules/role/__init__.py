__author__ = 'wilrona'

from ...modules import app
from views_role import prefix

app.register_blueprint(prefix, url_prefix='/configuration/role')
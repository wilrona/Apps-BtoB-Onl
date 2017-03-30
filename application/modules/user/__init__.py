__author__ = 'wilrona'

from ...modules import app
from views_user import prefix, prefix_param

app.register_blueprint(prefix, url_prefix='/user')
app.register_blueprint(prefix_param, url_prefix='/configuration/user') #Ancien parametre
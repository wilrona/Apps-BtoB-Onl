__author__ = 'wilrona'

from ...modules import app
from views_user import prefix, prefix_param, prefix_soldier

app.register_blueprint(prefix, url_prefix='/vente/user')
app.register_blueprint(prefix_param, url_prefix='/configuration/user') #Ancien parametre
app.register_blueprint(prefix_soldier, url_prefix='/vente/fieldsoldier') #Ancien parametre

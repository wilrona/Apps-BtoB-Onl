__author__ = 'User'


from ...modules import app
from views_company import prefix, prefix_param

app.register_blueprint(prefix, url_prefix='/configuration/company')
app.register_blueprint(prefix_param, url_prefix='/configuration/general')
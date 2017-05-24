"""
Initialize Flask app

"""
#coding=utf-8

from flask import Flask
import os
from datetime import timedelta
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.debug import DebuggedApplication

from flask.ext.login import LoginManager
# from flask_googlelogin import GoogleLogin
from flask_mongoengine import MongoEngine
from flask_mail import Mail, Message

from flask_apscheduler import APScheduler


app = Flask('application')

if os.getenv('FLASK_CONF') == 'TEST':
    app.config.from_object('application.settings.Testing')

elif 'SERVER_SOFTWARE' in os.environ and os.environ['SERVER_SOFTWARE'].startswith('Dev'):
    # Development settings
    app.config.from_object('application.settings.Development')

    # Flask-DebugToolbar
    toolbar = DebugToolbarExtension(app)

    # Google app engine mini profiler
    # https://github.com/kamens/gae_mini_profiler
    app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)

    from gae_mini_profiler import profiler, templatetags

    @app.context_processor
    def inject_profiler():
        return dict(profiler_includes=templatetags.profiler_includes())
    app.wsgi_app = profiler.ProfilerWSGIMiddleware(app.wsgi_app)
else:
    app.config.from_object('application.settings.Production')

# Enable jinja2 loop controls extension
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'static')

app.config['MONGODB_SETTINGS'] = {
    'db': 'crm_yoomee'
    # 'db': 'icicmtest',
    # 'host': 'localhost',
    # 'port': 28569
}

# This is the path to the upload directory
CURRENT_FILE = os.path.abspath(__file__)
CURRENT_DIR = os.path.dirname(CURRENT_FILE)

app.config['FOLDER_PROJECT'] = os.path.dirname(CURRENT_DIR)
app.config['FOLDER_APPS'] = CURRENT_DIR # Modules
app.config['STATIC_APPS'] = CURRENT_DIR+'/static'

ici_link_categorie = 'ici_cm/media/pictures/categories'
ici_link = 'ici_cm/media/pictures/companies'

app.config['UPLOAD_FOLDER_CATEGORIE'] = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(APP_ROOT))), ici_link_categorie)
app.config['UPLOAD_FOLDER_CLIENT'] = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(APP_ROOT))), ici_link)

# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])

app.config['SECRET_KEY'] = '4fdb4fed4631d84f17c9711'
app.config['SECURITY_PASSWORD_SALT'] = '4fdb4fed4631d84f17c97112e3d85442324848a29c4291a65ff53dc64bfd9a10'

# app.config["MAIL_SERVER"] = 'smtp.gmail.com'
# app.config["MAIL_PORT"] = 465
# app.config["MAIL_USE_TLS"] = False
# app.config["MAIL_USE_SSL"] = True
# app.config["MAIL_USERNAME"] = 'wilrona@gmail.com'
# app.config["MAIL_PASSWORD"] = ''

db = MongoEngine(app)
mail = Mail(app)

from application.modules.utilities.cron import Config

app.config.from_object(Config())

scheduler = APScheduler()
scheduler.init_app(app)

# app.permanent_session_lifetime = timedelta(seconds=1200)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'home'

# app.config.update(
#     SECRET_KEY='AIzaSyBBT8JaFtFr2Gknpe5GxvhYMWdxkxULHSc',
#     GOOGLE_LOGIN_CLIENT_ID='667156749456-lbd0uctkmb0vscjn2q0e1420f20fu435.apps.googleusercontent.com',
#     GOOGLE_LOGIN_CLIENT_SECRET='TOTRxDbDVTyC-I3uZ0ATX3kJ',
#     GOOGLE_LOGIN_REDIRECT_URI='http://localhost:9090/user/oauth2callback'
#     # GOOGLE_LOGIN_REDIRECT_URI='http://fdt.accentcom.agency/user/oauth2callback'
# )
#
# google_login = GoogleLogin(app)

# function for jinja2
import function

app.url_map.converters['objectid'] = function.ObjectIDConverter
app.jinja_env.filters['format_date'] = function.format_date
app.jinja_env.filters['format_date_month'] = function.format_date_month
app.jinja_env.filters['add_time'] = function.add_time
app.jinja_env.filters['format_price'] = function.format_price
app.jinja_env.filters['get_first_day'] = function.get_first_day
app.jinja_env.filters['get_last_day'] = function.get_last_day
app.jinja_env.filters['string'] = function.string


# Pull in URL dispatch routes
import urls







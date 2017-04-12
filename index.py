import sys
import os

# # Active your Virtual Environment, which I'm assuming you've already setup
# activate_this='/home/marcelj35/.virtualenvs/venv_name/bin/activate_this.py'
# execfile(activate_this, dict(__file__=activate_this))

# Appending our Flask project files
# sys.path.append('/home/marcelj35/webapps/gesacom/gesacom')
sys.path.insert(1, os.path.join('/home/yoomeeonl/webapps/crm/crm', 'lib'))
# sys.path.insert(0, '/home/marcelj35/webapps/gesacom/gesacom')

CURRENT_FILE = os.path.abspath(__file__)
CURRENT_DIR = os.path.dirname(CURRENT_FILE)
PROJECT_DIR = os.path.dirname(CURRENT_DIR)

# Add project top-dir to path (since it has no __init__.py)
sys.path.append(PROJECT_DIR + '/crm/')

# Launching our app
from application import app as application


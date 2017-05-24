import os
import sys

#coding=utf-8

sys.path.insert(1, os.path.join(os.path.abspath('.'), 'lib'))

# import application

from application import *

scheduler.start()

app.run(host='0.0.0.0', port=9090, debug=True)
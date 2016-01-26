import os, sys
import logging
from logging import handlers
from random import randint
import jinja2

from flask import Flask, render_template

VERSION = '0.1.0'
app = Flask(__name__)

# Debugging
LEVEL = logging.INFO
root = logging.getLogger('SystemLogger')
root.setLevel(LEVEL)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(LEVEL)
formatter = logging.Formatter('%(name)s[%(levelname)s] - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

# Logging student interactions
from interaction_logger import StructuredEvent
LOG_FILENAME = 'log/student_interactions/student_interactions.log'
student_interactions_logger = logging.getLogger('StudentInteractions')
student_interactions_logger.setLevel(logging.INFO)
handler = handlers.TimedRotatingFileHandler(LOG_FILENAME, when='D')
handler.setLevel(logging.INFO)
simple_formatter = logging.Formatter('%(message)s')
handler.setFormatter(simple_formatter)
student_interactions_logger.addHandler(handler)

# Modify Jinja2
app.jinja_env.filters['zip'] = zip

app.config.from_object('config.TestingConfig')

# Assets
from controllers.assets import assets

# Email
from flask.ext.mail import Mail
mail = Mail(app)

import controllers

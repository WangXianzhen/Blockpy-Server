import json
import os, sys
import logging
import logging.config
from random import randint
import jinja2
from natsort import natsorted

from flask import Flask, render_template

with open('secrets.json') as secrets_file:
    secrets = json.load(secrets_file)

VERSION = '0.1.0'
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

#from werkzeug.contrib.profiler import ProfilerMiddleware
#app.config['PROFILE'] = True
#app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[50])

# Modify Jinja2
app.jinja_env.filters['zip'] = zip
def attempt_json_load(data):
    try:
        return json.loads(data)
    except:
        return {}
app.jinja_env.filters['json_load'] = attempt_json_load
app.jinja_env.filters['list'] = list
app.jinja_env.filters['natsorted'] = natsorted
def get_setting(assignment, *keys):
    if assignment.settings:
        settings = json.loads(assignment.settings)
    else:
        settings = {}
    for key in keys:
        if key in settings:
            settings = settings[key]
        else:
            return None
    return settings
app.jinja_env.filters['get_setting'] = get_setting

if secrets['PRODUCTION']:
    app.config.from_object('config.ProductionConfig')
else:
    app.config.from_object('config.TestingConfig')

ERROR_LOG = os.path.join(app.config['ROOT_DIRECTORY'],
                         'log/errors.log')
STUDENT_INTERACTION_LOG = os.path.join(app.config['ROOT_DIRECTORY'], 
                                       'log/student_interactions/student_interactions.log')
LOGGING = {
    'version': 1,
    'handlers': {
        'console':{
            'class':'logging.StreamHandler',
            'formatter':'basicFormatter',
            'level': 'WARNING',
        },
        'errorHandler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': ERROR_LOG,
            'level': 'WARNING',
            'formatter': 'basicFormatter'
        }
    },
    'loggers': {
        'Feedbackfull': {
            'level': 'INFO',
            'handlers': ['FeedbackHandler']
        },
        'SystemLogger': {
            'level': 'WARNING',
            'handlers': ['console']
        },
        'StudentInteractions': {
            'level': 'INFO',
            'handlers': ['fileHandler']
        }
    },
    'root': {
        'level': 'WARNING',
        'handlers': ['console', 'errorHandler']
    },
    'formatters': {
        'basicFormatter': {
            'format': '%(name)s[%(levelname)s] - %(message)s'
        },
        'simpleFormatter': {
            'format': '%(message)s'
        }
    }
}
LOG_FILENAME = os.path.join(app.config['ROOT_DIRECTORY'], 'log/feedbackfull/feedbackfull.log')
if app.config['IS_PRODUCTION']:
    LOGGING['handlers']['fileHandler'] = {
        'class': 'logging.handlers.TimedRotatingFileHandler',
        'filename': STUDENT_INTERACTION_LOG,
        "level": "INFO",
        'when': 'D',
        'formatter': 'simpleFormatter'
    }
else:
    LOGGING['handlers']['fileHandler'] = {
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': STUDENT_INTERACTION_LOG,
        "level": "INFO",
        'formatter': 'simpleFormatter'
    }
    LOGGING
LOGGING['handlers']['FeedbackHandler'] = {
    'filename': LOG_FILENAME,
    'formatter': 'simpleFormatter',
    'class': 'logging.handlers.RotatingFileHandler'
}
    
logging.config.dictConfig(LOGGING)

# Assets
from controllers.assets import assets

# Email
from flask_mail import Mail
mail = Mail(app)

import controllers

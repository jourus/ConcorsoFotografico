# coding=latin-1

"""
The flask application package.
"""

from flask import Flask


import logging
from logging.config import dictConfig, fileConfig
from flask.logging import default_handler



dictConfig= dict(
    version = 1,
    formatters = {
        'f': {'format':
              '%(asctime)s %(name)-12s %(levelname)----8s %(message)s'}
        },
    handlers = {
        'h': {'class': 'logging.StreamHandler',
              'formatter': 'f',
              'level': logging.DEBUG}
        },
    root = {
        'handlers': ['h'],
        'level': logging.DEBUG,
        },
)


app = Flask(__name__)

app.logger.removeHandler(default_handler)
app.logger.config=dictConfig

# Accesso al DB
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:mysecretpassword@localhost/votazione'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:mysecretpassword@kubernetes.docker.internal/votazione'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



app.config['TESTING'] = True



app.logger.debug('Questo è debug')
app.logger.info('Questo è info')
app.logger.warning('Questo è warning')
app.logger.error('Questo è error')



import Concorso.views




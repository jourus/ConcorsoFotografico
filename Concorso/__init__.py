# coding=latin-1

"""
The flask application package.
"""

from flask import Flask
import logging
from flask_login import LoginManager
# from flask.logging import default_handler

app = Flask(__name__)


# dictConfig= dict(
#     version = 1,
#     formatters = {
#         'f': {'format':
#               '%(asctime)s %(name)-12s %(levelname)----8s %(message)s'}
#         },
#     handlers = {
#         'h': {'class': 'logging.StreamHandler',
#               'formatter': 'f',
#               'level': logging.DEBUG}
#         },
#     root = {
#         'handlers': ['h'],
#         'level': logging.DEBUG,
#         },
# )



# app.logger.removeHandler(default_handler)
# app.logger.config=dictConfig



logging.basicConfig(filename='demo.log', level=logging.DEBUG)

# from logging.config import fileConfig
# from os import path
# import os

# log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.cfg')
# path_rslv = path.split(path.dirname(path.abspath(__file__)))[1:] 
# fileName = path.join(*[".." for dotdot in range(len(path_rslv))], "logging.cfg")
# print(log_file_path)
# print(f"CWD = {os.getcwd()}")
# print(f"fileName = {fileName}")
# fileConfig("logging.cfg")



# Accesso al DB
##### app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:mysecretpassword@localhost/votazione'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:mysecretpassword@kubernetes.docker.internal/votazione'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['TESTING'] = True

#from appconfig import ProductionConfig
#app.config.from_object(ProductionConfig())
app.config.from_pyfile('settings.cfg', silent=True)


# Configure Login
app.secret_key = app.config['SECRET_KEY']
login_manager = LoginManager()
#login_manager.login_view = 'auth.login'
login_manager.init_app(app)

app.logger.debug('Questo è debug')
app.logger.info('Questo è info')
app.logger.warning('Questo è warning')
app.logger.error('Questo è error')



import Concorso.views
from .model import User




@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve

    """
    return User.query.get(user_id)
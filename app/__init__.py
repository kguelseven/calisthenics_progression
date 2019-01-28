import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object(Config)
login = LoginManager(app)
# vie function that handles logins
login.login_view = 'login'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
file_handler = RotatingFileHandler('logs/calisthenics-progression.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

app.logger.setLevel(logging.INFO)
app.logger.info('Calisthenics-Progression startup')

from app import routes, models, errors
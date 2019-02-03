import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment

app = Flask(__name__)
app.config.from_pyfile('_config.py')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
# view function for handling logins
login.login_view = 'auth.login'
login.login_message = ('Please log in to acess this page')
mail = Mail(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

from app.errors import bp as errors_bp
app.register_blueprint(errors_bp)

from app.auth import bp as auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

from app.main import bp as main_bp
app.register_blueprint(main_bp)
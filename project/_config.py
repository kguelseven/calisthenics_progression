import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

#main config
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')
MYSQL_CURSORCLASS = 'DictCursor'
WORKOUTS_PER_PAGE = 10
SQLALCHEMY_DATABASE_URI = os.environ.get('DB_URI')
SQLALCHEMY_POOL_RECYCLE = 299
SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')

SQLALCHEMY_TRACK_MODIFICATIONS = False

# mail settings
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True

#gmail authentification
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

# mail accounts
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
import os
from dotenv import load_dotenv

# folder where this script lives
basedir = os.path.abspath(os.path.dirname(__file__))
# load_dotenv(os.path.join(basedir, '.env'))

# Config MySQL
MYSQL_HOST = 'localhost'
MYSQL_USER = 'testuser'
MYSQL_PASSWORD = '11+11Gibt22!'
MYSQL_DB = 'calisthenics'
MYSQL_CURSORCLASS = 'DictCursor'
SECRET_KEY = os.environ.get('SECRET KEY') or 'you-will-never-guess'

DATABASE = 'app.db'
SECRET_KEY = os.environ.get('SECRET KEY') or 'you-will-never-guess'
DEBUG = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
WORKOUTS_PER_PAGE = 10
MAIL_SERVER = os.environ.get('MAIL_SERVER')
MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
ADMINS = ['your-email@example.com']

# define the full path for the database
DATABASE_PATH = os.path.join(basedir, DATABASE)

# the database uri
SQLALCHEMY_DATABASE_URI = 'mysql://richi:11+11Gibt22!@localhost/calisthenics'



    
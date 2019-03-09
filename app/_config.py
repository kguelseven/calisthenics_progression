import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

DEBUG = True
SECRET_KEY = os.environ.get('SECRET_KEY')
MYSQL_CURSORCLASS = 'DictCursor'
WORKOUTS_PER_PAGE = 10
SQLALCHEMY_DATABASE_URI = os.environ.get('DB_URI')

SQLALCHEMY_TRACK_MODIFICATIONS = False
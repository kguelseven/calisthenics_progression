import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET KEX') or 'you-will-never-guess'
    
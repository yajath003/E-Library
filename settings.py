import os

 # Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.sqlite3')
SQLALCHEMY_TRACK_MODIFICATIONS = True

SITE_NAME = 'E-Library'
IMAGES_PATH=os.path.join(basedir, 'static/images/uploads')
SECRET_KEY='you-will-never-guess'

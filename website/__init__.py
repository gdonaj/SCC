from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import logging
import os

database = SQLAlchemy()

def create_database(app):
    rootFolder = os.getcwd()
    DB_NAME = rootFolder + "/instance/database.db"
    if not path.exists(DB_NAME):
        database.create_all()

def create_app():

    rootFolder = os.getcwd()
    DB_NAME = rootFolder + "/instance/database.db"
    app = Flask(__name__)
    app.logger.setLevel(logging.INFO)
    app.config['SECRET_KEY'] = '12345678901234567890'    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    database.init_app(app)

    from .dbModels import User
    from .viewAdmin import viewAdmin
    from .viewUser import viewUser
    from .viewAccount import viewAccount
    from .viewTranscriber import viewTranscriber
    app.register_blueprint(viewAdmin, url_prefix='/')
    app.register_blueprint(viewUser, url_prefix='/')
    app.register_blueprint(viewAccount, url_prefix='/')
    app.register_blueprint(viewTranscriber, url_prefix='/')
    
    with app.app_context():
        database.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'viewAccount.login'
    login_manager.login_message = u"Za dostop do te strani se morate prijaviti."
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

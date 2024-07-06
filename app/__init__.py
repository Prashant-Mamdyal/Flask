from flask import Flask

from .extensions import api, db
from .routes import ns

def create_app():
    app = Flask(__name__)

    #db.config['SQLALCHEMY_DATABASE_URI']='mysql://username:password@localhost/db_name'
    app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:1234@localhost/flask_app'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    api.init_app(app)
    db.init_app(app)       

    api.add_namespace(ns)

    return app  
from flask import Flask

from .extensions import api, db
from .routes import customers_ns, orders_ns

def create_app(config_name = None):
    app = Flask(__name__)

    if config_name == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///:memory:'
        app.config['Testing']= True
    else:
        #db.config['SQLALCHEMY_DATABASE_URI']='mysql://username:password@localhost/db_name'
        app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:1234@localhost/flask_app'
        
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    

    api.init_app(app)
    db.init_app(app)
    
    with app.app_context():
        db.create_all()

    api.add_namespace(customers_ns)
    api.add_namespace(orders_ns)

    return app  
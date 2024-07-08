from flask import Flask

from .extensions import api, db
from .routes import customers_ns, orders_ns

def create_app():
    app = Flask(__name__)

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
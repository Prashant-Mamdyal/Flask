from flask import request
from flask_restx import Resource, Namespace
from .models import Customer
from .api_models import customer_model, customer_input_model
from .extensions import db

customers_ns = Namespace("customers", description='Customers endpoints')
orders_ns = Namespace('orders', description='Orders endpoints')


@customers_ns.route("/")
class CustomerList(Resource):
    @customers_ns.marshal_list_with(customer_model)
    def get(self):
        customers = Customer.query.all()
        return customers, 200
    
    @customers_ns.expect(customer_input_model)
    @customers_ns.marshal_with(customer_model)
    def post(self):
        data = request.json
        new_customer = Customer(name=data['name'], contact_info=data['contact_info'])
        db.session.add(new_customer)
        db.session.commit()
        return new_customer, 201
    

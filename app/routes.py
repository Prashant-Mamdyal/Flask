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
        customer = Customer.query.all()
        return customer, 200
    
    @customers_ns.expect(customer_input_model)
    @customers_ns.marshal_with(customer_model)
    def post(self):
        data = request.json
        new_customer = Customer(name=data['name'], contact_info=data['contact_info'])
        db.session.add(new_customer)
        db.session.commit()
        return new_customer, 201

@customers_ns.route("/<int:customer_id>")    
class CustomerDetails(Resource):
    @customers_ns.marshal_with(customer_model)
    def get(self, customer_id):
        customer = Customer.query.get(customer_id)
        return customer, 200
    
    @customers_ns.expect(customer_input_model)
    @customers_ns.marshal_with(customer_model)
    def put(self, customer_id):
        data = request.json
        customer = Customer.query.get(customer_id)
        customer.name = data['name']
        customer.contact_info = data['contact_info']
        db.session.commit()
        return customer, 200
    
    @customers_ns.marshal_list_with(customer_model)
    def delete(self, customer_id):
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer) 
        db.session.commit()
        return customer, 200
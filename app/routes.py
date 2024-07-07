from flask import request
from flask_restx import Resource, Namespace
from .models import Customer, Order, OrderItem
from .api_models import customer_model, customer_input_model, order_model, order_input_model, order_input_status_model, orderitem_model
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
    
#-----------------------------------------------
@orders_ns.route("/")
class OrderList(Resource):
    @orders_ns.marshal_list_with(order_model)
    def get(self):
        order = Order.query.all()
        return order, 200

    @orders_ns.expect(order_input_model)
    @orders_ns.marshal_with(order_model)
    def post(self):
        data = request.json
        new_order = Order(customer_id = data['customer_id'], order_date = data['order_date'], status = data['status'])
        db.session.add(new_order)
        db.session.commit()
        return new_order , 201
    
@orders_ns.route("/<int:order_id>")
class OrderDetails(Resource):
    @orders_ns.marshal_with(order_model)
    def get(self, order_id):
        new_order = Order.query.get_or_404(order_id)
        return new_order, 200

    @orders_ns.expect(order_input_model)
    @orders_ns.marshal_with(order_model)
    def put(self, order_id):
        data = request.json
        order = Order.query.get(order_id)
        order.customer_id = data['customer_id']
        order.order_date = data['order_date']
        order.status = data['status']
        db.session.commit()
        return order, 200 
    
    def delete(self, order_id):
        order = Order.query.get_or_404(order_id)
        db.session.delete(order)
        db.session.commit()
        return {"message":"Order deleted successfully"}, 200
    
@orders_ns.route("/<int:order_id>/status")
class OrderStatus(Resource):
    @orders_ns.expect(order_input_status_model)
    @orders_ns.marshal_with(order_model)
    def patch(self, order_id):
        data = request.json
        order = Order.query.get_or_404(order_id)
        order.status = data['status']
        db.session.commit()
        return order, 200
    
@orders_ns.route("<int:order_id>/items")
class OrderItemsList(Resource):
    @orders_ns.marshal_list_with(orderitem_model)
    def get(self, order_id):
        orderitem = OrderItem.query.get(order_id)
        return orderitem, 200
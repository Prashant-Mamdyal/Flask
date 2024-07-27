from flask import request
from flask_restx import Resource, Namespace
from datetime import datetime
from .models import Customer, Order, OrderItem, Shipment
from .api_models import customer_model, customer_input_model, order_model, order_input_model, orderitem_model, order_input_status_model
from .extensions import api, db

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
        if not customer:
            api.abort(404, f"Customer {customer_id} not found")
        return customer, 200
    
    @customers_ns.expect(customer_input_model)
    @customers_ns.marshal_with(customer_model)
    def put(self, customer_id):
        data = request.json
        customer = Customer.query.get(customer_id)
        if not customer:
            api.abort(404, f"Customer {customer_id} not found")
        customer.name = data['name']
        customer.contact_info = data['contact_info']
        db.session.commit()
        return customer, 200
    

    def delete(self, customer_id):
        customer = Customer.query.get(customer_id)
        if not customer:
            api.abort(404, f"Customer {customer_id} not found")
        
        if customer.orders:
            api.abort(400, f"Customer {customer_id} has associated data in orders tables and cannot be deleted")

        db.session.delete(customer) 
        db.session.commit()
        return {"message": "customer deleted successfully"}
    
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
        customer_id = data['customer_id']
        customer = Customer.query.get(customer_id)
        if not customer:
            api.abort(404, f"Customer {customer_id} not present")

        try:
            order_date = datetime.fromisoformat(data['order_date'])
        except ValueError:
            api.abort(400, "Invalid date format. Use ISO 8601 format.")

        new_order = Order(customer_id=customer_id, order_date=order_date, status=data['status'])
        db.session.add(new_order)
        db.session.commit()
        return new_order , 201
    
@orders_ns.route("/<int:order_id>")
class OrderDetails(Resource):
    @orders_ns.marshal_with(order_model)
    def get(self, order_id):
        order = Order.query.get(order_id)
        if not order:
            api.abort(404, f"Order {order_id} not found")
        return order, 200

    @orders_ns.expect(order_input_model)
    @orders_ns.marshal_with(order_model)
    def put(self, order_id):
        data = request.json
        customer_id = data['customer_id']
        customer = Customer.query.get(customer_id)
        if not customer:
            api.abort(404, f'Customer {customer_id} not present')

        try:
            order_date = datetime.fromisoformat(data['order_date'])
        except ValueError:
            api.abort(400, "Invalid date format. Use ISO 8601 format.")

        order = Order.query.get(order_id)
        if not order:
            api.abort(404, f'Order {order_id} not present')

        order.customer_id = customer_id
        order.order_date = order_date
        order.status = data['status']
        db.session.commit()
        return order, 200
    
    def delete(self, order_id):
        order = Order.query.get(order_id)
        if not order:
            api.abort(404, f'Order {order_id} not found')
            
        if order.order_items:
            api.abort(400, f'Order {order_id} has associated data in order items table and cannot be deleted')

        if order.shipments:
            api.abort(400, f'Order {order_id} has associated data in shipment table and cannot be deleted')

        db.session.delete(order)
        db.session.commit()
        return {"message": "Order deleted successfully"}, 200
    
@orders_ns.route("/<int:order_id>/status")
class OrderStatus(Resource):
    @orders_ns.expect(order_input_status_model)
    @orders_ns.marshal_with(order_model)
    def patch(self, order_id):
        data = request.json
        valid_statuses = {'Pending', 'Fulfilled', 'Cancelled'}

        if 'status' not in data or data['status'] not in valid_statuses:
            api.abort(400, 'Invalid status. Please set status to Pending, Fulfilled, or Cancelled.')

        order = Order.query.get(order_id)
        if not order:
            api.abort(404, f'Order {order_id } not found')
            
        order.status = data['status']
        db.session.commit()
        return order, 200
    
@orders_ns.route("/<int:order_id>/items")
class OrderItemsList(Resource):
    @orders_ns.marshal_list_with(orderitem_model)
    def get(self, order_id):
        order = Order.query.get(order_id)
        if not order:
            api.abort(404, f'Order {order_id} not present')

        order_items = OrderItem.query.filter_by(order_id=order_id).all()
        if not order_items:
            return [], 200  

        return order_items, 200
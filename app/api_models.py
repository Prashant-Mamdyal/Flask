from flask_restx import fields
from .extensions import api

product_model = api.model("Product", {
    "id": fields.Integer,
    "name": fields.String,
    "description": fields.String,
    "price": fields.Float,
    "stock": fields.Integer
})


orderitem_model = api.model("OrderItem", {
    "orderitem_id": fields.Integer,
    "product_id":fields.Nested(product_model),
    "quantity": fields.Integer,
    "price": fields.Float
})


order_model = api.model("Order", {
    "id": fields.Integer,
    "customer_id":fields.Integer,
    "order_date": fields.DateTime,
    "status": fields.String,
    "order_items":fields.Nested(orderitem_model)
})

order_input_model = api.model("Order", {
    "customer_id":fields.Integer,
    "order_date":fields.DateTime,
    "status": fields.String
})

order_input_status_model = api.model("Order", {
    "status":fields.String
})


customer_model = api.model("Customer",{
    "id" : fields.Integer,
    "name": fields.String,
    "contact_info" : fields.String,
    "orders": fields.Nested(order_model)
})

customer_input_model = api.model("Customer",{
    "name": fields.String,
    "contact_info": fields.String
})
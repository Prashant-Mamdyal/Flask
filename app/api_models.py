from flask_restx import fields
from .extensions import api

customer_model = api.model("Customer",{
    "id" : fields.Integer,
    "name": fields.String,
    "contact_info" : fields.String
})

customer_input_model = api.model("Customer",{
    "name": fields.String,
    "contact_info": fields.String
})
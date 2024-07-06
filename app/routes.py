from flask_restx import Resource, Namespace

ns = Namespace("api")


@ns.route("")
class Hello(Resource):
    def get(self):
        return {"hello":"restx"}
from flask_restful import Resource
from ..Modelos import db, Venta, VentaSchema
from flask_jwt_extended import jwt_required, get_jwt_identity

Venta_schema = VentaSchema()

class Vista_Venta(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        return[Venta_schema.dump(Venta) for Venta in Venta.query.all()]
    
 
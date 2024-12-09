from flask_restful import Resource
from ..Modelos import db, Venta, VentaSchema
from flask_jwt_extended import jwt_required

Venta_schema = VentaSchema()

class Vista_Venta(Resource):
    @jwt_required()
    def get(self):
        return[Venta_schema.dump(Venta) for Venta in Venta.query.all()]
    
 
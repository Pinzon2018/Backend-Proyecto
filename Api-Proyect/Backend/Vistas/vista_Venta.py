from flask_restful import Resource
from ..Modelos import db, Venta, VentaSchema

VentaSchema = VentaSchema()

class Vista_Venta(Resource):
    def get(self):
        return[VentaSchema.dump(Venta) for Venta in Venta.query.all()]
    
 
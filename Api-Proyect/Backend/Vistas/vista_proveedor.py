from flask import request
from flask_restful import Resource
from ..Modelos import db, Proveedor, ProveedorSchema
from flask_jwt_extended import jwt_required, get_jwt_identity

proveedor_schema = ProveedorSchema()

class VistaProveedor(Resource):
    @jwt_required()
    def get(self, Id_Proveedor=None):
        current_user = get_jwt_identity()
        if Id_Proveedor:
            proveedor = Proveedor.query.get_or_404(Id_Proveedor)
            return proveedor_schema.dump(proveedor)
        else:
            return [proveedor_schema.dump(u) for u in Proveedor.query.all()]

    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        nuevo_proveedor = Proveedor(
            Nombre_Prov=request.json['Nombre_Prov'],
            Telefono_Prov=request.json['Telefono_Prov'],
            Direccion_Prov=request.json['Direccion_Prov']
        )
        db.session.add(nuevo_proveedor)
        db.session.commit()
        return proveedor_schema.dump(nuevo_proveedor)

    @jwt_required()
    def put(self, Id_Proveedor):
        current_user = get_jwt_identity()
        proveedor = Proveedor.query.get(Id_Proveedor)
        if not proveedor:
            return 'Proveedor no encontrado', 404

        proveedor.Nombre_Prov = request.json.get('Nombre_Prov', proveedor.Nombre_Prov)
        proveedor.Telefono_Prov = request.json.get('Telefono_Prov', proveedor.Telefono_Prov)
        proveedor.Direccion_Prov = request.json.get('Direccion_Prov', proveedor.Direccion_Prov)

        db.session.commit()
        return proveedor_schema.dump(proveedor), 200
    
    @jwt_required()
    def delete(self, Id_Proveedor):
        current_user = get_jwt_identity()
        proveedor = Proveedor.query.get(Id_Proveedor)
        if not proveedor:
            return 'Proveedor no encontrado', 404
        
        db.session.delete(proveedor)
        db.session.commit()
        return 'Proveedor Eliminado', 204

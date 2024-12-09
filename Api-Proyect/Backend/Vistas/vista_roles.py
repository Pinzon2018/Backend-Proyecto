from flask import request
from flask_restful import Resource
from ..Modelos import db, Rol, RolSchema
from flask_jwt_extended import jwt_required, get_jwt_identity

rol_schema = RolSchema()

class VistaRol(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        return [rol_schema.dump(Rol) for Rol in Rol.query.all()]
    
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        nuevo_rol = Rol(Nombre = request.json['Nombre'])
        db.session.add(nuevo_rol)
        db.session.commit()
        return rol_schema.dump(nuevo_rol)
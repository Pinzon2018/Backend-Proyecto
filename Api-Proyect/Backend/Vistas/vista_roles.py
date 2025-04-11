from flask import request
from flask_restful import Resource
from ..Modelos import db, Rol, RolSchema
from flask_jwt_extended import jwt_required, get_jwt_identity

roles_schema = RolSchema(many=True)   # para listas
rol_schema = RolSchema()              # para un solo objeto

class VistaRol(Resource):
    @jwt_required()
    def get(self):
        roles = Rol.query.all()
        return roles_schema.dump(roles), 200  # lista completa

    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        nuevo_rol = Rol(Nombre=request.json['Nombre'])
        db.session.add(nuevo_rol)
        db.session.commit()
        return rol_schema.dump(nuevo_rol), 201
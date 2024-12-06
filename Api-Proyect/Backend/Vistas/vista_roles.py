from flask import request
from flask_restful import Resource
from ..Modelos import db, Rol, RolSchema

rol_schema = RolSchema()

class VistaRol(Resource):
    def get(self):
        return [rol_schema.dump(Rol) for Rol in Rol.query.all()]
    
    def post(self):
        nuevo_rol = Rol(Nombre = request.json['Nombre'])
        db.session.add(nuevo_rol)
        db.session.commit()
        return rol_schema.dump(nuevo_rol)
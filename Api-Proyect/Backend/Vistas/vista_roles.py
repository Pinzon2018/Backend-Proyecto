from flask import request
from flask_restful import Resource
from ..Modelos import db, Rol, RolSchema
from flask_jwt_extended import jwt_required, get_jwt_identity

roles_schema = RolSchema(many=True)   # para listas
rol_schema = RolSchema()              # para un solo objeto

class VistaRol(Resource):
    @jwt_required()
    def get(self):
        """
        Obtener todos los roles
        ---
        tags:
          - Roles
        security:
          - Bearer: []
        responses:
          200:
            description: Lista de roles existentes
            schema:
              type: array
              items:
                properties:
                  Id_Rol:
                    type: integer
                    example: 1
                  Nombre:
                    type: string
                    example: Administrador
        """
        roles = Rol.query.all()
        return roles_schema.dump(roles), 200  # lista completa

    @jwt_required()
    def post(self):
        """
        Crear un nuevo rol
        ---
        tags:
          - Roles
        security:
          - Bearer: []
        parameters:
          - in: body
            name: body
            description: Datos del nuevo rol
            required: true
            schema:
              type: object
              required:
                - Nombre
              properties:
                Nombre:
                  type: string
                  example: Empleado
        responses:
          201:
            description: Rol creado exitosamente
            schema:
              properties:
                Id_Rol:
                  type: integer
                Nombre:
                  type: string
        """
        current_user = get_jwt_identity()
        nuevo_rol = Rol(Nombre=request.json['Nombre'])
        db.session.add(nuevo_rol)
        db.session.commit()
        return rol_schema.dump(nuevo_rol), 201
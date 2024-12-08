from flask import request
from ..Modelos import db, Usuario
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash


class VistaLogin(Resource):
    def post(self):
        datos = request.json
        Nombre_Usu = datos.get("Nombre_Usu")
        Contraseña_hash = datos.get("Contraseña_hash")
        usuario = Usuario.query.filter_by(Nombre_Usu=Nombre_Usu).first()
        if usuario and usuario.verificar_contraseña(Contraseña_hash):
            access_token = create_access_token(identity=usuario.Id_Usuario)
            return {"access_token": access_token}, 200
        return {"error": "Credenciales inválidas"}, 401
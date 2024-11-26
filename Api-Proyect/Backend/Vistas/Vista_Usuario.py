from flask_restful import Resource
from flask import request
from datetime import datetime
from flaskr.modelos.modeloDB import db, Usuario, UsuarioSchema
from ..modelos import db, Usuario
from sqlalchemy.exc import IntergrityError
from flask_jwt_extended import jwt_required, create_access_token

usuario_Schema = UsuarioSchema()

# Procedemos a crear la vista de usuario, es decir una clase que tendra los metodos
class VistaUsuario(Resource):
    def get(self):
        return [usuario_Schema.dump(Usuario) for Usuario in Usuario.query.all()]

    def post(self):
        fecha = request.json['Fecha_Contrato_Inicio']
        Fecha_Contrato_Inicio_r = datetime.strptime(fecha, "%Y-%m-%d").date()
        nuevo_usuario = Usuario(
                                Nombre_Usu = request.json['Nombre_Usu'],\
                                Contraseña_Usu = request.json['Contraseña_Usu'],\
                                Cedula_Usu = request.json['Cedula_Usu'],\
                                Email_Usu = request.json['Email_Usu'],\
                                Telefono_Usu = request.json['Telefono_Usu'],\
                                Fecha_Contrato_Inicio = Fecha_Contrato_Inicio_r,
                                rol = request.json['rol']
                                )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        return usuario_Schema.dump(nuevo_usuario), 201 #retorna la nueva cancion en formato json

    def put (self, Id_Usuario):
        usuario = Usuario.query.get_or_404(Id_Usuario)
        usuario.Nombre_Usu = request.json.get('Nombre_Usu', usuario.Nombre_Usu)
        usuario.Contraseña_Usu = request.json.get('Contraseña_Usu', usuario.Contraseña_Usu)
        usuario.Email_Usu = request.json.get('Email_Usu', usuario.Email_Usu)
        usuario.Telefono_Usu = request.json.get('Telefono_Usu', usuario.Telefono_Usu)
        if 'Fecha_Contrato_Inicio' in request.json:
            fecha = request.json['Fecha_Contrato_Inicio']
            usuario.Fecha_Contrato_Inicio = datetime.strptime(fecha, "%Y-%m-%d").date()
        usuario.Cedula_Usu = request.json.get('Cedula_Usu', usuario.Cedula_Usu)
        usuario.rol = request.json.get('rol', usuario.rol)

        db.session.commit()
        return usuario_Schema.dump(usuario)

    def delete(self, Id_Usuario):
        usuario = Usuario.query.get_or_404(Id_Usuario) # Obtenemos el usuario
        db.session.delete(usuario) # Se eleimina el usuario con el metodo delete
        db.session.commit() # se guardan los datos
        return 'Se elimino el usuario exitosamente!.',204 # Retornamos un valor
 



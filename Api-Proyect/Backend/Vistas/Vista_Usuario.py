from flask_restful import Resource
from flask import Flask, request
from flaskr.modelos.modeloDB import db, Usuario,UsuarioSchema
from ..modelos import db, Usuario
from sqlalchemy.exc import IntergrityError
from flask_jwt_extended import jwt_required, create_access_token

app = Flask(__name__)

# Instanciamos el esquema que vamos a utilizar
usuario_Schema = UsuarioSchema()

# Procedemos a crear la vista de usuario, es decir una clase que tendra los metodos
class VistaUsuario(Resource):
    def get(self):
        return [usuario_Schema.dump(Usuario) for Usuario in Usuario.query.all()]

    def post(self):
        nuevo_usuario = Usuario(
                                Nombre_Usu = request.json['Nombre_Usu'],\
                                Contraseña_Usu = request.json['Contraseña_Usu'],\
                                Email_Usu = request.json['Email_Usu'],\
                                Telefono_Usu = request.json['Telefono_Usu'],\
                                Fecha_Inicio_Contrato_Usu = request.json['Fecha_Inicio_Contrato_Usu'],\
                                Cedula_Usu = request.json['Cedula_Usu'],\
                                Id_Rol = request.json['Id_Rol']
                                )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        return usuario_Schema.dump(nuevo_usuario), 201 #retorna la nueva cancion en formato json

    def put (self, Id_Usuario):
        usuario = Usuario.query.get_or_404(Id_Usuario)
        usuario.Id_Usuario = request.json.get('Id_Usuario', usuario.Id_Usuario)
        usuario.Nombre_Usu = request.json.get('Nombre_Usu', usuario.Nombre_Usu)
        usuario.Contraseña_Usu = request.json.get('Contraseña_Usu', usuario.Contraseña_Usu)
        usuario.Email_Usu = request.json.get('Email_Usu', usuario.Email_Usu)
        usuario.Telefono_Usu = request.json.get('Telefono_Usu', usuario.Telefono_Usu)
        usuario.Fecha_Inicio_Contrato_Usu = request.json.get('Fecha_Inicio_Contrato_Usu', usuario.Fecha_Inicio_Contrato_Usu)
        usuario.Cedula_Usu = request.json.get('Cedula_Usu', usuario.Cedula_Usu)
        usuario.Id_Rol = request.json.get('Id_Rol', usuario.Id_Rol)

        db.session.commit()
        return usuario_Schema.dump(usuario)

    def delete(self, Id_Usuario):
        usuario = Usuario.query.get_or_404(Id_Usuario) # Obtenemos el usuario
        db.session.delete(usuario) # Se eleimina el usuario con el metodo delete
        db.session.commit() # se guardan los datos
        return 'Se elimino el usuario exitosamente!.',204 # Retornamos un valor
 
"""@app.route("/vistaUsuario")
def home():
    app.logger.info(f'Solicitud en la ruta {request.path}')
    return "<p> QUE PEDO </p>"
# USUARIOS 
# #CATEGORIAS
# GET - POST PUT 

# Falta: DELETE"""



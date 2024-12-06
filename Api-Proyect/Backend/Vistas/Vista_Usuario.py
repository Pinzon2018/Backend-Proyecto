from flask_restful import Resource
from flask import request
from datetime import datetime
from ..Modelos import db, Usuario, UsuarioSchema
from flask_jwt_extended import jwt_required, create_access_token
import cloudinary

usuario_Schema = UsuarioSchema()

# Procedemos a crear la vista de usuario, es decir una clase que tendra los metodos
class VistaUsuario(Resource):
    def get(self):
        return [usuario_Schema.dump(Usuario) for Usuario in Usuario.query.all()]

    def post(self):
        fecha = request.form['Fecha_Contrato_Inicio']
        Fecha_Contrato_Inicio_r = datetime.strptime(fecha, "%Y-%m-%d").date()
        imagen_usu = None
        if 'imagen_usu' in request.files:  
            archivo_imagen = request.files['imagen_usu']
            if archivo_imagen:
                try:
                    result = cloudinary.uploader.upload(archivo_imagen)
                    imagen_usu = result['secure_url'] 
                except Exception as e:
                    return {'error': 'Error al subir la imagen a Cloudinary', 'details': str(e)}, 400
        nuevo_usuario = Usuario(
            Nombre_Usu=request.form['Nombre_Usu'],
            Contraseña_hash=request.form['Contraseña_hash'],
            Cedula_Usu=request.form['Cedula_Usu'],
            Email_Usu=request.form['Email_Usu'],
            Telefono_Usu=request.form['Telefono_Usu'],
            Fecha_Contrato_Inicio=Fecha_Contrato_Inicio_r,
            rol=request.form['rol'],
            imagen_usu=imagen_usu  
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        return usuario_Schema.dump(nuevo_usuario), 201 #retorna la nueva cancion en formato json

    def put (self, Id_Usuario):
        usuario = Usuario.query.get_or_404(Id_Usuario)
        usuario.Nombre_Usu = request.json.get('Nombre_Usu', usuario.Nombre_Usu)
        usuario.Contraseña_hash = request.json.get('Contraseña_hash', usuario.Contraseña_hash)
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

class VistaLogIn(Resource):
    def post(self):
        Nombre_Usu = request.json['Nombre_Usu']
        Contraseña_hash = request.json['Contraseña_hash']
        usuario = Usuario.query.filter_by(nombre=Nombre_Usu).first()
        access_token = create_access_token(identity={"id": usuario.Id_Usuario, "rol": usuario.rol})
        if usuario and usuario.verificar_contraseña(Contraseña_hash):
            return {"access_token": access_token, "mensaje": "Inicio de sesión exitoso"}, 200
        else:
            return {'mensaje': 'Nombre de usuario o contraseña incorrectos'}, 401
        
        
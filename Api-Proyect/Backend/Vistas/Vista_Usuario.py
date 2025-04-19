from flask_restful import Resource
from flask import request
from datetime import datetime
from ..Modelos import db, Usuario, UsuarioSchema
from werkzeug.security import generate_password_hash
import cloudinary.uploader
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..Modelos import Rol

usuario_Schema = UsuarioSchema()

# Procedemos a crear la vista de usuario, es decir una clase que tendra los metodos
class VistaUsuario(Resource):
    @jwt_required()
    def get(self, Id_Usuario=None):
        current_user = get_jwt_identity()
        if Id_Usuario:
            usuario = Usuario.query.get_or_404(Id_Usuario)
            return usuario_Schema.dump(usuario)
        else:
            return [usuario_Schema.dump(u) for u in Usuario.query.all()]

    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        data = request.get_json()
        print("Datos recibidos:", data)

        try:
            fecha = data['Fecha_Contrato_Inicio']
            Fecha_Contrato_Inicio_r = datetime.strptime(fecha, "%Y-%m-%d").date()

            rol_id = int(data['Id_Rol'])
            rol_existente = Rol.query.get(rol_id)
            if not rol_existente:
                return {"error": "Rol no encontrado"}, 400

            hashed_password = generate_password_hash(data['Contraseña_hash'])

            nuevo_usuario = Usuario(
                Nombre_Usu=data['Nombre_Usu'],
                Contraseña_hash=hashed_password,
                Cedula_Usu=data['Cedula_Usu'],
                Email_Usu=data['Email_Usu'],
                Telefono_Usu=data['Telefono_Usu'],
                Fecha_Contrato_Inicio=Fecha_Contrato_Inicio_r,
                rol=rol_id
            )

            db.session.add(nuevo_usuario)
            db.session.commit()

            return usuario_Schema.dump(nuevo_usuario), 201

        except Exception as e:
            print("Error en POST /usuarios:", e)
            return {"error": "Error al registrar el usuario", "detalle": str(e)}, 500

    

    @jwt_required()
    def put (self, Id_Usuario):
        current_user = get_jwt_identity()
        usuario = Usuario.query.get_or_404(Id_Usuario)
        usuario.Nombre_Usu = request.json.get('Nombre_Usu', usuario.Nombre_Usu)
        nueva_contraseña = request.json.get('Contraseña_hash', None)
        if nueva_contraseña:
            usuario.Contraseña_hash = generate_password_hash(nueva_contraseña)
        usuario.Email_Usu = request.json.get('Email_Usu', usuario.Email_Usu)
        usuario.Telefono_Usu = request.json.get('Telefono_Usu', usuario.Telefono_Usu)
        if 'Fecha_Contrato_Inicio' in request.json:
            fecha = request.json['Fecha_Contrato_Inicio']
            usuario.Fecha_Contrato_Inicio = datetime.strptime(fecha, "%Y-%m-%d").date()
        usuario.Cedula_Usu = request.json.get('Cedula_Usu', usuario.Cedula_Usu)
        usuario.rol = request.json.get('rol', usuario.rol)

        db.session.commit()
        return usuario_Schema.dump(usuario)

    @jwt_required()
    def delete(self, Id_Usuario):
        current_user = get_jwt_identity()
        usuario = Usuario.query.get_or_404(Id_Usuario) # Obtenemos el usuario
        db.session.delete(usuario) # Se eleimina el usuario con el metodo delete
        db.session.commit() # se guardan los datos
        return 'Se elimino el usuario exitosamente!.',204 # Retornamos un valor
    

class VistaPerfil(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        usuario = Usuario.query.get_or_404(int(current_user_id))  # asegúrate que sea int
        return usuario_Schema.dump(usuario)

    

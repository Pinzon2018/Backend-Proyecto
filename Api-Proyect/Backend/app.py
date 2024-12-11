from Backend import create_app
from flask_migrate import Migrate
from .Modelos import db, Usuario, Rol
from flask_restful import Api
from .Vistas import VistaSubcategoria, VistaProveedor, VistaRol, VistaCategoria, VistaUsuario, VistaLogin, VistaProducto, VistaPerfil
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash
import datetime
from flask import request

app = create_app('default')
app_context = app.app_context()
app_context.push()
db.init_app(app)
db.create_all()

@app.before_request
def log_request_token():
    auth_header = request.headers.get("Authorization", "")
    print(f"Authorization header: {auth_header}")

CORS(app)

jwt = JWTManager(app)

api = Api(app)

api.add_resource(VistaProveedor, '/proveedores', '/proveedores/<int:Id_Proveedor>')
api.add_resource(VistaRol, '/roles')
api.add_resource(VistaSubcategoria, '/subcategorias', '/subcategorias/<int:Id_Subcategoria>')
api.add_resource(VistaUsuario, '/usuarios', '/usuarios/<int:Id_Usuario>')
api.add_resource(VistaCategoria, '/categorias', '/categorias/<int:Id_Categoria>')
api.add_resource(VistaLogin, '/login')
api.add_resource(VistaProducto, '/productos', '/productos/<int:Id_Producto>')
api.add_resource(VistaPerfil, '/perfil')

migrate = Migrate()
migrate.init_app(app, db)

with app.app_context():
    db.create_all()
    
    rol_superadmin = Rol.query.filter_by(Nombre='superadmin').first()
    
    if not rol_superadmin:
        rol_superadmin = Rol(Nombre='superadmin')
        db.session.add(rol_superadmin)
        db.session.commit()

    usuario_superadmin = Usuario.query.filter_by(Nombre_Usu='admin').first()
    
    if not usuario_superadmin:
        hashed_password = generate_password_hash('admin_password')  
        nuevo_usuario = Usuario(
            Nombre_Usu='admin',
            Contraseña_hash=hashed_password,
            Cedula_Usu='123456789',
            Email_Usu='admin@example.com',
            Telefono_Usu='123456789',
            Fecha_Contrato_Inicio=datetime.datetime.utcnow(),
            rol=rol_superadmin.Id_Rol  
        )
        db.session.add(nuevo_usuario)
        db.session.commit()

@jwt.expired_token_loader
def expired_token_callback():
    return {"message": "El token ha expirado. Por favor, inicie sesión nuevamente."}, 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {"message": "Token inválido. Por favor, inicie sesión nuevamente."}, 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return {"message": "Falta el token. Proporcione el token en la cabecera Authorization."}, 401
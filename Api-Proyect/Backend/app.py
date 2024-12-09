from Backend import create_app
from flask_migrate import Migrate
from .Modelos import db, Usuario, Rol
from flask_restful import Api
from .Vistas import VistaSubcategoria, VistaProveedor, VistaRol, VistaCategoria, VistaUsuario, VistaLogin
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash
import datetime

app = create_app('default')
app_context = app.app_context()
app_context.push()
db.init_app(app)
db.create_all()

CORS(app)

jwt = JWTManager(app)

api = Api(app)

api.add_resource(VistaProveedor, '/proveedores', '/proveedores/<int:Id_Proveedor>')
api.add_resource(VistaRol, '/roles')
api.add_resource(VistaSubcategoria, '/subcategorias', '/subcategorias/<int:Id_Subcategoria>')
api.add_resource(VistaUsuario, '/usuarios', '/usuarios/<int:Id_Usuario>')
api.add_resource(VistaCategoria, '/categorias', '/categorias/<int:Id_Categoria>')
api.add_resource(VistaLogin, '/login')


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
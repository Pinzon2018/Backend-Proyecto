from Backend import create_app
from flask_migrate import Migrate
from Backend.Modelos import db, Usuario, Rol
from flask_restful import Api
from Backend.Vistas import (
    VistaSubcategoria, 
    VistaProveedor, 
    VistaRol, 
    VistaCategoria, 
    VistaUsuario, 
    VistaLogin, 
    VistaProducto, 
    VistaPerfil, 
    VistaVenta,
    # 📊 APIS DE HISTORIAL
    VistaHistorialProductos,
    VistaHistorialVenta,
    VistaHistorialGeneral,
    VistaAuditoriaSistema
)
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash
import datetime
from flask import request
from flasgger import Swagger

# 🔥 IMPORTAR TRIGGERS
from Backend.Utils.triggers import init_triggers

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

# 📊 APIS EXISTENTES
api.add_resource(VistaProveedor, '/proveedores', '/proveedores/<int:Id_Proveedor>')
api.add_resource(VistaRol, '/roles')
api.add_resource(VistaSubcategoria, '/subcategorias', '/subcategorias/<int:Id_Subcategoria>')
api.add_resource(VistaUsuario, '/usuarios', '/usuarios/<int:Id_Usuario>')
api.add_resource(VistaCategoria, '/categorias', '/categorias/<int:Id_Categoria>')
api.add_resource(VistaLogin, '/login')
api.add_resource(VistaProducto, '/productos', '/productos/<int:Id_Producto>')
api.add_resource(VistaPerfil, '/perfil')
api.add_resource(VistaVenta, '/ventas', '/ventas/<int:Id_Venta>')

# 🔥 APIS DE HISTORIAL Y AUDITORÍA
api.add_resource(VistaHistorialProductos, 
    '/historial-productos', 
    '/historial-productos/<int:Id_Movimiento_Prod>'
)
api.add_resource(VistaHistorialVenta, 
    '/historial-ventas', 
    '/historial-ventas/<int:Id_Venta_HV>'
)
api.add_resource(VistaHistorialGeneral, 
    '/historial-general', 
    '/historial-general/<int:Id_Movimiento>'
)
api.add_resource(VistaAuditoriaSistema, 
    '/auditoria-sistema', 
    '/auditoria-sistema/<int:Id_Auditoria>'
)

migrate = Migrate()
migrate.init_app(app, db)

with app.app_context():
    db.create_all()
    
    rol_superadmin = Rol.query.filter_by(Nombre='superadmin').first()
    
    if not rol_superadmin:
        rol_superadmin = Rol(Nombre='superadmin')
        db.session.add(rol_superadmin)
    
    rol_admin = Rol.query.filter_by(Nombre='Administrador').first()
    if not rol_admin:
        rol_admin = Rol(Nombre='Administrador')
        db.session.add(rol_admin)

    rol_empleado = Rol.query.filter_by(Nombre='Empleado').first()
    if not rol_empleado:
        rol_empleado = Rol(Nombre='Empleado')
        db.session.add(rol_empleado)

    # ✅ Hacer commit aquí para que los roles tengan IDs
    db.session.commit()

    # Creacion del usuario
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
            FK_Rol=rol_superadmin.Id_Rol  
        )
        db.session.add(nuevo_usuario)
        db.session.commit()

    # 🔥 INICIALIZAR TRIGGERS DE AUDITORÍA
    init_triggers(app)

@jwt.expired_token_loader
def expired_token_callback():
    return {"message": "El token ha expirado. Por favor, inicie sesión nuevamente."}, 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {"message": "Token inválido. Por favor, inicie sesión nuevamente."}, 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return {"message": "Falta el token. Proporcione el token en la cabecera Authorization."}, 401

swagger = Swagger(app)

if __name__ == '__main__':
    app.run(debug=True, port=5001)

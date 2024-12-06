from Backend import create_app
from flask_migrate import Migrate
from .Modelos import db
from flask_restful import Api
from .Vistas import VistaSubcategoria, VistaProveedor, VistaRol, VistaCategoria, VistaUsuario, VistaLogIn
from flask_cors import CORS
from flask_jwt_extended import jwt_required, JWTManager

app = create_app('default')
app_context = app.app_context()
app_context.push()
db.init_app(app)
db.create_all()

CORS(app)

api = Api(app)

api.add_resource(VistaProveedor, '/proveedores', '/proveedores/<int:Id_Proveedor>')
api.add_resource(VistaRol, '/roles')
api.add_resource(VistaSubcategoria, '/subcategorias', '/subcategorias/<int:Id_Subcategoria>')
api.add_resource(VistaUsuario, '/usuarios', '/usuarios/<int:Id_Usuario>')
api.add_resource(VistaCategoria, '/categorias', '/categorias/<int:Id_Categoria>')
api.add_resource(VistaLogIn, '/login')


migrate = Migrate()
migrate.init_app(app, db)

jwt = JWTManager(app)
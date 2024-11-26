from Backend import create_app
from flask_migrate import Migrate
from .Modelos import db
from flask_restful import Api
from .Vistas import VistaProveedor, VistaRol

app = create_app('default')
app_context = app.app_context()
app_context.push()
db.init_app(app)
db.create_all()

api = Api(app)

api.add_resource(VistaProveedor, '/proveedores', '/proveedores/<int:Id_Proveedor>')

migrate = Migrate()
migrate.init_app(app, db)

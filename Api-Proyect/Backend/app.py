from Backend import create_app
from .Modelos import db
from flask_restful import Api
from .Vistas.vista_subcategoria import VistaSubcategoria

app = create_app('default')
app_context = app.app_context()
app_context.push()
db.init_app(app)
db.create_all()

api = Api(app)

api.add_resource(VistaSubcategoria, '/subcategorias')
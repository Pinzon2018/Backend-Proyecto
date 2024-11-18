from flask_restful import Resource
from flask import Flask, request
from flaskr.modelos.modeloDB import db, Categoria, CategoriaSchema
from ..modelos import db, Categoria

app = Flask(__name__)

# Instaciamos el esquema que vamos a utilizar
categoria_Schema = categoria_Schema()

# Procedemos a crear la vista de canciones, es decir una clase que tendra los metodos
class VistaCategoria(Resource):
    def get(self):
        return [categoria_Schema.dump(Categoria) for Usuario in Usuario.query.all()]
    
    def post(self):
        nueva_categoria = Categoria(
            Nombre_Cat = request.json['Nombre_Cat'],\
            Descripcion_Cat = request.json['Descripcion_Cat'],\
            subcategorias = request.json['subcategorias']
        )

        db.session.add(nueva_categoria)
        db.session.commit()
        return categoria_Schema.dump(nueva_categoria), 201 # Retorna la nueva cancion en formato json

    def put(self, Id_Categoria):
        categoria = Categoria.query.get_or_404(Id_Categoria)
        categoria.Id_Categoria = request.json.get('Id_Categoria', categoria.Id_Categoria)
        categoria.Nombre_Cat = request.json.get('Nombre_Cat', categoria.Nombre_Cat)
        categoria.Descripcion_Cat = request.json.get('Descripcion_Cat', categoria.Descripcion_Cat)
        categoria.subcategoria = request.json.get('subcategoria', categoria.subcategoria)

        db.session.commit()
        return categoria_Schema.dump(categoria)
    
    def delete(self, Id_Categoria):
        categoria = Categoria.query.get_or_404(Id_Categoria)
        db.session.delete(categoria)
        db.session.commit()
        return 'Se elimino la categoria con exito!.',204

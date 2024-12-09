from flask_restful import Resource
from flask import request
from ..Modelos import db, Categoria, CategoriaSchema
from flask_jwt_extended import jwt_required

categoria_Schema = CategoriaSchema()

# Procedemos a crear la vista de canciones, es decir una clase que tendra los metodos
class VistaCategoria(Resource):
    @jwt_required()
    def get(self):
        return [categoria_Schema.dump(Categoria) for Categoria in Categoria.query.all()]
    
    @jwt_required()
    def post(self):
        nueva_categoria = Categoria(
            Nombre_Cat = request.json['Nombre_Cat'],\
            Descripcion_Cat = request.json['Descripcion_Cat']
        )

        db.session.add(nueva_categoria)
        db.session.commit()
        return categoria_Schema.dump(nueva_categoria), 201 # Retorna la nueva cancion en formato json

    @jwt_required()
    def put(self, Id_Categoria):
        categoria = Categoria.query.get_or_404(Id_Categoria)
        categoria.Nombre_Cat = request.json.get('Nombre_Cat', categoria.Nombre_Cat)
        categoria.Descripcion_Cat = request.json.get('Descripcion_Cat', categoria.Descripcion_Cat)

        db.session.commit()
        return categoria_Schema.dump(categoria)

    @jwt_required()  
    def delete(self, Id_Categoria):
        categoria = Categoria.query.get_or_404(Id_Categoria)
        db.session.delete(categoria)
        db.session.commit()
        return 'Se elimino la categoria con exito!.',204

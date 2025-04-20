from flask_restful import Resource
from flask import request
from ..Modelos import db, Categoria, CategoriaSchema
from flask_jwt_extended import jwt_required, get_jwt_identity

categoria_Schema = CategoriaSchema()

class VistaCategoria(Resource):
    @jwt_required()
    def get(self, Id_Categoria=None):
        current_user = get_jwt_identity()
        if Id_Categoria:
            categoria = Categoria.query.get_or_404(Id_Categoria)
            return categoria_Schema.dump(categoria)
        else:
            return [categoria_Schema.dump(u) for u in Categoria.query.all()]
    
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        nueva_categoria = Categoria(
            Nombre_Cat = request.json['Nombre_Cat'],\
            Descripcion_Cat = request.json['Descripcion_Cat']
        )

        db.session.add(nueva_categoria)
        db.session.commit()
        return categoria_Schema.dump(nueva_categoria), 201 

    @jwt_required()
    def put (self, Id_Categoria):
        current_user = get_jwt_identity()
        categoria = Categoria.query.get_or_404(Id_Categoria)
        categoria.Nombre_Cat = request.json.get('Nombre_Cat', categoria.Nombre_Cat)
        categoria.Descripcion_Cat = request.json.get('Descripcion_Cat', categoria.Descripcion_Cat)
        db.session.commit()
        return categoria_Schema.dump(categoria)
    
    @jwt_required()  
    def delete(self, Id_Categoria):
        current_user = get_jwt_identity()
        categoria = Categoria.query.get_or_404(Id_Categoria)
        db.session.delete(categoria)
        db.session.commit()
        return 'Se elimino la categoria con exito!.',204

from flask_restful import Resource
from ..Modelos import db, Subcategoria, SubcategoriaSchema
from flask import request


Subcategoria_schema = SubcategoriaSchema()

class VistaSubcategoria(Resource):
    def get(self):
        return  [Subcategoria_schema.dump(Subcategoria) for Subcategoria in Subcategoria.query.all()]
    
    def post(self):
        insercion_subcategoria  = Subcategoria(Nombre_Subcategoria = request.json['Nombre_Subcategoria'],
                                               Descripcion_Subcategoria = request.json['Descripcion_Subcategoria'],
                                               categoria = request.json['categoria'])
        db.session.add(insercion_subcategoria)
        db.session.commit()
        return Subcategoria_schema.dump(insercion_subcategoria), 201
    
    def put (self, Id_Subcategoria):
        Subcategoria = Subcategoria.query.get_or_404(Id_Subcategoria)
        Subcategoria.Id_Subcategoria = request.json.get('Id_Subcategoria', Subcategoria.Id_Subcategoria)
        Subcategoria.Descripcion_Subcategoria = request.json.get('Descripcion_Subcategoria', Subcategoria.Descripcion_Subcategoria)
        Subcategoria.categoria = request.json.get('categoria', Subcategoria.categoria)
        db.session.commit()
        return Subcategoria_schema.dump(Subcategoria)
    
    def delete (self, Id_Subcategoria):
        Subcategoria = Subcategoria.query.get_or_404(Id_Subcategoria)
        db.session.delete(Subcategoria)
        db.session.commit()
        return 'Subcategoria eliminada correctamente', 204
    
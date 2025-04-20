from flask_restful import Resource
from ..Modelos import db, Subcategoria, SubcategoriaSchema
from ..Modelos import db, Categoria
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity


Subcategoria_schema = SubcategoriaSchema()

class VistaSubcategoria(Resource):
    @jwt_required()
    def get(self, Id_Subcategoria=None):
        current_user = get_jwt_identity()
        if Id_Subcategoria:
            subcategoria = Subcategoria.query.get_or_404(Id_Subcategoria)
            return Subcategoria_schema.dump(subcategoria)  
        else:
            return [Subcategoria_schema.dump(u) for u in Subcategoria.query.all()]  # Aquí también
    @jwt_required()    
    def post(self):
        current_user = get_jwt_identity()
        data = request.get_json()
        print("Datos recibidos:", data)

        try:

            categoria_id = int(data['Id_Categoria'])
            categoria_existente = Categoria.query.get(categoria_id)
            if not categoria_existente:
                return {"error": "Rol no encontrado"}, 400

            nueva_subcategoria = Subcategoria(
                Nombre_Subcategoria=data['Nombre_Subcategoria'],
                Descripcion_Subcategoria=data['Descripcion_Subcategoria'],
                categoria=categoria_id
            )

            db.session.add(nueva_subcategoria)
            db.session.commit()

            return Subcategoria_schema.dump(nueva_subcategoria), 201

        except Exception as e:
            print("Error en POST /usuarios:", e)
            return {"error": "Error al registrar el usuario", "detalle": str(e)}, 500
    
    @jwt_required()
    def put(self, Id_Subcategoria):
        current_user = get_jwt_identity()
        subcategoria = Subcategoria.query.get_or_404(Id_Subcategoria)
    
        data = request.get_json()
    
        subcategoria.Nombre_Subcategoria = data.get('Nombre_Subcategoria', subcategoria.Nombre_Subcategoria)
        subcategoria.Descripcion_Subcategoria = data.get('Descripcion_Subcategoria', subcategoria.Descripcion_Subcategoria)
        subcategoria.categoria = data.get('Id_Categoria', subcategoria.categoria)
    
        db.session.commit()
        return Subcategoria_schema.dump(subcategoria), 200
    
    @jwt_required()
    def delete (self, Id_Subcategoria):
        current_user = get_jwt_identity()
        Subcategoria = Subcategoria.query.get_or_404(Id_Subcategoria)
        db.session.delete(Subcategoria)
        db.session.commit()
        return 'Subcategoria eliminada correctamente', 204
    
from flask_restful import Resource
from ..Modelos import db, Subcategoria, SubcategoriaSchema
from ..Modelos import db, Categoria
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity


Subcategoria_schema = SubcategoriaSchema()

class VistaSubcategoria(Resource):
    @jwt_required()
    def get(self, Id_Subcategoria=None):
        """
        Obtener subcategorías o una subcategoría específica
        ---
        tags:
          - Subcategorías
        security:
          - Bearer: []
        parameters:
          - name: Id_Subcategoria
            in: path
            required: false
            type: integer
            description: ID de la subcategoría a consultar (opcional)
        responses:
          200:
            description: Lista o detalle de subcategorías
            schema:
              type: object
              properties:
                Id_Subcategoria:
                  type: integer
                Nombre_Subcategoria:
                  type: string
                Descripcion_Subcategoria:
                  type: string
                Id_Categoria:
                  type: integer
        """
        current_user = get_jwt_identity()
        if Id_Subcategoria:
            subcategoria = Subcategoria.query.get_or_404(Id_Subcategoria)
            return Subcategoria_schema.dump(subcategoria)  
        else:
            return [Subcategoria_schema.dump(u) for u in Subcategoria.query.all()]  # Aquí también
    @jwt_required()    
    def post(self):
        """
        Crear una nueva subcategoría
        ---
        tags:
          - Subcategorías
        security:
          - Bearer: []
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required:
                - Nombre_Subcategoria
                - Descripcion_Subcategoria
                - Id_Categoria
              properties:
                Nombre_Subcategoria:
                  type: string
                  example: Zapatos deportivos
                Descripcion_Subcategoria:
                  type: string
                  example: Calzado especializado para actividades físicas
                Id_Categoria:
                  type: integer
                  example: 2
        responses:
          201:
            description: Subcategoría creada exitosamente
            schema:
              $ref: '#/definitions/Subcategoria'
          400:
            description: Categoría no encontrada
          500:
            description: Error al registrar la subcategoría
        """
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
        """
        Actualizar una subcategoría existente
        ---
        tags:
          - Subcategorías
        security:
          - Bearer: []
        parameters:
          - name: Id_Subcategoria
            in: path
            required: true
            type: integer
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                Nombre_Subcategoria:
                  type: string
                  example: Botas impermeables
                Descripcion_Subcategoria:
                  type: string
                  example: Botas para climas lluviosos
                Id_Categoria:
                  type: integer
                  example: 3
        responses:
          200:
            description: Subcategoría actualizada correctamente
        """
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
        """
        Eliminar una subcategoría
        ---
        tags:
          - Subcategorías
        security:
          - Bearer: []
        parameters:
          - name: Id_Subcategoria
            in: path
            required: true
            type: integer
        responses:
          204:
            description: Subcategoría eliminada correctamente
        """
        current_user = get_jwt_identity()
        Subcategoria = Subcategoria.query.get_or_404(Id_Subcategoria)
        db.session.delete(Subcategoria)
        db.session.commit()
        return 'Subcategoria eliminada correctamente', 204
    
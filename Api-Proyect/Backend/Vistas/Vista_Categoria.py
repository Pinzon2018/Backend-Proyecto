from flask_restful import Resource
from flask import request
from ..Modelos import db, Categoria, CategoriaSchema
from flask_jwt_extended import jwt_required, get_jwt_identity

categoria_Schema = CategoriaSchema()

class VistaCategoria(Resource):
    @jwt_required()
    def get(self, Id_Categoria=None):
        """
        Obtener uno o todas las categorias
        ---
        tags:
            - Categorias
        security:
            - Bearer: []
        parameters:
            - name: Id_Categoria
              in: path
              required: false
              type: integer
              description: Id de la Categoria a consultar (opcional)
        responses:
            200:
                description: Categoria(s) obtenidos exitosamente
        """
        current_user = get_jwt_identity()
        if Id_Categoria:
            categoria = Categoria.query.get_or_404(Id_Categoria)
            return categoria_Schema.dump(categoria)
        else:
            return [categoria_Schema.dump(u) for u in Categoria.query.all()]
    
    @jwt_required()
    def post(self):
        """
        Crear uns Categoria
        ---
        tags:
          - Categorias
        security:
          - Bearer: []
        parameters:
          - in: body
            name: categoria
            required: true
            schema:
              type: object
              required:
                - Nombre_Cat
                - Descripcion_Cat
              properties:
                Nombre_Cat:
                  type: string
                Descripcion_Cat:
                  type: string
        responses:
          201:
            description: Categoria creada exitosamente
          500:
            description: Error del servidor
        """
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
        """
        Actulizar datos de una Categoria
        ---
        tags:
          - Categorias
        security:
          - Bearer: []
        parameters:
          - name: Id_Categoria
            in: path
            required: true
            type: integer
          - in: body
            name: categorias
            schema: 
              type: object
              properties:
                Nombre_Cat:
                  type: string
                Descripcion_Cat:
                  type: string
        responses:
            200:
              description: Categoria actualizada correctamente
        """
        current_user = get_jwt_identity()
        categoria = Categoria.query.get_or_404(Id_Categoria)
        categoria.Nombre_Cat = request.json.get('Nombre_Cat', categoria.Nombre_Cat)
        categoria.Descripcion_Cat = request.json.get('Descripcion_Cat', categoria.Descripcion_Cat)
        db.session.commit()
        return categoria_Schema.dump(categoria)
    
    @jwt_required()  
    def delete(self, Id_Categoria):
        """
        Eliminar Categoria
        ---
        tags:
          - Categorias
        security:
          - Bearer: []
        parameters:
          - name: Id_Categoria
            in: path
            required: true
            type: integer
        responses:
            204:
              description: Categoria eliminada correctamente
        """
        current_user = get_jwt_identity()
        categoria = Categoria.query.get_or_404(Id_Categoria)
        db.session.delete(categoria)
        db.session.commit()
        return 'Se elimino la categoria con exito!.',204

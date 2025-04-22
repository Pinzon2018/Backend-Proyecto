from flask_restful import Resource
from flask import request
from ..Modelos import db, Producto, ProductoSchema
from flask_jwt_extended import jwt_required, get_jwt_identity

producto_schema = ProductoSchema()

class VistaProducto(Resource):
    @jwt_required()
    def get(self, Id_Producto=None):
        """
        Obtener todos los productos o un producto específico
        ---
        tags:
          - Productos
        security:
          - Bearer: []
        parameters:
          - name: Id_Producto
            in: path
            type: integer
            required: false
            description: ID del producto a obtener (opcional)
        responses:
          200:
            description: Lista de productos o producto específico
        """
        current_user = get_jwt_identity()
        if Id_Producto:
            producto = Producto.query.get_or_404(Id_Producto)
            return producto_schema.dump(producto)
        else:
            return [producto_schema.dump(u) for u in Producto.query.all()]

    @jwt_required()
    def post(self):
        """
        Crear un nuevo producto
        ---
        tags:
          - Productos
        security:
          - Bearer: []
        parameters:
          - in: body
            name: producto
            required: true
            schema:
              type: object
              required:
                - Nombre_Prod
                - Medida_Prod
                - Unidad_Medida_Prod
                - Precio_Neto_Unidad_Prod
                - Iva_Prod
                - Porcentaje_Ganancia
                - Unidades_Totales_Prod
                - Estado_Prod
                - Marca_Prod
                - FK_Id_Proveedor
                - FK_Id_Subcategoria
              properties:
                Nombre_Prod:
                  type: string
                Medida_Prod:
                  type: number
                Unidad_Medida_Prod:
                  type: string
                Precio_Neto_Unidad_Prod:
                  type: number
                Iva_Prod:
                  type: number
                Porcentaje_Ganancia:
                  type: number
                Unidades_Totales_Prod:
                  type: integer
                Estado_Prod:
                  type: string
                Marca_Prod:
                  type: string
                FK_Id_Proveedor:
                  type: integer
                FK_Id_Subcategoria:
                  type: integer
        responses:
          201:
            description: Producto creado exitosamente
        """
        current_user = get_jwt_identity()
    
        precio_neto = float(request.json['Precio_Neto_Unidad_Prod'])
        iva = float(request.json['Iva_Prod'])
        precio_bruto = precio_neto + iva
    
        nuevo_producto = Producto(
            Nombre_Prod = request.json['Nombre_Prod'],
            Medida_Prod = request.json['Medida_Prod'],
            Unidad_Medida_Prod = request.json['Unidad_Medida_Prod'],
            Precio_Bruto_Prod = precio_bruto,
            Precio_Neto_Unidad_Prod = precio_neto,
            Iva_Prod = iva,
            Porcentaje_Ganancia = request.json['Porcentaje_Ganancia'],
            Unidades_Totales_Prod = request.json['Unidades_Totales_Prod'],
            Estado_Prod = request.json['Estado_Prod'],
            Marca_Prod = request.json['Marca_Prod'],
            FK_Id_Proveedor = request.json['FK_Id_Proveedor'],
            FK_Id_Subcategoria = request.json['FK_Id_Subcategoria']
        )
    
        db.session.add(nuevo_producto)
        db.session.commit()
        return producto_schema.dump(nuevo_producto)
    
    @jwt_required()
    def put(self, Id_Producto):
        """
        Actualizar un producto
        ---
        tags:
          - Productos
        security:
          - Bearer: []
        parameters:
          - name: Id_Producto
            in: path
            required: true
            type: integer
            description: ID del producto a actualizar
          - in: body
            name: producto
            schema:
              type: object
              properties:
                Nombre_Prod:
                  type: string
                Medida_Prod:
                  type: number
                Unidad_Medida_Prod:
                  type: string
                Precio_Bruto_Prod:
                  type: number
                Precio_Neto_Unidad_Prod:
                  type: number
                Iva_Prod:
                  type: number
                Porcentaje_Ganancia:
                  type: number
                Unidades_Totales_Prod:
                  type: integer
                Estado_Prod:
                  type: string
                Marca_Prod:
                  type: string
                FK_Id_Proveedor:
                  type: integer
                FK_Id_Subcategoria:
                  type: integer
        responses:
          202:
            description: Producto actualizado correctamente
          404:
            description: Producto no encontrado
        """
        current_user = get_jwt_identity()
        producto = Producto.query.get(Id_Producto)
        if not producto:
            return 'Producto no encontrado', 404

        producto.Nombre_Prod = request.json.get('Nombre_Prod', producto.Nombre_Prod)
        producto.Medida_Prod = request.json.get('Medida_Prod', producto.Medida_Prod)
        producto.Unidad_Medida_Prod = request.json.get('Unidad_Medida_Prod', producto.Unidad_Medida_Prod)
        producto.Precio_Bruto_Prod = request.json.get('Precio_Bruto_Prod', producto.Precio_Bruto_Prod)
        producto.Precio_Neto_Unidad_Prod = request.json.get('Precio_Neto_Unidad_Prod', producto.Precio_Neto_Unidad_Prod)
        producto.Iva_Prod = request.json.get('Iva_Prod', producto.Iva_Prod)
        producto.Porcentaje_Ganancia = request.json.get('Porcentaje_Ganancia', producto.Porcentaje_Ganancia)
        producto.Unidades_Totales_Prod = request.json.get('Unidades_Totales_Prod', producto.Unidades_Totales_Prod)
        producto.Estado_Prod = request.json.get('Estado_Prod', producto.Estado_Prod)
        producto.Marca_Prod = request.json.get('Marca_Prod', producto.Marca_Prod)
        producto.FK_Id_Proveedor = request.json.get('FK_Id_Proveedor', producto.FK_Id_Proveedor)
        producto.FK_Id_Subcategoria = request.json.get('FK_Id_Subcategoria', producto.FK_Id_Subcategoria)

        db.session.commit()
        return producto_schema.dump(producto), 202

    @jwt_required()
    def delete(self, Id_Producto):
        """
        Eliminar un producto
        ---
        tags:
          - Productos
        security:
          - Bearer: []
        parameters:
          - name: Id_Producto
            in: path
            required: true
            type: integer
            description: ID del producto a eliminar
        responses:
          204:
            description: Producto eliminado exitosamente
          404:
            description: Producto no encontrado
        """
        current_user = get_jwt_identity()
        producto = Producto.query.get(Id_Producto)
        if not producto:
            return 'producto no encontrado', 404
        
        db.session.delete(producto)
        db.session.commit()
        return 'Producto eliminado', 204
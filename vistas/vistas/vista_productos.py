from flask_restful import Resource
from flask import request, jsonify
from ..modelos import db, Producto, ProductoSchema

producto_schema = ProductoSchema()

class VistaProducto(Resource):
    def get(self): 
        return [producto_schema.dump(Producto) for Producto in Producto.query.all()]

    def post(self):
        nuevo_producto = Producto(Nombre_Prod = request.json['Nombre_Prod'],
                                  Medida_Prod = request.json['Medida_Prod'],
                                  Unidad_Medida_Prod = request.json['Unidad_Medida_Prod'],
                                  Precio_Bruto_Prod = request.json['Precio_Bruto_Prod'],
                                  Precio_Neto_Unidad_Prod = request.json['Precio_Neto_Unidad_Prod'],
                                  Iva_Prod = request.json['Iva_Prod'],
                                  Porcentaje_Ganancia = request.json['Porcentaje_Ganancia'],
                                  Unidades_Totales_Prod = request.json['Unidades_Totales_Prod'],
                                  Estado_Prod = request.json['Estado_Prod'],
                                  Marca_Prod = request.json['Marca_Prod'],
                                  FK_Id_Proveedor = request.json['FK_Id_Proveedor'],
                                  FK_Id_Subcategoria = request.json['FK_Id_Subcategoria'])
        db.session.add(nuevo_producto)
        db.session.commit()
        return producto_schema.dump(nuevo_producto)
    
    def put(self, Id_Producto):
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

    def delete(self, Id_Producto):
        producto = Producto.query.get(Id_Producto)
        if not producto:
            return 'producto no encontrado', 404
        
        db.session.delete(producto)
        db.session.commit()
        return 'Producto eliminado', 204
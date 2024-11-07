from flask_restful import Resource
from flask import request, jsonify
from ..modelos import db, Producto, ProductoSchema

ProductoSchema = ProductoSchema()

class Vista_Producto(Resource):
    def get(self):
        return [ProductoSchema.dump(Producto) for Producto in Producto.query.all()] 
    
    def post(self):
        try:
            agregar_producto = Producto(id_Producto = request.json["id_Producto"],\
                                   Nombre_Prod = request.json["Nombre_Prod"],\
                                   Medida_Prod = request.json["Medida_Prod"],\
                                   Unidad_Medida_Prod =request.json["Unidad_Medida_Prod"],\
                                   Precio_Bruto_Prod = request.json["Precio_Bruto_Prod"],\
                                   Iva_Prod= request.json["Iva_Prod"],\
                                   Porcentaje_Ganancia_Prod = request.json["Porcentaje_Ganancia_Prod"],\
                                   Precio_Neto_Unidad_Prod = request.json["Precio_Neto_Unidad_Prod"],\
                                   Unidades_Totales_Prod = request.json["Unidades_Totales_Prod"],\
                                   Marca_Prod = request.json["Marca_Prod"],\
                                   Estado_Prod = request.json["Estado_Prod"],\
                                   id_Proveedor = request.json["id_Proveedor"],\
                                   id_Subcategoria = request.json["id_Subcategoria"],\
                                       )
                                    
                                
                                
            
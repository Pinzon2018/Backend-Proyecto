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
                                   id_Subcategoria = request.json["id_Subcategoria"])
            db.session.add(agregar_producto)
            db.session.commit
            
            return jsonify({
               'id_Producto': agregar_producto.id,
               'Nombre_Prod': agregar_producto.Nombre_Prod,
               'Medida_Prod': agregar_producto.Medida_Prod,
               'Unidad_Medida_Prod': agregar_producto.Unidad_Medida_Prod,
               'Precio_Bruto_Prod': agregar_producto.Precio_Bruto_Prod,
               'Iva_Prod': agregar_producto.Iva_Prod,
               'Porcentaje_Ganancia_Prod': agregar_producto.Porcentaje_Ganancia_Prod,
               'Precio_Neto_Unidad_Prod': agregar_producto.Precio_Neto_Unidad_Prod,
               'Unidades_Totales_Prod': agregar_producto.Unidades_Totales_Prod,
               'Marca_Prod': agregar_producto.Marca_Prod,
               'Estado_Prod': agregar_producto.Estado_Prod,
               'id_Proveedor': agregar_producto.id_Proveedor,
               'id_Subcategoria': agregar_producto.id_Subcategoria
            }), 201
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error al crear el producto: {str(e)}'}), 500
        
    def put(self,id_Producto):
        Producto = Producto.query.get(id_Producto)
        if not Producto:
            return jsonify({'message': 'Producto no encontrado'}), 404
        
        if not Producto:
            return jsonify({'messaje': 'No se han enviado datos'}), 400
        
        try:
            db.session.commit()
            return jsonify({
                'id_Producto': Producto.id_Producto,
                'Nombre_Prod': Producto.Nombre_Prod,
                'Medida_Prod': Producto.Medida_Prod,
                'Unidad_Medida_Prod': Producto.Unidad_Medida_Prod,
                'Precio_Bruto_Prod': Producto.Precio_Bruto_Prod,
                'Iva_Prod': Producto.Iva_Prod,
                'Porcentaje_Ganancia_Prod': Producto.Porcentaje_Ganancia_Prod,
                'Precio_Neto_Unidad_Prod': Producto.Precio_Neto_Unidad_Prod,
                'Unidades_Totales_Prod': Producto.Unidades_Totales_Prod,
                'Marca_Prod': Producto.Marca_Prod,
                'Estado_Prod': Producto.Estado_Prod,
                'id_Proveedor': Producto.id_Proveedor,
                'id_Subcategoria': Producto.id.Subcategoria
            }), 200
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error al actualizar el producto: {str(e)}'})
        
    def delete(self,id_producto):
        
        Producto= Producto.query.get(id_producto)
        if not Producto:
            return jsonify({'message': 'No se encontro el producto'}), 400
        
        try:
            db.session.delete(Producto)
            db.session.commit()
            return jsonify({'message': f'El producto ha sido eliminado'}), 200
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'Error al eliminar el producto:{str(e)}'})
                    
        
            
                                    
                                
                                
            
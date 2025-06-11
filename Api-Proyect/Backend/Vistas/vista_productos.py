from flask_restful import Resource
from flask import request, g
from ..Modelos import db, Producto, ProductoSchema, Usuario
from flask_jwt_extended import jwt_required, get_jwt_identity
from decimal import Decimal
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging

# Configurar logging
logger = logging.getLogger(__name__)

producto_schema = ProductoSchema()

class VistaProducto(Resource):
    
    def _set_user_context(self):
        """Establecer contexto de usuario para los triggers"""
        try:
            current_user_id = get_jwt_identity()
            if current_user_id:
                usuario = Usuario.query.get(current_user_id)
                g.current_user_id = current_user_id
                # ✅ CORREGIDO: Usar el nombre correcto del campo
                g.current_user_rol = getattr(usuario, 'FK_Id_Rol', None) or getattr(usuario, 'Id_Rol', None) or 1
                return current_user_id, g.current_user_rol
            g.current_user_id = 1
            g.current_user_rol = 1
            return 1, 1
        except Exception as e:
            logger.warning(f"Error estableciendo contexto de usuario: {e}")
            g.current_user_id = 1
            g.current_user_rol = 1
            return 1, 1

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
            description: ID del producto específico (opcional)
        responses:
          200:
            description: Lista de productos o producto específico
          404:
            description: Producto no encontrado
          401:
            description: Token inválido
        """
        try:
            logger.info(f"GET /productos llamado con Id_Producto: {Id_Producto}")
            current_user_id, _ = self._set_user_context()
            
            if Id_Producto:
                producto = Producto.query.get_or_404(Id_Producto)
                return producto_schema.dump(producto), 200
            else:
                # Solo productos activos por defecto
                productos = Producto.query.filter_by(Estado_Prod=True).all()
                logger.info(f"Productos encontrados: {len(productos)}")
                return [producto_schema.dump(p) for p in productos], 200
                
        except Exception as e:
            logger.error(f"Error al obtener productos: {str(e)}")
            return {'error': 'Error interno del servidor'}, 500

    @jwt_required()
    def post(self):
        """Crear un nuevo producto con cálculo automático de precio neto"""
        current_user_id, current_user_rol = self._set_user_context()
        logger.info(f"Usuario {current_user_id} creando producto")

        try:
            # Validación de datos requeridos
            if not request.json:
                return {'error': 'No se proporcionaron datos'}, 400

            required_fields = ['Nombre_Prod', 'Precio_Bruto_Prod']
            for field in required_fields:
                if field not in request.json or request.json[field] in [None, '', 0]:
                    return {'error': f'Campo {field} es requerido'}, 400

            # ✅ Validación y conversión de tipos
            try:
                precio_bruto = float(request.json.get('Precio_Bruto_Prod'))
                if precio_bruto <= 0:
                    return {'error': 'El precio bruto debe ser mayor a cero'}, 400
                    
                # IVA y Ganancia son opcionales, usar valores por defecto de Colombia
                iva = float(request.json.get('Iva_Prod', 0.19))  # 19% IVA Colombia
                ganancia = float(request.json.get('Porcentaje_Ganancia', 0.30))  # 30% ganancia por defecto
                
                # Validar que sean porcentajes decimales (0-1) no porcentajes (0-100)
                if iva > 1:
                    iva = iva / 100  # Convertir 19 a 0.19
                if ganancia > 1:
                    ganancia = ganancia / 100  # Convertir 30 a 0.30
                    
                unidades = int(request.json.get('Unidades_Totales_Prod', 0))
                
                if iva < 0 or ganancia < 0 or unidades < 0:
                    return {'error': 'Los valores no pueden ser negativos'}, 400
                    
            except (TypeError, ValueError) as e:
                return {'error': f'Error en tipos de datos: {str(e)}'}, 400

            # ✅ Verificar duplicados
            producto_existente = Producto.query.filter_by(Nombre_Prod=request.json['Nombre_Prod']).first()
            if producto_existente:
                return {'error': f'Ya existe un producto con el nombre "{request.json["Nombre_Prod"]}"'}, 409

            # ✅ Crear nuevo producto
            nuevo_producto = Producto(
                Nombre_Prod=request.json['Nombre_Prod'].strip(),
                Medida_Prod=str(request.json.get('Medida_Prod', '')).strip(),
                Unidad_Medida_Prod=request.json.get('Unidad_Medida_Prod', 'UNIDAD').strip(),
                Precio_Bruto_Prod=precio_bruto,
                Iva_Prod=iva,
                Porcentaje_Ganancia=ganancia,
                Unidades_Totales_Prod=unidades,
                Estado_Prod=True,
                Marca_Prod=request.json.get('Marca_Prod', '').strip(),
                FK_Id_Proveedor=request.json.get('FK_Id_Proveedor') if request.json.get('FK_Id_Proveedor') != '' else None,
                FK_Id_Subcategoria=request.json.get('FK_Id_Subcategoria') if request.json.get('FK_Id_Subcategoria') != '' else None
            )

            # ✅ Calcular precio neto automáticamente ANTES de guardar
            nuevo_producto.calcular_precio_neto()
            
            logger.info(f"Precio calculado - Bruto: ${precio_bruto:,.2f}, IVA: {iva*100}%, Ganancia: {ganancia*100}%, Neto: ${nuevo_producto.Precio_Neto_Unidad_Prod:,.2f}")

           # ✅ AÑADIR el producto a la sesión Y hacer commit inmediatamente
            db.session.add(nuevo_producto)
            db.session.commit()
            
            # Refrescar el objeto para obtener el ID generado
            db.session.refresh(nuevo_producto)
            logger.info(f"✅ Producto '{nuevo_producto.Nombre_Prod}' creado exitosamente con ID: {nuevo_producto.Id_Producto}")
            
            return {
                'message': 'Producto creado exitosamente',
                'producto': producto_schema.dump(nuevo_producto),
                'precio_calculado': {
                    'precio_bruto': float(nuevo_producto.Precio_Bruto_Prod),
                    'iva_porcentaje': f"{iva*100}%",
                    'ganancia_porcentaje': f"{ganancia*100}%",
                    'precio_neto': float(nuevo_producto.Precio_Neto_Unidad_Prod)
                }
            }, 201
            
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Error de integridad al crear producto: {str(e)}")
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if 'foreign key' in error_msg.lower():
                return {'error': 'Error: Proveedor o Subcategoría no válidos'}, 400
            return {'error': 'Error de integridad de datos'}, 400
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error de base de datos al crear producto: {str(e)}")
            return {'error': f'Error de base de datos: {str(e)}'}, 500
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error inesperado al crear producto: {str(e)}")
            return {'error': f'Error interno del servidor: {str(e)}'}, 500
    
    @jwt_required()
    def put(self, Id_Producto):
        """
        Actualizar un producto - Los triggers detectan cambios automáticamente
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
        responses:
          200:
            description: Producto actualizado exitosamente
          404:
            description: Producto no encontrado
          400:
            description: Error en los datos
        """
        current_user_id, current_user_rol = self._set_user_context()
        logger.info(f"Usuario {current_user_id} actualizando producto {Id_Producto}")
        
        try:
            producto = Producto.query.get(Id_Producto)
            if not producto:
                return {'error': 'Producto no encontrado'}, 404

            if not request.json:
                return {'error': 'No se proporcionaron datos para actualizar'}, 400

            # Validar campos numéricos si están presentes
            try:
                if 'Precio_Bruto_Prod' in request.json and request.json['Precio_Bruto_Prod'] not in (None, ''):
                    precio_bruto = float(request.json['Precio_Bruto_Prod'])
                    if precio_bruto < 0:
                        return {'error': 'El precio bruto no puede ser negativo'}, 400
                    producto.Precio_Bruto_Prod = precio_bruto

                if 'Iva_Prod' in request.json and request.json['Iva_Prod'] not in (None, ''):
                    iva = float(request.json['Iva_Prod'])
                    if iva < 0:
                        return {'error': 'El IVA no puede ser negativo'}, 400
                    producto.Iva_Prod = iva

                if 'Porcentaje_Ganancia' in request.json and request.json['Porcentaje_Ganancia'] not in (None, ''):
                    ganancia = float(request.json['Porcentaje_Ganancia'])
                    if ganancia < 0:
                        return {'error': 'El porcentaje de ganancia no puede ser negativo'}, 400
                    producto.Porcentaje_Ganancia = ganancia

                if 'Unidades_Totales_Prod' in request.json and request.json['Unidades_Totales_Prod'] not in (None, ''):
                    unidades = int(request.json['Unidades_Totales_Prod'])
                    if unidades < 0:
                        return {'error': 'Las unidades no pueden ser negativas'}, 400
                    producto.Unidades_Totales_Prod = unidades

            except (ValueError, TypeError):
                return {'error': 'Los campos numéricos deben tener valores válidos'}, 400

            # Actualizar otros campos
            if 'Nombre_Prod' in request.json:
                nuevo_nombre = request.json['Nombre_Prod']
                if nuevo_nombre and nuevo_nombre != producto.Nombre_Prod:
                    # Verificar que no existe otro producto con ese nombre
                    producto_existente = Producto.query.filter(
                        Producto.Nombre_Prod == nuevo_nombre,
                        Producto.Id_Producto != Id_Producto
                    ).first()
                    if producto_existente:
                        return {'error': f'Ya existe otro producto con el nombre "{nuevo_nombre}"'}, 409
                    producto.Nombre_Prod = nuevo_nombre

            # Actualizar campos opcionales
            campos_opcionales = ['Medida_Prod', 'Unidad_Medida_Prod', 'Estado_Prod', 'Marca_Prod', 'FK_Id_Proveedor', 'FK_Id_Subcategoria']
            for campo in campos_opcionales:
                if campo in request.json:
                    setattr(producto, campo, request.json[campo])

            # Recalcular precio neto si cambiaron los componentes
            if any(campo in request.json for campo in ['Precio_Bruto_Prod', 'Iva_Prod', 'Porcentaje_Ganancia']):
                producto.Precio_Neto_Unidad_Prod = round(
                    Decimal(producto.Precio_Bruto_Prod) * (1 + Decimal(producto.Iva_Prod) + Decimal(producto.Porcentaje_Ganancia)),
                    2
                )

            # ✅ LOS TRIGGERS SE EJECUTAN AUTOMÁTICAMENTE AL HACER commit()
            db.session.commit()
            
            logger.info(f"Producto '{producto.Nombre_Prod}' actualizado exitosamente")
            
            return {
                'message': 'Producto actualizado exitosamente',
                'producto': producto_schema.dump(producto)
            }, 200
            
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Error de integridad al actualizar producto: {str(e)}")
            return {'error': 'Error de integridad de datos'}, 400
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error de base de datos al actualizar producto: {str(e)}")
            return {'error': 'Error de base de datos'}, 500
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error inesperado al actualizar producto: {str(e)}")
            return {'error': 'Error interno del servidor'}, 500

    @jwt_required()
    def delete(self, Id_Producto):
        """
        Eliminar un producto - Los triggers se ejecutan automáticamente
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
          400:
            description: No se puede eliminar el producto
        """
        current_user_id, current_user_rol = self._set_user_context()
        logger.info(f"Usuario {current_user_id} eliminando producto {Id_Producto}")
        
        try:
            producto = Producto.query.get(Id_Producto)
            if not producto:
                return {'error': 'Producto no encontrado'}, 404
            
            # Verificar si el producto tiene ventas asociadas (opcional - dependiendo de tu lógica de negocio)
            # Podrías hacer un soft delete en lugar de hard delete
            
            producto_nombre = producto.Nombre_Prod
            producto_unidades = producto.Unidades_Totales_Prod
            
            logger.info(f"Eliminando producto: '{producto_nombre}' con {producto_unidades} unidades")
            
            # ✅ LOS TRIGGERS SE EJECUTAN AUTOMÁTICAMENTE AL HACER delete() y commit()
            db.session.delete(producto)
            db.session.commit()
            
            logger.info(f"Producto '{producto_nombre}' eliminado exitosamente")
            
            return {'message': f'Producto "{producto_nombre}" eliminado exitosamente'}, 204
            
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Error de integridad al eliminar producto: {str(e)}")
            return {'error': 'No se puede eliminar el producto porque tiene registros relacionados'}, 400
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error de base de datos al eliminar producto: {str(e)}")
            return {'error': 'Error de base de datos'}, 500
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error inesperado al eliminar producto: {str(e)}")
            return {'error': 'Error interno del servidor'}, 500


# ✅ CLASE ADICIONAL PARA GESTIÓN DE INVENTARIO
class VistaInventarioProducto(Resource):
    
    def _set_user_context(self):
        """Establecer contexto de usuario para los triggers"""
        try:
            current_user_id = get_jwt_identity()
            if current_user_id:
                usuario = Usuario.query.get(current_user_id)
                g.current_user_id = current_user_id
                g.current_user_rol = usuario.FK_Id_Rol if usuario else 1
                return current_user_id, usuario.FK_Id_Rol if usuario else 1
            return 1, 1
        except Exception as e:
            logger.warning(f"Error estableciendo contexto de usuario: {e}")
            return 1, 1

    @jwt_required()
    def get(self, Id_Producto):
        """
        Obtener información de inventario de un producto específico
        ---
        tags:
          - Inventario
        security:
          - Bearer: []
        parameters:
          - name: Id_Producto
            in: path
            required: true
            type: integer
            description: ID del producto
        responses:
          200:
            description: Información del inventario del producto
          404:
            description: Producto no encontrado
        """
        try:
            current_user_id, _ = self._set_user_context()
            
            producto = Producto.query.get_or_404(Id_Producto)
            
            return {
                'producto_id': producto.Id_Producto,
                'producto_nombre': producto.Nombre_Prod,
                'stock_actual': producto.Unidades_Totales_Prod,
                'precio_unitario': float(producto.Precio_Neto_Unidad_Prod or 0),
                'valor_inventario': float((producto.Precio_Neto_Unidad_Prod or 0) * (producto.Unidades_Totales_Prod or 0)),
                'estado': producto.Estado_Prod,
                'unidad_medida': producto.Unidad_Medida_Prod,
                'marca': producto.Marca_Prod,
                'alerta_stock_bajo': (producto.Unidades_Totales_Prod or 0) <= 5
            }, 200
            
        except Exception as e:
            logger.error(f"Error al obtener inventario del producto {Id_Producto}: {str(e)}")
            return {'error': 'Error interno del servidor'}, 500

    @jwt_required()
    def put(self, Id_Producto):
        """
        Ajustar inventario de un producto específico (establecer cantidad exacta)
        ---
        tags:
          - Inventario
        security:
          - Bearer: []
        parameters:
          - name: Id_Producto
            in: path
            required: true
            type: integer
            description: ID del producto
          - in: body
            name: ajuste
            required: true
            schema:
              type: object
              required:
                - cantidad
              properties:
                cantidad:
                  type: integer
                  description: Nueva cantidad exacta de inventario
                motivo:
                  type: string
                  description: Motivo del ajuste
        responses:
          200:
            description: Inventario ajustado exitosamente
          400:
            description: Error en los datos
          404:
            description: Producto no encontrado
        """
        current_user_id, current_user_rol = self._set_user_context()
        
        try:
            if not request.json:
                return {'error': 'No se proporcionaron datos'}, 400
                
            if 'cantidad' not in request.json:
                return {'error': 'Campo "cantidad" requerido'}, 400
                
            producto = Producto.query.get_or_404(Id_Producto)
            
            try:
                nueva_cantidad = int(request.json['cantidad'])
            except (ValueError, TypeError):
                return {'error': 'La cantidad debe ser un número entero'}, 400
            
            if nueva_cantidad < 0:
                return {'error': 'La cantidad no puede ser negativa'}, 400
            
            cantidad_anterior = producto.Unidades_Totales_Prod or 0
            motivo = request.json.get('motivo', 'Ajuste de inventario manual')
            
            # Actualizar cantidad
            producto.Unidades_Totales_Prod = nueva_cantidad
            
            # ✅ EL TRIGGER DE UPDATE SE EJECUTARÁ AUTOMÁTICAMENTE
            db.session.commit()
            
            diferencia = nueva_cantidad - cantidad_anterior
            
            logger.info(f"Ajuste de inventario - Producto {Id_Producto}: {cantidad_anterior} → {nueva_cantidad} ({diferencia:+d})")
            
            return {
                'message': f'Inventario ajustado exitosamente',
                'producto': {
                    'id': producto.Id_Producto,
                    'nombre': producto.Nombre_Prod,
                    'stock_anterior': cantidad_anterior,
                    'stock_nuevo': nueva_cantidad,
                    'diferencia': diferencia,
                    'motivo': motivo
                },
                'inventario': producto_schema.dump(producto)
            }, 200
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error de base de datos al ajustar inventario: {str(e)}")
            return {'error': 'Error de base de datos'}, 500
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error inesperado al ajustar inventario: {str(e)}")
            return {'error': 'Error interno del servidor'}, 500

    @jwt_required()
    def post(self, Id_Producto):
        """
        Agregar o quitar stock de un producto (operación relativa)
        ---
        tags:
          - Inventario
        security:
          - Bearer: []
        parameters:
          - name: Id_Producto
            in: path
            required: true
            type: integer
            description: ID del producto
          - in: body
            name: movimiento
            required: true
            schema:
              type: object
              required:
                - operacion
                - cantidad
              properties:
                operacion:
                  type: string
                  enum: ['AGREGAR', 'QUITAR']
                  description: Tipo de operación
                cantidad:
                  type: integer
                  description: Cantidad a agregar o quitar
                motivo:
                  type: string
                  description: Motivo del movimiento
        responses:
          200:
            description: Stock actualizado exitosamente
          400:
            description: Error en los datos o stock insuficiente
          404:
            description: Producto no encontrado
        """
        current_user_id, current_user_rol = self._set_user_context()
        
        try:
            if not request.json:
                return {'error': 'No se proporcionaron datos'}, 400
            
            if 'operacion' not in request.json or 'cantidad' not in request.json:
                return {'error': 'Campos "operacion" y "cantidad" son requeridos'}, 400
                
            operacion = request.json['operacion'].upper()
            motivo = request.json.get('motivo', f'Movimiento de inventario: {operacion.lower()}')
            
            if operacion not in ['AGREGAR', 'QUITAR']:
                return {'error': 'Operación debe ser "AGREGAR" o "QUITAR"'}, 400
            
            try:
                cantidad = int(request.json['cantidad'])
            except (ValueError, TypeError):
                return {'error': 'La cantidad debe ser un número entero'}, 400
                
            if cantidad <= 0:
                return {'error': 'La cantidad debe ser mayor a cero'}, 400
                
            producto = Producto.query.get_or_404(Id_Producto)
            stock_actual = producto.Unidades_Totales_Prod or 0
            
            if operacion == 'AGREGAR':
                nuevo_stock = stock_actual + cantidad
                tipo_movimiento = 'ENTRADA'
            else:  # QUITAR
                if stock_actual < cantidad:
                    return {
                        'error': f'Stock insuficiente. Stock actual: {stock_actual}, Cantidad solicitada: {cantidad}'
                    }, 400
                nuevo_stock = stock_actual - cantidad
                tipo_movimiento = 'SALIDA'
            
            # Actualizar stock
            producto.Unidades_Totales_Prod = nuevo_stock
            
            # ✅ EL TRIGGER DE UPDATE SE EJECUTARÁ AUTOMÁTICAMENTE
            db.session.commit()
            
            logger.info(f"Movimiento de inventario - Producto {Id_Producto}: {operacion} {cantidad} unidades ({stock_actual} → {nuevo_stock})")
            
            # Alerta de stock bajo
            alerta_stock_bajo = nuevo_stock <= 5
            if alerta_stock_bajo and operacion == 'QUITAR':
                logger.warning(f"ALERTA: Stock bajo para producto {producto.Nombre_Prod}: {nuevo_stock} unidades")
            
            return {
                'message': f'Stock {operacion.lower()} exitosamente',
                'operacion': {
                    'tipo': operacion,
                    'cantidad': cantidad,
                    'motivo': motivo,
                    'stock_anterior': stock_actual,
                    'stock_nuevo': nuevo_stock,
                    'diferencia': nuevo_stock - stock_actual
                },
                'producto': {
                    'id': producto.Id_Producto,
                    'nombre': producto.Nombre_Prod,
                    'stock_actual': nuevo_stock,
                    'alerta_stock_bajo': alerta_stock_bajo
                },
                'alerta': 'Stock bajo detectado' if alerta_stock_bajo else None
            }, 200
            
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error de base de datos en movimiento de inventario: {str(e)}")
            return {'error': 'Error de base de datos'}, 500
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error inesperado en movimiento de inventario: {str(e)}")
            return {'error': 'Error interno del servidor'}, 500


# ✅ CLASE PARA CONSULTAS DE INVENTARIO
class VistaInventarioGeneral(Resource):
    
    @jwt_required()
    def get(self):
        """
        Obtener resumen general del inventario
        ---
        tags:
          - Inventario
        security:
          - Bearer: []
        responses:
          200:
            description: Resumen del inventario
        """
        try:
            # Obtener estadísticas generales
            productos = Producto.query.filter_by(Estado_Prod=True).all()
            
            total_productos = len(productos)
            productos_con_stock = len([p for p in productos if (p.Unidades_Totales_Prod or 0) > 0])
            productos_sin_stock = len([p for p in productos if (p.Unidades_Totales_Prod or 0) == 0])
            productos_stock_bajo = len([p for p in productos if 0 < (p.Unidades_Totales_Prod or 0) <= 5])
            
            valor_total_inventario = sum([
                (p.Precio_Neto_Unidad_Prod or 0) * (p.Unidades_Totales_Prod or 0) 
                for p in productos
            ])
            
            # Top 5 productos con mayor stock
            productos_mayor_stock = sorted(
                productos, 
                key=lambda x: x.Unidades_Totales_Prod or 0, 
                reverse=True
            )[:5]
            
            # Productos con stock bajo
            productos_stock_bajo_lista = [
                p for p in productos 
                if 0 < (p.Unidades_Totales_Prod or 0) <= 5
            ]
            
            return {
                'resumen': {
                    'total_productos': total_productos,
                    'productos_con_stock': productos_con_stock,
                    'productos_sin_stock': productos_sin_stock,
                    'productos_stock_bajo': productos_stock_bajo,
                    'valor_total_inventario': round(valor_total_inventario, 2)
                },
                'productos_mayor_stock': [
                    {
                        'id': p.Id_Producto,
                        'nombre': p.Nombre_Prod,
                        'stock': p.Unidades_Totales_Prod or 0,
                        'valor': round((p.Precio_Neto_Unidad_Prod or 0) * (p.Unidades_Totales_Prod or 0), 2)
                    } for p in productos_mayor_stock
                ],
                'alertas_stock_bajo': [
                    {
                        'id': p.Id_Producto,
                        'nombre': p.Nombre_Prod,
                        'stock': p.Unidades_Totales_Prod or 0,
                        'precio_unitario': float(p.Precio_Neto_Unidad_Prod or 0)
                    } for p in productos_stock_bajo_lista
                ]
            }, 200
            
        except Exception as e:
            logger.error(f"Error al obtener resumen de inventario: {str(e)}")
            return {'error': 'Error interno del servidor'}, 500
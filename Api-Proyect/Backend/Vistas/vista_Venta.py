from flask_restful import Resource
from ..Modelos import db, Venta, VentaSchema, Producto, Detalle_Venta, Usuario, Rol
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from datetime import datetime
import logging

# Configurar logging
logger = logging.getLogger(__name__)

Venta_schema = VentaSchema(many=True)
venta_individual_schema = VentaSchema()

class VistaVenta(Resource):
    @jwt_required()
    def get(self, Id_Venta=None):
        """
        Obtener ventas
        ---
        tags:
          - Ventas
        security:
          - Bearer: []
        parameters:
          - name: Id_Venta
            in: path
            type: integer
            required: false
            description: ID de la venta específica (opcional)
        responses:
          200:
            description: Lista de ventas o venta específica
          404:
            description: Venta no encontrada
          401:
            description: Token inválido
        """
        try:
            current_user = get_jwt_identity()
            
            if Id_Venta:
                venta = Venta.query.get(Id_Venta)
                if not venta:
                    return {'error': 'Venta no encontrada'}, 404
                return venta_individual_schema.dump(venta), 200
            
            ventas = Venta.query.all()
            return Venta_schema.dump(ventas), 200
            
        except Exception as e:
            logger.error(f"Error al obtener ventas: {str(e)}")
            return {'error': 'Error interno del servidor'}, 500

    @jwt_required()
    def post(self):
        """
        Crear nueva venta
        ---
        tags:
          - Ventas
        security:
          - Bearer: []
        parameters:
          - in: body
            name: venta
            required: true
            schema:
              type: object
              required:
                - detalle_Venta
              properties:
                detalle_Venta:
                  type: array
                  items:
                    type: object
                    properties:
                      FK_Id_Producto:
                        type: integer
                      Cantidad:
                        type: integer
                Forma_Pago_Fact:
                  type: string
        responses:
          201:
            description: Venta creada exitosamente
          400:
            description: Error en la venta (stock insuficiente, datos inválidos)
          404:
            description: Usuario o producto no encontrado
          500:
            description: Error interno del servidor
        """
        try:
            # Validaciones iniciales
            if not request.json:
                return {'error': 'No se proporcionaron datos'}, 400
            
            detalle_Venta = request.json.get('detalle_Venta', [])
            if not detalle_Venta or len(detalle_Venta) == 0:
                return {'error': 'Debe incluir al menos un producto en la venta'}, 400
            
            forma_pago = request.json.get('Forma_Pago_Fact', 'EFECTIVO')
            if forma_pago not in ['EFECTIVO', 'TARJETA', 'TRANSFERENCIA']:
                return {'error': 'Forma de pago inválida. Use: EFECTIVO, TARJETA o TRANSFERENCIA'}, 400
            
            total = 0
            usuario_id = get_jwt_identity()
            
            # Validar usuario
            usuario = Usuario.query.get(usuario_id)
            if not usuario:
                return {'error': 'Usuario no encontrado'}, 404
            
            # Validar que el usuario tenga permisos para crear ventas
            if not self._validar_permisos_venta(usuario):
                return {'error': 'Usuario sin permisos para realizar ventas'}, 403

            # Validar disponibilidad de stock ANTES de crear la venta
            productos_validados = []
            
            for item in detalle_Venta:
                # Validar estructura del item
                if not isinstance(item, dict) or 'FK_Id_Producto' not in item or 'Cantidad' not in item:
                    return {'error': 'Estructura de detalle de venta inválida'}, 400
                
                try:
                    producto_id = int(item['FK_Id_Producto'])
                    cantidad = int(item['Cantidad'])
                except (ValueError, TypeError):
                    return {'error': 'ID de producto y cantidad deben ser números enteros'}, 400
                
                if cantidad <= 0:
                    return {'error': 'La cantidad debe ser mayor a cero'}, 400
                
                # Obtener producto
                producto = Producto.query.get(producto_id)
                if not producto:
                    return {'error': f"Producto con ID {producto_id} no encontrado"}, 404
                
                # Validar estado del producto
                if producto.Estado_Prod != 'ACTIVO':
                    return {'error': f"El producto {producto.Nombre_Prod} no está disponible para venta"}, 400
                
                # Validar stock disponible
                if producto.Unidades_Totales_Prod is None:
                    return {'error': f"Stock no definido para {producto.Nombre_Prod}"}, 400
                    
                if producto.Unidades_Totales_Prod < cantidad:
                    return {
                        'error': f"Stock insuficiente para {producto.Nombre_Prod}. "
                                f"Disponible: {producto.Unidades_Totales_Prod}, Solicitado: {cantidad}"
                    }, 400
                
                # Validar precio del producto
                if not producto.Precio_Neto_Unidad_Prod or producto.Precio_Neto_Unidad_Prod <= 0:
                    return {'error': f"Precio inválido para {producto.Nombre_Prod}"}, 400
                
                subtotal = float(producto.Precio_Neto_Unidad_Prod) * cantidad
                productos_validados.append({
                    'producto': producto,
                    'cantidad': cantidad,
                    'subtotal': subtotal
                })
                total += subtotal

            # Validar total mínimo de venta
            if total <= 0:
                return {'error': 'El total de la venta debe ser mayor a cero'}, 400

            # Iniciar transacción
            try:
                # Crear la venta
                nueva_venta = Venta(
                    FK_Id_Usuario=usuario.Id_Usuario,
                    Total_Venta=round(total, 2),
                    Forma_Pago_Fact=forma_pago
                )
                db.session.add(nueva_venta)
                db.session.flush()  # Para obtener el ID sin hacer commit

                # Procesar cada producto y crear detalles
                detalles_creados = []
                for item in productos_validados:
                    producto = item['producto']
                    cantidad = item['cantidad']
                    
                    # Actualizar stock
                    stock_anterior = producto.Unidades_Totales_Prod
                    producto.Unidades_Totales_Prod -= cantidad
                    
                    # Crear detalle de venta
                    detalle = Detalle_Venta(
                        FK_Id_Venta=nueva_venta.Id_Venta,
                        FK_Id_Producto=producto.Id_Producto,
                        Cantidad=cantidad,
                        precio_unitario=producto.Precio_Neto_Unidad_Prod
                    )
                    db.session.add(detalle)
                    detalles_creados.append({
                        'producto_id': producto.Id_Producto,
                        'producto_nombre': producto.Nombre_Prod,
                        'cantidad': cantidad,
                        'precio_unitario': float(producto.Precio_Neto_Unidad_Prod),
                        'subtotal': item['subtotal'],
                        'stock_anterior': stock_anterior,
                        'stock_nuevo': producto.Unidades_Totales_Prod
                    })

                # Confirmar transacción
                db.session.commit()
                
                # Log de la operación exitosa
                logger.info(f"Venta creada exitosamente - ID: {nueva_venta.Id_Venta}, "
                           f"Usuario: {usuario_id}, Total: ${total:,.2f}")
                
                # Los triggers se ejecutarán automáticamente aquí
                
                return {
                    'message': 'Venta creada exitosamente',
                    'venta': {
                        'id': nueva_venta.Id_Venta,
                        'total': f"${total:,.2f}",
                        'forma_pago': forma_pago,
                        'fecha': nueva_venta.Fecha_Venta.isoformat() if hasattr(nueva_venta, 'Fecha_Venta') else None,
                        'usuario_id': usuario.Id_Usuario,
                        'detalles': detalles_creados
                    }
                }, 201
                
            except IntegrityError as e:
                db.session.rollback()
                logger.error(f"Error de integridad al crear venta: {str(e)}")
                return {'error': 'Error de integridad de datos. Verifique las relaciones.'}, 400
                
            except SQLAlchemyError as e:
                db.session.rollback()
                logger.error(f"Error de base de datos al crear venta: {str(e)}")
                return {'error': 'Error de base de datos'}, 500
        
        except ValueError as e:
            logger.warning(f"Error de validación en venta: {str(e)}")
            return {'error': str(e)}, 400
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error inesperado al crear venta: {str(e)}")
            return {'error': 'Error interno del servidor'}, 500
    
    @jwt_required()
    def put(self, Id_Venta):
        """
        Actualizar una venta (limitado a forma de pago)
        ---
        tags:
          - Ventas
        security:
          - Bearer: []
        parameters:
          - name: Id_Venta
            in: path
            required: true
            type: integer
            description: ID de la venta a actualizar
          - in: body
            name: venta
            schema:
              type: object
              properties:
                Forma_Pago_Fact:
                  type: string
        responses:
          200:
            description: Venta actualizada exitosamente
          404:
            description: Venta no encontrada
          403:
            description: Sin permisos para actualizar
        """
        try:
            current_user = get_jwt_identity()
            venta = Venta.query.get(Id_Venta)
            
            if not venta:
                return {'error': 'Venta no encontrada'}, 404
            
            # Validar permisos (solo el usuario que creó la venta o admin)
            usuario = Usuario.query.get(current_user)
            if not usuario:
                return {'error': 'Usuario no encontrado'}, 404
                
            if venta.FK_Id_Usuario != current_user and not self._es_admin(usuario):
                return {'error': 'Sin permisos para actualizar esta venta'}, 403
            
            # Solo permitir actualizar forma de pago
            forma_pago = request.json.get('Forma_Pago_Fact')
            if forma_pago and forma_pago in ['EFECTIVO', 'TARJETA', 'TRANSFERENCIA']:
                venta.Forma_Pago_Fact = forma_pago
                db.session.commit()
                
                logger.info(f"Venta {Id_Venta} actualizada por usuario {current_user}")
                return venta_individual_schema.dump(venta), 200
            else:
                return {'error': 'Forma de pago inválida'}, 400
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al actualizar venta {Id_Venta}: {str(e)}")
            return {'error': 'Error interno del servidor'}, 500

    @jwt_required()
    def delete(self, Id_Venta):
        """
        Eliminar una venta (solo administradores)
        ---
        tags:
          - Ventas
        security:
          - Bearer: []
        parameters:
          - name: Id_Venta
            in: path
            required: true
            type: integer
            description: ID de la venta a eliminar
        responses:
          204:
            description: Venta eliminada exitosamente
          404:
            description: Venta no encontrada
          403:
            description: Sin permisos para eliminar
        """
        try:
            current_user = get_jwt_identity()
            usuario = Usuario.query.get(current_user)
            
            if not usuario:
                return {'error': 'Usuario no encontrado'}, 404
            
            # Solo administradores pueden eliminar ventas
            if not self._es_admin(usuario):
                return {'error': 'Solo administradores pueden eliminar ventas'}, 403
            
            venta = Venta.query.get(Id_Venta)
            if not venta:
                return {'error': 'Venta no encontrada'}, 404
            
            try:
                # Restaurar stock de productos antes de eliminar
                for detalle in venta.detalle_Venta_Venta:
                    producto = detalle.producto
                    if producto:
                        producto.Unidades_Totales_Prod += detalle.Cantidad
                        logger.info(f"Stock restaurado para producto {producto.Id_Producto}: +{detalle.Cantidad}")
                
                db.session.delete(venta)
                db.session.commit()
                
                logger.warning(f"Venta {Id_Venta} eliminada por administrador {current_user}")
                
                return {'message': 'Venta eliminada exitosamente'}, 204
                
            except SQLAlchemyError as e:
                db.session.rollback()
                logger.error(f"Error al eliminar venta {Id_Venta}: {str(e)}")
                return {'error': 'Error de base de datos al eliminar venta'}, 500
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error inesperado al eliminar venta {Id_Venta}: {str(e)}")
            return {'error': 'Error interno del servidor'}, 500

    def _validar_permisos_venta(self, usuario):
        """Validar si el usuario tiene permisos para realizar ventas"""
        try:
            # Verificar si el usuario está activo
            if not hasattr(usuario, 'estado') or usuario.estado != 'ACTIVO':
                return False
            
            # Verificar rol (asumiendo que existe relación con roles)
            if hasattr(usuario, 'rol') and usuario.rol:
                roles_permitidos = ['ADMIN', 'VENDEDOR', 'CAJERO']
                return usuario.rol.nombre in roles_permitidos
            
            return True  # Por defecto permitir si no hay restricciones de rol
            
        except Exception:
            return False

    def _es_admin(self, usuario):
        """Verificar si el usuario es administrador"""
        try:
            if hasattr(usuario, 'rol') and usuario.rol:
                return usuario.rol.nombre == 'ADMIN'
            return False
        except Exception:
            return False
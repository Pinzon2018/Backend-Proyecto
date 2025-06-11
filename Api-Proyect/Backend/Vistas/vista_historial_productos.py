from flask_restful import Resource
from flask import request
from ..Modelos import db, Historial_Productos, HistorialProductosSchema, Producto, Usuario, Rol
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import pytz

historial_productos_schema = HistorialProductosSchema()
colombia_tz = pytz.timezone('America/Bogota')

class VistaHistorialProductos(Resource):
    @jwt_required()
    def get(self, Id_Movimiento_Prod=None):
        """
        Obtener historial de movimientos de productos
        ---
        tags:
          - Historial Productos
        security:
          - Bearer: []
        parameters:
          - name: Id_Movimiento_Prod
            in: path
            type: integer
            required: false
            description: ID del movimiento específico (opcional)
          - name: fecha_inicio
            in: query
            type: string
            format: date
            description: Fecha inicio para filtrar (YYYY-MM-DD)
          - name: fecha_fin
            in: query
            type: string
            format: date
            description: Fecha fin para filtrar (YYYY-MM-DD)
          - name: producto_id
            in: query
            type: integer
            description: ID del producto para filtrar
          - name: tipo_movimiento
            in: query
            type: string
            description: Tipo de movimiento (ENTRADA, SALIDA, MODIFICACION, ELIMINACION)
          - name: usuario_id
            in: query
            type: integer
            description: ID del usuario para filtrar
        responses:
          200:
            description: Historial de productos obtenido exitosamente
        """
        current_user = get_jwt_identity()
        
        if Id_Movimiento_Prod:
            movimiento = Historial_Productos.query.get_or_404(Id_Movimiento_Prod)
            return historial_productos_schema.dump(movimiento)
        
        query = Historial_Productos.query
        
        # Filtros opcionales
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        producto_id = request.args.get('producto_id')
        tipo_movimiento = request.args.get('tipo_movimiento')
        usuario_id = request.args.get('usuario_id')
        
        if fecha_inicio:
            query = query.filter(Historial_Productos.Fecha_Movimiento_Prod >= fecha_inicio)
        if fecha_fin:
            query = query.filter(Historial_Productos.Fecha_Movimiento_Prod <= fecha_fin)
        if producto_id:
            query = query.filter(Historial_Productos.FK_Id_Producto_HP == producto_id)
        if tipo_movimiento:
            query = query.filter(Historial_Productos.Tipo_Movimiento == tipo_movimiento)
        if usuario_id:
            query = query.filter(Historial_Productos.FK_Id_Usuario_HP == usuario_id)
            
        movimientos = query.order_by(Historial_Productos.Fecha_Movimiento_Prod.desc()).all()
        return [historial_productos_schema.dump(m) for m in movimientos]

    @jwt_required()
    def post(self):
        """
        Crear registro en historial de productos (Usado por triggers internos)
        ---
        tags:
          - Historial Productos
        security:
          - Bearer: []
        parameters:
          - in: body
            name: historial_producto
            required: true
            schema:
              type: object
              required:
                - FK_Id_Producto_HP
                - FK_Id_Usuario_HP
                - FK_Id_Rol_HP
                - Tipo_Movimiento
                - Cantidad_Prod
                - Descripcion_Movimiento
              properties:
                FK_Id_Producto_HP:
                  type: integer
                FK_Id_Usuario_HP:
                  type: integer
                FK_Id_Rol_HP:
                  type: integer
                Producto:
                  type: string
                Tipo_Movimiento:
                  type: string
                  enum: [ENTRADA, SALIDA, MODIFICACION, ELIMINACION]
                Cantidad_Prod:
                  type: integer
                Descripcion_Movimiento:
                  type: string
                Estados:
                  type: boolean
        responses:
          201:
            description: Registro de historial creado exitosamente
        """
        current_user = get_jwt_identity()
        
        # Verificaciones
        producto = Producto.query.get_or_404(request.json['FK_Id_Producto_HP'])
        usuario = Usuario.query.get_or_404(request.json['FK_Id_Usuario_HP'])
        rol = Rol.query.get_or_404(request.json['FK_Id_Rol_HP'])
        
        nuevo_movimiento = Historial_Productos(
            Fecha_Movimiento_Prod=datetime.now(colombia_tz),
            FK_Id_Rol_HP=request.json['FK_Id_Rol_HP'],
            FK_Id_Usuario_HP=request.json['FK_Id_Usuario_HP'],
            FK_Id_Producto_HP=request.json['FK_Id_Producto_HP'],
            Producto=request.json.get('Producto', producto.Nombre_Prod),
            Tipo_Movimiento=request.json['Tipo_Movimiento'],
            Cantidad_Prod=request.json['Cantidad_Prod'],
            Descripcion_Movimiento=request.json['Descripcion_Movimiento'],
            Estados=request.json.get('Estados', True)
        )
        
        db.session.add(nuevo_movimiento)
        db.session.commit()
        return historial_productos_schema.dump(nuevo_movimiento), 201

# Funciones auxiliares para crear historial de productos
def crear_historial_producto(producto_id, usuario_id, rol_id, tipo_movimiento, cantidad, descripcion, producto_nombre=None):
    """
    Función auxiliar para crear registro en historial de productos
    """
    try:
        if not producto_nombre:
            producto = Producto.query.get(producto_id)
            producto_nombre = producto.Nombre_Prod if producto else "Producto Desconocido"
            
        nuevo_movimiento = Historial_Productos(
            Fecha_Movimiento_Prod=datetime.now(colombia_tz),
            FK_Id_Rol_HP=rol_id,
            FK_Id_Usuario_HP=usuario_id,
            FK_Id_Producto_HP=producto_id,
            Producto=producto_nombre,
            Tipo_Movimiento=tipo_movimiento,
            Cantidad_Prod=cantidad,
            Descripcion_Movimiento=descripcion,
            Estados=True
        )
        db.session.add(nuevo_movimiento)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error al crear historial de producto: {e}")
        return False

def registrar_entrada_producto(producto_id, cantidad, usuario_id, rol_id, descripcion="Entrada de producto"):
    """Registrar entrada de producto al inventario"""
    return crear_historial_producto(
        producto_id, usuario_id, rol_id, 
        "ENTRADA", cantidad, descripcion
    )

def registrar_salida_producto(producto_id, cantidad, usuario_id, rol_id, descripcion="Salida de producto por venta"):
    """Registrar salida de producto del inventario"""
    return crear_historial_producto(
        producto_id, usuario_id, rol_id, 
        "SALIDA", cantidad, descripcion
    )

def registrar_modificacion_producto(producto_id, usuario_id, rol_id, descripcion="Modificación de producto"):
    """Registrar modificación de producto"""
    return crear_historial_producto(
        producto_id, usuario_id, rol_id, 
        "MODIFICACION", 0, descripcion
    )

def registrar_eliminacion_producto(producto_id, usuario_id, rol_id, descripcion="Eliminación de producto"):
    """Registrar eliminación de producto"""
    return crear_historial_producto(
        producto_id, usuario_id, rol_id, 
        "ELIMINACION", 0, descripcion
    )
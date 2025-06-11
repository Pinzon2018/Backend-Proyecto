from flask_restful import Resource
from flask import request
from ..Modelos import db, Historial_General, HistorialGeneralSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

historial_general_schema = HistorialGeneralSchema(many=True)
historial_general_individual_schema = HistorialGeneralSchema()

class VistaHistorialGeneral(Resource):
    @jwt_required()
    def get(self, Id_Movimiento=None):
        """
        Obtener historial general de movimientos del sistema
        ---
        tags:
          - Historial General
        security:
          - Bearer: []
        parameters:
          - name: Id_Movimiento
            in: path
            type: integer
            required: false
            description: ID del movimiento específico (opcional)
          - name: fecha_inicio
            in: query
            type: string
            format: date
            description: Fecha de inicio para filtrar (YYYY-MM-DD)
          - name: fecha_fin
            in: query
            type: string
            format: date
            description: Fecha de fin para filtrar (YYYY-MM-DD)
          - name: tipo_movimiento
            in: query
            type: string
            description: Tipo de movimiento para filtrar
          - name: usuario_id
            in: query
            type: integer
            description: ID del usuario para filtrar
          - name: limit
            in: query
            type: integer
            description: Límite de registros (por defecto 100)
          - name: page
            in: query
            type: integer
            description: Página para paginación (por defecto 1)
        responses:
          200:
            description: Lista de historial general
        """
        current_user = get_jwt_identity()
        
        if Id_Movimiento:
            movimiento = Historial_General.query.get_or_404(Id_Movimiento)
            return historial_general_individual_schema.dump(movimiento)
        
        # Consulta base
        query = Historial_General.query
        
        # Filtros opcionales
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        tipo_movimiento = request.args.get('tipo_movimiento')
        usuario_id = request.args.get('usuario_id')
        
        if fecha_inicio:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            query = query.filter(Historial_General.Fecha_Movimiento >= fecha_inicio_dt)
            
        if fecha_fin:
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
            query = query.filter(Historial_General.Fecha_Movimiento <= fecha_fin_dt)
            
        if tipo_movimiento:
            query = query.filter(Historial_General.Tipo_Movimiento.ilike(f'%{tipo_movimiento}%'))
            
        if usuario_id:
            query = query.filter(Historial_General.FK_Id_Usuario_HG == usuario_id)
        
        # Paginación
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 100))
        
        # Ordenar por fecha descendente y aplicar paginación
        movimientos = query.order_by(Historial_General.Fecha_Movimiento.desc()).paginate(
            page=page, 
            per_page=limit, 
            error_out=False
        )
        
        return {
            'data': historial_general_schema.dump(movimientos.items),
            'pagination': {
                'page': page,
                'pages': movimientos.pages,
                'per_page': limit,
                'total': movimientos.total,
                'has_next': movimientos.has_next,
                'has_prev': movimientos.has_prev
            }
        }

    @jwt_required()
    def post(self):
        """
        Crear registro manual en historial general (casos especiales)
        ---
        tags:
          - Historial General
        security:
          - Bearer: []
        parameters:
          - in: body
            name: historial_general
            required: true
            schema:
              type: object
              required:
                - Tipo_Movimiento
                - Descripcion_Movimiento
              properties:
                FK_Id_Rol_HG:
                  type: integer
                FK_Id_Usuario_HG:
                  type: integer
                FK_Id_Movimiento_Producto:
                  type: integer
                FK_Id_Movimiento_Venta:
                  type: integer
                Tipo_Movimiento:
                  type: string
                Descripcion_Movimiento:
                  type: string
        responses:
          201:
            description: Registro de historial general creado
        """
        current_user = get_jwt_identity()
        
        nuevo_movimiento = Historial_General(
            FK_Id_Rol_HG=request.json.get('FK_Id_Rol_HG', 1),
            FK_Id_Usuario_HG=request.json.get('FK_Id_Usuario_HG', current_user),
            FK_Id_Movimiento_Producto=request.json.get('FK_Id_Movimiento_Producto'),
            FK_Id_Movimiento_Venta=request.json.get('FK_Id_Movimiento_Venta'),
            Tipo_Movimiento=request.json['Tipo_Movimiento'],
            Descripcion_Movimiento=request.json['Descripcion_Movimiento']
        )
        
        db.session.add(nuevo_movimiento)
        db.session.commit()
        
        return historial_general_individual_schema.dump(nuevo_movimiento), 201
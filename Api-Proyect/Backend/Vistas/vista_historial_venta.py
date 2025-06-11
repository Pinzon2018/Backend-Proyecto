from flask_restful import Resource
from flask import request
from ..Modelos import db, Historial_Venta, HistorialVentaSchema
from flask_jwt_extended import jwt_required, get_jwt_identity

historial_venta_schema = HistorialVentaSchema(many=True)
historial_venta_individual_schema = HistorialVentaSchema()

class VistaHistorialVenta(Resource):
    @jwt_required()
    def get(self, Id_Venta_HV=None):
        """
        Obtener historial de ventas
        ---
        tags:
          - Historial Ventas
        security:
          - Bearer: []
        parameters:
          - name: Id_Venta_HV
            in: path
            type: integer
            required: false
            description: ID del historial de venta específico (opcional)
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
          - name: usuario_id
            in: query
            type: integer
            description: ID del usuario para filtrar
        responses:
          200:
            description: Lista de historial de ventas
        """
        current_user = get_jwt_identity()
        
        if Id_Venta_HV:
            historial = Historial_Venta.query.get_or_404(Id_Venta_HV)
            return historial_venta_individual_schema.dump(historial)
        
        # Consulta base
        query = Historial_Venta.query
        
        # Filtros opcionales
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        usuario_id = request.args.get('usuario_id')
        
        if fecha_inicio:
            from datetime import datetime
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            query = query.filter(Historial_Venta.Fecha >= fecha_inicio_dt)
            
        if fecha_fin:
            from datetime import datetime
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
            query = query.filter(Historial_Venta.Fecha <= fecha_fin_dt)
            
        if usuario_id:
            query = query.filter(Historial_Venta.FK_Id_Usuario_HV == usuario_id)
        
        # Ordenar por fecha descendente
        historiales = query.order_by(Historial_Venta.Fecha.desc()).all()
        return historial_venta_schema.dump(historiales)
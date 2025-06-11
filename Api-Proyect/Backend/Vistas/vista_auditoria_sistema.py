from flask_restful import Resource
from flask import request
from ..Modelos import db, Auditoria_Sistema, AuditoriaSistemaSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

auditoria_sistema_schema = AuditoriaSistemaSchema(many=True)
auditoria_sistema_individual_schema = AuditoriaSistemaSchema()

class VistaAuditoriaSistema(Resource):
    @jwt_required()
    def get(self, Id_Auditoria=None):
        """
        Obtener registros de auditoría del sistema
        ---
        tags:
          - Auditoría Sistema
        security:
          - Bearer: []
        parameters:
          - name: Id_Auditoria
            in: path
            type: integer
            required: false
            description: ID de la auditoría específica (opcional)
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
          - name: tabla_afectada
            in: query
            type: string
            description: Tabla específica a filtrar (producto, venta, usuario, etc.)
          - name: accion
            in: query
            type: string
            description: Tipo de acción (INSERT, UPDATE, DELETE)
          - name: usuario_id
            in: query
            type: integer
            description: ID del usuario que realizó la acción
          - name: limit
            in: query
            type: integer
            description: Límite de registros (por defecto 50)
          - name: page
            in: query
            type: integer
            description: Página para paginación (por defecto 1)
        responses:
          200:
            description: Lista de registros de auditoría
        """
        current_user = get_jwt_identity()
        
        if Id_Auditoria:
            auditoria = Auditoria_Sistema.query.get_or_404(Id_Auditoria)
            return auditoria_sistema_individual_schema.dump(auditoria)
        
        # Consulta base
        query = Auditoria_Sistema.query
        
        # Filtros opcionales
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        tabla_afectada = request.args.get('tabla_afectada')
        accion = request.args.get('accion')
        usuario_id = request.args.get('usuario_id')
        
        if fecha_inicio:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            query = query.filter(Auditoria_Sistema.Fecha_Accion >= fecha_inicio_dt)
            
        if fecha_fin:
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
            query = query.filter(Auditoria_Sistema.Fecha_Accion <= fecha_fin_dt)
            
        if tabla_afectada:
            query = query.filter(Auditoria_Sistema.Tabla_Afectada.ilike(f'%{tabla_afectada}%'))
            
        if accion:
            query = query.filter(Auditoria_Sistema.Accion == accion.upper())
            
        if usuario_id:
            query = query.filter(Auditoria_Sistema.FK_Id_Usuario == usuario_id)
        
        # Paginación
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        
        # Ordenar por fecha descendente y aplicar paginación
        auditorias = query.order_by(Auditoria_Sistema.Fecha_Accion.desc()).paginate(
            page=page, 
            per_page=limit, 
            error_out=False
        )
        
        return {
            'data': auditoria_sistema_schema.dump(auditorias.items),
            'pagination': {
                'page': page,
                'pages': auditorias.pages,
                'per_page': limit,
                'total': auditorias.total,
                'has_next': auditorias.has_next,
                'has_prev': auditorias.has_prev
            }
        }

    @jwt_required()
    def post(self):
        """
        Crear registro manual de auditoría (para casos especiales)
        ---
        tags:
          - Auditoría Sistema
        security:
          - Bearer: []
        parameters:
          - in: body
            name: auditoria
            required: true
            schema:
              type: object
              required:
                - Tabla_Afectada
                - Id_Registro_Afectado
                - Accion
                - Descripcion
              properties:
                Tabla_Afectada:
                  type: string
                Id_Registro_Afectado:
                  type: integer
                Accion:
                  type: string
                Valores_Anteriores:
                  type: string
                Valores_Nuevos:
                  type: string
                Descripcion:
                  type: string
        responses:
          201:
            description: Registro de auditoría creado
        """
        current_user = get_jwt_identity()
        
        nueva_auditoria = Auditoria_Sistema(
            FK_Id_Usuario=current_user,
            Tabla_Afectada=request.json['Tabla_Afectada'],
            Id_Registro_Afectado=request.json['Id_Registro_Afectado'],
            Accion=request.json['Accion'].upper(),
            Valores_Anteriores=request.json.get('Valores_Anteriores'),
            Valores_Nuevos=request.json.get('Valores_Nuevos'),
            Descripcion=request.json['Descripcion'],
            IP_Usuario=request.remote_addr
        )
        
        db.session.add(nueva_auditoria)
        db.session.commit()
        
        return auditoria_sistema_individual_schema.dump(nueva_auditoria), 201
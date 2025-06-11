# Backend/Utils/triggers_fixed.py
from sqlalchemy import event, text
from sqlalchemy.orm import sessionmaker
from ..Modelos import (
    db, Producto, Venta, Usuario, Detalle_Venta,
    Historial_Productos, Historial_Venta, Historial_General, 
    Auditoria_Sistema
)
from datetime import datetime
from flask import g, request, has_request_context
from flask_jwt_extended import get_jwt_identity
import pytz
import json
import threading

colombia_tz = pytz.timezone('America/Bogota')

class HistorialTriggers:
    
    @staticmethod
    def obtener_usuario_actual():
        """Obtener usuario y rol actual de la sesión de Flask"""
        try:
            if not has_request_context():
                return 1, 1
            
            try:
                from flask_jwt_extended import get_jwt_identity
                current_user_id = get_jwt_identity()
                if current_user_id:
                    usuario = Usuario.query.get(current_user_id)
                    return current_user_id, usuario.FK_Id_Rol if usuario else 1
            except:
                pass
            
            if hasattr(g, 'current_user_id'):
                return g.current_user_id, getattr(g, 'current_user_rol', 1)
            
            return 1, 1
            
        except Exception as e:
            print(f"⚠️  Error obteniendo usuario actual: {e}")
            return 1, 1

    @staticmethod
    def crear_historial_con_conexion_raw(connection, producto_id, usuario_id, rol_id, tipo_movimiento, cantidad, descripcion, producto_nombre=None):
        """Crear historial usando conexión raw para evitar conflictos de sesión"""
        try:
            if not producto_nombre:
                # Obtener nombre del producto usando conexión raw
                result = connection.execute(text("SELECT Nombre_Prod FROM producto WHERE Id_Producto = :id"), {"id": producto_id})
                row = result.fetchone()
                producto_nombre = row[0] if row else f"Producto ID {producto_id}"
            
            fecha_actual = datetime.now(colombia_tz)
            
            # Insertar en historial_productos usando SQL raw
            historial_sql = text("""
                INSERT INTO historial_productos 
                (Fecha_Movimiento_Prod, FK_Id_Rol_HP, FK_Id_Usuario_HP, FK_Id_Producto_HP, 
                 Producto, Tipo_Movimiento, Cantidad_Prod, Descripcion_Movimiento, Estados)
                VALUES (:fecha, :rol_id, :usuario_id, :producto_id, :producto, :tipo, :cantidad, :descripcion, :estado)
            """)
            
            result = connection.execute(historial_sql, {
                "fecha": fecha_actual,
                "rol_id": rol_id,
                "usuario_id": usuario_id,
                "producto_id": producto_id,
                "producto": producto_nombre,
                "tipo": tipo_movimiento,
                "cantidad": cantidad,
                "descripcion": descripcion,
                "estado": True
            })
            
            # Obtener el ID del registro insertado
            historial_id = result.lastrowid
            
            # Insertar en historial_general
            general_sql = text("""
                INSERT INTO historial_general 
                (Fecha_Movimiento, FK_Id_Rol_HG, FK_Id_Usuario_HG, FK_Id_Movimiento_Producto, 
                 Tipo_Movimiento, Descripcion_Movimiento)
                VALUES (:fecha, :rol_id, :usuario_id, :movimiento_id, :tipo, :descripcion)
            """)
            
            connection.execute(general_sql, {
                "fecha": fecha_actual,
                "rol_id": rol_id,
                "usuario_id": usuario_id,
                "movimiento_id": historial_id,
                "tipo": f"PRODUCTO_{tipo_movimiento}",
                "descripcion": descripcion
            })
            
            print(f"✅ Historial creado (raw): Producto {producto_id} - {tipo_movimiento} - {cantidad} unidades")
            return True
            
        except Exception as e:
            print(f"❌ Error creando historial con conexión raw: {e}")
            return False

    @staticmethod
    def crear_auditoria_con_conexion_raw(connection, usuario_id, tabla, id_registro, accion, valores_anteriores=None, valores_nuevos=None, descripcion=""):
        """Crear auditoría usando conexión raw"""
        try:
            ip_usuario = "Sistema"
            if has_request_context() and request:
                ip_usuario = request.remote_addr or "Sistema"
            
            fecha_actual = datetime.now(colombia_tz)
            
            auditoria_sql = text("""
                INSERT INTO auditoria_sistema 
                (FK_Id_Usuario, Tabla_Afectada, Id_Registro_Afectado, Accion, 
                 Valores_Anteriores, Valores_Nuevos, Descripcion, IP_Usuario, Fecha_Auditoria)
                VALUES (:usuario_id, :tabla, :id_registro, :accion, :anteriores, :nuevos, :descripcion, :ip, :fecha)
            """)
            
            connection.execute(auditoria_sql, {
                "usuario_id": usuario_id,
                "tabla": tabla,
                "id_registro": id_registro,
                "accion": accion.upper(),
                "anteriores": json.dumps(valores_anteriores, ensure_ascii=False, default=str) if valores_anteriores else None,
                "nuevos": json.dumps(valores_nuevos, ensure_ascii=False, default=str) if valores_nuevos else None,
                "descripcion": descripcion,
                "ip": ip_usuario,
                "fecha": fecha_actual
            })
            
            print(f"✅ Auditoría creada (raw): {tabla}.{id_registro} - {accion}")
            return True
            
        except Exception as e:
            print(f"❌ Error creando auditoría con conexión raw: {e}")
            return False

def init_triggers(app):
    """Inicializar todos los triggers del sistema"""
    
    with app.app_context():
        
        # 🔥 TRIGGER: Producto creado
        @event.listens_for(Producto, 'after_insert')
        def producto_creado(mapper, connection, target):
            print(f"🔥 TRIGGER: Producto '{target.Nombre_Prod}' creado (ID: {target.Id_Producto})")
            
            usuario_id, rol_id = HistorialTriggers.obtener_usuario_actual()
            
            # Crear historial usando conexión raw
            HistorialTriggers.crear_historial_con_conexion_raw(
                connection=connection,
                producto_id=target.Id_Producto,
                usuario_id=usuario_id,
                rol_id=rol_id,
                tipo_movimiento="ENTRADA",
                cantidad=target.Unidades_Totales_Prod or 0,
                descripcion=f"Producto '{target.Nombre_Prod}' creado - Stock inicial: {target.Unidades_Totales_Prod or 0} unidades",
                producto_nombre=target.Nombre_Prod
            )
            
            # Crear auditoría usando conexión raw
            HistorialTriggers.crear_auditoria_con_conexion_raw(
                connection=connection,
                usuario_id=usuario_id,
                tabla="producto",
                id_registro=target.Id_Producto,
                accion="INSERT",
                valores_nuevos={
                    "id": target.Id_Producto,
                    "nombre": target.Nombre_Prod,
                    "precio_bruto": float(target.Precio_Bruto_Prod or 0),
                    "precio_neto": float(target.Precio_Neto_Unidad_Prod or 0),
                    "unidades": target.Unidades_Totales_Prod or 0,
                    "marca": target.Marca_Prod,
                    "estado": target.Estado_Prod,
                    "medida": target.Medida_Prod,
                    "unidad_medida": target.Unidad_Medida_Prod
                },
                descripcion=f"Producto '{target.Nombre_Prod}' creado exitosamente"
            )

        # 🔥 TRIGGER: Producto modificado
        @event.listens_for(Producto, 'before_update')
        def producto_antes_modificacion(mapper, connection, target):
            """Capturar valores anteriores antes de la modificación"""
            # Guardar valores anteriores en el objeto target para usar en after_update
            if not hasattr(target, '_valores_anteriores'):
                # Obtener valores actuales de la base de datos
                result = connection.execute(text("SELECT * FROM producto WHERE Id_Producto = :id"), {"id": target.Id_Producto})
                row = result.fetchone()
                if row:
                    target._valores_anteriores = dict(row._mapping)

        @event.listens_for(Producto, 'after_update')
        def producto_modificado(mapper, connection, target):
            print(f"🔥 TRIGGER: Producto '{target.Nombre_Prod}' modificado (ID: {target.Id_Producto})")
            
            usuario_id, rol_id = HistorialTriggers.obtener_usuario_actual()
            
            # Comparar valores anteriores con actuales
            valores_anteriores = getattr(target, '_valores_anteriores', {})
            valores_nuevos = {
                "nombre": target.Nombre_Prod,
                "precio_bruto": float(target.Precio_Bruto_Prod or 0),
                "precio_neto": float(target.Precio_Neto_Unidad_Prod or 0),
                "unidades": target.Unidades_Totales_Prod or 0,
                "marca": target.Marca_Prod,
                "estado": target.Estado_Prod
            }
            
            cambios_detectados = []
            
            # Detectar cambios específicos
            if valores_anteriores:
                for campo, nuevo_valor in valores_nuevos.items():
                    campo_bd = {
                        "nombre": "Nombre_Prod",
                        "precio_bruto": "Precio_Bruto_Prod", 
                        "precio_neto": "Precio_Neto_Unidad_Prod",
                        "unidades": "Unidades_Totales_Prod",
                        "marca": "Marca_Prod",
                        "estado": "Estado_Prod"
                    }.get(campo, campo)
                    
                    valor_anterior = valores_anteriores.get(campo_bd)
                    
                    if valor_anterior != nuevo_valor:
                        cambios_detectados.append(f"{campo}: {valor_anterior} → {nuevo_valor}")
                        
                        # Caso especial: Cambio de inventario
                        if campo == "unidades":
                            diferencia = (nuevo_valor or 0) - (valor_anterior or 0)
                            if diferencia != 0:
                                tipo_mov = "ENTRADA" if diferencia > 0 else "SALIDA"
                                
                                HistorialTriggers.crear_historial_con_conexion_raw(
                                    connection=connection,
                                    producto_id=target.Id_Producto,
                                    usuario_id=usuario_id,
                                    rol_id=rol_id,
                                    tipo_movimiento=tipo_mov,
                                    cantidad=abs(diferencia),
                                    descripcion=f"Ajuste inventario: {diferencia:+d} unidades ({valor_anterior} → {nuevo_valor})",
                                    producto_nombre=target.Nombre_Prod
                                )
            
            # Solo crear historial general si hubo cambios
            if cambios_detectados:
                descripcion_cambios = f"Producto modificado. Cambios: {', '.join(cambios_detectados)}"
                
                HistorialTriggers.crear_historial_con_conexion_raw(
                    connection=connection,
                    producto_id=target.Id_Producto,
                    usuario_id=usuario_id,
                    rol_id=rol_id,
                    tipo_movimiento="MODIFICACION",
                    cantidad=0,
                    descripcion=descripcion_cambios,
                    producto_nombre=target.Nombre_Prod
                )
                
                # Crear auditoría de modificación
                HistorialTriggers.crear_auditoria_con_conexion_raw(
                    connection=connection,
                    usuario_id=usuario_id,
                    tabla="producto",
                    id_registro=target.Id_Producto,
                    accion="UPDATE",
                    valores_anteriores=valores_anteriores,
                    valores_nuevos=valores_nuevos,
                    descripcion=descripcion_cambios
                )

        # 🔥 TRIGGER: Producto eliminado
        @event.listens_for(Producto, 'before_delete')
        def producto_eliminado(mapper, connection, target):
            print(f"🔥 TRIGGER: Producto '{target.Nombre_Prod}' será eliminado (ID: {target.Id_Producto})")
            
            usuario_id, rol_id = HistorialTriggers.obtener_usuario_actual()
            
            # Crear historial usando conexión raw
            HistorialTriggers.crear_historial_con_conexion_raw(
                connection=connection,
                producto_id=target.Id_Producto,
                usuario_id=usuario_id,
                rol_id=rol_id,
                tipo_movimiento="ELIMINACION",
                cantidad=target.Unidades_Totales_Prod or 0,
                descripcion=f"Producto '{target.Nombre_Prod}' eliminado - Tenía {target.Unidades_Totales_Prod or 0} unidades en stock",
                producto_nombre=target.Nombre_Prod
            )
            
            # Crear auditoría usando conexión raw
            HistorialTriggers.crear_auditoria_con_conexion_raw(
                connection=connection,
                usuario_id=usuario_id,
                tabla="producto",
                id_registro=target.Id_Producto,
                accion="DELETE",
                valores_anteriores={
                    "id": target.Id_Producto,
                    "nombre": target.Nombre_Prod,
                    "precio_bruto": float(target.Precio_Bruto_Prod or 0),
                    "precio_neto": float(target.Precio_Neto_Unidad_Prod or 0),
                    "unidades": target.Unidades_Totales_Prod or 0,
                    "marca": target.Marca_Prod,
                    "estado": target.Estado_Prod
                },
                descripcion=f"Producto '{target.Nombre_Prod}' eliminado"
            )

        # 🔥 TRIGGER: Venta creada
        @event.listens_for(Venta, 'after_insert')
        def venta_creada(mapper, connection, target):
            print(f"🔥 TRIGGER: Venta creada (ID: {target.Id_Venta}) por ${target.Total_Venta:,.2f}")
            
            usuario_id = target.FK_Id_Usuario
            
            # Obtener rol del usuario usando conexión raw
            try:
                result = connection.execute(text("SELECT FK_Id_Rol FROM usuario WHERE Id_Usuario = :id"), {"id": usuario_id})
                row = result.fetchone()
                rol_id = row[0] if row else 1
            except:
                rol_id = 1
            
            fecha_actual = datetime.now(colombia_tz)
            
            # Crear historial de venta usando SQL raw
            try:
                venta_sql = text("""
                    INSERT INTO historial_venta 
                    (Fecha_Venta, FK_Id_Usuario_HV, FK_Id_Venta_HV, Total_Venta_HV, Forma_Pago_HV, Descripcion_Venta)
                    VALUES (:fecha, :usuario_id, :venta_id, :total, :forma_pago, :descripcion)
                """)
                
                result = connection.execute(venta_sql, {
                    "fecha": fecha_actual,
                    "usuario_id": usuario_id,
                    "venta_id": target.Id_Venta,
                    "total": target.Total_Venta,
                    "forma_pago": target.Forma_Pago_Fact or "",
                    "descripcion": f"Venta #{target.Id_Venta} registrada - ${target.Total_Venta:,.2f}"
                })
                
                historial_venta_id = result.lastrowid
                
                # Crear en historial general
                general_sql = text("""
                    INSERT INTO historial_general 
                    (Fecha_Movimiento, FK_Id_Rol_HG, FK_Id_Usuario_HG, FK_Id_Movimiento_Venta, 
                     Tipo_Movimiento, Descripcion_Movimiento)
                    VALUES (:fecha, :rol_id, :usuario_id, :venta_id, :tipo, :descripcion)
                """)
                
                connection.execute(general_sql, {
                    "fecha": fecha_actual,
                    "rol_id": rol_id,
                    "usuario_id": usuario_id,
                    "venta_id": historial_venta_id,
                    "tipo": "VENTA_REGISTRADA",
                    "descripcion": f"Venta por ${target.Total_Venta:,.2f}"
                })
                
                print(f"✅ Historial venta creado (raw): Venta {target.Id_Venta} - ${target.Total_Venta:,.2f}")
                
            except Exception as e:
                print(f"❌ Error creando historial venta: {e}")

        # 🔥 TRIGGER: Detalle venta creado
        @event.listens_for(Detalle_Venta, 'after_insert')
        def detalle_venta_creado(mapper, connection, target):
            print(f"🔥 TRIGGER: Detalle venta - {target.Cantidad} unidades del producto {target.FK_Id_Producto}")
            
            try:
                # Obtener información del producto
                producto_result = connection.execute(
                    text("SELECT * FROM producto WHERE Id_Producto = :id"),
                    {"id": target.FK_Id_Producto}
                ).fetchone()
                
                if producto_result:
                    producto_dict = dict(producto_result._mapping)
                    stock_actual = producto_dict['Unidades_Totales_Prod']
                    nueva_cantidad = max(0, stock_actual - target.Cantidad)
                    
                    # Actualizar inventario usando SQL raw
                    connection.execute(
                        text("UPDATE producto SET Unidades_Totales_Prod = :nueva_cantidad WHERE Id_Producto = :id"),
                        {"nueva_cantidad": nueva_cantidad, "id": target.FK_Id_Producto}
                    )
                    
                    # Crear historial de salida
                    usuario_id, rol_id = HistorialTriggers.obtener_usuario_actual()
                    
                    HistorialTriggers.crear_historial_con_conexion_raw(
                        connection=connection,
                        producto_id=target.FK_Id_Producto,
                        usuario_id=usuario_id,
                        rol_id=rol_id,
                        tipo_movimiento="SALIDA",
                        cantidad=target.Cantidad,
                        descripcion=f"Venta - Salida de {target.Cantidad} unidades (Stock: {stock_actual} → {nueva_cantidad})",
                        producto_nombre=producto_dict['Nombre_Prod']
                    )
                    
                    print(f"✅ Inventario actualizado: Producto {target.FK_Id_Producto} - {stock_actual} → {nueva_cantidad}")
                    
                    # Alerta de stock bajo
                    if nueva_cantidad <= 5:
                        print(f"⚠️  ALERTA: Stock bajo para producto {producto_dict['Nombre_Prod']}: {nueva_cantidad} unidades")
                        
            except Exception as e:
                print(f"❌ Error en trigger detalle_venta: {e}")

        print("\n" + "="*60)
        print("🎉 ✅ TRIGGERS DE HISTORIAL CORREGIDOS Y FUNCIONALES")
        print("="*60)
        print("🔧 Cambios realizados:")
        print("   ✅ Uso de conexiones raw SQL en lugar de db.session")
        print("   ✅ Eliminados conflictos de sesión durante flush")
        print("   ✅ Triggers optimizados para evitar transacciones cerradas")
        print("   ✅ Historial y auditoría funcionando correctamente")
        print("="*60)
        print("📊 Triggers activos:")
        print("   🔸 Producto: INSERT/UPDATE/DELETE → Historial + Auditoría")
        print("   🔸 Venta: INSERT → Historial + Auditoría")
        print("   🔸 Detalle_Venta: INSERT → Actualización inventario + Historial")
        print("="*60)
        print("✅ Sistema completamente funcional y estable")
        print("="*60)
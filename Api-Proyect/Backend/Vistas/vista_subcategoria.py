from flask_restful import Resource
from flask import request
from ..Modelos import db, Subcategoria, SubcategoriaSchema, Categoria
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

subcategoria_schema = SubcategoriaSchema()
subcategorias_schema = SubcategoriaSchema(many=True)

class VistaSubcategoria(Resource):
    @jwt_required()
    def get(self, Id_Subcategoria=None):
        """Obtener subcategorías"""
        try:
            if Id_Subcategoria:
                subcategoria = Subcategoria.query.options(
                    db.joinedload(Subcategoria.categoria_rl)
                ).get_or_404(Id_Subcategoria)
                return subcategoria_schema.dump(subcategoria), 200
            else:
                # CARGAR LA RELACIÓN CON CATEGORÍA
                subcategorias = Subcategoria.query.options(
                    db.joinedload(Subcategoria.categoria_rl)
                ).all()
                return subcategorias_schema.dump(subcategorias), 200
        except Exception as e:
            print(f"❌ Error en GET subcategorías: {str(e)}")
            return {"error": "Error al obtener subcategorías", "detalle": str(e)}, 500

    @jwt_required()    
    def post(self):
        """Crear una nueva subcategoría"""
        try:
            data = request.get_json()
            print(f"📥 Datos subcategoría recibidos: {data}")
            
            if not data:
                return {"error": "No se enviaron datos"}, 400
            
            # Validar campos requeridos - CORREGIDO: usar el nombre correcto del campo
            nombre = data.get('Nombre_Subcategoria', '').strip()
            descripcion = data.get('Descripcion_Subcategoria', '').strip()
            # CAMBIO CRÍTICO: Aceptar tanto Id_Categoria como FK_Categoria
            categoria_id = data.get('Id_Categoria') or data.get('FK_Categoria')
            
            print(f"🔍 Datos extraídos - Nombre: '{nombre}', Descripción: '{descripcion}', CategoriaID: {categoria_id}")
            
            if not all([nombre, descripcion, categoria_id]):
                return {
                    "error": "Todos los campos son requeridos",
                    "campos_faltantes": {
                        "nombre": not bool(nombre),
                        "descripcion": not bool(descripcion),
                        "categoria_id": not bool(categoria_id)
                    }
                }, 400
            
            # Validar longitudes
            if len(nombre) < 3:
                return {"error": "El nombre debe tener al menos 3 caracteres"}, 400
            
            if len(descripcion) < 10:
                return {"error": "La descripción debe tener al menos 10 caracteres"}, 400
            
            # Validar que la categoría existe
            try:
                categoria_id = int(categoria_id)
                print(f"🔍 Categoria ID convertido: {categoria_id}")
            except (ValueError, TypeError) as e:
                print(f"❌ Error conversión categoria_id: {e}")
                return {"error": "ID de categoría inválido"}, 400
                
            categoria = Categoria.query.get(categoria_id)
            print(f"🔍 Categoría encontrada: {categoria}")
            
            if not categoria:
                return {"error": f"Categoría con ID {categoria_id} no encontrada"}, 400

            # Verificar duplicados en la misma categoría
            duplicado = Subcategoria.query.filter_by(
                Nombre_Subcategoria=nombre,
                FK_Categoria=categoria_id
            ).first()
            
            if duplicado:
                return {"error": "Ya existe una subcategoría con este nombre en la categoría seleccionada"}, 400

            # Crear subcategoría - USANDO EL NOMBRE CORRECTO DEL CAMPO
            nueva_subcategoria = Subcategoria(
                Nombre_Subcategoria=nombre,
                Descripcion_Subcategoria=descripcion,
                FK_Categoria=categoria_id  # CORRECTO: usar FK_Categoria, no Id_Categoria
            )
            
            print(f"🔍 Objeto subcategoría creado: {nueva_subcategoria}")
            print(f"🔍 Atributos: Nombre={nueva_subcategoria.Nombre_Subcategoria}, FK={nueva_subcategoria.FK_Categoria}")

            # TRANSACCIÓN MEJORADA
            try:
                db.session.add(nueva_subcategoria)
                print(f"✅ Objeto agregado a la sesión")
                
                db.session.flush()  # Para obtener el ID antes del commit
                print(f"✅ Flush ejecutado - ID temporal: {nueva_subcategoria.Id_Subcategoria}")
                
                db.session.commit()
                print(f"✅ Commit ejecutado - ID final: {nueva_subcategoria.Id_Subcategoria}")
                
                # Recargar el objeto con la relación para la respuesta
                nueva_subcategoria = Subcategoria.query.options(
                    db.joinedload(Subcategoria.categoria_rl)
                ).get(nueva_subcategoria.Id_Subcategoria)
                
            except Exception as commit_error:
                db.session.rollback()
                print(f"❌ Error en commit: {commit_error}")
                raise commit_error

            return {
                "success": True,
                "message": "Subcategoría creada exitosamente",
                "subcategoria": subcategoria_schema.dump(nueva_subcategoria)
            }, 201

        except IntegrityError as e:
            db.session.rollback()
            print(f"❌ Error de integridad: {str(e)}")
            return {"error": "Error de integridad en la base de datos", "detalle": str(e)}, 400
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error general en POST subcategoría: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"error": "Error al crear subcategoría", "detalle": str(e)}, 500
    
    @jwt_required()
    def put(self, Id_Subcategoria):
        """Actualizar subcategoría"""
        try:
            subcategoria = Subcategoria.query.get_or_404(Id_Subcategoria)
            data = request.get_json()
            
            if 'Nombre_Subcategoria' in data:
                nuevo_nombre = data['Nombre_Subcategoria'].strip()
                if len(nuevo_nombre) < 3:
                    return {"error": "El nombre debe tener al menos 3 caracteres"}, 400
                    
                if nuevo_nombre != subcategoria.Nombre_Subcategoria:
                    # Verificar duplicados
                    duplicado = Subcategoria.query.filter(
                        Subcategoria.Nombre_Subcategoria == nuevo_nombre,
                        Subcategoria.FK_Categoria == subcategoria.FK_Categoria,
                        Subcategoria.Id_Subcategoria != Id_Subcategoria
                    ).first()
                    if duplicado:
                        return {"error": "Ya existe una subcategoría con este nombre en la categoría"}, 400
                subcategoria.Nombre_Subcategoria = nuevo_nombre
                
            if 'Descripcion_Subcategoria' in data:
                nueva_descripcion = data['Descripcion_Subcategoria'].strip()
                if len(nueva_descripcion) < 10:
                    return {"error": "La descripción debe tener al menos 10 caracteres"}, 400
                subcategoria.Descripcion_Subcategoria = nueva_descripcion
                
            if 'Id_Categoria' in data or 'FK_Categoria' in data:
                categoria_id = int(data.get('Id_Categoria', data.get('FK_Categoria')))
                if not Categoria.query.get(categoria_id):
                    return {"error": "Categoría no encontrada"}, 400
                subcategoria.FK_Categoria = categoria_id

            db.session.commit()
            
            # Recargar con relaciones
            subcategoria = Subcategoria.query.options(
                db.joinedload(Subcategoria.categoria_rl)
            ).get(Id_Subcategoria)
            
            return {
                "success": True,
                "message": "Subcategoría actualizada exitosamente",
                "subcategoria": subcategoria_schema.dump(subcategoria)
            }, 200
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error en PUT: {str(e)}")
            return {"error": "Error al actualizar", "detalle": str(e)}, 500
    
    @jwt_required()
    def delete(self, Id_Subcategoria):
        """Eliminar subcategoría"""
        try:
            subcategoria = Subcategoria.query.get_or_404(Id_Subcategoria)
            nombre = subcategoria.Nombre_Subcategoria
            
            # Verificar si tiene productos asociados
            if subcategoria.productos:
                return {
                    "error": f"No se puede eliminar. Hay {len(subcategoria.productos)} productos asociados"
                }, 400
            
            db.session.delete(subcategoria)
            db.session.commit()
            
            return {
                "success": True, 
                "message": f"Subcategoría '{nombre}' eliminada exitosamente"
            }, 200
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error en DELETE: {str(e)}")
            return {"error": "Error al eliminar", "detalle": str(e)}, 500
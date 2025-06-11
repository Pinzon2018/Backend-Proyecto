from flask_restful import Resource
from flask import request, jsonify
from ..Modelos import db, Categoria, CategoriaSchema, Subcategoria
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

categoria_schema = CategoriaSchema()
categorias_schema = CategoriaSchema(many=True)

class VistaCategoria(Resource):
    @jwt_required()
    def get(self, Id_Categoria=None):
        """Obtener una o todas las categorías con contador de subcategorías"""
        try:
            if Id_Categoria:
                # Obtener categoría específica con sus subcategorías
                categoria = Categoria.query.options(
                    db.joinedload(Categoria.subcategorias)
                ).get_or_404(Id_Categoria)
                
                resultado = categoria_schema.dump(categoria)
                # Agregar contador de subcategorías
                resultado['total_subcategorias'] = len(categoria.subcategorias)
                resultado['subcategorias_nombres'] = [sub.Nombre_Subcategoria for sub in categoria.subcategorias]
                
                return resultado, 200
            else:
                # Obtener todas las categorías con contador de subcategorías
                categorias_con_contador = db.session.query(
                    Categoria,
                    func.count(Subcategoria.Id_Subcategoria).label('total_subcategorias')
                ).outerjoin(Subcategoria).group_by(Categoria.Id_Categoria).all()
                
                resultado = []
                for categoria, total_sub in categorias_con_contador:
                    cat_data = categoria_schema.dump(categoria)
                    cat_data['total_subcategorias'] = total_sub
                    resultado.append(cat_data)
                
                return resultado, 200
        except Exception as e:
            print(f"❌ Error en GET categorías: {str(e)}")
            return {"error": "Error al obtener categorías", "detalle": str(e)}, 500
    
    @jwt_required()
    def post(self):
        """Crear una nueva categoría"""
        try:
            data = request.get_json()
            print(f"📥 Datos categoría recibidos: {data}")
            
            # Validaciones básicas
            if not data:
                return {"error": "No se enviaron datos"}, 400
            
            nombre = data.get('Nombre_Cat', '').strip()
            descripcion = data.get('Descripcion_Cat', '').strip()
            
            if not nombre or not descripcion:
                return {"error": "Nombre y descripción son requeridos"}, 400
            
            # Validar longitudes
            if len(nombre) < 3:
                return {"error": "El nombre debe tener al menos 3 caracteres"}, 400
                
            if len(descripcion) < 10:
                return {"error": "La descripción debe tener al menos 10 caracteres"}, 400
            
            # Verificar duplicados (insensible a mayúsculas)
            duplicado = Categoria.query.filter(
                func.lower(Categoria.Nombre_Cat) == func.lower(nombre)
            ).first()
            
            if duplicado:
                return {"error": "Ya existe una categoría con este nombre"}, 400
            
            # Crear categoría
            nueva_categoria = Categoria(
                Nombre_Cat=nombre,
                Descripcion_Cat=descripcion
            )
            
            db.session.add(nueva_categoria)
            db.session.commit()
            
            print(f"✅ Categoría creada con ID: {nueva_categoria.Id_Categoria}")
            
            # Preparar respuesta con contador
            resultado = categoria_schema.dump(nueva_categoria)
            resultado['total_subcategorias'] = 0
            
            return {
                "success": True,
                "message": "Categoría creada exitosamente",
                "categoria": resultado
            }, 201
            
        except IntegrityError as e:
            db.session.rollback()
            print(f"❌ Error de integridad: {str(e)}")
            return {"error": "Error de integridad: Nombre duplicado"}, 400
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error en POST categoría: {str(e)}")
            return {"error": "Error interno del servidor", "detalle": str(e)}, 500

    @jwt_required()
    def put(self, Id_Categoria):
        """Actualizar una categoría"""
        try:
            categoria = Categoria.query.get_or_404(Id_Categoria)
            data = request.get_json()
            
            if 'Nombre_Cat' in data:
                nombre = data['Nombre_Cat'].strip()
                if len(nombre) < 3:
                    return {"error": "El nombre debe tener al menos 3 caracteres"}, 400
                    
                if nombre.lower() != categoria.Nombre_Cat.lower():
                    # Verificar duplicados
                    duplicado = Categoria.query.filter(
                        func.lower(Categoria.Nombre_Cat) == func.lower(nombre),
                        Categoria.Id_Categoria != Id_Categoria
                    ).first()
                    if duplicado:
                        return {"error": "Ya existe una categoría con este nombre"}, 400
                categoria.Nombre_Cat = nombre
                
            if 'Descripcion_Cat' in data:
                descripcion = data['Descripcion_Cat'].strip()
                if len(descripcion) < 10:
                    return {"error": "La descripción debe tener al menos 10 caracteres"}, 400
                categoria.Descripcion_Cat = descripcion

            db.session.commit()
            
            # Respuesta con contador actualizado
            total_sub = Subcategoria.query.filter_by(FK_Categoria=Id_Categoria).count()
            resultado = categoria_schema.dump(categoria)
            resultado['total_subcategorias'] = total_sub
            
            return {
                "success": True,
                "message": "Categoría actualizada exitosamente",
                "categoria": resultado
            }, 200
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error en PUT categoría: {str(e)}")
            return {"error": "Error al actualizar", "detalle": str(e)}, 500
    
    @jwt_required()  
    def delete(self, Id_Categoria):
        """Eliminar una categoría"""
        try:
            categoria = Categoria.query.get_or_404(Id_Categoria)
            
            # Verificar subcategorías asociadas
            total_subcategorias = Subcategoria.query.filter_by(FK_Categoria=Id_Categoria).count()
            
            if total_subcategorias > 0:
                return {
                    "error": f"No se puede eliminar. Hay {total_subcategorias} subcategorías asociadas",
                    "subcategorias_asociadas": total_subcategorias
                }, 400
            
            nombre_categoria = categoria.Nombre_Cat
            db.session.delete(categoria)
            db.session.commit()
            
            return {
                "success": True, 
                "message": f"Categoría '{nombre_categoria}' eliminada exitosamente"
            }, 200
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error en DELETE categoría: {str(e)}")
            return {"error": "Error al eliminar", "detalle": str(e)}, 500
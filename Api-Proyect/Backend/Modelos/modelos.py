from marshmallow import fields, post_dump
from flask_sqlalchemy import SQLAlchemy
import enum
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Numeric
import pytz
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

db = SQLAlchemy()

class Rol(db.Model):
    __tablename__ = 'rol'
    
    Id_Rol = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(180))   

    usuarios = db.relationship("Usuario", back_populates="rol_rl")
    # ✅ ELIMINADAS las relaciones a historiales para evitar restricciones

class Proveedor(db.Model): 
    __tablename__ = 'proveedor'
    
    Id_Proveedor = db.Column(db.Integer, primary_key=True)
    Nombre_Prov = db.Column(db.String(180))
    Telefono_Prov = db.Column(db.String(15))  
    Direccion_Prov = db.Column(db.String(50))
    
    producto = db.relationship("Producto", back_populates="proveedor")
    fecha_Registro_Prod = db.relationship("Fecha_Registro_Prod", back_populates="proveedor")

class Usuario(db.Model):    
    __tablename__ = 'usuario'
    
    Id_Usuario = db.Column(db.Integer, primary_key=True)
    Nombre_Usu = db.Column(db.String(250))
    Contraseña_hash = db.Column(db.String(255))
    Cedula_Usu = db.Column(db.String(20))
    Email_Usu = db.Column(db.String(250))
    Telefono_Usu = db.Column(db.String(15))
    Fecha_Contrato_Inicio = db.Column(db.Date)
    FK_Rol = db.Column(db.Integer, db.ForeignKey('rol.Id_Rol'))

    rol_rl = db.relationship("Rol", back_populates="usuarios")
    venta_Usuario = db.relationship("Venta", back_populates="usuario")
    # ✅ ELIMINADAS las relaciones a historiales para evitar restricciones
    
    @property
    def contraseña(self):
        raise AttributeError("La contraseña no es un atributo legible")
    
    @contraseña.setter
    def contraseña(self, password):
        self.Contraseña_hash = generate_password_hash(password)
        
    def verificar_contraseña(self, password):
        return check_password_hash(self.Contraseña_hash, password)

class Categoria(db.Model):   
    __tablename__ = 'categoria'
    Id_Categoria = db.Column(db.Integer, primary_key=True)
    Nombre_Cat = db.Column(db.String(80), nullable=False)
    Descripcion_Cat = db.Column(db.String(250), nullable=False)
    
    subcategorias = db.relationship("Subcategoria", back_populates="categoria_rl", cascade="all, delete-orphan")

class Subcategoria(db.Model):
    __tablename__ = 'subcategoria'
    Id_Subcategoria = db.Column(db.Integer, primary_key=True)
    Nombre_Subcategoria = db.Column(db.String(250), nullable=False)
    Descripcion_Subcategoria = db.Column(db.String(500), nullable=False)
    FK_Categoria = db.Column(db.Integer, db.ForeignKey('categoria.Id_Categoria'), nullable=False)
    
    categoria_rl = db.relationship("Categoria", back_populates="subcategorias")
    productos = db.relationship("Producto", back_populates="subcategoria", cascade="all, delete-orphan")

class Producto(db.Model):  
    __tablename__ = 'producto'
    
    Id_Producto = db.Column(db.Integer, primary_key=True, nullable=False)
    Nombre_Prod = db.Column(db.String(100), nullable=False)
    Medida_Prod = db.Column(db.String(50)) 
    Unidad_Medida_Prod = db.Column(db.String(80), default='UNIDAD')
    Precio_Bruto_Prod = db.Column(Numeric(12, 2), nullable=False)
    Iva_Prod = db.Column(Numeric(5, 4), default=0.19)  # 0.19 = 19% IVA Colombia
    Porcentaje_Ganancia = db.Column(Numeric(5, 4), default=0.30)  # 30% ganancia por defecto
    Unidades_Totales_Prod = db.Column(db.Integer, default=0)
    Estado_Prod = db.Column(db.Boolean, default=True)
    Marca_Prod = db.Column(db.String(60))
    Precio_Neto_Unidad_Prod = db.Column(Numeric(12, 2))  # Se calcula automáticamente
    FK_Id_Proveedor = db.Column(db.Integer, db.ForeignKey("proveedor.Id_Proveedor"))
    FK_Id_Subcategoria = db.Column(db.Integer, db.ForeignKey("subcategoria.Id_Subcategoria"))
    
    # Relaciones
    proveedor = db.relationship("Proveedor", back_populates="producto")
    subcategoria = db.relationship("Subcategoria", back_populates="productos")
    fecha_Registro_Prod = db.relationship("Fecha_Registro_Prod", back_populates="producto")
    detalle_Venta_Prod = db.relationship("Detalle_Venta", back_populates="producto")
    
    def calcular_precio_neto(self):
        """
        ✅ Calcula el precio neto según la fórmula correcta para Colombia:
        Precio Neto = Precio Bruto × (1 + IVA + Ganancia)
        
        Ejemplo: 
        - Precio Bruto: $10,000 COP
        - IVA: 19% (0.19)
        - Ganancia: 30% (0.30)
        - Precio Neto = $10,000 × (1 + 0.19 + 0.30) = $10,000 × 1.49 = $14,900 COP
        """
        if self.Precio_Bruto_Prod:
            try:
                precio_bruto = Decimal(str(self.Precio_Bruto_Prod))
                iva = Decimal(str(self.Iva_Prod or 0))
                ganancia = Decimal(str(self.Porcentaje_Ganancia or 0))
                
                # ✅ Fórmula optimizada
                multiplicador = Decimal('1') + iva + ganancia
                precio_neto = precio_bruto * multiplicador
                
                # Redondear a 2 decimales (centavos)
                self.Precio_Neto_Unidad_Prod = precio_neto.quantize(Decimal('0.01'))
                
                return float(self.Precio_Neto_Unidad_Prod)
            except (ValueError, TypeError, Decimal.InvalidOperation) as e:
                # En caso de error, usar valores por defecto
                self.Precio_Neto_Unidad_Prod = self.Precio_Bruto_Prod
                return float(self.Precio_Bruto_Prod or 0)
        
        return 0.0
    
    def __repr__(self):
        return f"<Producto {self.Id_Producto}: {self.Nombre_Prod} - ${self.Precio_Neto_Unidad_Prod} COP>"

colombia_tz = pytz.timezone('America/Bogota')

class Venta(db.Model):
    __tablename__ = 'venta'
    
    Id_Venta = db.Column(db.Integer, primary_key=True)
    Fecha_Venta = db.Column(db.DateTime, default=lambda: datetime.now(colombia_tz))
    Total_Venta = db.Column(db.Numeric(10,2))
    Forma_Pago_Fact = db.Column(db.String(50))
    FK_Id_Usuario = db.Column(db.Integer, db.ForeignKey("usuario.Id_Usuario"))
    
    usuario = db.relationship("Usuario", back_populates="venta_Usuario")
    detalle_Venta_Venta = db.relationship("Detalle_Venta", back_populates="venta")
    # ✅ ELIMINADA la relación a historial_venta para evitar restricciones

class Factura(db.Model):
    __tablename__ = 'factura'
    
    Id_Factura = db.Column(db.Integer, primary_key=True)
    Fecha_Generacion_Fact = db.Column(db.DateTime)
    Impuestos_Fact = db.Column(db.Float)
    
    detalle_Venta_Fact = db.relationship("Detalle_Venta", back_populates="factura")

class Detalle_Venta(db.Model):
    __tablename__ = 'detalle_venta'
    
    Id_Detalle_Venta = db.Column(db.Integer, primary_key=True)
    Cantidad = db.Column(db.Integer)
    precio_unitario = db.Column(db.Numeric(10,2), nullable=False)
    FK_Id_Venta = db.Column(db.Integer, db.ForeignKey("venta.Id_Venta"))
    FK_Id_Producto = db.Column(db.Integer, db.ForeignKey("producto.Id_Producto"))
    FK_Id_Factura = db.Column(db.Integer, db.ForeignKey("factura.Id_Factura"))
    
    factura = db.relationship("Factura", back_populates="detalle_Venta_Fact")
    producto = db.relationship("Producto", back_populates="detalle_Venta_Prod")
    venta = db.relationship("Venta", back_populates="detalle_Venta_Venta")

# ✅ HISTORIALES SIN RESTRICCIONES FK - SOLO AUDITORÍA
class Historial_Venta(db.Model):
    __tablename__ = 'historial_venta'
    
    Id_Venta_HV = db.Column(db.Integer, primary_key=True)
    FK_Id_Venta_HV = db.Column(db.Integer)  # ✅ SIN FK constraint
    FK_Id_Usuario_HV = db.Column(db.Integer)  # ✅ SIN FK constraint
    Fecha = db.Column(db.DateTime)
    Total_Venta = db.Column(db.Float)

    # ✅ SIN relaciones back_populates para evitar restricciones

class Historial_Productos(db.Model):
    __tablename__ = 'historial_productos'
    
    Id_Movimiento_Prod = db.Column(db.Integer, primary_key=True)
    Fecha_Movimiento_Prod = db.Column(db.DateTime)
    FK_Id_Rol_HP = db.Column(db.Integer)  # ✅ SIN FK constraint
    FK_Id_Usuario_HP = db.Column(db.Integer)  # ✅ SIN FK constraint
    FK_Id_Producto_HP = db.Column(db.Integer)  # ✅ SIN FK constraint
    Producto = db.Column(db.String(100))
    Tipo_Movimiento = db.Column(db.String(50))
    Cantidad_Prod = db.Column(db.Integer)
    Descripcion_Movimiento = db.Column(db.String(100))
    Estados = db.Column(db.Boolean)

    # ✅ SIN relaciones back_populates para evitar restricciones

class Historial_General(db.Model):
    __tablename__ = 'historial_general'
    
    Id_Movimiento = db.Column(db.Integer, primary_key=True)
    Fecha_Movimiento = db.Column(db.DateTime)
    FK_Id_Rol_HG = db.Column(db.Integer)  # ✅ SIN FK constraint
    FK_Id_Usuario_HG = db.Column(db.Integer)  # ✅ SIN FK constraint
    FK_Id_Movimiento_Producto = db.Column(db.Integer)  # ✅ SIN FK constraint
    FK_Id_Movimiento_Venta = db.Column(db.Integer)  # ✅ SIN FK constraint
    Tipo_Movimiento = db.Column(db.String(100))
    Descripcion_Movimiento = db.Column(db.String(250))

    # ✅ SIN relaciones back_populates para evitar restricciones

class Fecha_Registro_Prod(db.Model):
    __tablename__ = 'fecha_registro_prod'
    
    Id_Fecha_Registro = db.Column(db.Integer, primary_key=True, nullable=False)
    Fecha_Registro = db.Column(db.Date)
    Cantidad = db.Column(db.Integer)
    FK_Id_Proveedor = db.Column(db.Integer, db.ForeignKey("proveedor.Id_Proveedor"))
    FK_Id_Producto = db.Column(db.Integer, db.ForeignKey("producto.Id_Producto"))
    
    producto = db.relationship("Producto", back_populates="fecha_Registro_Prod")
    proveedor = db.relationship("Proveedor", back_populates="fecha_Registro_Prod")

class Auditoria_Sistema(db.Model):
    __tablename__ = 'auditoria_sistema'
    
    Id_Auditoria = db.Column(db.Integer, primary_key=True)
    Fecha_Accion = db.Column(db.DateTime, default=lambda: datetime.now(colombia_tz))
    FK_Id_Usuario = db.Column(db.Integer, db.ForeignKey("usuario.Id_Usuario"))
    Tabla_Afectada = db.Column(db.String(50))
    Id_Registro_Afectado = db.Column(db.Integer)
    Accion = db.Column(db.String(20))
    Valores_Anteriores = db.Column(db.Text)
    Valores_Nuevos = db.Column(db.Text)
    Descripcion = db.Column(db.String(250))
    IP_Usuario = db.Column(db.String(45))
    
    usuario_auditoria = db.relationship("Usuario")

# SCHEMAS - Serialización

class EnumADiccionario(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return{"llave": value.name, "valor": value.value}

class RolSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Rol
        include_relationships = True
        load_instance = True

class UsuarioSchema(SQLAlchemyAutoSchema):
    rol_rl = fields.Nested(RolSchema)

    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True

class VentaSchema(SQLAlchemyAutoSchema):
    usuario = fields.Nested(UsuarioSchema)
    detalle_Venta = fields.Nested("Detalle_VentaSchema", many=True)

    class Meta:
        model = Venta
        include_relationships = True
        load_instance = True

    @post_dump
    def convert_decimal_to_float(self, data, **kwargs):
        for key, value in data.items():
            if isinstance(value, Decimal):
                data[key] = float(value)
        return data
    
    Total_Venta_Formateado = fields.Method("get_total_formateado")

    def get_total_formateado(self, obj):
        return "${:,.0f}".format(obj.Total_Venta).replace(",", ".")

class ProveedorSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Proveedor
        include_relationships = True
        load_instance = True

class CategoriaSchema(SQLAlchemyAutoSchema):
    subcategorias = fields.Nested("SubcategoriaSchema", many=True, exclude=["categoria_rl"])
    
    class Meta:
        model = Categoria
        include_relationships = True
        load_instance = True

class SubcategoriaSchema(SQLAlchemyAutoSchema):
    categoria_rl = fields.Nested(CategoriaSchema, exclude=["subcategorias"])
    productos = fields.Nested("ProductoSchema", many=True, exclude=["subcategoria"])

    class Meta:
        model = Subcategoria
        include_relationships = True
        load_instance = True

class ProductoSchema(SQLAlchemyAutoSchema):
    proveedor = fields.Nested(ProveedorSchema, exclude=["producto"])
    subcategoria = fields.Nested(SubcategoriaSchema, exclude=["productos"])
    
    class Meta:
        model = Producto
        include_relationships = True
        load_instance = True
    
    @post_dump
    def convertir_decimales(self, data, **kwargs):
        """Convertir Decimal a float sin formatear (para evitar problemas con el frontend)"""
        campos_numericos = ['Precio_Bruto_Prod', 'Precio_Neto_Unidad_Prod', 'Iva_Prod', 'Porcentaje_Ganancia']
        
        for campo in campos_numericos:
            if campo in data and isinstance(data[campo], Decimal):
                data[campo] = float(data[campo])
        
        return data
        # Formatear precios en pesos colombianos
    """ for campo in ['Precio_Bruto_Prod', 'Precio_Neto_Unidad_Prod']:
            if campo in data and isinstance(data[campo], (float, int)):
                # Formato colombiano: $1.500.000,50
                data[campo] = f"${data[campo]:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")"""
        

class Fecha_Registro_ProdSchema(SQLAlchemyAutoSchema):
    proveedor = fields.Nested(ProveedorSchema)
    producto = fields.Nested(ProductoSchema)
    
    class Meta:
        model = Fecha_Registro_Prod
        include_relationships = True
        load_instance = True

class FacturaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Factura
        include_relationships = True
        load_instance = True

class Detalle_VentaSchema(SQLAlchemyAutoSchema):
    venta = fields.Nested(VentaSchema)
    producto = fields.Nested(ProductoSchema)
    factura = fields.Nested(FacturaSchema)

    class Meta:
        model = Detalle_Venta
        include_relationships = True
        load_instance = True

    @post_dump
    def convert_decimal_to_float(self, data, **kwargs):
        for key, value in data.items():
            if isinstance(value, Decimal):
                data[key] = float(value)
        return data

# ✅ SCHEMAS DE HISTORIALES SIN RELACIONES FK
class HistorialVentaSchema(SQLAlchemyAutoSchema):
    # ✅ Campos calculados para mostrar información sin FK
    usuario_nombre = fields.Method("get_usuario_nombre")
    
    class Meta:
        model = Historial_Venta
        include_relationships = False  # ✅ Sin relaciones
        load_instance = True
    
    def get_usuario_nombre(self, obj):
        if obj.FK_Id_Usuario_HV:
            usuario = Usuario.query.get(obj.FK_Id_Usuario_HV)
            return usuario.Nombre_Usu if usuario else "Usuario eliminado"
        return "Usuario desconocido"

class HistorialProductosSchema(SQLAlchemyAutoSchema):
    # ✅ Campos calculados para mostrar información sin FK
    usuario_nombre = fields.Method("get_usuario_nombre")
    rol_nombre = fields.Method("get_rol_nombre")
    producto_nombre = fields.Method("get_producto_nombre")
    
    class Meta:
        model = Historial_Productos
        include_relationships = False  # ✅ Sin relaciones
        load_instance = True
    
    def get_usuario_nombre(self, obj):
        if obj.FK_Id_Usuario_HP:
            usuario = Usuario.query.get(obj.FK_Id_Usuario_HP)
            return usuario.Nombre_Usu if usuario else "Usuario eliminado"
        return "Usuario desconocido"
    
    def get_rol_nombre(self, obj):
        if obj.FK_Id_Rol_HP:
            rol = Rol.query.get(obj.FK_Id_Rol_HP)
            return rol.Nombre if rol else "Rol eliminado"
        return "Rol desconocido"
    
    def get_producto_nombre(self, obj):
        # Preferir el nombre guardado en el historial
        if obj.Producto:
            return obj.Producto
        elif obj.FK_Id_Producto_HP:
            producto = Producto.query.get(obj.FK_Id_Producto_HP)
            return producto.Nombre_Prod if producto else "Producto eliminado"
        return "Producto desconocido"

class HistorialGeneralSchema(SQLAlchemyAutoSchema):
    # ✅ Campos calculados para mostrar información sin FK
    usuario_nombre = fields.Method("get_usuario_nombre")
    rol_nombre = fields.Method("get_rol_nombre")
    
    class Meta:
        model = Historial_General
        include_relationships = False  # ✅ Sin relaciones
        load_instance = True
    
    def get_usuario_nombre(self, obj):
        if obj.FK_Id_Usuario_HG:
            usuario = Usuario.query.get(obj.FK_Id_Usuario_HG)
            return usuario.Nombre_Usu if usuario else "Usuario eliminado"
        return "Usuario desconocido"
    
    def get_rol_nombre(self, obj):
        if obj.FK_Id_Rol_HG:
            rol = Rol.query.get(obj.FK_Id_Rol_HG)
            return rol.Nombre if rol else "Rol eliminado"
        return "Rol desconocido"

class AuditoriaSistemaSchema(SQLAlchemyAutoSchema):
    usuario_auditoria = fields.Nested(UsuarioSchema)
    
    class Meta:
        model = Auditoria_Sistema
        include_relationships = True
        load_instance = True
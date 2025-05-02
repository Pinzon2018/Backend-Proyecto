
from marshmallow import fields
from flask_sqlalchemy import SQLAlchemy
import enum
from werkzeug.security import generate_password_hash, check_password_hash

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()

class Rol(db.Model):
    __tablename__ = 'rol'

    Id_Rol = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(180))      

    usuarios= db.relationship("Usuario", back_populates="rol_Usuario")
    HP_rol = db.relationship("Historial_Productos", back_populates = "rol_HP")
    HG_rol = db.relationship("Historial_General", back_populates = "rol_HG")
    rol_Venta = db.relationship("Venta", back_populates = "venta_Rol")



class Proveedor(db.Model): 
    __tablename__ = 'proveedor'

    Id_Proveedor = db.Column(db.Integer, primary_key=True)
    Nombre_Prov = db.Column(db.String(180))
    Telefono_Prov = db.Column(db.String(15))  
    Direccion_Prov = db.Column(db.String(50))
    producto= db.relationship("Producto", back_populates="proveedor")
    fecha_Registro_Prod= db.relationship("Fecha_Registro_Prod", back_populates="proveedor")

class Usuario(db.Model):    
    __tablename__ = 'usuario'

    Id_Usuario = db.Column(db.Integer, primary_key=True)
    Nombre_Usu = db.Column(db.String(250))
    Contraseña_hash = db.Column(db.String(255))
    Cedula_Usu = db.Column(db.String(20), unique=True)
    Email_Usu = db.Column(db.String(250), unique=True)
    Telefono_Usu = db.Column(db.String(15))
    Fecha_Contrato_Inicio = db.Column(db.Date)
    FK_Id_Rol = db.Column(db.Integer, db.ForeignKey('rol.Id_Rol'))

    rol_Usuario = db.relationship("Rol", back_populates="usuarios")
    venta_Usuario = db.relationship("Venta", back_populates="usuario")
    HV_usuario = db.relationship ("Historial_Venta", back_populates = "usuario_HV")
    HP_usuario = db.relationship ("Historial_Productos", back_populates = "usuario_HP")
    HG_usuario = db.relationship ("Historial_General", back_populates = "usuario_HG")

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
    Nombre_Cat = db.Column(db.String(80))
    Descripcion_Cat = db.Column(db.String(150))
    subcategorias = db.relationship("Subcategoria", back_populates="categoria_rl")

class Subcategoria(db.Model):
    __tablename__ = 'subcategoria'

    Id_Subcategoria = db.Column(db.Integer, primary_key=True)
    Nombre_Subcategoria = db.Column(db.String(250))
    Descripcion_Subcategoria = db.Column(db.String(250))
    categoria = db.Column(db.Integer, db.ForeignKey('categoria.Id_Categoria'))
    categoria_rl = db.relationship("Categoria", back_populates="subcategorias")
    productos = db.relationship("Producto", back_populates="subcategoria")

    
class Producto(db.Model):  
    __tablename__ = 'producto'

    Id_Producto = db.Column(db.Integer, primary_key=True, nullable=False)
    Nombre_Prod = db.Column(db.String(100))
    Medida_Prod = db.Column(db.Integer)
    Unidad_Medida_Prod = db.Column(db.String(80))
    Precio_Bruto_Prod = db.Column(db.Float)
    Precio_Neto_Unidad_Prod = db.Column(db.Float)
    Iva_Prod = db.Column(db.Float)  
    Porcentaje_Ganancia = db.Column(db.Float)
    Unidades_Totales_Prod = db.Column(db.Integer)
    Estado_Prod = db.Column(db.String(50))
    Marca_Prod = db.Column(db.String(60))
    FK_Id_Proveedor = db.Column(db.Integer, db.ForeignKey("proveedor.Id_Proveedor"))
    FK_Id_Subcategoria = db.Column(db.Integer, db.ForeignKey("subcategoria.Id_Subcategoria"))
   
    proveedor = db.relationship("Proveedor", back_populates="producto")
    subcategoria = db.relationship("Subcategoria", back_populates="productos")
    fecha_Registro_Prod= db.relationship("Fecha_Registro_Prod", back_populates="producto")
    detalle_Venta= db.relationship("Detalle_Venta", back_populates = "producto")
    HP_producto = db.relationship("Historial_Productos", back_populates = "producto_HP")

class Venta(db.Model):
    __tablename__ = 'venta'

    Id_Venta = db.Column(db.Integer, primary_key=True)
    Fecha_Venta = db.Column(db.DateTime)
    Total_Venta = db.Column(db.Float)
    Forma_Pago_Fact = db.Column(db.String(50))
    FK_Id_Usuario = db.Column(db.Integer, db.ForeignKey("usuario.Id_Usuario"))
    FK_Id_Rol = db.Column(db.Integer, db.ForeignKey("rol.Id_Rol"))


    venta_Rol = db.relationship("Rol", back_populates = "rol_Venta")
    usuario = db.relationship("Usuario", back_populates="venta_Usuario")
    detalle_Venta= db.relationship("Detalle_Venta", back_populates = "venta")
    historial_venta = db.relationship("Historial_Venta", back_populates = "venta_HV")

class Factura(db.Model):
    __tablename__ = 'factura'

    Id_Factura = db.Column(db.Integer, primary_key=True)
    Fecha_Generacion_Fact = db.Column(db.DateTime)
    Impuestos_Fact= db.Column(db.Float)
    detalle_Venta= db.relationship("Detalle_Venta", back_populates = "factura")

class Detalle_Venta(db.Model):
    __tablename__ = 'detalle_venta'

    Id_Detalle_Venta = db.Column(db.Integer, primary_key=True)
    Cantidad = db.Column(db.Integer)
    Precio_Unidad = db.Column(db.Float)
    FK_Id_Venta = db.Column(db.Integer, db.ForeignKey("venta.Id_Venta"))
    FK_Id_Producto = db.Column(db.Integer, db.ForeignKey("producto.Id_Producto"))
    FK_Id_Factura = db.Column(db.Integer, db.ForeignKey("factura.Id_Factura"))
    
    factura= db.relationship("Factura", back_populates = "detalle_Venta")
    producto= db.relationship("Producto", back_populates = "detalle_Venta")
    venta= db.relationship("Venta", back_populates = "detalle_Venta")


class Historial_Venta(db.Model):
    __tablename__ = 'historial_venta'

    Id_Venta_HV = db.Column(db.Integer, primary_key=True)
    FK_Id_Venta_HV = db.Column(db.Integer, db.ForeignKey("venta.Id_Venta"))
    FK_Id_Usuario_HV = db.Column(db.Integer, db.ForeignKey("usuario.Id_Usuario"))
    Fecha = db.Column(db.DateTime)
    Total_Venta = db.Column(db.Float)
    
    venta_HV = db.relationship("Venta", back_populates = "historial_venta")
    usuario_HV = db.relationship("Usuario", back_populates = "HV_usuario")
    HG_HV = db.relationship("Historial_General", back_populates = "HV_HG")

class Historial_Productos (db.Model):
    __tablename__ = 'historial_productos'

    Id_Movimiento_Prod = db.Column(db.Integer, primary_key=True)
    Fecha_Movimiento_Prod = db.Column(db.DateTime)
    FK_Id_Rol_HP = db.Column(db.Integer, db.ForeignKey("rol.Id_Rol"))
    FK_Id_Usuario_HP = db.Column(db.Integer, db.ForeignKey("usuario.Id_Usuario"))
    FK_Id_Producto_HP = db.Column(db.Integer, db.ForeignKey("producto.Id_Producto"))
    Producto = db.Column(db.String(100))
    Tipo_Movimiento  = db.Column(db.String(50))
    Cantidad_Prod = db.Column(db.Integer)
    Descripcion_Movimiento = db.Column(db.String(50))
    Estados = db.Column(db.Boolean)

    usuario_HP = db.relationship("Usuario", back_populates = "HP_usuario")
    producto_HP = db.relationship("Producto", back_populates= "HP_producto")
    rol_HP = db.relationship("Rol", back_populates = "HP_rol")
    HG_HP = db.relationship("Historial_General", back_populates = "HP_HG")

class Historial_General (db.Model):
    __tablename__ = 'historial_general'

    Id_Movimiento = db.Column(db.Integer, primary_key =True)
    Fecha_Movimiento = db.Column(db.DateTime)
    FK_Id_Rol_HG = db.Column(db.Integer, db.ForeignKey("rol.Id_Rol"))
    FK_Id_Usuario_HG = db.Column(db.Integer, db.ForeignKey("usuario.Id_Usuario"))
    FK_Id_Movimiento_Producto = db.Column(db.Integer, db.ForeignKey("historial_productos.Id_Movimiento_Prod"))
    FK_Id_Movimiento_Venta = db.Column(db.Integer, db.ForeignKey("historial_venta.Id_Venta_HV"))
    Tipo_Movimiento = db.Column(db.String(100))
    Descripcion_Movimiento = db.Column(db.String(250))
    
    HP_HG = db.relationship("Historial_Productos", back_populates = "HG_HP")
    HV_HG = db.relationship("Historial_Venta", back_populates = "HG_HV")
    usuario_HG = db.relationship("Usuario", back_populates = "HG_usuario")
    rol_HG = db.relationship("Rol", back_populates = "HG_rol") 


class Fecha_Registro_Prod(db.Model):
    __tablename__ = 'fecha_registro_prod'

    Id_Fecha_Registro = db.Column(db.Integer, primary_key=True, nullable=False)
    Fecha_Registro = db.Column(db.Date)
    Cantidad = db.Column(db.Integer)
    FK_Id_Proveedor = db.Column(db.Integer, db.ForeignKey("proveedor.Id_Proveedor"))
    FK_Id_Producto = db.Column(db.Integer, db.ForeignKey("producto.Id_Producto"))
    producto = db.relationship("Producto", back_populates="fecha_Registro_Prod")
    proveedor= db.relationship("Proveedor", back_populates="fecha_Registro_Prod")





    
#serializacion 

class EnumADiccionario(fields.Field): #maneja campos personalizados
    def _serialize(self, value, attr, obj, **kwargs): #metodo -valor, -atributo, -objeto, -argumentos
        if value is None:  #evita serializar un valor nulo
            return None
        return{"llave": value.name, "valor": value.value}
            


class RolSchema(SQLAlchemyAutoSchema):  #1
    
    class Meta:
        model = Rol
        include_relationships = True
        load_instance = True


class UsuarioSchema(SQLAlchemyAutoSchema):   #2
    
    rol_Usuario = fields.Nested(RolSchema)

    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True
        exclude = ("Contraseña_hash",)

class VentaSchema(SQLAlchemyAutoSchema):  #9
    
    usuario = fields.Nested(UsuarioSchema)
     
    class Meta:
        model = Venta
        include_relationships = True
        load_instance = True




class ProveedorSchema(SQLAlchemyAutoSchema): #3
    
    class Meta:
        model = Proveedor
        include_relationships = True
        load_instance = True



class CategoriaSchema(SQLAlchemyAutoSchema): #6
    
    class Meta:
        model = Categoria
        include_relationships = True
        load_instance = True

class SubcategoriaSchema(SQLAlchemyAutoSchema):  #7
    
    categoria_rl = fields.Nested(CategoriaSchema)

    class Meta:
        model = Subcategoria
        include_relationships = True
        load_instance = True

class ProductoSchema(SQLAlchemyAutoSchema):  #8
    
    proveedor = fields.Nested(ProveedorSchema)
    subcategoria = fields.Nested(SubcategoriaSchema)

    class Meta:
        model = Producto
        include_relationships = True
        load_instance = True

class FechaRegistroProdSchema (SQLAlchemyAutoSchema): #4
    
    proveedor = fields.Nested(ProveedorSchema)
    producto = fields.Nested(ProductoSchema)
    
    class Meta:
        model = Fecha_Registro_Prod
        include_relationships = True
        load_instance = True



class FacturaSchema(SQLAlchemyAutoSchema): #10

    class Meta:
        model = Factura
        include_relationships = True
        load_instance = True


class DetalleVentaSchema(SQLAlchemyAutoSchema):  #11
    
    venta = fields.Nested(VentaSchema)
    producto = fields.Nested(ProductoSchema)
    factura = fields.Nested(FacturaSchema)

    class Meta:
        model = Detalle_Venta
        include_relationships = True
        load_instance = True


class HistorialVentaSchema(SQLAlchemyAutoSchema):  #11
    
    venta_HV = fields.Nested(VentaSchema)
    usuario_HV= fields.Nested(UsuarioSchema)
    

    class Meta:
        model = Historial_Venta
        include_relationships = True
        load_instance = True


class HistorialProductosSchema(SQLAlchemyAutoSchema):  #11
    
    usuario_HP= fields.Nested(UsuarioSchema)
    producto_HP= fields.Nested(ProductoSchema)
    rol_HP= fields.Nested(RolSchema)

    class Meta:
        model = Historial_Productos
        include_relationships = True
        load_instance = True

class HistorialGeneralSchema(SQLAlchemyAutoSchema):  #11
    
    usuario_HG= fields.Nested(UsuarioSchema)
    HV_HG= fields.Nested(HistorialVentaSchema)
    HP_HG= fields.Nested(HistorialProductosSchema)
    rol_HG= fields.Nested(RolSchema)

    class Meta:
        model = Historial_General
        include_relationships = True
        load_instance = True






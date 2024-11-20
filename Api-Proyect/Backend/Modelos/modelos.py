
from marshmallow import fields
from flask_sqlalchemy import SQLAlchemy
import enum

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

db = SQLAlchemy()

class Rol(db.Model):
    
    
    Id_Rol = db.Column(db.Integer, primary_key=True)
    Nombre = db.Column(db.String(180))
    
    Usuario= db.relationship('Usuario', back_populates="Rol")


class Proveedor(db.Model):
    
    Id_Proveedor = db.Column(db.Integer, primary_key=True)
    Nombre_Prov = db.Column(db.String(180))
    Telefono_Prov = db.Column(db.String(15))  
    Direccion_Prov = db.Column(db.String(50))

    Fecha_Registro_Prod= db.relationship('Fecha_Registro_Prod', back_populates="Proveedor")
    Producto= db.relationship('Producto', back_populates="Proveedor")


class Usuario(db.Model):
    
    Id_Usuario = db.Column(db.Integer, primary_key=True)
    Nombre_Usu = db.Column(db.String(250))
    Contraseña_Usu = db.Column(db.String(255))
    Cedula_Usu = db.Column(db.String(20))
    Email_Usu = db.Column(db.String(250))
    Telefono_Usu = db.Column(db.String(15))  # Cambiado de Integer a String para telefonos
    Fecha_Contrato_Inicio = db.Column(db.DateTime)
    FK_Id_Rol = db.Column(db.Integer, db.ForeignKey('Rol.Id_Rol'))
    
    Rol = db.relationship('Rol', back_populates="Usuario")
    Venta_Empleado = db.relationship('Venta', back_populates='Empleado')

class Categoria(db.Model):
    
    Id_Categoria = db.Column(db.Integer, primary_key=True)
    Nombre_Cat = db.Column(db.String(80))
    Descripcion_Cat = db.Column(db.String(150))
    
    Subcategoria_Categoria = db.relationship('Subcategoria', back_populates="Categoria")

class Subcategoria(db.Model):

    Id_Subcategoria = db.Column(db.Integer, primary_key=True)
    Nombre_Subcategoria = db.Column(db.String(250))
    Descripcion_Subcategoria = db.Column(db.String(250))
    FK_Id_Categoria = db.Column(db.Integer, db.ForeignKey("Categoria.Id_Categoria"))

    Categoria = db.relationship('Categoria', back_populates="Subcategoria_Categoria")
    Producto = db.relationship('Producto', back_populates='Subcategoria')

    
class Producto(db.Model):
    
    Id_Producto = db.Column(db.Integer, primary_key=True, nullable=False)
    Nombre_Prod = db.Column(db.String(100))
    Medida_Prod = db.Column(db.Integer)
    Unidad_Medida_Prod = db.Column(db.String(80))
    Precio_Bruto_Prod = db.Column(db.Float(19,0))
    Precio_Neto_Unidad_Prod = db.Column(db.Float(19,2))
    Iva_Prod = db.Column(db.Float(3,2))
    Porcentaje_Ganancia = db.Column(db.Float(3,2))
    Unidades_Totales_Prod = db.Column(db.Integer)
    Estado_Prod = db.Column(db.String(50))
    Marca_Prod = db.Column(db.String(60))
    FK_Id_Proveedor = db.Column(db.Integer, db.ForeignKey("Proveedor.Id_Proveedor"))
    FK_Id_Subcategoria = db.Column(db.Integer, db.ForeignKey("Subcategoria.Id_Subcategoria"))
    
    Proveedor = db.relationship('Proveedor', back_populates='Producto')
    Subcategoria = db.relationship('Subcategoria', back_populates='Producto')
    Fecha_Registro_Prod= db.relationship('Fecha_Registro_Prod', back_populates="Producto")
    Detalle_Venta= db.relationship('Detalle_Venta', back_populates = "Producto")

class Venta(db.Model):
    

    Id_Venta = db.Column(db.Integer, primary_key=True)
    Fecha_Venta = db.Column(db.DateTime)
    Total_Venta = db.Column(db.Float)
    Forma_Pago_Fact = db.Column(db.String(50))
    FK_Id_Usuario = db.Column(db.Integer, db.ForeignKey("Usuario.Id_Usuario"))
 
    Usuario = db.relationship('Usuario', back_populates='Venta_Usuario')
    Detalle_Venta= db.relationship('Detalle_Venta', back_populates = "Venta")

class Factura(db.Model):
    

    Id_Factura = db.Column(db.Integer, primary_key=True)
    Fecha_Generacion_Fact = db.Column(db.DateTime)
    Impuestos_Fact= db.Column(db.Float(5,2))
    
    Detalle_Venta= db.relationship('Detalle_Venta', back_populates = "Factura")

class Detalle_Venta(db.Model):

    Id_Detalle_Venta = db. Column(db.Integer, primary_key=True)
    Cantidad = db.Column(db.Integer)
    Precio_Unidad = db.Column(db.Float)
    FK_Id_Venta = db.Column(db.Integer, db.ForeignKey("Venta.Id_Venta"))
    FK_Id_Producto = db.Column(db.Integer, db.ForeignKey("Producto.Id_Producto"))
    FK_Id_Factura = db.Column(db.Integer, db.ForeignKey("Factura.Id_Factura"))
    
    Factura= db.relationship('Factura', back_populates = "Detalle_Venta")
    Producto= db.relationship('Producto', back_populates = "Detalle_Venta")
    Venta= db.relationship('Venta', back_populates = "Detalle_Venta")


class Fecha_Registro_Prod(db.Model):
    
    Id_Fecha_Registro = db.Column(db.Integer, primary_key=True, nullable=False)
    Fecha_Registro = db.Column(db.Date)
    Cantidad = db.Column(db.Integer)
    FK_Id_Proveedor = db.Column(db.Integer, db.ForeignKey("Proveedor.Id_Proveedor"))
    FK_Id_Producto = db.Column(db.Integer, db.ForeignKey("Producto.Id_Producto"))
    
    
    Producto = db.relationship('Producto', back_populates="Fecha_Registro_Prod")
    Proveedor= db.relationship('Proveedor', back_populates="Fecha_Registro_Prod")


    
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
    
    Rol = fields.Nested(RolSchema)

    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True

class VentaSchema(SQLAlchemyAutoSchema):  #9
    
    Usuario = fields.Nested(UsuarioSchema)
     
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
    
    Categoria = fields.Nested(CategoriaSchema)

    class Meta:
        model = Subcategoria
        include_relationships = True
        load_instance = True

class ProductoSchema(SQLAlchemyAutoSchema):  #8
    
    Proveedor = fields.Nested(ProveedorSchema)
    Subcategoria = fields.Nested(SubcategoriaSchema)

    class Meta:
        model = Producto
        include_relationships = True
        load_instance = True

class Fecha_Registro_Prod (SQLAlchemyAutoSchema): #4
    
    Proveedor = fields.Nested(ProveedorSchema)
    Producto = fields.Nested(ProductoSchema)
    
    class Meta:
        model = Fecha_Registro_Prod
        include_relationships = True
        load_instance = True



class FacturaSchema(SQLAlchemyAutoSchema): #10

    class Meta:
        model = Factura
        include_relationships = True
        load_instance = True


class Detalle_VentaSchema(SQLAlchemyAutoSchema):  #11
    
    Venta = fields.Nested(VentaSchema)
    Producto = fields.Nested(ProductoSchema)
    Factura = fields.Nested(FacturaSchema)

    class Meta:
        model = Detalle_Venta
        include_relationships = True
        load_instance = True


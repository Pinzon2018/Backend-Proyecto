from sqlalchemy import Enum
from marshmallow import fields
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy  # => ORM
from datetime import datetime
from sqlalchemy import DateTime



app = Flask(__name__)  # instancia de flask

# configuración de la conexion de la base de datos y migracion
USER_DB = 'root'
PASS_DB = 'paula10'
URL_DB = 'localhost'
NAME_DB = 'bellaYActualV3'
FULL_URL_DB = f'mysql+pymysql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}'

app.config['SQLALCHEMY_DATABASE_URI'] = FULL_URL_DB
app.config['SQL_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# migracion de datos
migrate = Migrate()
migrate.init_app(app, db)

#creacion de tablas 

class Rol(db.Model): #db.model es una clase base de SQLAlchemy al utilizarla con Flask
    __tablename__ = 'Rol'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(180))
    descripcion = db.Column(db.String(180))
    

    def __init__(self, id, nombre, descripcion): #construtor que inicializa        
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
    
    def json(self): # conversion a formato json
        return {'id': self.id, 'nombre': self.nombre, 'descripcion': self.descripcion} #devuelve un diccionario
    
    def __str__(self):  #metodo __str__
        return str(self.__class__) + ":" + str(self.__dict__) #devuelve el nombre de la clase y el diccionario en formato string legible

class Empleado(db.Model):
    __tablename__ = 'Empleado'
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(250))
    apellidos = db.Column(db.String(250))
    correo = db.Column(db.String(250))
    telefono = db.Column(db.Integer)
    fechaContratoInicio = db.Column(db.DateTime)
    fechaContratoFinalizado = db.Column(db.DateTime)
    Rol = db.Column(db.Integer, db.ForeignKey("Rol.id"))
    

    def __init__(self, id, nombres, apellidos, correo, telefono, fechaContratoInicio, fechaContratoFinalizado, idRol):
        self.id = id
        self.nombres = nombres
        self.apellidos = apellidos
        self.correo = correo
        self.telefono = telefono
        self.fechaContratoInicio = fechaContratoInicio
        self.fechaContratoFinalizado = fechaContratoFinalizado
        self.idRol = idRol

    def json(self): 
   
        return{'id': self.id, 'nombres': self.nombres, 'apellidos': self.apellidos, 'telefono': self.telefono, 'fechaContratoInicio': self.fechaContratoInicio, 'fechaContratoFinalizado': self.fechaContratoFinalizado, 'idRol': self.idRol}

    def __str__(self):  #metodo __str__
        return str(self.__class__) + ":" + str(self.__dict__)






class Categoria(db.Model):
    __tablename__ = 'Categoria'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(250))
    descripcion = db.Column(db.String(250))
    

    def __init__(self, id, nombre, descripcion):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion

    def json(self): 
   
        return{'id': self.id, 'nombre': self.nombre, 'descripcion': self.descripcion}
    
    def __str__(self):  
        return str(self.__class__) + ":" + str(self.__dict__)


class Subcategoria(db.Model):
    __tablename__ = 'Subcategoria'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(250))
    descripcion = db.Column(db.String(250))
    Categoria =  db.Column(db.Integer, db.ForeignKey("Categoria.id"))

    
    
    def __init__(self, nombre, descripcion, Categoria):
        self.nombre = nombre
        self.descripcion = descripcion
        self.Categoria = Categoria

   
    def json(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'Categoria': self.Categoria
        }
    
    def __str__(self):  
        return str(self.__class__) + ":" + str(self.__dict__)

class Producto(db.Model):
    __tablename__ = 'Producto'

    id = db.Column(db.Integer, primary_key=True)
    nombreProd = db.Column(db.String(250))
    medidaProd = db.Column(db.Integer)
    unidadMedidaProd = db.Column(db.String(250))
    precioUnidadProd = db.Column(db.Float)
    costoProd = db.Column(db.Float)
    ivaProd = db.Column(db.Float)
    porcentajeGanancia = db.Column(db.Float)
    unidadesTotalesProd = db.Column(db.Integer)
    estado = db.Column(db.String(250))
    marcaProd = db.Column(db.String(250))
    proveedor = db.Column(db.Integer, db.ForeignKey("Proveedor.id"))
    subcategoria = db.Column(db.Integer, db.ForeignKey("Subcategoria.id"))
    
    
    
    
    def __init__(self, nombre_prod, medida_prod, unidad_medida_prod, precioUnidadProd, costo_prod, iva_prod, 
                 porcentaje_ganancia, unidades_totales_prod, estado, marca_prod, id_proveedor, id_subcategoria):
        self.nombre_prod = nombre_prod
        self.medida_prod = medida_prod
        self.unidad_medida_prod = unidad_medida_prod
        self.precioUnidadProd = precioUnidadProd
        self.costo_prod = costo_prod
        self.iva_prod = iva_prod
        self.porcentaje_ganancia = porcentaje_ganancia
        self.unidades_totales_prod = unidades_totales_prod
        self.estado = estado
        self.marca_prod = marca_prod
        self.id_proveedor = id_proveedor
        self.id_subcategoria = id_subcategoria

    
    def json(self):
        return {
            'id': self.id,
            'nombre_prod': self.nombre_prod,
            'medida_prod': self.medida_prod,
            'unidad_medida_prod': self.unidad_medida_prod,
            'precioUnidadProd' : self.precioUnidadProd,
            'costo_prod': self.costo_prod,
            'iva_prod': self.iva_prod,
            'porcentaje_ganancia': self.porcentaje_ganancia,
            'unidades_totales_prod': self.unidades_totales_prod,
            'estado': self.estado,
            'marca_prod': self.marca_prod,
            'id_proveedor': self.id_proveedor,
            'id_subcategoria': self.id_subcategoria
        }
    
    def __str__(self):  
        return str(self.__class__) + ":" + str(self.__dict__)


class Venta(db.Model):
    __tablename__ = 'Venta'
    id = db.Column(db.Integer, primary_key=True)
    fechaVenta = db.Column(db.DateTime)
    totalVenta = db.Column(db.Float)
    empleado = db.Column(db.Integer, db.ForeignKey("Empleado.id"))
 
   
 
    def __init__(self, fecha_venta, totalVenta, idEmpleado):
        self.fecha_venta = fecha_venta
        self.total_venta = totalVenta
        self.id_empleado = idEmpleado

    
    def json(self):
        return {
            'id': self.id,
            'fechaVenta': self.fechaVenta,
            'totalVenta': self.totalVenta,
            'idEmpleado': self.idEmpleado
        }

    def __str__(self):  
        return str(self.__class__) + ":" + str(self.__dict__)

class empresasProveedoras(db.Model): 
    __tablename__ = 'empresasProveedoras'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(250))
    encargadoDespacho = db.Column(db.String(180))
    telefonoEmpresa = db.Column(db.String(180))
    direccionEmpresa = db.Column(db.String(180))
    
    


    def __init__(self, nombre, encargadoDespacho, telefonoEmpresa, direccionEmpresa):
        self.nombre = nombre
        self.encargadoDespacho = encargadoDespacho
        self.telefonoEmpresa = telefonoEmpresa
        self.direccionEmpresa = direccionEmpresa

    
    def json(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'encargadoDespacho': self.encargadoDespacho,
            'telefonoEmpresa': self.telefonoEmpresa,
            'direccionEmpresa': self.direccionEmpresa
        }
    
    def __str__(self):  
        return str(self.__class__) + ":" + str(self.__dict__)

class Proveedor(db.Model):
    __tablename__ = 'Proveedor'
    
    id = db.Column(db.Integer, primary_key=True)
    nombreProv = db.Column(db.String(180))
    apellidoProv = db.Column(db.String(180))
    cedula = db.Column(db.String(180))
    telefonoProv = db.Column(db.String(180))
    direccionProv = db.Column(db.String(180))
    empresasProveedoras = db.Column(db.Integer, db.ForeignKey("empresasProveedoras.id"))
    
    

    def __init__(self, nombreProv, apellidoProv, cedula, telefonoProv, direccionProv, empresasProveedoras):
        self.nombreProv = nombreProv
        self.apellidoProv = apellidoProv
        self.cedula = cedula
        self.telefonoProv = telefonoProv
        self.direccionProv = direccionProv
        self.empresasProveedoras = empresasProveedoras

   
    def json(self):
        return {
            'id': self.id,
            'nombreProv': self.nombreProv,
            'apellidoProv': self.apellidoProv,
            'cedula': self.cedula,
            'telefonoProv': self.telefonoProv,
            'direccionProv': self.direccionProv,
            'empresasProveedoras': self.empresasProveedoras
        }
    
    def __str__(self):  
        return str(self.__class__) + ":" + str(self.__dict__)





class Cliente(db.Model):
    __tablename__ = 'Cliente'
    
    id = db.Column(db.Integer, primary_key=True)
    nombresCliente = db.Column(db.String(250))
    apellidosCliente = db.Column(db.String(180))
    cedula = db.Column(db.String(180))
    direccion = db.Column(db.String(180))
    telefono = db.Column(db.String(180))

    def __init__(self, nombresCliente, apellidosCliente, cedula, direccion, telefono):
        self.nombresCliente = nombresCliente
        self.apellidosCliente = apellidosCliente
        self.cedula = cedula
        self.direccion = direccion
        self.telefono = telefono

    
    def json(self):
        return {
            'id': self.id,
            'nombresCliente': self.nombresCliente,
            'apellidosCliente': self.apellidosCliente,
            'cedula': self.cedula,
            'direccion': self.direccion,
            'telefono': self.telefono
        }

    def __str__(self):  
        return str(self.__class__) + ":" + str(self.__dict__)
    
class tablaDePagos (db.Model):
    __tablename__ = 'tablaDePagos'
    
    id = db.Column (db.Integer, primary_key = True)
    metodosDePago = db.Column(db.String(250))
    totalAPagar = db.Column(db.Numeric(19,0))
    fechaDePago = db.Column(db.DateTime)
    estadoPago = db.Column(db.String(250))
    venta = db.Column(db.Integer, db.ForeignKey ("Venta.id"))

    
    
    def __init__(self, id, metodosDePago, totalAPagar, fechaDePago, estadoPago, venta):
        self.id= id
        self.metodosDePago = metodosDePago
        self.totalAPagar = totalAPagar
        self.fechaDePago = fechaDePago
        self.estadoPago = estadoPago
        self.venta = venta

    
    def json(self):
        return {
            'id': self.id,
            'metodosDePago': self.metodosDePago,
            'totalAPagar': self.totalAPagar,
            'fechaDePago': self.fechaDePago,
            'estadoPago': self.estadoPago,
            'venta': self.venta
        }

    def __str__(self):  
        return str(self.__class__) + ":" + str(self.__dict__)


class Factura(db.Model):
    __tablename__ = 'Factura'

    id = db.Column(db. Integer, primary_key= True)
    fechaGeneracionFactura = db.Column (db.DateTime)
    impuestosFactura = db.Column (db.Numeric(19,0))
    tablaDePagos = db.Column (db.Integer, db.ForeignKey('tablaDePagos.id'))
    
    
    
    def __init__(self, id, fechaGeneracionFactura, impuestosFactura, tablaDePagos):
        self.id= id
        self.fechaGeneracionFactura = fechaGeneracionFactura
        self.impuestosFactura = impuestosFactura
        self.tablaDePagos = tablaDePagos

    
    def json(self):
        return {
            'id': self.id,
            'fechaGeneracionFactura': self.fechaGeneracionFactura,
            'impuestosFactura': self.impuestosFactura,
            'tablaDePagos': self.tablaDePagos
        }

    def __str__(self):  
        return str(self.__class__) + ":" + str(self.__dict__)


    

class detalleVentaProductos(db.Model):
    __tablename__ = 'detalleVentaProductos'
    id = db. Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer)
    precioUnidad = db.Column(db.Float)
    cedula = db.Column(db.String(180))
    direccion = db.Column(db.String(180))
    telefono = db.Column(db.String(180))
    venta = db.Column(db.Integer, db.ForeignKey("Venta.id"))
    producto = db.Column(db.Integer, db.ForeignKey("Producto.id"))
    cliente = db.Column(db.Integer, db.ForeignKey("Cliente.id"))
  
    


    def __init__(self, id, cantidad, precioUnidad, cedula, direccion, telefono, Venta, Producto, Cliente):
        self.id = id
        self.cantidad = cantidad
        self.precioUnidad = precioUnidad
        self.cedula = cedula
        self.direccion = direccion
        self.telefono = telefono
        self.Venta = Venta
        self.Producto = Producto
        self.Cliente = Cliente

    
    def json(self):
        return {
            'id': self.id,
            'cantidad': self.cantidad,
            'precioUnidad': self.precioUnidad,
            'cedula': self.cedula,
            'direccion': self.direccion,
            'telefono': self.telefono,
            'Venta': self.Venta,
            'Producto': self.Producto,
            'Cliente': self.Cliente
        }

    
    def __str__(self):
        return str(self.__class__) + ":" + str(self.__dict__)
    








#Serializacion



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

class EmpleadoSchema(SQLAlchemyAutoSchema):   #2
    
    rol = fields.Nested(RolSchema)

    class Meta:
        model = Empleado
        include_relationships = True
        load_instance = True

class VentaSchema(SQLAlchemyAutoSchema):  #9
    
    Empleado = fields.Nested(EmpleadoSchema)
   
    class Meta:
        model = Venta
        include_relationships = True
        load_instance = True


class tablaDePagosSchema (SQLAlchemyAutoSchema): #4
    
    Venta = fields.Nested(VentaSchema)
    
    class Meta:
        model = tablaDePagos
        include_relationships = True
        load_instance = True

class empresasProveedorasSchema(SQLAlchemyAutoSchema): #4
    
    class Meta:
        model = empresasProveedoras
        include_relationships = True
        load_instance = True

class ProveedorSchema(SQLAlchemyAutoSchema): #3
    
    empresasProveedoras = fields.Nested(empresasProveedorasSchema) 

    class Meta:
        model = Proveedor
        include_relationships = True
        load_instance = True



class ClienteSchema(SQLAlchemyAutoSchema):  #5
    
    class Meta:
        model = Cliente
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




class FacturaSchema(SQLAlchemyAutoSchema): #10
    
    tablaDePagos= fields.Nested(tablaDePagosSchema)

    class Meta:
        model = Factura
        include_relationships = True
        load_instance = True


class detalleVentaProductosSchema(SQLAlchemyAutoSchema):  #11
    
    Venta = fields.Nested(VentaSchema)
    Producto = fields.Nested(ProductoSchema)
    Cliente = fields.Nested(ClienteSchema)

    class Meta:
        model = detalleVentaProductos
        include_relationships = True
        load_instance = True
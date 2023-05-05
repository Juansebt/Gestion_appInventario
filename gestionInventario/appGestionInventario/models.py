from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from datetime import datetime

# Create your models here.

estadosMantenimiento = [
    ('Satisfactorio','Satisfactorio'),
    ('Requiere Ajuste','Requiere Ajuste'),
    ('Requiere Reparación','Requiere Reparación'),
    ('Requiere Remplazo','Requiere Remplazo'),
    ('Defecto Corregido','Defecto Corregido'),
]

tiposProveedor = [
    ('Persona Júridica','Persona Júridica'),
    ('Persona Natural','Persona Natural'),
]

tiposUsuario = [
    ('Administrativo','Administrativo'),
    ('Instructor','Instructor'),
    ('Aprendiz','Aprendiz'),
]

tiposElemento = [
    ('EQU','Equipo'),
    ('HER','Herramientas'),
    ('MAT','Materiales'),
    ('MAQ','Maquinaria'),
]

estadosElementos = [
    ('Bueno','Bueno'),
    ('Regular','Regular'),
    ('Malo','Malo'),
]

estadosSolicitud = [
    ('Solicitada','Solicitada'),
    ('Aprovada','Aprovada'),
    ('Rechazada','Rechazada'),
    ('Atendida','Atendida'),
    ('Cancelada','Cancelada'),
]

class Ficha(models.Model):
    ficCodigo = models.IntegerField(unique=True, db_comments="Código de la ficha")
    ficNombre = models.CharField(max_length=100, db_comments="Nombre de la ficha")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True, db_comments="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True, db_comments="Fecha y hora de la última actualización")
    
    def __str__(self) -> str:
        return f"{self.ficCodigo} - {self.ficNombre}"
    
class UnidadMedida(models.Model):
    uniNombre = models.CharField(max_length=45, unique=True, db_comments="Nombre de la unidad de medida")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True, db_comments="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True, db_comments="Fecha y hora de la última actualización")
    
    def __str__(self) -> str:
        return f"{self.uniNombre}"
    
class Proveedor(models.Model):
    proTipo = models.CharField(max_length=20, choices=tiposProveedor, db_comments="Tipo de proveedor")
    proIdentificacion = models.CharField(max_length=15, unique=True, db_comments="Identificación del proveedor CC - NIT")
    proNombre = models.CharField(max_length=60, db_comments="Nombre del proveedor")
    proRepresentanteLegal = models.CharField(max_length=60, null=True, db_comments="Nombre del representate legal si es persona júridica")
    proTelefono = models.IntegerField(max_length=15, null=True, db_comments="Número telefónico del proveedor")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True, db_comments="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True, db_comments="Fecha y hora de la última actualización")
    
    def __str__(self) -> str:
        return f"{self.proNombre}"
    
class User(AbstractUser): #Hereda del metodo AbstractUser
    userFoto = models.FileField(upload_to=f"usuarios/", null=True, blank=True, db_comments="Foto del usuario")
    userTipo = models.CharField(max_length=25, choices=tiposUsuario, db_comments="Tipo de usuario")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True, db_comments="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True, db_comments="Fecha y hora de la última actualización")
    
    def __str__(self) -> str:
        return f"{self.username}"
    
class Elemento(models.Model):
    eleCodigo = models.CharField(max_length=15, unique=True, db_comments="Código del elemento")
    eleNombre = models.CharField(max_length=50, db_comments="Nombre del elemento")
    eleTipo = models.CharField(max_length=3, choices=tiposElemento, db_comments="Tipo de elemento")
    eleEstado = models.CharField(max_length=20, choices=estadosElementos, db_comments="Estado del elemento")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True, db_comments="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True, db_comments="Fecha y hora de la última actualización")
    
    def __str__(self) -> str:
        return f"{self.eleCodigo} - {self.eleNombre}"
    
class Devolutivo(models.Model):
    devPlacaSena = models.CharField(max_length=45, unique=True, db_comments="Código inventario SENA")
    devSerial = models.CharField(max_length=45, null=True, db_comments="Serial del elemento devolutivo")
    devDescripcion = models.TextField(db_comments="Descripción del elemento devolutivo")
    devMarca = models.CharField(max_length=45, null=True, db_comments="Marca del elemento devolutivo")
    devFechaIngresoSENA = models.DateField(db_comments="Fecha de ingreso del elemento al inventario SENA")
    devValor = models.DecimalField(max_digits=11, decimal_places=2, db_comments="Valor del elemento registrado en el inventario SENA")
    devFoto = models.FileField(upload_to=f"elementos/", null=True, blank=True, db_comments="Foto de los elementos devolutivos")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True, db_comments="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True, db_comments="Fecha y hora de la última actualización")
    devElemento = models.ForeignKey(Elemento, on_delete=models.PROTECT, db_comments="Llave foranea - hace la relación al elemento") #Elemento foraneo - relación con la clase Elemento
    
    def __str__(self) -> str:
        return f"{self.devElemento}"
    
class Material(models.Model):
    matReferencia = models.TextField(null=True, db_comments="Referencia o descripción del material del elemento")
    matMarca = models.CharField(max_length=50, null=True, db_comments="Marca del material del elemento si tiene")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True, db_comments="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True, db_comments="Fecha y hora de la última actualización")
    matElemento = models.ForeignKey(Elemento, on_delete=models.PROTECT, db_comments="Llave foranea - referencia al elemento")
    matUnidadMedida = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT, db_comments="Llave foranea que referencia a la unidad de medida")
    
    def __str__(self) -> str:
        return f"{self.matElemento}"
    
class EntradaMaterial(models.Model):
    entNumeroFactura = models.CharField(max_length=15, db_comments="Número de la factura")
    entFechaHora = models.DateTimeField(auto_now_add=True, db_comments="Fecha y hora que entregan los materiales")
    entEntregadoPor = models.CharField(max_length=100, db_comments="Nombre de la persona que entrega los materiales")
    entObservaciones = models.TextField(null=True, db_comments="Observaciones que se requieran hacer")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True, db_comments="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True, db_comments="Fecha y hora de la última actualización")
    entProveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, db_comments="Llave foranea - referencia al proveedor que entrega los materiales")
    entUsuarioRecibe = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_comments="Llave foranea - referencia al usuario que recibe")
    
    def __str__(self) -> str:
        return f"{self.entNumeroFactura}"
    
class DetalleEntradaMaterial(models.Model):
    detCantidad = models.IntegerField(db_comments="Canidad que ingresa del material")
    detPrecioUnitario = models.IntegerField(db_comments="Precio del material que ingresa")
    detEstado = models.CharField(max_length=10, choices=estadosElementos, db_comments="Estado del elemento")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True, db_comments="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True, db_comments="Fecha y hora de la última actualización")
    detEntradaMaterial = models.ForeignKey(EntradaMaterial, on_delete=models.PROTECT, db_comments="Llave foranea - referencia la entrada registrada")
    detMaterial = models.ForeignKey(Material, on_delete=models.PROTECT, db_comments="Llave foranea - referencia al material que se esta registrando")
    
    def __str__(self) -> str:
        return f"{self.detMaterial} - {self.detCantidad}"
    
class SolicitudElemento(models.Model):
    solProyecto = models.TextField(db_comments="Nombre del proyecto que se esta desarrollando")
    solFechaHoraRequerida = models.DateTimeField(null=True, db_comments="Fecha y hora que se requiere el elemento")
    solEstado = models.CharField(max_length=25, choices=estadosSolicitud, db_comments="Estado en que puede estar la solicitud")
    solObservaciones = models.TextField(null=True, db_comments="Observaciones de la soliciud si se requiere")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True, db_comments="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True, db_comments="Fecha y hora de la última actualización")
    solFicha = models.ForeignKey(Ficha, on_delete=models.PROTECT, db_comments="Llave foranes - hace referencia a las fichas donde se utilizarán los elementos")
    solUsuario = models.ForeignKey(User, on_delete=models.PROTECT, db_comments="Llave foranea - hace referencia a los usuarios que hacen la solicitud")
    
    def __str__(self) -> str:
        return f"{self.solProyecto} - {self.solFicha} - {self.solUsuario}"
    
class DetalleSolicitud(models.Model):
    detCantidadRequerida = models.IntegerField(db_comments="Cantidad que se requiere del elemento")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True, db_comments="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True, db_comments="Fecha y hora de la última actualización")
    detElemento = models.ForeignKey(Elemento, on_delete=models.PROTECT, db_comments="Llave foranea - referecia al elemento solicitado")
    detSolicitud = models.ForeignKey(SolicitudElemento, on_delete=models.PROTECT, db_comments="Llave foranea - hace referencia a la soliciud del detalle")
    detUnidadMedida = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT, db_comments="Llave foranea - hace referencia a la unidad de medida que se requiere")
    
    def __str__(self) -> str:
        return f"{self.detCantidadRequerida} - {self.detElemento}"
    
class SalidaDetalleSolicitud(models.Model):
    salCantidadEntregada = models.IntegerField(db_comments="Cantidad del elemento entregado")
    solObservaciones = models.TextField(null=True, db_comments="Onservaciones de la salida de los elementos")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True, db_comments="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True, db_comments="Fecha y hora de la última actualización")
    salDetalleSolicitud = models.ForeignKey(DetalleSolicitud, on_delete=models.PROTECT, db_comments="Llave foranea - referencia al detalle de la solicitud")
    
    def __str__(self) -> str:
        return f"{self.salCantidadEntregada} - {self.salDetalleSolicitud}"
    
class DevolucionElemento(models.Model):
    devCantidadDevolucion = models.IntegerField(db_comments="Cantidad devuelta por el instructor después de utilizarla en la formación")
    devObservaciones = models.TextField(null=True, db_comments="Observación que el asistene quiera agregar en la devolución")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True, db_comments="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True, db_comments="Fecha y hora de la última actualización")
    devSalida = models.ForeignKey(SalidaDetalleSolicitud, on_delete=models.PROTECT, db_comments="Llave foranea - referencia a la salida de los elementos")
    devUsuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, db_comments="Usuario que hace la devolción de los elementos - Llave foranea")
    
    def __str__(self) -> str:
        return f"{self.devSalida} - {self.devCantidadDevolucion}"
    
class EstadoMantenimiento(models.Model):
    estNombre = models.CharField(max_length=25, choices=estadosMantenimiento, unique=True, db_comments="Nombre del estado de mantenimiento")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True, db_comments="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True, db_comments="Fecha y hora de la última actualización")
    
    def __str__(self) -> str:
        return f"{self.estNombre}"
    
class Mantenimiento(models.Model):
    manObservaciones = models.TextField(db_comments="Espacio para registrar las observaciones presentadas en el mantenimiento")
    manFechaHoraMantenimiento = models.DateTimeField(db_comments="Fecha y hora en la que se realizo en mantenimiento")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True, db_comments="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True, db_comments="Fecha y hora de la última actualización")
    manElemento = models.ForeignKey(Elemento, on_delete=models.PROTECT, db_comments="Llave foranea - referencia al elemento")
    manEstado = models.ForeignKey(EstadoMantenimiento, on_delete=models.PROTECT, db_comments="Llave foranea - referencia al estado del elemento")
    manUsuario = models.ForeignKey(settings.AUTH_USER_MODEL, db_comments="Llave foranea - referencia al usuario")
    
    def __str__(self) -> str:
        return f"{self.manElemento} - {self.manEstado}"
    
class UbicacionFisica(models.Model):
    ubiDeposito = models.SmallIntegerField(db_comments="Número de ubicación del desposito")
    ubiEstante = models.SmallIntegerField(null=True, db_comments="Número de ubicación del estante")
    ubiEntrepano = models.SmallIntegerField(null=True, db_comments="Número de ubicación del entrepano")
    ubiLocker = models.SmallIntegerField(db_comments="Número de ubicación del locker")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True, db_comments="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True, db_comments="Fecha y hora de la última actualización")
    ubiElemento = models.ForeignKey(Elemento, on_delete=models.PROTECT, db_comments="Llave foranea - referencia al elemento")
    
    def __str__(self) -> str:
        return f"{self.ubiElemento} - {self.ubiDeposito} - {self.ubiEstante} - {self.ubiEntrepano} - {self.ubiLocker}"
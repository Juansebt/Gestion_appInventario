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
    ('PJ','Persona Júridica'),
    ('PN','Persona Natural'),
]

tiposUsuario = [
    ('Administrativo','Administrativo'),
    ('Instructor','Instructor'),
    ('Aprendiz','Aprendiz'),
]

tiposElemento = [
    ('EQI','Equipo'),
    ('HER','Herramientas'),
    ('MAT','Materiales'),
    ('MAQ','Maquinaria'),
]

estadosElementos = [
    ('Bueno','Bueno'),
    ('Regular','Regular'),
    ('Malo','Malo'),
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
    
class EstadoMantenimiento(models.Model):
    estNombre = models.CharField(max_length=25, choices=estadosMantenimiento, unique=True, db_comments="Nombre del estado de mantenimiento")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True, db_comments="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True, db_comments="Fecha y hora de la última actualización")
    
    def __str__(self) -> str:
        return f"{self.estNombre}"
    
class Proveedor(models.Model):
    proTipo = models.CharField(max_length=2, choices=tiposProveedor, db_comments="Tipo de proveedor")
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
    devValor = models.DecimalField(db_comments="Valor del elemento registrado en el inventario SENA")
    devEstado = models.CharField(max_length=10, choices=estadosElementos, db_comments="Estado del elemento devolutivo")
    devFoto = models.FileField(upload_to=f"elementos/", null=True, blank=True, db_comments="Foto de los elementos devolutivos")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True, db_comments="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True, db_comments="Fecha y hora de la última actualización")
    devElemento = models.ForeignKey(Elemento, on_delete=models.PROTECT, db_comments="Llave foranea - hace la relación al elemento") #Elemento foraneo - relación con la clase Elemento
    
    def __str__(self) -> str:
        return f"{self.devElemento}"
    
class Material(models.Model):
    matReferencia = models.TextField(db_comments="Referencia del material del elemento")
    matMarca = models.CharField(max_length=50,null=True, db_comments="Marca del material del elemento")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True, db_comments="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True, db_comments="Fecha y hora de la última actualización")
    matElemento = models.ForeignKey(Elemento, on_delete=models.PROTECT, db_comments="Llave foranea - referencia al elemento")
    matUnidadMedida = models.ForeignKey(UnidadMedida, on_delete=models.PROTECT, db_comments="Llave foranea que referencia a UnidadMedida")
    
    def __str__(self) -> str:
        return f"{self.matReferencia} - {self.matElemento} - {self.matUnidadMedida}"
    
class UbicacionFisica(models.Model):
    ubiDeposito = models.SmallIntegerField(db_comments="Número de ubicación del desposito")
    ubiEstante = models.SmallIntegerField(db_comments="Número de ubicación del estante")
    ubiEntrepano = models.SmallIntegerField(db_comments="Número de ubicación del entrepano")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True, db_comments="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True, db_comments="Fecha y hora de la última actualización")
    ubiElemento = models.ForeignKey(Elemento, on_delete=models.PROTECT, db_comments="Llave foranea - referencia al elemento")
    
    def __str__(self) -> str:
        return f"{self.ubiElemento}"
    
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
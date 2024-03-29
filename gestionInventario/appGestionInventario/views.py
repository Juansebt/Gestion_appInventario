from django.shortcuts import render, redirect
from django.db import Error, transaction
from django.contrib.auth.models import Group
from appGestionInventario.models import *
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.contrib.auth import authenticate, logout
from django.http import JsonResponse
from smtplib import SMTPException
from django.contrib import auth
from django.conf import settings
from django import forms
import threading
import urllib
import json
import random
import string
import os

# Create your views here.

def inicio(request):
    return render(request, "inicio.html")

def vistaRegistrarUsuario(request):
    roles = Group.objects.all()
    retorno = {"roles":roles, "user":None, "tipoUsuario":tipoUsuario}
    return render(request, "administrador/frmRegistrarUsuario.html", retorno)

def vistaGestionarUsuarios(request):
    mensaje = ""
    estado = ""
    try:
        usuarios = User.objects.all()
        estado = True
    except Error as error:
        mensaje = f"Problemas al obtener los productos {error}"
    retorno = {"mensaje":mensaje, "estado":estado, "listaUsuarios":usuarios}
    return render(request, "administrador/listarUsuarios.html",retorno)

def registrarUsuario(request):
    estado = False
    mensaje = f""
    try:
        nombres = request.POST["txtNombres"]
        apellidos = request.POST["txtApellidos"]
        correo = request.POST["txtCorreo"]
        tipo = request.POST["cbTipo"]
        foto = request.FILES.get("fileFoto", False)
        idRol = int(request.POST["cbRol"])
        
        with transaction.atomic():
            # Crear un objeto de tipo User
            user = User(username=correo, first_name=nombres, last_name=apellidos, email=correo, userTipo=tipo, userFoto=foto)
            user.save()
            # obtener el Rol de acuerdo al id del rol
            rol = Group.objects.get(pk=idRol)
            # agregar al usuario a ese rol
            user.groups.add(rol)
            # si el rol es Administrador se habilita para que tenga acceso al sitio web del administrador
            if(rol.name=="Administrador"):
                user.is_staff = True
            # guardamos el usuario con lo que tenemos
            user.save()
            # llamamos la función generarPassword
            passwordGenerado = generarPassword()
            print(f"password {passwordGenerado}")
            # con el usuario creado llamamos a la función set_password que encripta el password
            # y lo agrega al campo password del user
            user.set_password(passwordGenerado)
            # se actualiza el user
            user.save()
            estado = True
            mensaje = f"Ususario agregado correctamente"
            retorno = {"mensaje":mensaje,"estado":estado}
            # enviar correo al usuario
            asunto = 'Registro Sistema CIES-NEIVA'
            mensaje = f'Cordial saludo, <b>{user.first_name} {user.last_name}</b>, nos permitimos \
                informarle que usted ha sido registrado en el sistema de Gestión de Inventarios \
                del centro de la industria, la empresa y los servicios CIES de la ciudad de Neiva.\
                    No permitimos enviarle las credenciales de ingreso a nuestro sistema.<br>\
                    <br><b>USERNAME: {user.username}\
                    <br><b>PASSWORD: {passwordGenerado}\
                    <br><br>Lo invitamos a ingresar al sistema en la url:\
                    https://gestioninventario.sena.edu.co.'
            threa = threading.Thread(target=enviarCorreo, args=(asunto,mensaje,user.email))
            threa.start()
            return redirect("/vistaGestionarUsuarios/", retorno)
    except Error as error:
        transaction.rollback()
        mensaje = f"{error}"
    retorno = {"mensaje":mensaje, "user":user, "estado":estado}
    return render(request, "administrador/frmRegistrarUsuario.html", retorno)

def generarPassword():
    longitud = 10
    caracteres = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
    password = ''
    for i in range(longitud):
        password += ''.join(random.choice(caracteres))
    return password

def vistaLogin(request):
    if (cerrarSesion):
        mensaje = f"Se ha cerrado sesión"
    retorno = {"mensaje":mensaje}
    return render(request,"login.html",retorno)

# class LoginForm(forms.Form):
#     password = forms.CharField(widget=forms.PasswordInput())

def login(request):
    # validar recaptcha
    """ Begin reCAPTCHA validation """
    recaptcha_response = request.POST.get('g-recaptcha-response')
    url = 'https://www.google.com/recaptcha/api/siteverify'
    values = {
        'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
        'response': recaptcha_response
    }
    data = urllib.parse.urlencode(values).encode()
    req = urllib.request.Request(url, data=data)
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode())
    print(result)
    """ End reCAPTCHA validation """
    
    if result['success']:
        username = request.POST['txtUsername']
        password = request.POST['txtPassword']
        user = authenticate(username=username, password=password)
        if user is not None:
            # registrar la varibale de sesión
            auth.login(request, user)
            if user.groups.filter(name='Administrador').exists():
                return redirect('/inicioAdministrador')
            elif user.groups.filter(name='Asistente').exists():
                return redirect('/inicioAsistente')
            else:
                return redirect('/inicioInstructor')
        else:
            mensaje = f"Usuario o contraseña incorrectas"
            return render(request,"login.html",{"mensaje":mensaje})
    else:
        mensaje = f"Debe validar primero el recaptcha"
        return render(request,"login.html",{"mensaje":mensaje})
    
def inicioAdministrador(request):
    if request.user.is_authenticated:
        return render(request,"administrador/inicio.html")
    else:
        retorno = {"mensaje":"Debe ingresar con sus credenciales"}
        return render(request,"login.html",retorno)
    
def inicioAsistente(request):
    if request.user.is_authenticated:
        return render(request,"asistente/inicio.html")
    else:
        retorno = {"mensaje":"Debe ingresar con sus credenciales"}
        return render(request,"login.html",retorno)
    
def inicioInstructor(request):
    if request.user.is_authenticated:
        return render(request,"instructor/inicio.html")
    else:
        retorno = {"mensaje":"Debe ingresar con sus credenciales"}
        return render(request,"login.html",retorno)

def enviarCorreo(asunto=None,mensaje=None,destinatario=None):
    remitente = settings.EMAIL_HOST_USER
    template = get_template('enviarCorreo.html')
    contenido = template.render({
        'destinatario': destinatario,
        'mensaje': mensaje,
        'asunto': asunto,
        'remitente': remitente,
    })
    try:
        correo = EmailMultiAlternatives(asunto, mensaje, remitente, [destinatario])
        correo.attach_alternative(contenido, 'text/html')
        correo.send(fail_silently=True)
    except SMTPException as error:
        print(error)
        
def cerrarSesion(request):
    logout(request)
    # eliminar la sesión actual
    request.session.flush()
    return redirect("/vistaLogin/")

def vistaGestionarDevolutivos(request):
    if request.user.is_authenticated:
        elementosDevolutivos = Devolutivo.objects.all()
        retorno = {"listaElementosDevolutivos":elementosDevolutivos}
        print(elementosDevolutivos)
        return render(request, "asistente/listarDevolutivos.html",retorno)
    else:
        mensaje = f"Debe iniciar sesión"
        return render(request, "login.html",{"mensaje":mensaje})
    
def vistaRegistrarDevolutivo(request):
    retorno = {"tipoElementos":tipoElemento,"estados":estadosElementos}
    print(retorno)
    return render(request,"asistente/frmRegistrarDevolutivos.html",retorno)

def registrarDevolutivo(request):
    estado = False
    mensaje = ""
    try:
        placaSena = request.POST["txtPlacaSena"]
        fechaInventarioSena = request.POST["txtFechaSena"]
        tipoElemento = request.POST["cbTipoElemento"]
        serial = request.POST.get("txtserial",False)
        marca = request.POST.get("txtMarca",False)
        valorUnitario = int(request.POST["txtValorUnitario"])
        estado = request.POST["cbEstado"]
        nombre = request.POST["txtNombre"]
        descripcion = request.POST["txtDescripcion"]
        deposito = request.POST["cbDeposito"]
        estante = request.POST.get("txtEstante",False)
        entrepano = request.POST.get("txtEntrepano",False)
        locker = request.POST.get("txtLocker",False)
        archivo = request.FILES.get("fileFoto",False)
        
        with transaction.atomic():
            # obtener cuantos elementos se han registrado
            cantidad = Elemento.objects.all().count()
            # crear un código a partir de la cantidad, ajustando 0 al inicio
            codigoElemento = tipoElemento.upper() + str(cantidad+1).rjust(6, '0')
            # crear ele elemento
            elemento = Elemento(eleCodigo = codigoElemento, eleNombre = nombre,
                                eleTipo = tipoElemento, eleEstado = estado)
            # salvar el elemento en la base de datos
            elemento.save()
            # crear objeto ubicación física del elemento
            ubicacion = UbicacionFisica(ubiDeposito = deposito, ubiEstante = estante,
                                        ubiEntrepano = entrepano, ubiLocker = locker,
                                        ubiElemento = elemento)
            # registrar la ubicación fisíca del en la base de datos
            ubicacion.save()
            # crear devolutivo
            elementoDevolutivo = Devolutivo(devPlacaSena = placaSena, devSerial = serial,
                                             devDescripcion = descripcion, devMarca = marca,
                                             devFechaIngresoSENA = fechaInventarioSena,
                                             devValor = valorUnitario, devFoto = archivo, devElemento = elemento)
            # registrar el elemento en la base de datos
            elementoDevolutivo.save()
            estado = True
            mensaje = f"Elemento Devolutivo registrado satisfactoriamente con el código: {codigoElemento}"
    except Error as error:
        transaction.rollback()
        mensaje = f"Error {error}"
    retorno = {"mensaje":mensaje,"devolutivo":elementoDevolutivo,"estado":estado}
    return render(request,"asistente/frmRegistrarDevolutivos.html",retorno)

def vistaRegistrarMaterial(request):
    unidadesMedidad = UnidadMedida.objects.all()
    retorno = {"unidadesMedida":unidadesMedidad,"estados":estadosElementos}
    return render(request,"asistente/frmRegistrarMaterial.html", retorno)

def registrarMaterial(request):
    estado = False
    mensaje = ""
    try:
        nombre = request.POST["txtNombre"]
        # unidadMedida = int(request.POST["cbUnidadMedida"])
        marca = request.POST.get("txtMarca",None)
        descripcion = request.POST.get("txtDescripcion",None)
        estado = request.POST["cbEstado"]
        deposito = request.POST["cbDeposito"]
        estante = request.POST.get("txtEstante",False)
        entrepano = request.POST.get("txtEntrepano",False)
        locker = request.POST.get("txtLocker",False)
        with transaction.atomic():
            # unidadM = UnidadMedida.objects.get(pk=unidadMedida)
            cantidad = Elemento.objects.all().filter(eleTipo='MAT').count()
            codigoElemento = "MAT" + str(cantidad+1).rjust(6, '0')
            #crear elemento
            elemento = Elemento(eleCodigo = codigoElemento, eleNombre = nombre,
                                eleTipo = "MAT", eleEstado = estado)
            #slavar elemento en la base de datos
            elemento.save()
            #crear el maerial
            material = Material(matReferencia = descripcion, matMarca = marca, matElemento = elemento)
            material.save()
            #crear objeto ubicación física del elemento
            ubicacion = UbicacionFisica(ubiDeposito = deposito, ubiEstante = estante,
                                        ubiEntrepano = entrepano, ubiLocker = locker, ubiElemento = elemento)
            #registrar en la base de datos la ubicación física del elemento
            ubicacion.save()
            estado = True
            mensaje = f"Material registrado satisfactoriamente con el código: {codigoElemento}"
    except Error as error:
        transaction.rollback()
        mensaje = f"Error {error}"
    retorno = {"mensaje":mensaje,"material":material,"estado":estado}
    return render(request, "asistente/frmRegistrarMaterial.html", retorno)

def vistaEntradaMaterial(request):
    proveedores = Proveedor.objects.all()
    usuarios = User.objects.all()
    materiales = Material.objects.all()
    unidadesMedida = UnidadMedida.objects.all()
    
    retorno = {"proveedores":proveedores,"usuarios":usuarios,"materiales":materiales,"unidadesMedida":unidadesMedida}
    return render(request,"asistente/frmRegistrarEntradaMaterial.html",retorno)

def registrarEntradaMaterial(request):
    if request.method == 'POST':
        estado = False
        mensaje = f""
        try:
            with transaction.atomic():
                codigoFactura = request.POST["codigoFactura"]
                entregadoPor = request.POST["entregadoPor"]
                idProveedor = int(request.POST["proveedor"])
                recibidoPor = int(request.POST["recibidoPor"])
                fechaHora = request.POST.get("fechaHora",None)
                observaciones = request.POST["observaciones"]
                userRecibe = User.objects.get(pk=recibidoPor)
                proveedor  = Proveedor.objects.get(pk=idProveedor)
                entradaMaterial = EntradaMaterial(entNumeroFactura = codigoFactura, entFechaHora = fechaHora,
                                                  entUsuarioRecibe = userRecibe, entEntregadoPor = entregadoPor,
                                                  entProveedor = proveedor, entObservaciones = observaciones)
                entradaMaterial.save()
                detalleMateriales = json.loads(request.POST["detalle"])
                for detalle in detalleMateriales:
                    material = Material.objects.get(id=int(detalle["idMaterial"]))
                    cantidad = int(detalle["cantidad"])
                    precio = int(detalle["precio"])
                    estado = detalle["estado"]
                    unidadMedida = UnidadMedida.objects.get(pk=int(detalle["idUnidadMedida"]))
                    detalleEntrada = DetalleEntradaMaterial(detEntradaMaterial = entradaMaterial, detMaterial = material,
                                                            detUnidadMedida = unidadMedida, detCantidad = cantidad,
                                                            detPrecioUnitario = precio, devEstado = estado)
                    detalleEntrada.save()
                estado =True
                mensaje = f"Se ha registrado la entrada de materiales correctamente"
        except Error as error:
            transaction.rollback()
            mensaje = f"Error: {error}"
        retorno = {"estado":estado,"mensaje":mensaje}
        return JsonResponse(retorno)
    
def vistaSolicitudElemento(request):
    elementos = Elemento.objects.all()
    unidadesMedidas = UnidadMedida.objects.all()
    usuarios = User.objects.all()
    materiales = Material.objects.all()
    fichas = Ficha.objects.all()
    
    retorno = {"elementos":elementos,"unidadesMedidas":unidadesMedidas,"usuarios":usuarios,"materiales":materiales,"fichas":fichas}
    return render(request, "instructor/frmSolicitudElemento.html",retorno)

def registrarSolicitudElemento(request):
    if request.method == 'POST':
        estado = False
        mensaje = f""
        try:
            with transaction.atomic():
                ficha = request.POST['ficha']
                # data = json.loads(request.body)
                # ficha = Ficha.objects.get(ficCodigo = data['ficha'])
                nombreProyecto = request.POST['proyecto']
                fechaHoraRequerida = request.POST.get('fechaHoraRequerida',None)
                fechaHoraFin = request.POST.get('fechaHoraFin',None)
                observaciones = request.POST['observaciones']
                fichaSolicitud = Ficha.objects.get(pk=ficha)
                solicitudElemento = SolicitudElemento(solUsuario = request.user, solFicha = fichaSolicitud, solProyecto = nombreProyecto,
                                                      solFechaHoraRequerida = fechaHoraRequerida, solFechaHoraFin = fechaHoraFin,
                                                      solEstado = "Solicitada", solObservaciones = observaciones)
                solicitudElemento.save()
                detallesElementos = json.loads(request.POST["detalle"])
                for detalle in detallesElementos:
                    elemento = Elemento.objects.get(id=int(detalle['idElemento']))
                    cantidad = int(detalle['cantidad'])
                    unidadMedida = UnidadMedida.objects.get(pk=int(detalle['idUnidadMedida']))
                    detalleSolicitud = DetalleSolicitud(detSolicitud = solicitudElemento, detElemento = elemento,
                                                        detUnidadMedida = unidadMedida, detCantidadRequerida = cantidad)
                    detalleSolicitud.save()
                    
                estado = True
                mensaje = f"Se ha registrado la solicitud de elementos correctamente"
                
                usuarios = User.objects.all()
                
                for user in usuarios:
                    if user.groups.filter(name="Administrador").exists():
                        correoAdministrador = user.email
                        break
                    
                # enviar correo al instructor y al administrador
                asunto = 'Registro Solicitud de Materiales - Inventario CIES'
                contenido = f'Codrial saludo.<br>\
                    Le informamos que se ha registrado una solicitud de elementos al Sistema de Gestión \
                    de Inventario del centro de la industria, la empresa y los servicios CIES.<br>\
                    Datos de la solicitud: <br>\
                        <ul>\
                            <li>Nombre: <b>{user.first_name} {user.last_name}</b></li>\
                            <li>Ficha: <b>{ficha.ficCodigo} - {ficha.ficNombre}</b></li>\
                            <li>Fecha-hora requerida: <b>{fechaHoraRequerida}</b></li>\
                            <li>Fecha-hora fin: <b>{fechaHoraFin}</b></li>\
                            <li>Fecha requerida: <b>{fechaHoraRequerida}</b></li>\
                            <li>Cantidad: <b>{cantidad}</b></li>\
                        </ul>\
                    <br>La solicitud será revisada para poder ser aprovada por el administrador \
                    <br>Lo invitamos a ingresar al sistema en el siguiente link:<br>\
                    https://gestioninventario.sena.edu.co.'
                threa = threading.Thread(target=enviarCorreo, args=(asunto,contenido,[user.email, correoAdministrador])) 
                threa.start()
        except Error as error:
            transaction.rollback()
            mensaje = f"Error: {error}"
        retorno = {"estado":estado,"mensaje":mensaje}
        return JsonResponse(retorno)

def vistaUserAdministrador(request):
    if request.user.is_authenticated:
        return render(request,"administrador/userView.html")
    
def vistaUserAsistente(request):
    if request.user.is_authenticated:
        return render(request,"asistente/userView.html")
    
def vistaUserInstructor(request):
    if request.user.is_authenticated:
        return render(request,"instructor/userView.html")
    
def vistaUpdateUserAdministrador(request):
    if request.user.is_authenticated:
        return render(request,"administrador/updateUsuario.html")
    
def vistaUpdateUserAsistente(request):
    if request.user.is_authenticated:
        return render(request,"asistente/updateUsuario.html")
    
def vistaUpdateUserInstructor(request):
    if request.user.is_authenticated:
        return render(request,"instructor/updateUsuario.html")
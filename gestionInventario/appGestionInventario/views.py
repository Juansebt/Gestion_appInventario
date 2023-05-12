from django.shortcuts import render, redirect
from django.db import Error, transaction
from django.contrib.auth.models import Group
from appGestionInventario.models import *
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.contrib.auth import authenticate, logout
from django.contrib import auth
from django.conf import settings
from smtplib import SMTPException
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
                    <br><b>USERNAME:<\b> {user.username}\
                    <br><b>PASSWORD:<\b> {passwordGenerado}\
                    <br><br>Lo invitamos a ingresar al sistema en la url:\
                    https://gestioninventario.sena.edu.co.'
            threa = threading.Thread(target=enviarCorreo, args=(asunto,mensaje,user.email))
            threa.start()
            return redirect("/vistaGestionarUsuarios/", retorno)
    except Error as error:
        transaction.rollback()
        mensaje = f"{error}"
    retorno = {"mensaje":mensaje, "user":user, "estado":estado}
    return render(request, "administrado/frmRegistrarUsuario.html", retorno)

def generarPassword():
    longitud = 10
    caracteres = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
    password = ''
    for i in range(longitud):
        password += ''.join(random.choice(caracteres))
    return password

def vistaLogin(request):
    return render(request,"login.html")

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
    return redirect("/inicio")

# def cerrarSesion(request):
#     # eliminar la sesión actual
#     request.session.flush()
#     return redirect("/inicio")

def vistaGestionarDevolutivos(request):
    if request.user.is_authenticated:
        elementosDevolutivos = Devolutivo.objects.all()
        retorno = {"listaElementosDevolutivos":elementosDevolutivos}
        print(elementosDevolutivos)
        return render(request, "administrador/listarDevolutivos.html",retorno)
    else:
        mensaje = f"Debe iniciar sesión"
        return render(request, "login.html",{"mensaje":mensaje})
    
def vistaRegistrarDevolutivo(request):
    retorno = {"tipoElementos":tipoElemento,"estados":estadosElementos}
    print(retorno)
    return render(request,"administrador/frmRegistrarDevolutivos.html",retorno)

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
    return render(request,"administrador/frmRegistrarDevolutivos.html",retorno)
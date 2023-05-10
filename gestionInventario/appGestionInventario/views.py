from django.shortcuts import render, redirect
from django.db import Error, transaction
from django.contrib.auth.models import Group
from appGestionInventario.models import *
from django.conf import settings
import random
import string
import os

# Create your views here.

def inicio(request):
    return render(request, "inicio.html")

def vistaRegistrarUsuario(request):
    roles = Group.objects.all()
    retorno = {"roles":roles, "user":None}
    return render(request, "administrador/frmRegistrarUsuario.html", retorno)

def listarUsuarios(request):
    mensaje = ""
    estado = ""
    try:
        roles = Group.objects.all()
        estado = True
    except Error as error:
        mensaje = f"Problemas al obtener los productos {error}"
    retorno = {"mensaje":mensaje, "estado":estado, "listaRoles":roles}
    return render(request, "listarUsuarios.html",retorno)

def registrarUsuario(request):
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
            mensaje = f"Ususario agregado correctamente"
            retorno = {"mensaje":mensaje}
            # enviar correo al usuario
            return redirect("/vistaGestionarUsuarios/", retorno)
    except Error as error:
        transaction.rollback()
        mensaje = f"{error}"
    retorno = {"mensaje":mensaje, "user":user}
    return render(request, "administrado/frmRegistrarUsuario.html", retorno)

def generarPassword():
    longitud = 10
    caracteres = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation
    password = ''
    for i in range(longitud):
        password += ''.join(random.choice(caracteres))
    return password


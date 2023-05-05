from django.shortcuts import render, redirect
from django.db import Error, transaction
from django.contrib.auth.models import Group
from appGestionInventario.models import *
import random
import string

# Create your views here.

def inicio(request):
    return render(request, "inicio.html")

def vistaRegistrarUsuario(request):
    roles = Group.objects.all()
    retorno = {"roles":roles, "user":None}
    return render(request, "administrador/frmRegistrarUsuario.html", retorno)

def registrarUsuario(request):
    try:
        nombres = request.POST["txtNombres"]
        apellidos = request.POST["txtApellidos"]
        correo = request.POST["txtCorreo"]
        tipo = request.POST["cbTipo"]
        foto = request.FILES.get("fileFoto", False)
        idRol = int(request.POST["cbRol"])
        
        with transaction.atomic():
            user = User(username=correo, first_name=nombres, last_name=apellidos, email=correo, userTipo=tipo, userFoto=foto)
            user.save()
            rol = Group.objects.get(pk=idRol)
            user.groups.add(rol)
            if(rol.name=="Administrador"):
                user.is_staff = True
            user.save()
            passwordGenerado = generarPassword()
            print(f"password {passwordGenerado}")
            user.set_password(passwordGenerado)
            user.save()
            mensaje = f"Ususario agregado correctamente"
            retorno = {"mensaje":mensaje}
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
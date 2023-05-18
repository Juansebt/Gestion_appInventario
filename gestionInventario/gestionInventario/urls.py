"""
URL configuration for gestionInventario project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from appGestionInventario import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('inicio/', views.inicio),
    path('vistaRegistrarUsuario/', views.vistaRegistrarUsuario),
    path('registrarUsuario/', views.registrarUsuario),
    path('vistaGestionarUsuarios/', views.vistaGestionarUsuarios),
    path('login/', views.login),
    path('cerrarSesion/', views.cerrarSesion),
    path('vistaLogin/', views.vistaLogin),
    path('inicioAdministrador/', views.inicioAdministrador),
    path('vistaGestionarDevolutivos/', views.vistaGestionarDevolutivos),
    path('vistaRegistrarDevolutivo/', views.vistaRegistrarDevolutivo),
    path('registrarDevolutivo/',views.registrarDevolutivo),
    path('inicioAsistente/', views.inicioAsistente),
    path('inicioInstructor/', views.inicioInstructor),
]

#Para poder tener acceso a la carpeta media y poder ver las fotos
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
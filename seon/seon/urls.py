from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    ################################// USUARIOS \\#########################################################
    path('admin/', admin.site.urls),
    path('register/', views.register_user, name='register_user'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('menu_rutinas/', views.menu_rutinas, name='menu_rutinas'),
    ################################// REGISTRO DE TERCEROS \\#########################################################
    path('registro_terceros/', views.registro_terceros, name='registro_terceros'),
    path('lista_terceros/', views.lista_terceros, name='lista_terceros'),
    path('editar_tercero/<str:codter>/', views.editar_tercero, name='editar_tercero'),
    path('eliminar_tercero/<str:codter>/', views.eliminar_tercero, name='eliminar_tercero'),
    ################################// BÁSCULA \\#########################################################
    path('bascula/', views.bascula_view, name="bascula_view"),
    path('eliminar_bascula/<int:id>/', views.eliminar_bascula, name='eliminar_bascula'),
    path('eliminar_dispositivo/<int:id>/', views.eliminar_dispositivo, name="eliminar_dispositivo"),
    path('registro/', views.registro_view, name="registro_view"),
    path('eliminar_registros/', views.eliminar_registros, name="eliminar_registros"),
    path('editar_bascula/<int:id>/', views.editar_registro_bascula, name='editar_registro_bascula'),
    path('editar_dispositivo/<int:id>/', views.editar_registro_dispositivo, name='editar_registro_dispositivo'),
    path("imprimir/<str:tipo>/<int:id>/", views.imprimir_registro, name="imprimir_registro"),
]


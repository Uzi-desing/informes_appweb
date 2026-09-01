from django.urls import path

from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('informes/nuevo/', views.crear_informe_view, name='crear_informe'),
    path('registrar/<uuid:uuid>/piezas/', views.registrar_piezas_view, name='registrar_piezas'),
    path('registrar/<uuid:uuid>/cancelar/', views.cancelar_informe_view, name='cancelar_informe'),
    path('clientes/nuevo/', views.crear_cliente_view, name='crear_cliente'),
    path('informes/', views.lista_informes_view, name='lista_informes'),
    path('clientes/', views.lista_clientes_view, name='lista_clientes'),
    path('informes/<uuid:uuid>/', views.detalle_informe_view, name='detalle_informe'),
]
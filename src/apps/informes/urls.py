from django.urls import path

from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('informes/nuevo/', views.crear_informe_view, name='crear_informe'),
    path('registrar/<uuid:uuid>/piezas/', views.registrar_piezas, name='registrar_piezas'),
]
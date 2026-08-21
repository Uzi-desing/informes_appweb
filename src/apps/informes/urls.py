from django.urls import path

from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('informes/nuevo/', views.crear_informe_view, name='crear_informe'),
]
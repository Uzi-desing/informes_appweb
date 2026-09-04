from django.contrib import admin

from .models import (
    Categoria,
    CategoriaDano,
    Cliente,
    InformeDano,
    Pieza,
    PiezaRechazada,
    UsuarioTransportista,
    Vehiculo,
)


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('descripcion',)


@admin.register(CategoriaDano)
class CategoriaDanoAdmin(admin.ModelAdmin):
    list_display = ('motivo',)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'mail', 'domicilio')
    search_fields = ('nombre', 'mail', 'domicilio')
    ordering = ('nombre',)


@admin.register(UsuarioTransportista)
class UsuarioTransportistaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'dni')
    search_fields = ('nombre', 'apellido', 'dni')


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('patente', 'tipo')
    list_filter = ('tipo',)


@admin.register(Pieza)
class PiezaAdmin(admin.ModelAdmin):
    list_display = ('categoria', 'medida')
    list_filter = ('categoria',)
    search_fields = ('medida',)


@admin.register(InformeDano)
class InformeDanoAdmin(admin.ModelAdmin):
    list_display = ('remito_recepcion', 'cliente', 'empleado', 'fecha', 'finalizado')
    list_filter = ('finalizado', 'fecha')
    search_fields = ('remito_recepcion', 'cliente__nombre')
    readonly_fields = ('uuid_identificador', 'remito_recepcion', 'fecha')


@admin.register(PiezaRechazada)
class PiezaRechazadaAdmin(admin.ModelAdmin):
    list_display = ('informe', 'pieza', 'categoria_dano', 'cantidad')
    readonly_fields = ('uuid_identificador',)
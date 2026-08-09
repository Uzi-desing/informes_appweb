from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Empleado, Rol, Usuario

# Register your models here.

# Carga de datos del empleado en la misma vista de creación de usuario.
class EmpleadoInline(admin.StackedInline):
    model = Empleado
    can_delete = False
    verbose_name_plural = 'Perfil de Empleado'
    fk_name = 'usuario'

class CustomUserAdmin(UserAdmin):
    inlines = (EmpleadoInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'es_empleado', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Configuración', {'fields': ('es_empleado',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('puesto', 'slug')
    prepopulated_fields = {'slug': ('puesto',)}

admin.site.register(Usuario, CustomUserAdmin)

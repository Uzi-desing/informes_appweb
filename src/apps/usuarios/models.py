from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify


# Create your models here.
class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    es_empleado = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.username

class Rol(models.Model):
    puesto = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.puesto)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.puesto

class Empleado(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_empleado')
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True, related_name='empleado')
    dni = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20)

    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'

    def __str__(self):
        nombre_completo = self.usuario.get_full_name()
        display_nombre = nombre_completo if nombre_completo else self.usuario.username
        puesto = self.rol.puesto if self.rol else 'Sin Rol'
        return f"{display_nombre} - {puesto}"


    

    

    
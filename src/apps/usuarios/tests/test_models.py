import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from apps.usuarios.models import Empleado, Rol

User = get_user_model()


@pytest.mark.django_db
def test_usuario_str_es_username(usuario_operario):
    assert str(usuario_operario) == usuario_operario.username


@pytest.mark.django_db
def test_usuario_email_unico(usuario_operario):
    with pytest.raises(IntegrityError):
        User.objects.create_user(
            username='otro',
            password='clave123',
            email=usuario_operario.email,
        )


@pytest.mark.django_db
def test_rol_slug_automatico():
    rol = Rol.objects.create(puesto='Operario')
    assert rol.slug == 'operario'


@pytest.mark.django_db
def test_rol_slug_unico(rol_operario):
    with pytest.raises(IntegrityError):
        Rol.objects.create(puesto='Operario')


@pytest.mark.django_db
def test_empleado_str_con_rol(empleado_operario):
    assert str(empleado_operario) == 'Juan Perez - Operario'


@pytest.mark.django_db
def test_empleado_str_sin_rol(usuario_operario):
    empleado = Empleado.objects.create(
        usuario=usuario_operario,
        rol=None,
        dni='40111222',
        telefono='011-654321',
    )
    assert str(empleado) == 'Juan Perez - Sin Rol'
import pytest
from django.contrib.auth import get_user_model

from apps.usuarios.models import Empleado, Rol

User = get_user_model()


@pytest.fixture
def rol_operario(db):
    return Rol.objects.create(puesto='Operario')


@pytest.fixture
def usuario_operario(db):
    user = User.objects.create_user(
        username='operario1',
        password='clave123',
        email='operario1@test.com',
        first_name='Juan',
        last_name='Perez',
    )
    user.raw_password = 'clave123'
    return user


@pytest.fixture
def empleado_operario(db, rol_operario, usuario_operario):
    return Empleado.objects.create(
        usuario=usuario_operario,
        rol=rol_operario,
        dni='30111222',
        telefono='011-123456',
    )
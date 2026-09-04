import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.test import RequestFactory
from django.urls import reverse

from apps.informes.decorators import bloqueo_informe_pendiente, solo_operarios

User = get_user_model()

rf = RequestFactory()


def dummy_view(request):
    return HttpResponse('ok')


def build_request(usuario=None):
    request = rf.get('/')
    request.user = usuario if usuario is not None else AnonymousUser()
    return request


@pytest.mark.django_db
def test_solo_operarios_sin_login_redirige_al_login():
    response = solo_operarios(dummy_view)(build_request())
    assert response.status_code == 302
    assert reverse('login') in response.url


@pytest.mark.django_db
def test_solo_operarios_usuario_inactivo_lanza_permission_denied(usuario_operario):
    usuario_operario.is_active = False
    with pytest.raises(PermissionDenied):
        solo_operarios(dummy_view)(build_request(usuario_operario))


@pytest.mark.django_db
def test_solo_operarios_superuser_pasa():
    superuser = User.objects.create_user(
        username='super', password='clave123', email='super@test.com', is_superuser=True
    )
    response = solo_operarios(dummy_view)(build_request(superuser))
    assert response.content == b'ok'


@pytest.mark.django_db
def test_solo_operarios_sin_perfil_lanza_permission_denied(usuario_operario):
    with pytest.raises(PermissionDenied):
        solo_operarios(dummy_view)(build_request(usuario_operario))


@pytest.mark.django_db
def test_solo_operarios_con_rol_diferente_lanza_permission_denied(usuario_operario):
    from apps.usuarios.models import Empleado, Rol

    otro_rol = Rol.objects.create(puesto='Administrador')
    Empleado.objects.create(
        usuario=usuario_operario,
        rol=otro_rol,
        dni='30111222',
        telefono='011-123456',
    )
    with pytest.raises(PermissionDenied):
        solo_operarios(dummy_view)(build_request(usuario_operario))


@pytest.mark.django_db
def test_solo_operarios_con_rol_operario_pasa(empleado_operario):
    response = solo_operarios(dummy_view)(build_request(empleado_operario.usuario))
    assert response.content == b'ok'


@pytest.mark.django_db
def test_bloqueo_informe_pendiente_redirige(empleado_operario, informe):
    response = bloqueo_informe_pendiente(dummy_view)(
        build_request(empleado_operario.usuario)
    )
    assert response.status_code == 302
    assert str(informe.uuid_identificador) in response.url
    assert reverse('registrar_piezas', kwargs={'uuid': informe.uuid_identificador}) in response.url


@pytest.mark.django_db
def test_bloqueo_informe_pendiente_sin_pendiente_pasa(empleado_operario):
    response = bloqueo_informe_pendiente(dummy_view)(
        build_request(empleado_operario.usuario)
    )
    assert response.content == b'ok'
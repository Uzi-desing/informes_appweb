import pytest

from apps.usuarios.backends import SesionBackend


@pytest.mark.django_db
def test_user_can_authenticate_siempre_true(usuario_operario):
    assert SesionBackend().user_can_authenticate(usuario_operario) is True


@pytest.mark.django_db
def test_get_user_con_usuario_activo(usuario_operario):
    assert SesionBackend().get_user(usuario_operario.pk) == usuario_operario


@pytest.mark.django_db
def test_get_user_con_usuario_inactivo(usuario_operario):
    usuario_operario.is_active = False
    usuario_operario.save()
    assert SesionBackend().get_user(usuario_operario.pk) is None


@pytest.mark.django_db
def test_get_user_inexistente():
    assert SesionBackend().get_user(99999) is None
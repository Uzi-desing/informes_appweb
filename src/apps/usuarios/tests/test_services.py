import pytest
from django.contrib.sessions.backends.db import SessionStore
from django.test import RequestFactory

from apps.usuarios.services import procesar_login, procesar_logout


@pytest.mark.django_db
def test_procesar_login_autentica_al_usuario(mocker, usuario_operario):
    request = RequestFactory().post('/login/')
    request.session = SessionStore()
    request.user = usuario_operario
    form = mocker.Mock()
    form.get_user.return_value = usuario_operario

    procesar_login(request, form)

    assert request.session.get('_auth_user_id') == str(usuario_operario.pk)


@pytest.mark.django_db
def test_procesar_logout_desloguea_y_retorna_mensaje(usuario_operario):
    request = RequestFactory().get('/logout/')
    request.session = SessionStore()
    request.user = usuario_operario
    request.session['_auth_user_id'] = str(usuario_operario.pk)

    mensaje = procesar_logout(request)

    assert mensaje == "Haz cerrado sesión."
    assert '_auth_user_id' not in request.session
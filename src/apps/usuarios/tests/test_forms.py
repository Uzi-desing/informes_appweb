import pytest

from apps.usuarios.forms import LoginForm


def test_login_form_campos_necesarios():
    form = LoginForm()
    assert 'username' in form.fields
    assert 'password' in form.fields


@pytest.mark.django_db
def test_login_form_valido(usuario_operario):
    form = LoginForm(data={
        'username': usuario_operario.username,
        'password': usuario_operario.raw_password,
    })
    assert form.is_valid()
    assert form.get_user() == usuario_operario


@pytest.mark.django_db
def test_login_form_invalido_credenciales_incorrectas():
    form = LoginForm(data={'username': 'nadie', 'password': 'incorrecta'})
    assert not form.is_valid()
    errores = form.errors.as_data()['__all__']
    assert any(
        "El usuario o la contraseña son incorrectos" in str(e)
        for e in errores
    )


@pytest.mark.django_db
def test_login_form_invalido_usuario_inactivo(usuario_operario):
    usuario_operario.is_active = False
    usuario_operario.save()
    form = LoginForm(data={
        'username': usuario_operario.username,
        'password': usuario_operario.raw_password,
    })
    assert not form.is_valid()
    errores = form.errors.as_data()['__all__']
    assert any("inhabilitada por la administración" in str(e) for e in errores)
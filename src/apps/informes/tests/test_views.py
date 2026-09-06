import pytest
from django.urls import reverse

from apps.informes.models import Pieza


@pytest.mark.django_db
def test_crear_pieza_sin_login_redirige_al_login(client):
    response = client.get(reverse('crear_pieza'))
    assert response.status_code == 302
    assert reverse('login') in response.url


@pytest.mark.django_db
def test_crear_pieza_get_muestra_formulario(client, empleado_operario, categoria):
    client.force_login(empleado_operario.usuario)

    response = client.get(reverse('crear_pieza'))

    assert response.status_code == 200
    assert 'Información de la Pieza' in response.content.decode()


@pytest.mark.django_db
def test_crear_pieza_post_crea_y_redirige(client, empleado_operario, categoria):
    client.force_login(empleado_operario.usuario)

    response = client.post(
        reverse('crear_pieza'),
        {'categoria': categoria.pk, 'medida': '0.73'},
    )

    assert response.status_code == 302
    assert response.url == reverse('home')
    assert Pieza.objects.count() == 1
    assert Pieza.objects.first().medida == '0.73'


@pytest.mark.django_db
def test_crear_pieza_post_duplicado_no_registra(client, empleado_operario, categoria):
    client.force_login(empleado_operario.usuario)
    datos = {'categoria': categoria.pk, 'medida': '0.73'}

    client.post(reverse('crear_pieza'), datos)
    response = client.post(reverse('crear_pieza'), datos)

    assert response.status_code == 302
    assert Pieza.objects.count() == 1


@pytest.mark.django_db
def test_crear_pieza_post_invalido_no_crea(client, empleado_operario):
    client.force_login(empleado_operario.usuario)

    response = client.post(reverse('crear_pieza'), {'categoria': '', 'medida': ''})

    assert response.status_code == 200
    assert Pieza.objects.count() == 0
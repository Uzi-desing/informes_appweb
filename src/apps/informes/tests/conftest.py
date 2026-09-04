import pytest

from apps.informes.models import (
    Categoria,
    CategoriaDano,
    Cliente,
    InformeDano,
    Pieza,
    UsuarioTransportista,
    Vehiculo,
)


@pytest.fixture
def cliente(db):
    return Cliente.objects.create(
        nombre='Cliente A',
        telefono='123',
        mail='cliente@test.com',
        domicilio='Calle 1',
    )


@pytest.fixture
def categoria(db):
    return Categoria.objects.create(descripcion='horizontal')


@pytest.fixture
def categoria_dano(db):
    return CategoriaDano.objects.create(motivo='dobladura')


@pytest.fixture
def pieza(db, categoria):
    return Pieza.objects.create(categoria=categoria, medida='0.73')


@pytest.fixture
def transportista(db):
    return UsuarioTransportista.objects.create(
        nombre='Carlos',
        apellido='Gomez',
        dni='30123456',
    )


@pytest.fixture
def vehiculo(db):
    return Vehiculo.objects.create(patente='ABC123', tipo='CAMION')


@pytest.fixture
def informe(db, empleado_operario, cliente, transportista, vehiculo):
    return InformeDano.objects.create(
        empleado=empleado_operario,
        cliente=cliente,
        transportista=transportista,
        vehiculo=vehiculo,
        remito_recepcion='R-0001',
    )
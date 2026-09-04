import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.informes.models import (
    Categoria,
    CategoriaDano,
    Cliente,
    InformeDano,
    PiezaRechazada,
    UsuarioTransportista,
    Vehiculo,
)


@pytest.mark.django_db
def test_categoria_str():
    assert str(Categoria.objects.create(descripcion='Puerta')) == 'Puerta'


@pytest.mark.django_db
def test_categoria_dano_str():
    assert str(CategoriaDano.objects.create(motivo='Abrillar')) == 'Abrillar'


@pytest.mark.django_db
def test_cliente_str(cliente):
    assert str(cliente) == 'Cliente A'


@pytest.mark.django_db
def test_cliente_mail_no_requerido():
    Cliente.objects.create(nombre='X', telefono='1', domicilio='Y')
    assert Cliente.objects.count() == 1


@pytest.mark.django_db
def test_transportista_nombre_completo(transportista):
    assert transportista.nombre_completo == 'Carlos Gomez'


@pytest.mark.django_db
def test_transportista_str(transportista):
    assert str(transportista) == 'Carlos Gomez (DNI: 30123456)'


@pytest.mark.django_db
def test_transportista_dni_unico(transportista):
    with pytest.raises(IntegrityError):
        UsuarioTransportista.objects.create(
            nombre='Otro', apellido='Otro', dni='30123456'
        )


@pytest.mark.django_db
def test_vehiculo_str(vehiculo):
    assert str(vehiculo) == 'ABC123 (Camión)'


@pytest.mark.django_db
def test_vehiculo_patente_unica(vehiculo):
    with pytest.raises(IntegrityError):
        Vehiculo.objects.create(patente='ABC123', tipo='CAMIONETA')


@pytest.mark.django_db
def test_pieza_str(pieza):
    assert str(pieza) == 'horizontal - 0.73'


@pytest.mark.django_db
def test_informe_str(informe, cliente):
    assert str(informe) == 'Informe Nº R-0001 - Cliente A'


@pytest.mark.django_db
def test_informe_normaliza_remito_antes_de_guardar(
    empleado_operario, cliente, transportista, vehiculo
):
    informe = InformeDano(
        empleado=empleado_operario,
        cliente=cliente,
        transportista=transportista,
        vehiculo=vehiculo,
        remito_recepcion='  lo que sea 1  ',
    )
    informe.save()
    assert informe.remito_recepcion == 'LOQUESEA1'


@pytest.mark.django_db
def test_informe_remito_unico(informe):
    with pytest.raises(ValidationError):
        InformeDano.objects.create(
            empleado=informe.empleado,
            cliente=informe.cliente,
            transportista=informe.transportista,
            vehiculo=informe.vehiculo,
            remito_recepcion='R-0001',
        )


@pytest.mark.django_db
def test_informe_no_finalizado_por_defecto(informe):
    assert informe.finalizado is False
    assert informe.esta_bloqueado is False


@pytest.mark.django_db
def test_informe_finalizar_con_piezas(informe, pieza, categoria_dano):
    PiezaRechazada.objects.create(
        informe=informe,
        pieza=pieza,
        categoria_dano=categoria_dano,
        cantidad=2,
    )
    informe.finalizar()
    assert informe.finalizado is True
    assert informe.esta_bloqueado is True


@pytest.mark.django_db
def test_informe_finalizar_vacio_lanza_validationerror(informe):
    with pytest.raises(ValidationError):
        informe.finalizar()


@pytest.mark.django_db
def test_pieza_rechazada_guardar_en_informe_finalizado_lanza_error(
    informe, pieza, categoria_dano
):
    PiezaRechazada.objects.create(
        informe=informe,
        pieza=pieza,
        categoria_dano=categoria_dano,
        cantidad=1,
    )
    informe.finalizar()
    with pytest.raises(ValidationError):
        PiezaRechazada.objects.create(
            informe=informe,
            pieza=pieza,
            categoria_dano=categoria_dano,
            cantidad=3,
        )


@pytest.mark.django_db
def test_pieza_rechazada_cantidad_minima_no_permitida(informe, pieza, categoria_dano):
    pieza_rechazada = PiezaRechazada(
        informe=informe,
        pieza=pieza,
        categoria_dano=categoria_dano,
        cantidad=0,
    )
    with pytest.raises(ValidationError):
        pieza_rechazada.full_clean()


@pytest.mark.django_db
def test_pieza_rechazada_url_segura_sin_imagen(informe, pieza, categoria_dano):
    pr = PiezaRechazada.objects.create(
        informe=informe,
        pieza=pieza,
        categoria_dano=categoria_dano,
        cantidad=1,
    )
    assert pr.url_segura is None


@pytest.mark.django_db
def test_pieza_rechazada_url_segura_con_imagen(mocker, informe, pieza, categoria_dano):
    mock_sas = mocker.patch(
        'apps.informes.models.AzureBlobService.generate_url_sas',
        return_value='https://sas-url',
    )
    pr = PiezaRechazada(
        informe=informe,
        pieza=pieza,
        categoria_dano=categoria_dano,
        cantidad=1,
    )
    pr.imagen = 'piezas-rechazadas-images/x.jpg'
    assert pr.url_segura == 'https://sas-url'
    mock_sas.assert_called_once_with('piezas-rechazadas-images/x.jpg')
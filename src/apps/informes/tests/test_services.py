import uuid

import pytest
from django.http import Http404

from apps.informes.models import InformeDano, UsuarioTransportista, Vehiculo
from apps.informes.services.informe_service import InformeService


@pytest.mark.django_db
def test_crear_informe_completo(mocker, empleado_operario, cliente):
    informe_form = mocker.Mock()
    informe_form.cleaned_data = {'cliente': cliente, 'remito_recepcion': 'R-XYZ'}
    informe = mocker.Mock()
    informe_form.save.return_value = informe

    transportista_form = mocker.Mock()
    transportista_form.cleaned_data = {
        'dni': '30123456', 'nombre': 'Carlos', 'apellido': 'Gomez'
    }

    vehiculo_form = mocker.Mock()
    vehiculo_form.cleaned_data = {'patente': 'abc 123', 'tipo': 'CAMION'}

    InformeService.crear_informe_completo(
        informe_form, transportista_form, vehiculo_form, empleado_operario
    )

    transportista = UsuarioTransportista.objects.get(dni='30123456')
    assert transportista.nombre == 'carlos'
    assert transportista.apellido == 'gomez'

    vehiculo = Vehiculo.objects.get(patente='ABC123')
    assert vehiculo.tipo == 'CAMION'

    informe_form.save.assert_called_once_with(commit=False)
    assert informe.empleado == empleado_operario
    assert informe.transportista == transportista
    assert informe.vehiculo == vehiculo
    informe.save.assert_called_once_with()


@pytest.mark.django_db
def test_cancelar_informe_borra_y_retorna_remito(informe):
    remito = InformeService.cancelar_informe(informe)
    assert remito == 'R-0001'
    assert not InformeDano.objects.filter(pk=informe.pk).exists()


@pytest.mark.django_db
def test_obtener_informes_orden_default_y_paginado(cliente, empleado_operario):
    for i in range(7):
        crear_informe(empleado_operario, cliente, f'R-{i:04d}')
    page = InformeService.obtener_informes(1)
    assert page.paginator.per_page == 6
    assert len(page.object_list) == 6
    assert page.has_next() is True


@pytest.mark.django_db
def test_obtener_informes_filtro_por_cliente(cliente, empleado_operario):
    crear_informe(empleado_operario, cliente, 'R-0001')
    page = InformeService.obtener_informes(1, q=cliente.nombre)
    assert page.object_list.count() == 1


@pytest.mark.django_db
def test_obtener_informes_filtro_por_empleado(cliente, empleado_operario):
    informe = crear_informe(empleado_operario, cliente, 'R-0001')
    page = InformeService.obtener_informes(1, empleado_id=empleado_operario.pk)
    assert [i.pk for i in page.object_list] == [informe.pk]


@pytest.mark.django_db
def test_obtener_detalle_informe(cliente, empleado_operario):
    informe = crear_informe(empleado_operario, cliente, 'R-0001')
    result, _piezas = InformeService.obtener_detalle_informe(informe.uuid_identificador)
    assert result.pk == informe.pk


@pytest.mark.django_db
def test_obtener_detalle_informe_404_si_no_existe():
    with pytest.raises(Http404):
        InformeService.obtener_detalle_informe(uuid.uuid4())


@pytest.mark.django_db
def test_obtener_ultimo_informe(cliente, empleado_operario):
    informe = crear_informe(empleado_operario, cliente, 'R-0001')
    assert InformeService.obtener_ultimo_informe().pk == informe.pk


def crear_informe(empleado, cliente, remito):
    transportista, _ = UsuarioTransportista.objects.get_or_create(
        dni='30123456', defaults={'nombre': 'Carlos', 'apellido': 'Gomez'}
    )
    vehiculo, _ = Vehiculo.objects.get_or_create(
        patente='ABC123', defaults={'tipo': 'CAMION'}
    )
    return InformeDano.objects.create(
        empleado=empleado,
        cliente=cliente,
        transportista=transportista,
        vehiculo=vehiculo,
        remito_recepcion=remito,
    )
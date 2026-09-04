import uuid

import pytest

from apps.informes.models import Cliente
from apps.informes.services.cliente_service import ClienteService
from apps.informes.services.image_service import ImageProcessorService
from apps.informes.services.pieza_service import PiezaService


@pytest.mark.django_db
def test_crear_cliente_normaliza(mocker):
    form = mocker.Mock()
    cliente = Cliente(
        nombre='  Empresa   ',
        telefono='123',
        mail='  EMPRESA@TEST.COM  ',
        domicilio='  Calle 1  ',
    )
    form.save.return_value = cliente

    result = ClienteService.crear_cliente(form)

    assert result.nombre == 'empresa'
    assert result.mail == 'empresa@test.com'
    assert result.domicilio == 'calle 1'


@pytest.mark.django_db
def test_obtener_clientes_paginado_y_anotado(cliente):
    page = ClienteService.obtener_clientes(1)
    assert page.object_list[0].pk == cliente.pk
    assert page.object_list[0].total_informes == 0


@pytest.mark.django_db
def test_obtener_clientes_filtro_por_nombre(cliente):
    page = ClienteService.obtener_clientes(1, q='cliente a')
    assert page.object_list.count() == 1


@pytest.mark.django_db
def test_procesar_piezas_y_finalizar(mocker, informe, pieza, categoria_dano):
    from apps.informes.models import PiezaRechazada

    PiezaRechazada.objects.create(
        informe=informe,
        pieza=pieza,
        categoria_dano=categoria_dano,
        cantidad=1,
    )
    formset = mocker.Mock()
    formset.save.return_value = ['p1', 'p2']

    result = PiezaService.procesar_piezas_y_finalizar(informe, formset)

    assert result == ['p1', 'p2']
    formset.save.assert_called_once_with()
    informe.refresh_from_db()
    assert informe.finalizado is True


@pytest.mark.django_db
def test_imagen_optimizar_nombre_y_jpeg():
    from io import BytesIO

    from django.core.files.uploadedfile import SimpleUploadedFile
    from PIL import Image

    buf = BytesIO()
    Image.new('RGB', (2000, 1000), (255, 0, 0)).save(buf, format='PNG')
    uploaded = SimpleUploadedFile('foto.png', buf.getvalue(), content_type='image/png')

    nombre, archivo = ImageProcessorService.optimizar_imagen(
        uploaded, uuid.uuid4(), 'Cliente Uno', 'R-0001'
    )

    assert nombre.startswith('cliente-uno_r-0001_')
    assert nombre.endswith('.jpg')

    img = Image.open(archivo)
    assert img.format == 'JPEG'
    assert img.width <= 1280
    assert img.height <= 720
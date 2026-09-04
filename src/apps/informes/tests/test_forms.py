import pytest

from apps.informes.forms import (
    InformeDanoForm,
    PiezaRechazadaFormSet,
    TransportistaForm,
    VehiculoForm,
)


@pytest.mark.django_db
def test_informe_dano_form_campos(cliente):
    form = InformeDanoForm(data={'cliente': cliente.pk, 'remito_recepcion': 'R1'})
    assert form.is_valid()
    assert form.fields['remito_recepcion'].error_messages['required'] == (
        'El Nº de Remito es obligatorio.'
    )


@pytest.mark.django_db
def test_informe_dano_form_requiere_campos():
    form = InformeDanoForm(data={})
    assert not form.is_valid()
    assert 'cliente' in form.errors
    assert 'remito_recepcion' in form.errors


@pytest.mark.django_db
def test_transportista_form_dni_valido():
    form = TransportistaForm(
        data={'nombre': 'Carlos', 'apellido': 'Gomez', 'dni': '30123456'}
    )
    assert form.is_valid()
    assert form.cleaned_data['dni'] == '30123456'


@pytest.mark.django_db
def test_transportista_form_dni_con_puntos_limpia():
    form = TransportistaForm(
        data={'nombre': 'Carlos', 'apellido': 'Gomez', 'dni': '30.123.456'}
    )
    assert form.is_valid()
    assert form.cleaned_data['dni'] == '30123456'


@pytest.mark.django_db
def test_transportista_form_dni_no_numerico_invalido():
    form = TransportistaForm(
        data={'nombre': 'Carlos', 'apellido': 'Gomez', 'dni': 'abc123'}
    )
    assert not form.is_valid()
    assert 'El DNI debe contener únicamente números.' in str(form.errors['dni'])


@pytest.mark.django_db
def test_transportista_form_dni_corto_invalido():
    form = TransportistaForm(
        data={'nombre': 'Carlos', 'apellido': 'Gomez', 'dni': '123'}
    )
    assert not form.is_valid()
    assert 'El DNI debe tener entre 7 u 9 dígitos.' in str(form.errors['dni'])


@pytest.mark.django_db
def test_vehiculo_form_valido():
    assert VehiculoForm(data={'patente': 'ABC123', 'tipo': 'CAMION'}).is_valid()


@pytest.mark.django_db
def test_vehiculo_form_requiere_tipo():
    form = VehiculoForm(data={'patente': 'ABC123', 'tipo': ''})
    assert not form.is_valid()
    assert 'Seleccione el tipo de Transporte.' in str(form.errors['tipo'])


@pytest.mark.django_db
def test_formset_cantidad_cero_invalido(informe, pieza, categoria_dano):
    data = formset_data(informe, pieza, categoria_dano)
    data['piezas_rechazadas-0-cantidad'] = '0'
    formset = PiezaRechazadaFormSet(data, instance=informe)
    assert not formset.is_valid()
    assert 'La cantidad debe ser mayor a 0.' in str(
        formset.errors[0].get('cantidad', [])
    )


@pytest.mark.django_db
def test_formset_requiere_al_menos_una_pieza(informe):
    prefix = formset_prefix()
    data = {
        f'{prefix}-TOTAL_FORMS': '0',
        f'{prefix}-INITIAL_FORMS': '0',
        f'{prefix}-MIN_NUM_FORMS': '1',
        f'{prefix}-MAX_NUM_FORMS': '1000',
    }
    formset = PiezaRechazadaFormSet(data, instance=informe)
    assert not formset.is_valid()
    assert any(
        'Debe registrar al menos una pieza.' in str(e)
        for e in formset.non_form_errors()
    )


@pytest.mark.django_db
def test_formset_con_una_pieza_es_valido(informe, pieza, categoria_dano):
    from io import BytesIO

    from django.core.files.uploadedfile import SimpleUploadedFile
    from PIL import Image

    buffer = BytesIO()
    Image.new('RGB', (10, 10), 'red').save(buffer, format='JPEG')

    data = formset_data(informe, pieza, categoria_dano)
    files = {
        'piezas_rechazadas-0-imagen': SimpleUploadedFile(
            'foto.jpg', buffer.getvalue(), content_type='image/jpeg'
        )
    }
    formset = PiezaRechazadaFormSet(data, files, instance=informe)
    assert formset.is_valid()


def formset_prefix():
    return PiezaRechazadaFormSet().prefix


def formset_data(informe, pieza, categoria_dano):
    prefix = formset_prefix()
    return {
        f'{prefix}-TOTAL_FORMS': '1',
        f'{prefix}-INITIAL_FORMS': '0',
        f'{prefix}-MIN_NUM_FORMS': '1',
        f'{prefix}-MAX_NUM_FORMS': '1000',
        f'{prefix}-0-pieza': pieza.pk,
        f'{prefix}-0-categoria_dano': categoria_dano.pk,
        f'{prefix}-0-cantidad': '1',
        f'{prefix}-0-observaciones': '',
        f'{prefix}-0-imagen': '',
        f'{prefix}-0-id': '',
        f'{prefix}-0-informe': informe.pk,
    }
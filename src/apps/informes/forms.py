from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from .models import Cliente, InformeDano, PiezaRechazada, UsuarioTransportista, Vehiculo

CLASE_INPUT = (
    'w-full rounded-lg border border-gray-300 dark:border-gray-600 '
    'bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 '
    'px-3 py-2 text-sm placeholder-gray-400 dark:placeholder-gray-500 '
    'focus:outline-none focus:ring-2 focus:ring-brand/50 focus:border-brand '
    'transition-colors duration-200'
)

CLASE_FILE_INPUT = (
    'w-full text-sm text-gray-900 dark:text-gray-100 '
    'file:mr-3 file:cursor-pointer file:rounded-lg file:border-0 '
    'file:bg-brand file:px-3 file:py-2 file:text-xs file:font-semibold '
    'file:text-white hover:file:bg-red-700 transition-colors duration-200'
)


class InformeDanoForm(forms.ModelForm):
    class Meta:
        model = InformeDano
        fields = ['cliente', 'remito_recepcion']  # noqa: RUF012
        widgets = {  # noqa: RUF012
            'cliente': forms.Select(attrs={'class': CLASE_INPUT}),
            'remito_recepcion': forms.TextInput(attrs={'class': CLASE_INPUT}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        mensaje_personalizado = {
            'cliente': 'El Cliente es obligatorio.',
            'remito_recepcion': 'El Nº de Remito es obligatorio.',
        }
        for campo, mensaje in mensaje_personalizado.items():
            self.fields[campo].required = True
            self.fields[campo].error_messages['required'] = mensaje


class TransportistaForm(forms.ModelForm):
    class Meta:
        model = UsuarioTransportista
        fields = ['nombre', 'apellido', 'dni']
        widgets = {  # noqa: RUF012
            'nombre': forms.TextInput(attrs={'class': CLASE_INPUT}),
            'apellido': forms.TextInput(attrs={'class': CLASE_INPUT}),
            'dni': forms.TextInput(attrs={
                'class': CLASE_INPUT,
                'inputmode': 'numeric',
                'pattern': '[0-9]*',
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        mensajes_personalizados = {
            'nombre': 'El Nombre es obligatorio.',
            'apellido': 'El Apellido es obligatorio.',
            'dni': 'El DNI es obligatorio.'
        }
        for campo, mensaje in mensajes_personalizados.items():
            self.fields[campo].required = True
            self.fields[campo].error_messages['required'] = mensaje

    def clean_dni(self):
        dni = self.cleaned_data.get('dni', '').replace('.', '').strip()

        if not dni.isdigit():
            raise ValidationError('El DNI debe contener únicamente números.')
        if len(dni) < 7 or len(dni) > 9:
            raise ValidationError('El DNI debe tener entre 7 u 9 dígitos.')

        return dni

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ['patente', 'tipo']
        widgets = {
            'patente': forms.TextInput(attrs={'class': CLASE_INPUT}),
            'tipo': forms.Select(attrs={'class': CLASE_INPUT}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        mensajes_personalizados = {
            'patente': 'La Patente es obligatoria.',
            'tipo': 'Seleccione el tipo de Transporte.',
        }
        for campo, mensaje in mensajes_personalizados.items():
            self.fields[campo].required = True
            self.fields[campo].error_messages['required'] = mensaje

class PiezaRechazadaForm(forms.ModelForm):
    class Meta:
        model = PiezaRechazada
        fields = ['pieza', 'categoria_dano', 'cantidad', 'observaciones', 'imagen']  # noqa: RUF012
        widgets = {  # noqa: RUF012
            'pieza': forms.Select(attrs={'class': CLASE_INPUT}),
            'categoria_dano': forms.Select(attrs={'class': CLASE_INPUT}),
            'cantidad': forms.NumberInput(attrs={'class': CLASE_INPUT, 'min': '1'}),
            'observaciones': forms.Textarea(attrs={'class': CLASE_INPUT, 'rows': '2'}),
            'imagen': forms.ClearableFileInput(attrs={
                'class': CLASE_FILE_INPUT,
                'capture': 'environment',
                'accept': 'image/*'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        mensajes_personalizados = {
            'pieza': 'Seleccione una pieza.',
            'categoria_dano': 'Seleccione el tipo de daño.',
            'cantidad': 'La cantidad es obligatoria y debe ser mayor a 0.',
            'imagen': 'La fotografia es obligatoria.'
        }

        for campo, mensaje in mensajes_personalizados.items():
            self.fields[campo].required = True
            self.fields[campo].error_messages['required'] = mensaje
            self.fields[campo].widget.attrs['required'] = 'required'

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is None or cantidad < 1:
            raise ValidationError('La cantidad debe ser mayor a 0.')
        return cantidad

PiezaRechazadaFormSet = inlineformset_factory(
    parent_model=InformeDano,
    model=PiezaRechazada,
    form=PiezaRechazadaForm,
    extra=0,
    min_num=1,
    validate_min=True,
    can_delete=True,
    error_messages={
        'too_few_forms': 'Debe registrar al menos una pieza.',
    },
)

# Formulario Cliente
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'telefono', 'mail', 'domicilio']  # noqa: RUF012
        widgets = {  # noqa: RUF012
            'nombre': forms.TextInput(attrs={'class': CLASE_INPUT}),
            'telefono': forms.TextInput(attrs={'class': CLASE_INPUT, 'inputmode': 'tel'}),
            'mail': forms.EmailInput(attrs={'class': CLASE_INPUT}),
            'domicilio': forms.TextInput(attrs={'class': CLASE_INPUT}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        mensajes_personalizados = {
            'nombre': 'El Nombre es obligatorio.',
            'telefono': 'El Teléfono es obligatorio.',
            'domicilio': 'El Domicilio es obligatorio.',
        }
        for campo, mensaje in mensajes_personalizados.items():
            self.fields[campo].required = True
            self.fields[campo].error_messages['required'] = mensaje
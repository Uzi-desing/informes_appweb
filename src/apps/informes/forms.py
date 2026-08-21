from django import forms
from django.core.exceptions import ValidationError

from .models import InformeDano, UsuarioTransportista, Vehiculo


class InformeDanoForm(forms.ModelForm):
    class Meta:
        model = InformeDano
        fields = ['cliente', 'remito_recepcion']  # noqa: RUF012
        widgets = {  # noqa: RUF012
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'remito_recepcion': forms.TextInput(attrs={'class': 'form-input'}),
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
            'nombre': forms.TextInput(attrs={'class': 'form-input'}),
            'apellido': forms.TextInput(attrs={'class': 'form-input'}),
            'dni': forms.TextInput(attrs={
                'class': 'form-input',
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
            'patente': forms.TextInput(attrs={'class': 'form-input'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
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
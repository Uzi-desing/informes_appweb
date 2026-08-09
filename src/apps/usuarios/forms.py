from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    error_messages = {  # noqa: RUF012
        'invalid_login': "El usuario o la contraseña son incorrectos. Por favor, verifique sus credenciales.",
        'inactive': "Esta cuenta ha sido inhabilitada por la administración.",
    }

    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(attrs={
            'placeholder': 'Ingrese su usuario',
            'autocomplete': 'username'
        }) 
    )

    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Ingrese su contraseña',
            'autocomplete': 'current-password'
        })
    )
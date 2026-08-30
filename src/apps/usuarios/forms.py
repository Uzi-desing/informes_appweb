from django import forms
from django.contrib.auth.forms import AuthenticationForm

CLASE_INPUT = (
    'w-full rounded-lg border border-gray-300 dark:border-gray-600 '
    'bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 '
    'pl-10 pr-3 py-2 text-sm placeholder-gray-400 dark:placeholder-gray-500 '
    'focus:outline-none focus:ring-2 focus:ring-secondary/50 focus:border-secondary '
    'transition-colors duration-200'
)

CLASE_PASSWORD = (
    'w-full rounded-lg border border-gray-300 dark:border-gray-600 '
    'bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 '
    'pl-10 pr-12 py-2 text-sm placeholder-gray-400 dark:placeholder-gray-500 '
    'focus:outline-none focus:ring-2 focus:ring-secondary/50 focus:border-secondary '
    'transition-colors duration-200'
)


class LoginForm(AuthenticationForm):
    error_messages = {  # noqa: RUF012
        'invalid_login': "El usuario o la contraseña son incorrectos. Por favor, verifique sus credenciales.",
        'inactive': "Esta cuenta ha sido inhabilitada por la administración.",
    }

    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(attrs={
            'class': CLASE_INPUT,
            'placeholder': 'Ingrese su usuario',
            'autocomplete': 'username'
        }) 
    )

    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': CLASE_PASSWORD,
            'placeholder': 'Ingrese su contraseña',
            'autocomplete': 'current-password'
        })
    )
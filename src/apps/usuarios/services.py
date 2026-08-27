import logging

from django.contrib.auth import login, logout

logger = logging.getLogger(__name__)

# Service encargado de gestionar la logica de las sesiones de los usuarios.
def procesar_login(request, form):
    user = form.get_user()
    login(request, user)

    logger.info(f"Ingreso exitoso: Usuario '{user.username}' (IP: {request.META.get('REMOTE_ADDR')})")

def procesar_logout(request):
    usuario = request.user.username if request.user.is_authenticated else 'Anonimo'
    logout(request)

    logger.info(f"Cierre de sesión: Usuario ('{usuario}')")
    return "Haz cerrado sesión."




from django.contrib.auth import login, logout


# Service encargado de gestionar la logica de las sesiones de los usuarios.
def procesar_login(request, form):
    user = form.get_user()
    login(request, user)

    nombre_mostrar = user.get_short_name() or user.username
    return f"Bienvenido/a {nombre_mostrar}."

def procesar_logout(request):
    logout(request)
    return "Haz cerrado sesión."




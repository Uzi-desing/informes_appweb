from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def solo_operarios(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        user = request.user

        if not user.is_active:
            raise PermissionDenied("Tu cuenta se encuentra inactiva.")

        if user.is_superuser:
            return view_func(request, *args, **kwargs)

        perfil = getattr(user, 'perfil_empleado', None)

        if perfil is not None and perfil.rol is not None:
            rol_slug = perfil.rol.slug 
            if rol_slug.lower() == 'operario':
                return view_func(request, *args, **kwargs)
            
        raise PermissionDenied("Acceso Denegado: Se requiere perfil de Operario.")

    return _wrapped_view
    
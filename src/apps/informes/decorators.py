from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from .models import InformeDano


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

def bloqueo_informe_pendiente(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        perfil = getattr(request.user, 'perfil_empleado', None)
        if perfil is not None:
            pendiente = InformeDano.objects.filter(
                empleado=perfil, finalizado=False
            ).order_by('fecha').first()
            if pendiente:
                return redirect('registrar_piezas', uuid=pendiente.uuid_identificador)
        return view_func(request, *args, **kwargs)

    return _wrapped_view

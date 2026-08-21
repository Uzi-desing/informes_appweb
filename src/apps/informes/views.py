import logging

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import DatabaseError, IntegrityError
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from .decorators import solo_operarios
from .forms import InformeDanoForm, TransportistaForm, VehiculoForm
from .services.informe_service import InformeService

logger = logging.getLogger(__name__)


# Create your views here.
@never_cache
@require_http_methods(["GET", "POST"])
@solo_operarios
def home(request):
    return render(request, 'home.html')

@never_cache
@require_http_methods(["GET", "POST"])
@solo_operarios
def crear_informe_view(request):
    if request.method == 'POST':
        informe_form = InformeDanoForm(request.POST)
        transportista_form = TransportistaForm(request.POST)
        vehiculo_form = VehiculoForm(request.POST)

        if informe_form.is_valid() and transportista_form.is_valid() and vehiculo_form.is_valid():
            try:
                informe = InformeService.crear_informe_completo(informe_form, transportista_form, vehiculo_form, request.user.perfil_empleado)
                messages.success(request, f"Informe Nº {informe.remito_recepcion} creado con éxito.")
                logger.info(f"Informe Nº {informe.remito_recepcion} creado por '{request.user.username}'.")
                return redirect('home')
            except (ValidationError, IntegrityError, DatabaseError) as e:
                logger.error(f"Error técnico al guardar informe: {e!s}")
                messages.error(request, "No se pudo guardar el informe, verifique la información.")
            except Exception as e:  # noqa: BLE001
                logger.error(f"Error técnico al crear informe: {e!s}")
                messages.error(request, 'Error interno al guardar el informe.')
        else:
            messages.error(request, "Por favor, revisa los campos del formulario.")
    else:
        informe_form = InformeDanoForm()
        transportista_form = TransportistaForm()
        vehiculo_form = VehiculoForm()

    context = {
        'informe_form': informe_form,
        'transportista_form': transportista_form,
        'vehiculo_form': vehiculo_form
    }

    return render(request, 'crear_informe.html', context)

import logging

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import DatabaseError, IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from .decorators import bloqueo_informe_pendiente, solo_operarios
from .forms import InformeDanoForm, TransportistaForm, VehiculoForm, PiezaRechazadaFormSet
from .models import InformeDano
from .services.informe_service import InformeService
from .services.pieza_service import PiezaService

logger = logging.getLogger(__name__)


# Create your views here.
@never_cache
@require_http_methods(["GET", "POST"])
@solo_operarios
@bloqueo_informe_pendiente
def home(request):
    return render(request, 'home.html')

@never_cache
@require_http_methods(["GET", "POST"])
@solo_operarios
@bloqueo_informe_pendiente
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
                return redirect('registrar_piezas', uuid=informe.uuid_identificador)
            
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

@require_http_methods(["GET", "POST"])
@solo_operarios
def registrar_piezas_view(request, uuid):
    informe = get_object_or_404(InformeDano, uuid_identificador=uuid)

    if informe.esta_bloqueado:
        logger.warning(f"Intento de acceso a informe finalizado (UUID: {uuid})")
        messages.error(request, "Este informe ya fue completado y finalizado.")
        return redirect('home')

    if request.method == 'POST':
        formset = PiezaRechazadaFormSet(request.POST, request.FILES, instance=informe)

        if formset.is_valid():
            try:
                PiezaService.procesar_piezas_y_finalizar(informe, formset)

                logger.info(f"Informe Nº{informe.remito_recepcion} completado con exito.")
                messages.success(request, f"Informe Nº{informe.remito_recepcion} completado exitosamente.")

                return redirect('home')

            except ValidationError as e:
                messages.error(request, str(e))

            except Exception as e:  # noqa: BLE001
                logger.error(f"Error grave al guardar piezas del informe {informe.remito_recepcion}: {e!s}")
                messages.error(request, "Ocurrió un error interno al guardar las piezas y las imágenes.")
        else:
            for error in formset.non_form_errors():
                messages.error(request, error)
            messages.error(request, "Revise los formularios de las piezas.")
    else:
        formset = PiezaRechazadaFormSet(instance=informe)

    context = {
        'informe': informe,
        'formset': formset
    }
    return render(request, 'agregar_piezas.html', context)

@never_cache
@require_http_methods(["POST"])
@solo_operarios
def cancelar_informe_view(request, uuid):
    perfil = getattr(request.user, 'perfil_empleado', None)
    informe = get_object_or_404(
        InformeDano,
        uuid_identificador=uuid,
        finalizado=False,
        empleado=perfil,
    )

    try:
        remito = InformeService.cancelar_informe(informe)
    except Exception as e:  # noqa: BLE001
        logger.error(f"Error al cancelar el informe {uuid}: {e!s}")
        messages.error(request, "No se pudo cancelar el informe.")
        return redirect('registrar_piezas', uuid=uuid)

    logger.info(f"Informe Nº{remito} cancelado por '{request.user.username}'.")
    messages.info(request, f"Informe Nº{remito} cancelado y eliminado.")
    return redirect('home')
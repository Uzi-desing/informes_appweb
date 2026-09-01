import logging

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import DatabaseError, IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods

from apps.usuarios.models import Empleado

from .decorators import bloqueo_informe_pendiente, solo_operarios
from .forms import (
    ClienteForm,
    InformeDanoForm,
    PiezaRechazadaFormSet,
    TransportistaForm,
    VehiculoForm,
)
from .models import InformeDano
from .services.cliente_service import ClienteService
from .services.informe_service import InformeService
from .services.pdf_service import PdfService
from .services.pieza_service import PiezaService

logger = logging.getLogger(__name__)


# Create your views here.
@never_cache
@require_http_methods(["GET", "POST"])
@solo_operarios
@bloqueo_informe_pendiente
def home(request):
    ultimo_informe = InformeService.obtener_ultimo_informe()
    return render(request, 'home.html', {'ultimo_informe': ultimo_informe})

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
                messages.success(request, f"Informe Nº {informe.remito_recepcion} completado exitosamente.")

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

@never_cache
@require_http_methods(["GET", "POST"])
@solo_operarios
def crear_cliente_view(request):
    if request.method == 'POST':
        cliente_form = ClienteForm(request.POST)

        if cliente_form.is_valid():
            try:
                cliente = ClienteService.crear_cliente(cliente_form)
                logger.info(f"Nuevo cliente '{cliente.nombre}' registrado por '{request.user.username}'.")
                messages.success(request, f"Cliente {cliente.nombre} registrado exitosamente.")

                return redirect('home')

            except (ValidationError, IntegrityError, DatabaseError) as e:
                logger.error(f"Error técnico al guardar cliente: {e!s}")
                messages.error(request, "No se pudo guardar el cliente, verifique la información.")

            except Exception as e:  # noqa: BLE001
                logger.error(f"Error al crear cliente: {e!s}")
                messages.error(request, 'Error interno al guardar el cliente.')

        else:
            messages.error(request, "Revisa los campos del formulario.")

    else:
        cliente_form = ClienteForm()

    context = {
        'cliente_form': cliente_form
    }          

    return render(request, 'crear_cliente.html', context) 

@never_cache
@require_http_methods(["GET"])
@solo_operarios
def lista_informes_view(request):
    q = request.GET.get('q', '').strip()
    empleado_id = request.GET.get('empleado', '').strip()
    orden = request.GET.get('orden', 'fecha_desc')

    page_obj = InformeService.obtener_informes(
        request.GET.get('page'), q, empleado_id, orden
    )

    empleados = Empleado.objects.select_related('usuario').only(
        'id', 'usuario__first_name', 'usuario__last_name', 'usuario__username'
    )

    context = {
        'page_obj': page_obj,
        'empleados': empleados,
        'filtros': {
            'q': q, 'empleado': empleado_id, 'orden': orden,
        },
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, '_tabla_informes.html', context)

    return render(request, 'ver_informes.html', context)

@never_cache
@require_http_methods(["GET"])
@solo_operarios
def lista_clientes_view(request):
    q = request.GET.get('q', '').strip()
    orden = request.GET.get('orden', 'nombre_asc')

    page_obj = ClienteService.obtener_clientes(
        request.GET.get('page'), q, orden
    )

    context = {
        'page_obj': page_obj,
        'filtros': {'q': q, 'orden': orden},
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, '_tabla_clientes.html', context)

    return render(request, 'ver_clientes.html', context)

@never_cache
@require_http_methods(["GET"])
@solo_operarios
def detalle_informe_view(request, uuid):
    informe, piezas = InformeService.obtener_detalle_informe(uuid)
    return render(request, 'detalle_informe.html', {'informe': informe, 'piezas': piezas,})

@never_cache
@require_http_methods(["GET"])
@solo_operarios
def generar_reporte_pdf_view(request, uuid):
    informe, _ = InformeService.obtener_detalle_informe(uuid)
    pdf = PdfService.generar_reporte(informe)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Informe_{informe.id}.pdf"'
    return response
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q

from apps.informes.models import InformeDano, UsuarioTransportista, Vehiculo


class InformeService:
    ORDENES_PERMITIDAS = {  # noqa: RUF012
        'fecha_asc': 'fecha',
        'fecha_desc': '-fecha',
        'id_asc': 'id',
        'id_desc': '-id',
    }

    @staticmethod
    @transaction.atomic
    def crear_informe_completo(informe_form, transportista_form, vehiculo_form, empleado):
        transportista, _ = UsuarioTransportista.objects.get_or_create(
            dni = transportista_form.cleaned_data['dni'],
            defaults={
                'nombre': transportista_form.cleaned_data['nombre'].strip().lower(),
                'apellido': transportista_form.cleaned_data['apellido'].strip().lower()
            }
        )

        patente_limpia = vehiculo_form.cleaned_data['patente'].replace(" ", "").upper()
        vehiculo, _ = Vehiculo.objects.get_or_create(
            patente = patente_limpia,
            defaults={'tipo': vehiculo_form.cleaned_data['tipo']}
        )

        informe = informe_form.save(commit=False)
        informe.empleado = empleado
        informe.transportista = transportista
        informe.vehiculo = vehiculo
        informe.save()

        return informe

    @staticmethod
    @transaction.atomic
    def cancelar_informe(informe):
        remito = informe.remito_recepcion
        informe.delete()

        return remito

    @staticmethod
    def obtener_informes(page_number, q='', empleado_id='', orden='fecha_desc'):
        informes = (
            InformeDano.objects
            .select_related('cliente', 'empleado__usuario')
            .only(
                'id', 'fecha', 'remito_recepcion', 'finalizado',
                'cliente__nombre',
                'empleado__usuario__first_name',
                'empleado__usuario__last_name',
                'empleado__usuario__username',
            )
        )

        q = (q or '').strip()
        if q:
            if q.isdigit():
                informes = informes.filter(
                    Q(id=q)
                    | Q(cliente__nombre__icontains=q)
                    | Q(remito_recepcion__icontains=q)
                )
            else:
                informes = informes.filter(
                    Q(cliente__nombre__icontains=q)
                    | Q(remito_recepcion__icontains=q)
                )

        if empleado_id:
            informes = informes.filter(empleado_id=empleado_id)

        orden_efectivo = InformeService.ORDENES_PERMITIDAS.get(orden, '-fecha')
        informes = informes.order_by(orden_efectivo, 'id')

        paginator = Paginator(informes, 6)
        return paginator.get_page(page_number)
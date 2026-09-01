from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q

from apps.informes.models import Cliente


class ClienteService:
    @staticmethod
    @transaction.atomic
    def crear_cliente(cliente_form):
        cliente = cliente_form.save(commit=False)
        cliente.nombre = cliente.nombre.strip().lower()
        cliente.domicilio = cliente.domicilio.strip().lower()
        if cliente.mail:
            cliente.mail = cliente.mail.strip().lower()
        cliente.save()

        return cliente

    ORDENES_PERMITIDAS = {  # noqa: RUF012
        'nombre_asc': 'nombre',
        'nombre_desc': '-nombre',
    }

    @staticmethod
    def obtener_clientes(page_number, q='', orden='nombre_asc'):
        clientes = (
            Cliente.objects
            .annotate(total_informes=Count('informes'))
            .only('nombre', 'telefono', 'mail', 'domicilio')
        )

        q = (q or '').strip()
        if q:
            clientes = clientes.filter(
                Q(nombre__icontains=q) | Q(domicilio__icontains=q)
            )

        orden_efectivo = ClienteService.ORDENES_PERMITIDAS.get(orden, 'nombre')
        clientes = clientes.order_by(orden_efectivo, 'id')
        paginator = Paginator(clientes, 6)
        return paginator.get_page(page_number)

    
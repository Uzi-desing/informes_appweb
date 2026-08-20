from django.db import models


class InformesDanoQuerySet(models.QuerySet):
    # Realiza una sola consulta a la DB toda la informacion del informe, del empleado que lo hizo, el cliente, el transportista, vehículo y las piezas.
    def con_relaciones(self):
        return self.select_related(
            'empleado__usuario',
            'cliente',
            'transportista',
            'vehiculo'
        ).prefetch_related(
            'piezas_rechazadas__pieza__categoria',
            'piezas_rechazadas__categoria_dano'
        )

    def pendientes(self):
        return self.filter(finalizado=False)

    def finalizados(self):
        return self.filter(finalizado=True)
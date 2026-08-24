from django.db import transaction


class PiezaService:
    @staticmethod
    @transaction.atomic
    def procesar_piezas_y_finalizar(informe, formset):
        piezas_guardadas = formset.save()
        informe.finalizar()

        return piezas_guardadas
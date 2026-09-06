from django.db import transaction

from apps.informes.models import Categoria, Pieza


class PiezaService:
    @staticmethod
    @transaction.atomic
    def procesar_piezas_y_finalizar(informe, formset):
        piezas_guardadas = formset.save()
        informe.finalizar()

        return piezas_guardadas

    @staticmethod
    @transaction.atomic
    def crear_pieza(categoria, medida):
        if not isinstance(categoria, Categoria):
            try:
                categoria = Categoria.objects.get(pk=categoria)
            except Categoria.DoesNotExist:
                raise ValueError(f"La categoría '{categoria}' no existe.")

        medida_normalizada = medida.strip().replace(',', '.')

        pieza, creado = Pieza.objects.get_or_create(
            categoria=categoria,
            medida=medida_normalizada,
        )
        return pieza, creado
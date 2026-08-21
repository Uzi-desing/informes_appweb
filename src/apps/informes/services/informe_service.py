from django.db import transaction

from apps.informes.models import UsuarioTransportista, Vehiculo


class InformeService:
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
from django.db import transaction


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
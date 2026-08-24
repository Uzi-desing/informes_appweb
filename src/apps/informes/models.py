import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from apps.usuarios.models import Empleado

from .managers import InformesDanoQuerySet
from .services.azure_service import AzureBlobService
from .services.image_service import ImageProcessorService
from .storage_backends import AzureMediaStorage


# Create your models here.
class Categoria(models.Model):
    descripcion = models.CharField(max_length=100)

    class Meta: 
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.descripcion

class CategoriaDano(models.Model):
    motivo = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Tipo de Daño'
        verbose_name_plural = 'Tipos de Daño'

    def __str__(self):
        return self.motivo

class Cliente(models.Model):
    nombre = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    mail = models.EmailField(unique=True, null=True, blank=True)
    domicilio = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.nombre

class UsuarioTransportista(models.Model):
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    dni = models.CharField(max_length=20, unique=True)
    class Meta:
        verbose_name = 'Transportista'
        verbose_name_plural = 'Transportistas'

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
    
    def __str__(self):
        return f"{self.nombre_completo} (DNI: {self.dni})"

class Vehiculo(models.Model):
    class TipoTransporte(models.TextChoices):
        CAMION = 'CAMION', 'Camión'
        SEMIREMOLQUE = 'SEMIREMOLQUE', 'Semirremolque'
        CAMIONETA = 'CAMIONETA', 'Camioneta'
        FURGONETA = 'FURGONETA', 'Furgoneta'
        PARTICULAR = 'PARTICULAR', 'Particular'

    OPCIONES_TRANSPORTE = TipoTransporte.choices

    patente = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(max_length=20, choices=TipoTransporte.choices, default=TipoTransporte.CAMION)

    class Meta: 
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'

    def __str__(self):
        return f"{self.patente} ({self.get_tipo_display()})"

class Pieza(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='piezas')
    medida = models.CharField(max_length=100)

    class Meta: 
        verbose_name = 'Pieza'
        verbose_name_plural = 'Piezas'

    def __str__(self):
        return f"{self.categoria.descripcion} - {self.medida}"

class InformeDano(models.Model):
    uuid_identificador = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="Indentificador único del reporte para trazabilidad"
    )

    empleado = models.ForeignKey(Empleado, on_delete=models.PROTECT, related_name='informes_creados')
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='informes')
    transportista = models.ForeignKey(UsuarioTransportista, on_delete=models.PROTECT, related_name='informes')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT, related_name='informes')
    remito_recepcion = models.CharField(
        max_length=100,
        unique=True,
        error_messages={
            'unique': 'El número de remito ya se encuentra en el sistema.'
        },
    )
    fecha = models.DateField(auto_now_add=True)
    finalizado = models.BooleanField(default=False)

    objects = InformesDanoQuerySet.as_manager()

    @property
    def esta_bloqueado(self):
        return self.finalizado

    def finalizar(self):
        if not self.piezas_rechazadas.exists():
            raise ValidationError("No se puede finalizar un informe vacío.")
        self.finalizado = True
        self.save(update_fields=['finalizado'])

    def clean(self):
        if self.remito_recepcion:
            self.remito_recepcion = self.remito_recepcion.strip().replace(" ", "").upper()
        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Informe Nº {self.remito_recepcion} - {self.cliente.nombre}"

class PiezaRechazada(models.Model):
    uuid_identificador = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    informe = models.ForeignKey(InformeDano, on_delete=models.CASCADE, related_name='piezas_rechazadas')
    pieza = models.ForeignKey('Pieza', on_delete=models.PROTECT, related_name='piezas_rechazadas')
    categoria_dano = models.ForeignKey('CategoriaDano', on_delete=models.PROTECT, related_name='piezas_rechazadas')
    observaciones = models.TextField(blank=True, null=True)
    cantidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    imagen = models.ImageField(upload_to='piezas-rechazadas-images/', storage=AzureMediaStorage(), blank=True, null=True)

    @property
    def url_segura(self):
        if self.imagen:
            return AzureBlobService.generate_url_sas(self.imagen.name)
        return None

    def save(self, *args, **kwargs):
        if self.informe.esta_bloqueado:
            raise ValidationError("No se puede modificar piezas en un informe finalizado.")

        procesar = bool(self.imagen and (self.pk is None))

        if self.pk and self.imagen:
            try:
                original = PiezaRechazada.objects.get(pk=self.pk)
                if original.imagen.name != self.imagen.name:
                    if original.imagen: 
                        original.imagen.delete(save=False)
                    procesar = True
            except PiezaRechazada.DoesNotExist:
                procesar = True

        if procesar:
            nombre_cliente = self.informe.cliente.nombre
            num_informe = self.informe.remito_recepcion
            
            nombre_img, archivo_opt = ImageProcessorService.optimizar_imagen(
                self.imagen,
                self.uuid_identificador,
                nombre_cliente,
                num_informe
            )
            self.imagen.save(nombre_img, archivo_opt, save=False)

        super().save(*args, **kwargs)


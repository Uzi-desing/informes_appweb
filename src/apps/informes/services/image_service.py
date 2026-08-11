import uuid
from io import BytesIO

from django.core.files.base import ContentFile
from django.utils.text import slugify
from PIL import Image


class ImageProcessorService:
    @staticmethod
    def optimizar_imagen(imagen_field, identificador_uuid, nombre_cliente, num_informe):
        # Comprime la imagen y genera un nombre unico para el archivo
        img = Image.open(imagen_field)

        if img.mode != 'RGB':
            img = img.convert('RGB')

        img.thumbnail((1280, 720), Image.Resampling.LANCZOS)

        output = BytesIO()
        img.save(output, format='JPEG', quality=70, optimize=True)
        output.seek(0)

        cliente_seguro = slugify(nombre_cliente)
        informe_seguro = slugify(num_informe)

        nombre_imagen = f"{cliente_seguro}_{informe_seguro}_{identificador_uuid.hex[:8]}_{uuid.uuid4().hex[:4]}.jpg"

        archivo_listo = ContentFile(output.read())

        return nombre_imagen, archivo_listo

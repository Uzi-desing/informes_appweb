import os
from io import BytesIO
from typing import Any, Optional

import requests
from django.conf import settings
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader, simpleSplit
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

from .azure_service import AzureBlobService

# --- Paleta de Colores ---
ROJO = '#e8232a'
NEGRO = '#1a1a1a'
GRIS_OSCURO = '#333333'
GRIS_MED = '#555555'
GRIS_CLARO = '#cccccc'
GRIS_FONDO = '#f4f4f4'
GRIS_META = '#f9f9f9'
ROJO_LIGHT = '#fff0f0'
BLANCO = '#ffffff'


class GeneradorReportePDF:
    def __init__(self, informe: Any):
        self.informe = informe
        self.buffer = BytesIO()
        self.c = canvas.Canvas(self.buffer, pagesize=A4)
        self.width, self.height = A4

        # Márgenes
        self.ml = 42
        self.mr = self.width - 42
        self.mt = self.height - 36
        self.mb = 42
        self.img_col_w = 260
        self.img_h = 140
        self.gap = 10

        self.y_curr = self.mt
        self.page_num = 1
        self.logo_reader = self._preload_logo()

    # --- Utilidades para el dibujo ---
    def _rect_fill(self, x: float, y: float, w: float, h: float, fill: str, stroke: Optional[str] = None, lw: float = 0.5, radius: float = 0):
        self.c.setLineWidth(lw)
        self.c.setFillColor(fill)
        if stroke:
            self.c.setStrokeColor(stroke)
            self.c.roundRect(x, y, w, h, radius, fill=1, stroke=1)
        else:
            self.c.setStrokeColor(fill)
            self.c.roundRect(x, y, w, h, radius, fill=1, stroke=0)

    def _text(self, x: float, y: float, txt: Any, font: str = 'Helvetica', size: float = 10, color: str = '#000000', align: str = 'left'):
        self.c.setFont(font, size)
        self.c.setFillColor(color)
        if align == 'center':
            self.c.drawCentredString(x, y, str(txt))
        elif align == 'right':
            self.c.drawRightString(x, y, str(txt))
        else:
            self.c.drawString(x, y, str(txt))

    def _line(self, x1: float, y1: float, x2: float, y2: float, color: str = GRIS_CLARO, lw: float = 0.5):
        self.c.setStrokeColor(color)
        self.c.setLineWidth(lw)
        self.c.line(x1, y1, x2, y2)

    def _formatear_dni(self, dni: Any) -> str:
        """Convierte un DNI en string con separadores de miles usando puntos."""
        if not dni:
            return ""
        try:
            return f"{int(dni):,}".replace(",", ".")
        except (ValueError, TypeError):
            return str(dni)

    def _nombre_empleado(self, empleado: Any) -> str:
        """Devuelve el nombre completo del empleado o su username como fallback."""
        nombre = empleado.usuario.get_full_name()
        return nombre or empleado.usuario.username

    def _preload_logo(self) -> Optional[ImageReader]:
        try:
            logo_path = os.path.join(settings.STATICFILES_DIRS[0], 'img', 'logo.png')
            img = Image.open(logo_path)
            if img.mode in ('RGBA', 'LA', 'P'):
                bg = Image.new('RGB', img.size, (255, 255, 255))
                mask = img.convert('RGBA').split()[-1]
                bg.paste(img, mask=mask)
                img = bg
            return ImageReader(img)
        except Exception:
            return None

    def _load_image(self, pieza: Any) -> Optional[ImageReader]:
        if not pieza.imagen:
            return None
        try:
            url_sas = AzureBlobService.generate_url_sas(pieza.imagen.name, expira_en_min=5)
            with requests.get(url_sas, timeout=5) as res:
                res.raise_for_status()
                img = Image.open(BytesIO(res.content))
                if img.mode in ('RGBA', 'LA', 'P'):
                    bg = Image.new('RGB', img.size, (255, 255, 255))
                    mask = img.convert('RGBA').split()[-1]
                    bg.paste(img, mask=mask)
                    img = bg
                return ImageReader(img)
        except Exception:
            return None

    # --- Paginación y Textos globales ---
    def _dibujar_paginacion(self):
        y_pag = 20
        texto = f'INFORME N°{self.informe.id}  |  Página {self.page_num}'
        self._text(self.mr, y_pag, texto, 'Helvetica-Bold', 8, GRIS_MED, 'right')

    # --- Encabezado del Informe ---
    def dibujar_encabezado(self, es_primera_pagina: bool = False):
        ancho = self.mr - self.ml
        w1, w2 = 130, 140
        w3 = ancho - w1 - w2
        y = self.y_curr

        self.c.setLineWidth(0.8)
        self.c.setStrokeColor(NEGRO)
        for x_off, w in [(0, w1), (w1, w2), (w1 + w2, w3)]:
            self.c.rect(self.ml + x_off, y - 35, w, 35)

        self._text(self.ml + w1 / 2, y - 21, 'DOCUMENTOS DEL SIG', 'Helvetica-Bold', 9, GRIS_OSCURO, 'center')

        if self.logo_reader:
            lw, lh = 85, 26
            lx = self.ml + w1 + (w2 - lw) / 2
            self.c.drawImage(self.logo_reader, lx, y - 30, width=lw, height=lh, preserveAspectRatio=True)

        self._text(self.ml + w1 + w2 + w3 / 2, y - 15, 'DOCUMENTO OPERATIVO', 'Helvetica-Bold', 8, GRIS_OSCURO, 'center')
        self._text(self.ml + w1 + w2 + w3 / 2, y - 27, f'INFORME N°{self.informe.id}', 'Helvetica-Bold', 11, ROJO, 'center')

        self.y_curr -= 35

        self._rect_fill(self.ml, self.y_curr - 26, ancho, 26, BLANCO, NEGRO)
        self._text(self.ml + ancho / 2, self.y_curr - 17, 'RECHAZO DE MATERIALES', 'Helvetica-Bold', 14, NEGRO, 'center')
        self.y_curr -= 26

        if es_primera_pagina:
            self._dibujar_meta()
        else:
            self.y_curr -= 16

        self._text(self.ml, self.y_curr - 2, 'Detalle de Piezas Rechazadas', 'Helvetica-Bold', 12, NEGRO)
        total = self.informe.piezas_rechazadas.count()
        self._text(self.mr, self.y_curr - 2, f'{total} {"pieza" if total == 1 else "piezas"}', 'Helvetica', 10, GRIS_MED, 'right')
        self._line(self.ml, self.y_curr - 8, self.ml + 220, self.y_curr - 8, ROJO, lw=2)
        self.y_curr -= 20

    # --- Detalles generales del Informe ---
    def _dibujar_meta(self):
        ancho = self.mr - self.ml
        y = self.y_curr

        self._rect_fill(self.ml, y - 70, ancho, 70, GRIS_META, GRIS_CLARO)

        bw, bh = 80, 56
        bx = self.mr - bw
        self._rect_fill(bx, y - bh, bw, bh, ROJO, radius=3)
        self._text(bx + bw / 2, y - 16, 'INFORME', 'Helvetica-Bold', 7, BLANCO, 'center')
        self._text(bx + bw / 2, y - 42, str(self.informe.id), 'Helvetica-Bold', 26, BLANCO, 'center')

        empleado = self._nombre_empleado(self.informe.empleado)

        campos = [
            ('Remito Recepción', self.informe.remito_recepcion or 'N/A'),
            ('Fecha',            self.informe.fecha.strftime('%d/%m/%Y')),
            ('Cliente',          self.informe.cliente.nombre.title()),
            ('Empleado a Cargo', empleado.title()),
        ]
        col_w = (ancho - bw - 16) / 2
        row_h = 32
        x_cols = [self.ml + 12, self.ml + 12 + col_w + 12]

        for i, (label, val) in enumerate(campos):
            col = i % 2
            row = i // 2
            cx = x_cols[col]
            cy = y - 16 - row * row_h
            self._text(cx, cy,      label, 'Helvetica-Bold', 9, GRIS_MED)
            self._text(cx, cy - 12, val,   'Helvetica',      11,  NEGRO)
            self._line(cx, cy - 18, cx + col_w - 12, cy - 18, GRIS_CLARO)

        self.y_curr -= 95

    # Cards para las Piezas Rechazadas
    def _calc_card_height(self, pieza: Any) -> float:
        txt_col = (self.mr - self.ml) - self.img_col_w - 16
        obs = pieza.observaciones or 'Sin observaciones.'
        lines = simpleSplit(obs, 'Helvetica', 10, txt_col - 8)
        n_lines = max(1, len(lines))

        datos_h = 40 + 20 + 16 + n_lines * 14
        body_h = max(self.img_h, datos_h)
        return 28 + body_h + 16

    def dibujar_pieza(self, pieza: Any, numero: int, es_ultima: bool = False):
        card_h = self._calc_card_height(pieza)
        ancho = self.mr - self.ml

        espacio_necesario = card_h
        if es_ultima:
            espacio_necesario += 140

        if self.y_curr - espacio_necesario < self.mb + 15:
            self._dibujar_paginacion()
            self.c.showPage()
            self.page_num += 1
            self.y_curr = self.mt
            self.dibujar_encabezado(es_primera_pagina=False)

        y_top = self.y_curr

        self._rect_fill(self.ml, y_top - card_h, ancho, card_h, BLANCO, GRIS_CLARO, radius=4)

        self._rect_fill(self.ml, y_top - 28, ancho, 28, GRIS_FONDO, GRIS_CLARO, radius=4)
        self._rect_fill(self.ml, y_top - 28, ancho, 14, GRIS_FONDO)

        self._text(self.ml + 12, y_top - 19, f'PIEZA N° {numero}', 'Helvetica-Bold', 11, ROJO)

        dano_txt = str(pieza.categoria_dano).title()
        dano_w = stringWidth(f'Daño: {dano_txt}', 'Helvetica-Bold', 9) + 20
        dano_x = self.mr - dano_w - 8
        self._rect_fill(dano_x, y_top - 23, dano_w, 18, ROJO_LIGHT, '#ffbbbb')
        self._text(dano_x + dano_w / 2, y_top - 15, f'Daño: {dano_txt}', 'Helvetica-Bold', 9, '#c0392b', 'center')

        x_img = self.ml + 10
        img_draw_w = self.img_col_w - 20
        y_img_top = y_top - 34
        y_img_bot = y_top - card_h + 12
        h_img = y_img_top - y_img_bot

        img_reader = self._load_image(pieza)
        if img_reader:
            self.c.drawImage(img_reader, x_img, y_img_bot, width=img_draw_w, height=h_img, preserveAspectRatio=True, anchor='c')
        else:
            self._rect_fill(x_img, y_img_bot, img_draw_w, h_img, '#ebebeb', GRIS_CLARO)
            self._text(x_img + img_draw_w / 2, y_img_bot + h_img / 2 - 5, 'Sin imagen', 'Helvetica', 10, GRIS_MED, 'center')

        self._line(self.ml + self.img_col_w, y_top - 30, self.ml + self.img_col_w, y_top - card_h + 8, GRIS_CLARO)

        x_txt = self.ml + self.img_col_w + 12
        max_tw = self.mr - x_txt - 10
        cy = y_top - 45

        self._text(x_txt,      cy, 'Cantidad',      'Helvetica-Bold', 9, GRIS_OSCURO)
        self._text(x_txt + 70, cy, 'Categoria / Medida', 'Helvetica-Bold', 9, GRIS_OSCURO)
        cy -= 18

        self._text(x_txt, cy, str(pieza.cantidad), 'Helvetica-Bold', 18, ROJO)
        tipo_med = f'{pieza.pieza.categoria.descripcion.title()} — {pieza.pieza.medida}'

        for l in simpleSplit(tipo_med, 'Helvetica', 10, max_tw - 70):
            self._text(x_txt + 70, cy, l, 'Helvetica', 10, NEGRO)
            cy -= 14
        cy -= 6

        self._line(x_txt, cy + 4, self.mr - 10, cy + 4)
        cy -= 14

        self._text(x_txt, cy, 'Observaciones', 'Helvetica-Bold', 9, GRIS_OSCURO)
        cy -= 14
        obs = pieza.observaciones or 'Sin observaciones particulares.'
        for line in simpleSplit(obs, 'Helvetica', 10, max_tw):
            self._text(x_txt, cy, line, 'Helvetica', 10, NEGRO)
            cy -= 14

        self.y_curr -= (card_h + self.gap)

    # --- Pie de Página, Fijo al final de la página ---
    def dibujar_pie_final(self):
        ancho = self.mr - self.ml

        if self.y_curr < self.mb + 140:
            self._dibujar_paginacion()
            self.c.showPage()
            self.page_num += 1
            self.y_curr = self.mt
            self.dibujar_encabezado(es_primera_pagina=False)

        y_pie = self.mb + 65

        self._rect_fill(self.ml, y_pie, ancho, 65, BLANCO, GRIS_CLARO, radius=4)

        self._rect_fill(self.ml, y_pie + 47, ancho, 18, GRIS_FONDO, GRIS_CLARO, radius=4)
        self._rect_fill(self.ml, y_pie + 47, ancho, 9,  GRIS_FONDO)
        self._text(self.ml + 12, y_pie + 52, 'INFORMACIÓN DEL TRANSPORTE', 'Helvetica-Bold', 9, NEGRO)

        if self.informe.transportista:
            tr = self.informe.transportista
            vehiculo = self.informe.vehiculo
            mitad = self.ml + ancho / 2

            self._text(self.ml + 12, y_pie + 32, 'Vehículo:', 'Helvetica-Bold', 9, GRIS_MED)
            self._text(self.ml + 65, y_pie + 32, vehiculo.get_tipo_display(), 'Helvetica', 10, NEGRO)
            self._text(mitad,      y_pie + 32, 'Patente:', 'Helvetica-Bold', 9, GRIS_MED)
            self._text(mitad + 55, y_pie + 32, vehiculo.patente, 'Helvetica', 10, NEGRO)
            self._text(self.ml + 12, y_pie + 14, 'Chofer:', 'Helvetica-Bold', 9, GRIS_MED)
            self._text(self.ml + 65, y_pie + 14, tr.nombre_completo.title(), 'Helvetica', 10, NEGRO)
            self._text(mitad,      y_pie + 14, 'DNI:', 'Helvetica-Bold', 9, GRIS_MED)
            self._text(mitad + 55, y_pie + 14, self._formatear_dni(tr.dni), 'Helvetica', 10, NEGRO)

        firma_w = 170
        y_firma = self.mb + 25

        self._line(self.ml + 16, y_firma, self.ml + 16 + firma_w, y_firma, NEGRO, 0.7)
        self._text(self.ml + 16 + firma_w / 2, y_firma - 12, 'Firma Conductor', 'Helvetica', 9, GRIS_OSCURO, 'center')

        if self.informe.transportista:
            tr = self.informe.transportista
            self._text(self.ml + 16 + firma_w / 2, y_firma - 24, tr.nombre_completo.title(), 'Helvetica', 9, GRIS_MED, 'center')

        x_f2 = self.mr - 16 - firma_w
        self._line(x_f2, y_firma, self.mr - 16, y_firma, NEGRO, 0.7)
        self._text(x_f2 + firma_w / 2, y_firma - 12, 'Firma Control ECVA', 'Helvetica-Bold', 9, NEGRO, 'center')
        emp = self.informe.empleado
        self._text(x_f2 + firma_w / 2, y_firma - 24, self._nombre_empleado(emp).title(), 'Helvetica', 9, GRIS_MED, 'center')

        dni_empleado = self._formatear_dni(emp.dni)
        self._text(x_f2 + firma_w / 2, y_firma - 36, f'DNI: {dni_empleado}', 'Helvetica', 9, GRIS_MED, 'center')

    # --- Generación del Documento en Formato PDF ---
    def generar(self) -> bytes:
        self.dibujar_encabezado(es_primera_pagina=True)

        piezas = list(self.informe.piezas_rechazadas.all())
        total_piezas = len(piezas)

        for idx, pieza in enumerate(piezas, 1):
            es_ultima = (idx == total_piezas)
            self.dibujar_pieza(pieza, idx, es_ultima=es_ultima)

        self.dibujar_pie_final()

        self._dibujar_paginacion()
        self.c.showPage()
        self.c.save()

        pdf = self.buffer.getvalue()
        self.buffer.close()

        return pdf


class PdfService:
    @staticmethod
    def generar_reporte(informe) -> bytes:
        return GeneradorReportePDF(informe).generar()
import base64
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from apps.usuarios.models import Empleado, Rol, Usuario

from .models import (
    AzureMediaStorage,
    Categoria,
    CategoriaDano,
    Cliente,
    InformeDano,
    Pieza,
    PiezaRechazada,
    UsuarioTransportista,
)

PNG_1X1 = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
)


class ModelosInformesTests(TestCase):
    def setUp(self):
        self.rol = Rol.objects.create(puesto='Supervisor')
        self.usuario = Usuario.objects.create_user(
            username='jperez',
            email='jperez@test.com',
            password='clave123',
            first_name='Juan',
            last_name='Pérez',
        )
        self.empleado = Empleado.objects.create(
            usuario=self.usuario,
            rol=self.rol,
            dni='30123456',
            telefono='155551234',
        )
        self.categoria = Categoria.objects.create(descripcion='Motor')
        self.categoria_dano = CategoriaDano.objects.create(motivo='Rayadura')
        self.cliente = Cliente.objects.create(
            nombre='ACME S.A.',
            telefono='0800123456',
            mail='contacto@acme.com',
            domicilio='Av. Siempre Viva 742',
        )
        self.transportista = UsuarioTransportista.objects.create(
            nombre='Carlos',
            apellido='Gómez',
            dni='29876543',
            patente='AB123CD',
        )
        self.pieza = Pieza.objects.create(categoria=self.categoria, medida='1.5 m')

    def _crear_informe(self, remito='REM 001', **kwargs):
        return InformeDano.objects.create(
            empleado=self.empleado,
            cliente=self.cliente,
            transportista=self.transportista,
            remito_recepcion=remito,
            **kwargs,
        )

    def test_categoria_str(self):
        self.assertEqual(str(self.categoria), 'Motor')

    def test_categoria_dano_str(self):
        self.assertEqual(str(self.categoria_dano), 'Rayadura')

    def test_cliente_str(self):
        self.assertEqual(str(self.cliente), 'ACME S.A.')

    def test_transportista_str(self):
        self.assertEqual(str(self.transportista), 'Carlos Gómez (AB123CD)')

    def test_pieza_str(self):
        self.assertEqual(str(self.pieza), 'Motor - 1.5 m')

    def test_informe_asigna_patente_del_transportista(self):
        informe = self._crear_informe()
        self.assertEqual(informe.patente_informe, 'AB123CD')

    def test_informe_normaliza_remito(self):
        informe = self._crear_informe(remito='  rem 001 ')
        self.assertEqual(informe.remito_recepcion, 'REM001')

    def test_remito_recepcion_unico(self):
        self._crear_informe(remito='REM001')
        with self.assertRaises(ValidationError):
            self._crear_informe(remito='REM001')

    def test_esta_bloqueado(self):
        informe = self._crear_informe()
        self.assertFalse(informe.esta_bloqueado)

    def test_finalizar_informe_vacio_lanza_error(self):
        informe = self._crear_informe()
        with self.assertRaises(ValidationError):
            informe.finalizar()

    def test_finalizar_informe_con_pieza(self):
        informe = self._crear_informe()
        PiezaRechazada.objects.create(
            informe=informe,
            pieza=self.pieza,
            categoria_dano=self.categoria_dano,
        )
        informe.finalizar()
        self.assertTrue(informe.finalizado)
        self.assertTrue(informe.esta_bloqueado)

    def test_no_agregar_pieza_a_informe_finalizado(self):
        informe = self._crear_informe()
        PiezaRechazada.objects.create(
            informe=informe,
            pieza=self.pieza,
            categoria_dano=self.categoria_dano,
        )
        informe.finalizar()
        with self.assertRaises(ValidationError):
            PiezaRechazada.objects.create(
                informe=informe,
                pieza=self.pieza,
                categoria_dano=self.categoria_dano,
            )

    def test_pieza_rechazada_sin_imagen(self):
        informe = self._crear_informe()
        pieza = PiezaRechazada.objects.create(
            informe=informe,
            pieza=self.pieza,
            categoria_dano=self.categoria_dano,
            observaciones='Rayón en puerta',
        )
        self.assertIsNone(pieza.url_segura)
        self.assertEqual(pieza.cantidad, 1)

    def test_manager_pendientes_y_finalizados(self):
        informe_pendiente = self._crear_informe(remito='PEND01')
        informe_finalizado = self._crear_informe(remito='FINA01', finalizado=True)
        self.assertIn(informe_pendiente, InformeDano.objects.pendientes())
        self.assertIn(informe_finalizado, InformeDano.objects.finalizados())

    def test_manager_con_relaciones(self):
        informe = self._crear_informe()
        PiezaRechazada.objects.create(
            informe=informe,
            pieza=self.pieza,
            categoria_dano=self.categoria_dano,
        )
        resultado = InformeDano.objects.con_relaciones().get(pk=informe.pk)
        self.assertEqual(resultado.empleado.usuario.username, 'jperez')
        self.assertEqual(resultado.piezas_rechazadas.count(), 1)

    def _crear_pieza_con_imagen(self, remito='REMIMG01'):
        informe = self._crear_informe(remito=remito)
        imagen = SimpleUploadedFile('rayadura.png', PNG_1X1, content_type='image/png')
        with patch.object(AzureMediaStorage, '_save', side_effect=lambda name, content: name):
            return PiezaRechazada.objects.create(
                informe=informe,
                pieza=self.pieza,
                categoria_dano=self.categoria_dano,
                imagen=imagen,
            )

    def test_guardar_pieza_con_imagen(self):
        pieza = self._crear_pieza_con_imagen()
        self.assertTrue(pieza.imagen.name.startswith('piezas-rechazadas-images/acme-sa_remimg01'))
        self.assertTrue(pieza.imagen.name.endswith('.jpg'))

    def test_url_segura_genera_sas(self):
        pieza = self._crear_pieza_con_imagen()
        with patch(
            'apps.informes.models.AzureBlobService.generate_url_sas',
            return_value='https://fake-url',
        ) as mock_sas:
            url = pieza.url_segura
            mock_sas.assert_called_once_with(pieza.imagen.name)
        self.assertEqual(url, 'https://fake-url')

    def test_pieza_imagen_fallo_azure(self):
        informe = self._crear_informe(remito='REMFAL01')
        imagen = SimpleUploadedFile('rayadura.png', PNG_1X1, content_type='image/png')
        with patch.object(AzureMediaStorage, '_save', side_effect=Exception('Azure caído')):
            with self.assertRaises(Exception):
                PiezaRechazada.objects.create(
                    informe=informe,
                    pieza=self.pieza,
                    categoria_dano=self.categoria_dano,
                    imagen=imagen,
                )

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from apps.usuarios.models import Empleado, Rol

from .models import (
    Categoria,
    CategoriaDano,
    Cliente,
    InformeDano,
    Pieza,
    PiezaRechazada,
    UsuarioTransportista,
    Vehiculo,
)

Usuario = get_user_model()


class BaseInformeTest(TestCase):
    def setUp(self):
        self.rol = Rol.objects.create(puesto='Operario')
        self.usuario = Usuario.objects.create_user(
            username='operario1', password='clave123',
            email='operario1@test.com', first_name='Juan', last_name='Perez',
        )
        self.empleado = Empleado.objects.create(
            usuario=self.usuario, rol=self.rol,
            dni='30111222', telefono='011-123456',
        )
        self.cliente = Cliente.objects.create(
            nombre='Cliente Test', telefono='011-555',
            mail='cliente@test.com', domicilio='Calle 123',
        )
        self.conductor = UsuarioTransportista.objects.create(
            nombre='juan', apellido='romero', dni='30111222',
        )
        self.vehiculo = Vehiculo.objects.create(
            patente='AF482CK', tipo=Vehiculo.TipoTransporte.CAMION,
        )
        self.categoria = Categoria.objects.create(descripcion='Horizontal')
        self.categoria_dano = CategoriaDano.objects.create(motivo='Dobladura')
        self.pieza = Pieza.objects.create(categoria=self.categoria, medida='0.73')

    def crear_informe(self, remito='AB-1234', **kwargs):
        return InformeDano.objects.create(
            empleado=self.empleado, cliente=self.cliente,
            transportista=self.conductor, vehiculo=self.vehiculo,
            remito_recepcion=remito, **kwargs
        )


class TestCategoria(BaseInformeTest):
    def test_str(self):
        self.assertEqual(str(self.categoria), 'Horizontal')


class TestCategoriaDano(BaseInformeTest):
    def test_str(self):
        self.assertEqual(str(self.categoria_dano), 'Dobladura')


class TestCliente(BaseInformeTest):
    def test_str(self):
        self.assertEqual(str(self.cliente), 'Cliente Test')


class TestUsuarioTransportista(BaseInformeTest):
    def test_nombre_completo_y_str(self):
        self.assertEqual(self.conductor.nombre_completo, 'juan romero')
        self.assertEqual(str(self.conductor), 'juan romero (DNI: 30111222)')


class TestVehiculo(BaseInformeTest):
    def test_str(self):
        self.assertEqual(str(self.vehiculo), 'AF482CK (Camión)')

    def test_patente_unica(self):
        with self.assertRaises(IntegrityError):
            Vehiculo.objects.create(patente='AF482CK', tipo='CAMION')


class TestPieza(BaseInformeTest):
    def test_str(self):
        self.assertEqual(str(self.pieza), 'Horizontal - 0.73')


class TestInformeDano(BaseInformeTest):
    def test_str(self):
        informe = self.crear_informe()
        self.assertEqual(str(informe), 'Informe Nº AB-1234 - Cliente Test')

    def test_clean_normaliza_remito(self):
        informe = self.crear_informe(remito='  ab 12 34 ')
        informe.refresh_from_db()
        self.assertEqual(informe.remito_recepcion, 'AB1234')

    def test_save_requiere_remito(self):
        with self.assertRaises(ValidationError):
            self.crear_informe(remito='')

    def test_remito_unico(self):
        self.crear_informe(remito='AB-1234')
        with self.assertRaises(ValidationError):
            self.crear_informe(remito='AB-1234')

    def test_esta_bloqueado_inicial(self):
        self.assertFalse(self.crear_informe().esta_bloqueado)

    def test_finalizar_sin_piezas_error(self):
        informe = self.crear_informe()
        with self.assertRaisesMessage(ValidationError, 'informe vacío'):
            informe.finalizar()

    def test_finalizar_con_piezas(self):
        informe = self.crear_informe()
        PiezaRechazada.objects.create(
            informe=informe, pieza=self.pieza,
            categoria_dano=self.categoria_dano, cantidad=2,
        )
        informe.finalizar()
        informe.refresh_from_db()
        self.assertTrue(informe.finalizado)


class TestPiezaRechazada(BaseInformeTest):
    def test_cantidad_default(self):
        pr = PiezaRechazada.objects.create(
            informe=self.crear_informe(), pieza=self.pieza,
            categoria_dano=self.categoria_dano,
        )
        self.assertEqual(pr.cantidad, 1)

    def test_url_segura_sin_imagen(self):
        pr = PiezaRechazada.objects.create(
            informe=self.crear_informe(), pieza=self.pieza,
            categoria_dano=self.categoria_dano,
        )
        self.assertIsNone(pr.url_segura)

    def test_no_editable_en_informe_finalizado(self):
        informe = self.crear_informe()
        PiezaRechazada.objects.create(
            informe=informe, pieza=self.pieza, categoria_dano=self.categoria_dano,
        )
        informe.finalizar()
        with self.assertRaisesMessage(ValidationError, 'finalizado'):
            PiezaRechazada.objects.create(
                informe=informe, pieza=self.pieza, categoria_dano=self.categoria_dano,
            )


class TestQuerySet(BaseInformeTest):
    def test_pendientes_y_finalizados(self):
        informe = self.crear_informe(remito='PEND-1')
        PiezaRechazada.objects.create(
            informe=informe, pieza=self.pieza, categoria_dano=self.categoria_dano,
        )
        informe.finalizar()

        self.crear_informe(remito='FINAL-1', finalizado=False)

        self.assertEqual(InformeDano.objects.pendientes().count(), 1)
        self.assertEqual(InformeDano.objects.finalizados().count(), 1)

    def test_con_relaciones_no_rompe(self):
        self.crear_informe()
        self.assertEqual(InformeDano.objects.con_relaciones().count(), 1)

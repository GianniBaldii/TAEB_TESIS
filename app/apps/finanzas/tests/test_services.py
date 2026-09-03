from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.alumnos.models import Alumno, AlumnoEscuela
from apps.clases.models import Clase, ClaseAlumno
from apps.escuelas.models import Escuela, EscuelaDocente
from apps.usuarios.models import Docente
from apps.finanzas.models import ConceptoFinanciero, ConfiguracionCuota, ObligacionPago, Pago, PagoAplicacion
from apps.finanzas.selectors.finanzas_selectors import alumnos_de_clase, estado_obligacion, obligaciones_con_saldo
from apps.finanzas.services.cuota_service import generar_cuotas_periodo
from apps.finanzas.services.excepciones import FinanzasError
from apps.finanzas.services.obligacion_service import calcular_fecha_atraso, crear_obligaciones
from apps.finanzas.services.pago_service import registrar_pago, saldo_obligacion


class FinanzasServiceTests(TestCase):
    def setUp(self):
        self.escuela = Escuela.objects.create(nombre="TAEB")
        self.usuario = get_user_model().objects.create_user(username="docente", password="test")
        docente = Docente.objects.create(usuario=self.usuario, dni="100")
        EscuelaDocente.objects.create(escuela=self.escuela, docente=docente)
        self.conceptos = {c.codigo: c for c in ConceptoFinanciero.objects.filter(escuela=self.escuela)}
        ConfiguracionCuota.objects.create(escuela=self.escuela, monto_actual=Decimal("35000"), dia_vencimiento=10, dias_tolerancia=5)
        self.inscripciones = []
        for numero in range(3):
            alumno = Alumno.objects.create(nombre=f"Alumno {numero}", apellido="Prueba", dni=f"200{numero}")
            self.inscripciones.append(AlumnoEscuela.objects.create(escuela=self.escuela, alumno=alumno))

    def generar(self, inscripciones=None, anio=2026, mes=9, monto=Decimal("35000")):
        return generar_cuotas_periodo(escuela=self.escuela, alumnos_escuela=inscripciones or self.inscripciones, anio=anio, mes=mes, monto=monto, fecha_vencimiento=date(anio, mes, 10), dias_tolerancia=5, usuario=self.usuario)

    def test_genera_cuota_para_uno_y_varios_alumnos(self):
        resultado = self.generar(self.inscripciones[:1])
        self.assertEqual(len(resultado["creadas"]), 1)
        resultado = self.generar(self.inscripciones[1:])
        self.assertEqual(len(resultado["creadas"]), 2)

    def test_no_duplica_cuota_y_permite_periodo_siguiente(self):
        self.generar()
        repeticion = self.generar()
        siguiente = self.generar(anio=2026, mes=10)
        self.assertEqual(len(repeticion["creadas"]), 0)
        self.assertEqual(len(repeticion["omitidas"]), 3)
        self.assertEqual(len(siguiente["creadas"]), 3)

    def test_un_alumno_en_dos_clases_recibe_una_cuota(self):
        clase_a = Clase.objects.create(escuela=self.escuela, nombre="Adultos")
        clase_b = Clase.objects.create(escuela=self.escuela, nombre="Competición")
        ClaseAlumno.objects.create(clase=clase_a, alumno_escuela=self.inscripciones[0])
        ClaseAlumno.objects.create(clase=clase_b, alumno_escuela=self.inscripciones[0])
        seleccion = list(alumnos_de_clase(clase_a)) + list(alumnos_de_clase(clase_b))
        self.assertEqual(len(self.generar(seleccion)["creadas"]), 1)

    def test_rechaza_alumno_de_otra_escuela(self):
        otra = Escuela.objects.create(nombre="Otra")
        alumno = Alumno.objects.create(nombre="Otro", apellido="Alumno", dni="999")
        inscripcion = AlumnoEscuela.objects.create(escuela=otra, alumno=alumno)
        with self.assertRaises(FinanzasError):
            self.generar([inscripcion])

    def test_rechaza_alumno_o_inscripcion_inactivos(self):
        self.inscripciones[0].activo = False
        self.inscripciones[0].save()
        with self.assertRaises(FinanzasError): self.generar([self.inscripciones[0]])
        self.inscripciones[0].activo = True
        self.inscripciones[0].alumno.activo = False
        self.inscripciones[0].alumno.save()
        with self.assertRaises(FinanzasError): self.generar([self.inscripciones[0]])

    def test_fecha_atraso_empieza_despues_de_tolerancia(self):
        self.assertEqual(calcular_fecha_atraso(date(2026, 9, 10), 5), date(2026, 9, 16))

    def test_cambio_configuracion_no_modifica_cuota_historica(self):
        cuota = self.generar(self.inscripciones[:1])["creadas"][0]
        configuracion = ConfiguracionCuota.objects.get(escuela=self.escuela)
        configuracion.monto_actual = Decimal("40000")
        configuracion.save()
        cuota.refresh_from_db()
        self.assertEqual(cuota.monto_original, Decimal("35000"))

    def test_genera_examen_y_torneo_manuales(self):
        for codigo in (ConceptoFinanciero.Codigo.EXAMEN, ConceptoFinanciero.Codigo.TORNEO):
            resultado = crear_obligaciones(escuela=self.escuela, concepto=self.conceptos[codigo], alumnos_escuela=self.inscripciones[:1], monto=Decimal("25000"), fecha_vencimiento=date(2026, 12, 20), dias_tolerancia=0, descripcion=codigo.title(), usuario=self.usuario)
            self.assertEqual(len(resultado["creadas"]), 1)

    def test_concepto_inactivo_impide_cobro(self):
        concepto = self.conceptos[ConceptoFinanciero.Codigo.EXAMEN]
        concepto.activo = False
        concepto.save()
        with self.assertRaises(FinanzasError):
            crear_obligaciones(escuela=self.escuela, concepto=concepto, alumnos_escuela=self.inscripciones[:1], monto=10, fecha_vencimiento=date(2026, 12, 20), dias_tolerancia=0, descripcion="Examen", usuario=self.usuario)

    def test_pago_parcial_completo_y_exceso(self):
        obligacion = self.generar(self.inscripciones[:1])["creadas"][0]
        registrar_pago(obligacion=obligacion, monto=Decimal("20000"), metodo=Pago.Metodo.TRANSFERENCIA, fecha_pago=date(2026, 9, 5), referencia="REF", observaciones="", usuario=self.usuario)
        self.assertEqual(saldo_obligacion(obligacion), Decimal("15000"))
        with self.assertRaises(FinanzasError):
            registrar_pago(obligacion=obligacion, monto=Decimal("16000"), metodo=Pago.Metodo.EFECTIVO, fecha_pago=date(2026, 9, 6), referencia="", observaciones="", usuario=self.usuario)
        registrar_pago(obligacion=obligacion, monto=Decimal("15000"), metodo=Pago.Metodo.EFECTIVO, fecha_pago=date(2026, 9, 6), referencia="", observaciones="", usuario=self.usuario)
        self.assertEqual(saldo_obligacion(obligacion), Decimal("0"))

    def test_saldo_ignora_pago_no_confirmado(self):
        obligacion = self.generar(self.inscripciones[:1])["creadas"][0]
        pago = Pago.objects.create(escuela=self.escuela, alumno_escuela=self.inscripciones[0], monto_total=1000, metodo_pago=Pago.Metodo.EFECTIVO, estado=Pago.Estado.ANULADO, fecha_pago=date.today(), registrado_por=self.usuario)
        PagoAplicacion.objects.create(pago=pago, obligacion_pago=obligacion, monto_aplicado=1000)
        self.assertEqual(saldo_obligacion(obligacion), Decimal("35000"))

    def test_estados_calculados(self):
        obligacion = self.generar(self.inscripciones[:1])["creadas"][0]
        anotada = obligaciones_con_saldo(ObligacionPago.objects.filter(pk=obligacion.pk)).get()
        self.assertEqual(estado_obligacion(anotada, date(2026, 9, 9)), {"pago": "PENDIENTE", "temporal": "VIGENTE"})
        self.assertEqual(estado_obligacion(anotada, date(2026, 9, 11))["temporal"], "VENCIDA")
        self.assertEqual(estado_obligacion(anotada, date(2026, 9, 16))["temporal"], "ATRASADA")

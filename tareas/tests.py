import json
from datetime import datetime
from io import StringIO
from zoneinfo import ZoneInfo

from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import Client, TestCase

from .models import Tarea


class TareasAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.pendiente = Tarea.objects.create(
            titulo="Proyecto de estructuras de datos",
            curso="Algoritmos y Programación II",
            fecha_entrega=datetime(2026, 9, 28, 23, 59, tzinfo=ZoneInfo("America/Guatemala")),
        )
        cls.completada = Tarea.objects.create(
            titulo="Práctica de HTML y CSS",
            curso="Programación Web",
            fecha_entrega=datetime(2026, 9, 25, 23, 59, tzinfo=ZoneInfo("America/Guatemala")),
            estado="completada",
        )

    def setUp(self):
        self.url = f"/api/tareas/{self.pendiente.id}/"
        self.client = Client(enforce_csrf_checks=True)

    def test_listado_contrato_y_orden(self):
        respuesta = self.client.get("/api/tareas/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.json()), 2)
        self.assertEqual(respuesta.json()[0]["id"], self.completada.id)
        self.assertEqual(set(respuesta.json()[0]), {"id", "titulo", "curso", "fechaEntrega", "estado"})

    def test_consultar_una_tarea(self):
        respuesta = self.client.get(self.url)
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json(), {
            "id": self.pendiente.id,
            "titulo": "Proyecto de estructuras de datos",
            "curso": "Algoritmos y Programación II",
            "fechaEntrega": "2026-09-28T23:59:00-06:00",
            "estado": "pendiente",
        })

    def test_filtrar_ambos_estados(self):
        for estado, tarea in [("pendiente", self.pendiente), ("completada", self.completada)]:
            with self.subTest(estado=estado):
                respuesta = self.client.get("/api/tareas/", {"estado": estado})
                self.assertEqual(respuesta.status_code, 200)
                self.assertEqual([x["id"] for x in respuesta.json()], [tarea.id])

    def test_listado_vacio(self):
        Tarea.objects.all().delete()
        respuesta = self.client.get("/api/tareas/?estado=pendiente")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json(), [])

    def test_filtros_invalidos(self):
        for consulta in ["estado=vencida", "estado=", "estado=Pendiente", "estado=pendiente&estado=completada", "curso=Web"]:
            with self.subTest(consulta=consulta):
                respuesta = self.client.get(f"/api/tareas/?{consulta}")
                self.assertEqual(respuesta.status_code, 400)
                self.assertIn("error", respuesta.json())

    def test_completar_persiste_y_actualiza_filtros(self):
        respuesta = self.client.patch(self.url, {"estado": "completada"}, content_type="application/json")
        self.assertEqual(respuesta.status_code, 200)
        self.pendiente.refresh_from_db()
        self.assertEqual(self.pendiente.estado, "completada")
        self.assertEqual(respuesta.json()["titulo"], self.pendiente.titulo)
        self.assertEqual(respuesta.json()["curso"], self.pendiente.curso)
        self.assertEqual(self.client.get(self.url).json()["estado"], "completada")
        self.assertEqual(self.client.get("/api/tareas/?estado=pendiente").json(), [])

    def test_completar_es_idempotente(self):
        primera = self.client.patch(self.url, {"estado": "completada"}, content_type="application/json")
        segunda = self.client.patch(self.url, {"estado": "completada"}, content_type="application/json")
        self.assertEqual(segunda.status_code, 200)
        self.assertEqual(primera.json(), segunda.json())

    def test_rechaza_cuerpo_invalido_sin_cambiar_datos(self):
        for cuerpo in [{}, [], None, {"estado": "pendiente"}, {"estado": "vencida"}, {"estado": 1}, {"estado": "completada", "titulo": "Otro"}]:
            with self.subTest(cuerpo=cuerpo):
                respuesta = self.client.patch(self.url, json.dumps(cuerpo), content_type="application/json")
                self.assertEqual(respuesta.status_code, 400)
                self.pendiente.refresh_from_db()
                self.assertEqual(self.pendiente.estado, "pendiente")
                self.assertEqual(self.pendiente.titulo, "Proyecto de estructuras de datos")

    def test_json_malformado(self):
        for cuerpo in [b'{"estado":', b"", b"\xff"]:
            with self.subTest(cuerpo=cuerpo):
                respuesta = self.client.patch(self.url, cuerpo, headers={"Content-Type": "application/json"})
                self.assertEqual(respuesta.status_code, 400)
                self.assertEqual(respuesta.json()["error"]["codigo"], "JSON_INVALIDO")

    def test_tipo_de_contenido_incorrecto(self):
        respuesta = self.client.patch(self.url, '{"estado":"completada"}', content_type="text/plain")
        self.assertEqual(respuesta.status_code, 415)

    def test_tarea_inexistente_get_y_patch(self):
        for metodo in [self.client.get, self.client.patch]:
            respuesta = metodo("/api/tareas/999999/")
            self.assertEqual(respuesta.status_code, 404)
            self.assertEqual(respuesta.json(), {"error": {
                "codigo": "TAREA_NO_ENCONTRADA",
                "mensaje": "No existe una tarea con el id 999999.",
            }})

    def test_no_permite_crear_reemplazar_ni_eliminar(self):
        for url, permitidos in [("/api/tareas/", "GET"), (self.url, "GET, PATCH")]:
            for verbo in ["post", "put", "delete"]:
                with self.subTest(url=url, verbo=verbo):
                    respuesta = getattr(self.client, verbo)(url)
                    self.assertEqual(respuesta.status_code, 405)
                    self.assertEqual(respuesta["Allow"], permitidos)
                    self.assertEqual(respuesta.json()["error"]["codigo"], "METODO_NO_PERMITIDO")
        self.assertEqual(Tarea.objects.count(), 2)

    def test_ruta_inexistente_json(self):
        respuesta = self.client.get("/api/no-existe/")
        self.assertEqual(respuesta.status_code, 404)
        self.assertEqual(respuesta.json()["error"]["codigo"], "RUTA_NO_ENCONTRADA")

    def test_base_de_datos_rechaza_estado_invalido(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Tarea.objects.filter(pk=self.pendiente.id).update(estado="vencida")

    def test_inicio_describe_api(self):
        respuesta = self.client.get("/")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.json()["endpoints"]), 4)


class DatosDemoTests(TestCase):
    def test_carga_es_idempotente_y_conserva_cambios(self):
        call_command("cargar_demo", stdout=StringIO())
        self.assertEqual(Tarea.objects.count(), 6)
        self.assertEqual(Tarea.objects.filter(estado="pendiente").count(), 5)
        Tarea.objects.filter(pk=1).update(estado="completada")
        call_command("cargar_demo", stdout=StringIO())
        self.assertEqual(Tarea.objects.count(), 6)
        self.assertEqual(Tarea.objects.get(pk=1).estado, "completada")

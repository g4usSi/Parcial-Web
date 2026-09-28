from datetime import datetime
from zoneinfo import ZoneInfo

from django.core.management.base import BaseCommand
from django.db import transaction

from tareas.models import Tarea


class Command(BaseCommand):
    help = "Carga seis tareas de ejemplo sin sobrescribir tareas existentes."

    @transaction.atomic
    def handle(self, *args, **options):
        ejemplos = [
            (1, "Proyecto de estructuras de datos", "Algoritmos y Programación II", "2026-09-27T23:59:00", "pendiente"),
            (2, "Cuestionario de termodinámica", "Física General", "2026-09-28T18:00:00", "pendiente"),
            (3, "Ensayo de ética digital", "Humanidades y Ética", "2026-10-02T23:59:00", "pendiente"),
            (4, "Ejercicios de cálculo", "Matemática Aplicada", "2026-10-03T17:00:00", "pendiente"),
            (5, "Informe de arquitectura", "Arquitectura de Computadores", "2026-10-05T20:00:00", "pendiente"),
            (6, "Práctica de HTML y CSS", "Programación Web", "2026-09-25T23:59:00", "completada"),
        ]
        creadas = 0
        for identificador, titulo, curso, fecha, estado in ejemplos:
            _, creada = Tarea.objects.get_or_create(
                id=identificador,
                defaults={
                    "titulo": titulo,
                    "curso": curso,
                    "fecha_entrega": datetime.fromisoformat(fecha).replace(tzinfo=ZoneInfo("America/Guatemala")),
                    "estado": estado,
                },
            )
            creadas += creada
        self.stdout.write(self.style.SUCCESS(f"{creadas} tareas creadas. Total: {Tarea.objects.count()}."))

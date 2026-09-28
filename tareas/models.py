from django.db import models


class Tarea(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        COMPLETADA = "completada", "Completada"

    titulo = models.CharField(max_length=200)
    curso = models.CharField(max_length=150)
    fecha_entrega = models.DateTimeField()
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.PENDIENTE)

    class Meta:
        ordering = ["fecha_entrega", "id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(estado__in=["pendiente", "completada"]),
                name="tarea_estado_valido",
            )
        ]

    def __str__(self):
        return self.titulo

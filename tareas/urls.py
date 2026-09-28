from django.urls import path
from . import views

urlpatterns = [
    path("tareas/", views.listar_tareas, name="tareas-lista"),
    path("tareas/<int:tarea_id>/", views.detalle_tarea, name="tareas-detalle"),
]

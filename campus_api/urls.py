from django.urls import include, path
from tareas import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("api/", include("tareas.urls")),
]

handler404 = "tareas.views.ruta_no_encontrada"

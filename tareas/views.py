import json

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Tarea


def error(codigo, mensaje, status):
    return JsonResponse({"error": {"codigo": codigo, "mensaje": mensaje}}, status=status)


def metodo_no_permitido(metodos):
    respuesta = error("METODO_NO_PERMITIDO", "Método HTTP no permitido para este endpoint.", 405)
    respuesta["Allow"] = ", ".join(metodos)
    return respuesta


def serializar_tarea(tarea):
    return {
        "id": tarea.id,
        "titulo": tarea.titulo,
        "curso": tarea.curso,
        "fechaEntrega": timezone.localtime(tarea.fecha_entrega).isoformat(),
        "estado": tarea.estado,
    }


def inicio(request):
    if request.method != "GET":
        return metodo_no_permitido(["GET"])
    return JsonResponse({
        "nombre": "Campus Virtual — API de tareas (Serie III)",
        "endpoints": {
            "consultar_tareas": "GET /api/tareas/",
            "consultar_una_tarea": "GET /api/tareas/{id}/",
            "filtrar_por_estado": "GET /api/tareas/?estado=pendiente",
            "completar_tarea": "PATCH /api/tareas/{id}/",
        },
        "cuerpo_para_completar": {"estado": "completada"},
    })


# API local sin sesiones ni autenticación por cookies, consumida desde Postman.
@csrf_exempt
def listar_tareas(request):
    if request.method != "GET":
        return metodo_no_permitido(["GET"])
    desconocidos = set(request.GET) - {"estado"}
    if desconocidos:
        return error("PARAMETRO_INVALIDO", "El único filtro permitido es 'estado'.", 400)
    tareas = Tarea.objects.all()
    if "estado" in request.GET:
        estados = request.GET.getlist("estado")
        if len(estados) != 1 or estados[0] not in Tarea.Estado.values:
            return error("ESTADO_INVALIDO", "El estado debe ser 'pendiente' o 'completada'.", 400)
        tareas = tareas.filter(estado=estados[0])
    return JsonResponse([serializar_tarea(tarea) for tarea in tareas], safe=False)


@csrf_exempt
def detalle_tarea(request, tarea_id):
    if request.method not in ["GET", "PATCH"]:
        return metodo_no_permitido(["GET", "PATCH"])
    try:
        tarea = Tarea.objects.get(pk=tarea_id)
    except Tarea.DoesNotExist:
        return error("TAREA_NO_ENCONTRADA", f"No existe una tarea con el id {tarea_id}.", 404)

    if request.method == "PATCH":
        if request.content_type != "application/json":
            return error("TIPO_DE_CONTENIDO_INVALIDO", "Utiliza Content-Type: application/json.", 415)
        try:
            datos = json.loads(request.body)
        except (ValueError, UnicodeDecodeError):
            return error("JSON_INVALIDO", "El cuerpo debe contener JSON válido.", 400)
        if not isinstance(datos, dict) or set(datos) != {"estado"}:
            return error("CUERPO_INVALIDO", "Envía únicamente el campo 'estado'.", 400)
        if datos["estado"] != Tarea.Estado.COMPLETADA:
            return error("ESTADO_INVALIDO", "Esta operación solo permite marcar una tarea como 'completada'.", 400)
        tarea.estado = Tarea.Estado.COMPLETADA
        tarea.save(update_fields=["estado"])

    return JsonResponse(serializar_tarea(tarea))


def ruta_no_encontrada(request, exception):
    return error("RUTA_NO_ENCONTRADA", "El endpoint solicitado no existe.", 404)

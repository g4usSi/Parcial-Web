# Campus Virtual — API de tareas

Implementación de la Serie III con Django y SQLite. Incluye seis tareas de ejemplo (cinco pendientes y una completada), colección Postman y pruebas automatizadas. No necesita frontend.

## Iniciar en Windows

En PowerShell, desde esta carpeta:

```powershell
powershell -ExecutionPolicy Bypass -File .\iniciar.ps1
```

El script prepara el entorno virtual, instala las dependencias, aplica migraciones, carga los datos y arranca en **http://127.0.0.1:8000**. La excepción de ejecución aplica únicamente a ese proceso. Detener con `Ctrl+C`.

En este equipo ya se preparó `.venv`. Para arrancar sin reinstalar:

```powershell
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --noreload
```

Alternativa manual con Python 3.10 o superior instalado:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py cargar_demo
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000 --noreload
```

La carga de ejemplo no sobrescribe cambios si se ejecuta nuevamente. Las fechas de ejemplo son fijas para que las respuestas sean reproducibles.

## Probar con Postman

1. Iniciar el servidor.
2. Importar `postman/Serie_III_Tareas.postman_collection.json`.
3. Las variables `base_url` y `tarea_id` vienen definidas en la colección. No hace falta importar un environment.
4. Abrir la carpeta **Operaciones solicitadas** y ejecutar las peticiones en orden, o ejecutar toda la colección con Collection Runner.
5. El PATCH completa realmente la tarea seleccionada en SQLite. La consulta siguiente comprueba el cambio. Al repetir la colección, completar esa tarea sigue siendo válido.
6. La carpeta **Validaciones y errores** comprueba respuestas 400, 404, 405 y 415. Estas respuestas son resultados esperados.

Los scripts de Postman verifican códigos, campos, estados y persistencia del cambio mediante una consulta posterior. La primera petición selecciona automáticamente una tarea existente en la variable `tarea_id`.

## Endpoints

| Método | Ruta | Función |
| --- | --- | --- |
| GET | `/api/tareas/` | Consultar todas las tareas |
| GET | `/api/tareas/{id}/` | Consultar una tarea |
| GET | `/api/tareas/?estado=pendiente` | Filtrar; también admite `completada` |
| PATCH | `/api/tareas/{id}/` | Completar con `{"estado":"completada"}` |

Conservar la barra final de las rutas. Las respuestas exitosas usan `200 OK`. El detalle del contrato y las respuestas del ejercicio están en [RESPUESTAS_SERIE_III.md](RESPUESTAS_SERIE_III.md).

## Ejecutar pruebas

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
```

Las pruebas usan una base temporal y no modifican los datos de demostración.

## Archivos principales

- `tareas/models.py`: datos y restricción de estados.
- `tareas/views.py`: endpoints, serialización y validaciones.
- `tareas/tests.py`: pruebas del contrato y persistencia.
- `tareas/migrations/`: creación de la base de datos.
- `postman/Serie_III_Tareas.postman_collection.json`: colección importable.
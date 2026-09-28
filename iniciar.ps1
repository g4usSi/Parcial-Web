$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

$taskPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $taskPython)) {
    $taskBundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 -m venv .venv
    }
    if (-not (Test-Path -LiteralPath $taskPython)) {
        if (Test-Path -LiteralPath $taskBundledPython) {
            & $taskBundledPython -m venv .venv
        } else {
            throw 'Instala Python 3.10 o superior y vuelve a ejecutar este archivo.'
        }
    }
}
if (-not (Test-Path -LiteralPath $taskPython)) { throw 'No se pudo crear el entorno virtual.' }
& $taskPython -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'No se pudieron instalar las dependencias.' }
& $taskPython manage.py migrate
if ($LASTEXITCODE -ne 0) { throw 'Falló la migración.' }
& $taskPython manage.py cargar_demo
if ($LASTEXITCODE -ne 0) { throw 'Falló la carga de datos.' }
& $taskPython manage.py runserver 127.0.0.1:8000 --noreload

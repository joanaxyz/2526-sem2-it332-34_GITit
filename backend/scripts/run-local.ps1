param(
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

$BackendRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Python = Join-Path $BackendRoot ".venv\Scripts\python.exe"
$DatabasePath = (Join-Path $BackendRoot "db.sqlite3").Replace("\", "/")

$env:DATABASE_URL = "sqlite:///$DatabasePath"
$env:DATABASE_CONN_MAX_AGE = "0"
$env:DATABASE_CONN_HEALTH_CHECKS = "False"
$env:REDIS_URL = ""

Push-Location $BackendRoot
try {
    & $Python "manage.py" "runserver" "127.0.0.1:$Port" "--noreload"
}
finally {
    Pop-Location
}

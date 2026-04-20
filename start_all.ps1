# ============================================================
# Script para arrancar servidor y cliente BuckshotRoulette
# Ejecutar: powershell -ExecutionPolicy Bypass -File start_all.ps1
# ============================================================

Write-Host "[INICIO] Iniciando BuckshotRoulette (Servidor + Cliente)..." -ForegroundColor Cyan

# Obtener la ruta del script
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# Verificar y crear venv si no existe
$venvPath = Join-Path $projectRoot "venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "[WARNING] Entorno virtual no encontrado. Creando..." -ForegroundColor Yellow
    Write-Host "[INFO] Creando venv..." -ForegroundColor Cyan
    & python -m venv $venvPath
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Error al crear el entorno virtual" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "[OK] Venv creado" -ForegroundColor Green
    
    Write-Host "`n[INFO] Instalando dependencias..." -ForegroundColor Cyan
    & "$venvPath\Scripts\activate.ps1"
    pip install -r (Join-Path $projectRoot "requirements.txt")
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Error al instalar dependencias" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "[OK] Dependencias instaladas" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[OK] Entorno virtual encontrado" -ForegroundColor Green
}

# Activar venv
& "$venvPath\Scripts\Activate.ps1"

Write-Host "[OK] Entorno virtual activado" -ForegroundColor Green

# Iniciar servidor en una nueva ventana de PowerShell
Write-Host "[INFO] Arrancando servidor Flask..." -ForegroundColor Cyan
$serverPath = Join-Path $projectRoot "servidor"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$serverPath'; python app.py"

# Esperar un poco para que el servidor se inicie
Start-Sleep -Seconds 3

# Iniciar cliente en una nueva ventana de PowerShell
Write-Host "[INFO] Arrancando cliente Pygame..." -ForegroundColor Cyan
$clientPath = Join-Path $projectRoot "cliente"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$clientPath'; python main.py"

Write-Host "[OK] ¡Ambos procesos iniciados!" -ForegroundColor Green
Write-Host "[INFO] Servidor: http://localhost:5000" -ForegroundColor Yellow
Write-Host "[INFO] Cliente: Ventana Pygame" -ForegroundColor Yellow
Write-Host "`nPresiona Ctrl+C en cualquier ventana para detener los procesos" -ForegroundColor Gray

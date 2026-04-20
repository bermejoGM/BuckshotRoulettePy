@echo off
REM ============================================================
REM Script para arrancar servidor y cliente BuckshotRoulette
REM Ejecutar: start_all.bat
REM ============================================================

echo.
echo [INICIO] Iniciando BuckshotRoulette (Servidor + Cliente)...
echo.

REM Obtener ruta actual
setlocal enabledelayedexpansion
set "projectRoot=%~dp0"

REM Verificar si existe el venv, si no, crearlo
if not exist "%projectRoot%venv" (
    echo [WARNING] Entorno virtual no encontrado. Creando...
    echo [INFO] Creando venv...
    python -m venv "%projectRoot%venv"
    if errorlevel 1 (
        echo [ERROR] Error al crear el entorno virtual
        pause
        exit /b 1
    )
    echo [OK] Venv creado
    echo.
    echo [INFO] Instalando dependencias...
    call "%projectRoot%venv\Scripts\activate.bat"
    pip install -r "%projectRoot%requirements.txt"
    if errorlevel 1 (
        echo [ERROR] Error al instalar dependencias
        pause
        exit /b 1
    )
    echo [OK] Dependencias instaladas
    echo.
) else (
    echo [OK] Entorno virtual encontrado
)

REM Activar venv
call "%projectRoot%venv\Scripts\activate.bat"

echo [OK] Entorno virtual activado
echo.

REM Iniciar servidor en una nueva ventana
echo [INFO] Arrancando servidor Flask en puerto 5000...
start cmd /k "cd /d "%projectRoot%servidor" && python app.py"

REM Esperar a que el servidor se inicie
timeout /t 3 /nobreak

REM Iniciar cliente en una nueva ventana
echo [INFO] Arrancando cliente Pygame...
start cmd /k "cd /d "%projectRoot%cliente" && python main.py"

echo.
echo [OK] ¡Ambos procesos iniciados!
echo [INFO] Servidor: http://localhost:5000
echo [INFO] Cliente: Ventana Pygame
echo.
echo Cierra las ventanas para detener los procesos.
echo.
pause

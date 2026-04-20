#!/usr/bin/env python3
"""
Script multiplataforma para arrancar servidor y cliente BuckshotRoulette
Uso: python start_all.py
"""

import subprocess
import sys
import os
import time
import platform
from pathlib import Path

def print_banner(text, color="cyan"):
    """Imprime texto con color"""
    colors = {
        "cyan": "\033[96m",
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")

def check_venv():
    """Verifica si existe el entorno virtual, si no lo crea"""
    project_root = Path(__file__).parent
    venv_path = project_root / "venv"
    
    if not venv_path.exists():
        print_banner("[WARNING] Entorno virtual no encontrado. Creando...", "yellow")
        print_banner("[INFO] Creando venv...", "cyan")
        
        result = subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            capture_output=True
        )
        
        if result.returncode != 0:
            print_banner("[ERROR] Error al crear el entorno virtual", "red")
            print_banner(result.stderr.decode(), "red")
            sys.exit(1)
        
        print_banner("[OK] Venv creado", "green")
        
        print_banner("\n[INFO] Instalando dependencias...", "cyan")
        pip_path = venv_path / ("Scripts" if platform.system() == "Windows" else "bin") / "pip"
        requirements = project_root / "requirements.txt"
        
        result = subprocess.run(
            [str(pip_path), "install", "-r", str(requirements)],
            capture_output=True
        )
        
        if result.returncode != 0:
            print_banner("[ERROR] Error al instalar dependencias", "red")
            print_banner(result.stderr.decode(), "red")
            sys.exit(1)
        
        print_banner("[OK] Dependencias instaladas", "green")
        print("")
    else:
        print_banner("[OK] Entorno virtual encontrado", "green")

def activate_venv(project_root):
    """Retorna el comando para activar el venv según el SO"""
    if platform.system() == "Windows":
        return str(project_root / "venv" / "Scripts" / "activate.bat")
    else:
        return f"source {project_root}/venv/bin/activate"

def start_server(project_root):
    """Inicia el servidor Flask"""
    print_banner("\n[INFO] Arrancando servidor Flask en puerto 5000...", "cyan")
    server_path = project_root / "servidor"
    
    if platform.system() == "Windows":
        # En Windows, abrir en nueva ventana CMD
        subprocess.Popen(
            f'start cmd /k "cd /d {server_path} && python app.py"',
            shell=True
        )
    else:
        # En Linux/Mac, usar xterm o terminal disponible
        try:
            subprocess.Popen(
                ["gnome-terminal", "--", "bash", "-c", 
                 f"cd {server_path} && python app.py; bash"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except FileNotFoundError:
            # Fallback: ejecutar en background
            subprocess.Popen(
                ["python", "app.py"],
                cwd=str(server_path)
            )

def start_client(project_root):
    """Inicia el cliente Pygame"""
    print_banner("[INFO] Arrancando cliente Pygame...", "cyan")
    client_path = project_root / "cliente"
    
    if platform.system() == "Windows":
        # En Windows, abrir en nueva ventana CMD
        subprocess.Popen(
            f'start cmd /k "cd /d {client_path} && python main.py"',
            shell=True
        )
    else:
        # En Linux/Mac, usar xterm o terminal disponible
        try:
            subprocess.Popen(
                ["gnome-terminal", "--", "bash", "-c", 
                 f"cd {client_path} && python main.py; bash"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except FileNotFoundError:
            # Fallback: ejecutar en background
            subprocess.Popen(
                ["python", "main.py"],
                cwd=str(client_path)
            )

def main():
    """Función principal"""
    print_banner("\n[INICIO] Iniciando BuckshotRoulette (Servidor + Cliente)...", "cyan")
    
    try:
        # Verificar y crear venv si es necesario
        check_venv()
        project_root = Path(__file__).parent
        
        # Iniciar servidor
        start_server(project_root)
        time.sleep(3)
        
        # Iniciar cliente
        start_client(project_root)
        
        print_banner("\n[OK] ¡Ambos procesos iniciados!", "green")
        print_banner("[INFO] Servidor: http://localhost:5000", "yellow")
        print_banner("[INFO] Cliente: Ventana Pygame", "yellow")
        print_banner("\nPresiona Ctrl+C aquí para ver estado, o cierra las ventanas para detener.\n", "yellow")
        
        # Mantener el script ejecutándose
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print_banner("\n\n[WARNING] Interrupcion del usuario detectada", "yellow")
        print_banner("Cierra las ventanas del servidor y cliente manualmente", "yellow")
        sys.exit(0)
    except Exception as e:
        print_banner(f"\n[ERROR] Error: {e}", "red")
        sys.exit(1)

if __name__ == "__main__":
    main()

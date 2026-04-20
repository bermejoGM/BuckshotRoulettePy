"""
Script para inicializar la base de datos MongoDB Atlas
Verifica la conexión y muestra información de la BD
"""
import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar configuración y database
from config import get_config
from mongodb import init_db

def main():
    """Inicializar base de datos MongoDB"""
    print("="*60)
    print("INICIALIZANDO BASE DE DATOS - Buckshot Roulette")
    print("(MongoDB Atlas)")
    print("="*60)
    
    try:
        # Obtener configuración
        config = get_config()
        print(f"\nConfiguración: {config.__class__.__name__}")
        
        # Mostrar URL (ocultando contraseña)
        url_display = config.MONGODB_URL
        if '@' in url_display:
            # Ocultar contraseña en la visualización
            parts = url_display.split('@')
            url_display = "mongodb+srv://***:***@" + parts[1]
        print(f"MongoDB URL: {url_display}")
        print(f"Base de datos: {config.DB_NAME}")
        
        # Inicializar database
        print("\nConectando a MongoDB Atlas...")
        db = init_db(config)
        
        print("\n[OK] Conexion exitosa a MongoDB Atlas")
        print("\nColecciones disponibles:")
        print("   - puntuaciones: Almacena todas las puntuaciones")
        print("   - sesiones_juego: Registra información de cada partida")
        
        # Obtener estadísticas
        print("\nEstadísticas actuales:")
        try:
            count_puntuaciones = db.count('puntuaciones')
            count_sesiones = db.count('sesiones_juego')
            print(f"   - Total de puntuaciones: {count_puntuaciones}")
            print(f"   - Total de sesiones: {count_sesiones}")
        except Exception as e:
            print(f"   (Error al obtener estadísticas: {e})")
        
        # Listar índices
        print("\nÍndices creados:")
        try:
            # Obtener índices de puntuaciones
            indexes_puntuaciones = db.get_collection('puntuaciones').list_indexes()
            for idx in indexes_puntuaciones:
                print(f"   - {idx['name']}")
        except Exception as e:
            print(f"   (Error al listar índices: {e})")
        
        print("\n" + "="*60)
        print("TODO LISTO - Puedes ejecutar el servidor con:")
        print("   python app.py")
        print("="*60 + "\n")
        
        return 0
    
    except Exception as e:
        print(f"\n[ERROR] Error al conectar a MongoDB Atlas:")
        print(f"   {e}")
        print("\n[INFO] Por favor verifica:")
        print("   1. Tienes una cuenta en MongoDB Atlas (atlas.mongodb.com)")
        print("   2. Creaste un cluster")
        print("   3. La MONGODB_URL en .env es correcta")
        print("   4. Tu IP está permitida en Network Access")
        print("   5. Las credenciales de usuario son correctas")
        print("\n" + "="*60 + "\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())

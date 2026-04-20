"""
Configuración del servidor - Variables de entorno y settings
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración base"""
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'
    
    # MongoDB Atlas
    MONGODB_URL = os.getenv(
        'MONGODB_URL', 
        'mongodb://localhost:27017/'
    )
    DB_NAME = os.getenv('DB_NAME', 'buckshot_roulette')
    
    # API Settings
    API_TITLE = 'Buckshot Roulette API'
    API_VERSION = '1.0'
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Game Settings
    MAX_VIDAS = 3
    PUNTOS_BALA_REAL = 10
    PUNTOS_FOGUEO_SELF = 5
    MIN_BALAS_REALES = 1
    MAX_BALAS_REALES = 4
    MIN_BALAS_FOGUEO = 1
    MAX_BALAS_FOGUEO = 4


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    MONGODB_URL = os.getenv(
        'MONGODB_URL', 
        'mongodb://localhost:27017/'
    )
    DB_NAME = os.getenv('DB_NAME', 'buckshot_roulette_dev')


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    if not os.getenv('MONGODB_URL'):
        raise ValueError("MONGODB_URL environment variable must be set in production")


class TestingConfig(Config):
    """Configuración para tests"""
    TESTING = True
    MONGODB_URL = os.getenv(
        'MONGODB_URL',
        'mongodb://localhost:27017/'
    )
    DB_NAME = os.getenv('DB_NAME', 'buckshot_roulette_test')


# Seleccionar configuración según entorno
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Obtener configuración según variable de entorno"""
    env = os.getenv('FLASK_ENV', 'development')
    return config_by_name.get(env, DevelopmentConfig)

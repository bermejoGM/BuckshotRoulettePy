"""
Manejo de conexión a MongoDB Atlas con connection pooling optimizado
Reemplaza database.py (PostgreSQL) con pymongo
"""
from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from contextlib import contextmanager
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MongoDatabase:
    """Clase para manejar conexiones MongoDB Atlas con pool"""
    
    def __init__(self, config):
        """
        Inicializar conexión MongoDB
        
        config debe contener:
        - MONGODB_URL: Connection string (ej: mongodb+srv://user:pass@cluster.mongodb.net/)
        - DB_NAME: Nombre de la base de datos
        """
        self.config = config
        self.client = None
        self.db = None
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Inicializar conexión MongoDB con connection pooling"""
        try:
            # Configuración optimizada para servidor OLTP (aplicación de juego)
            self.client = MongoClient(
                self.config.MONGODB_URL,
                # Connection Pool Settings (Traditional Long-Running Server)
                maxPoolSize=50,              # Basado en picos concurrentes esperados
                minPoolSize=10,              # Conexiones pre-calentadas
                maxIdleTimeMS=300000,        # 5 minutos (release conexiones ociosas)
                connectTimeoutMS=10000,      # 10 segundos para conectarse
                socketTimeoutMS=30000,       # 30 segundos para operaciones
                serverSelectionTimeoutMS=5000, # 5 segundos para seleccionar servidor
                # SSL/TLS (obligatorio en Atlas)
                ssl=True,
                tlsAllowInvalidCertificates=False,
                retryWrites=True,            # Reintentar escrituras fallidas
                w='majority'                 # Confirmar escrituras en mayoría
            )
            
            # Obtener base de datos
            self.db = self.client[self.config.DB_NAME]
            
            # Probar conexión
            self.client.admin.command('ping')
            logger.info("[OK] Conexion a MongoDB Atlas establecida correctamente")
            
            # Crear índices
            self._create_indexes()
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"[ERROR] Error al conectar MongoDB Atlas: {e}")
            raise
        except Exception as e:
            logger.error(f"[ERROR] Error al inicializar MongoDB: {e}")
            raise
    
    def _create_indexes(self):
        """Crear índices para optimizar consultas"""
        try:
            # Índice para ranking (puntuaciones descendentes)
            self.db.puntuaciones.create_index([("puntos", DESCENDING)])
            
            # Índice para filtrar por fecha
            self.db.puntuaciones.create_index([("fecha", DESCENDING)])
            
            # Índice para session_id (único)
            self.db.sesiones_juego.create_index([("session_id", 1)], unique=True)
            
            # Índice para filtrar sesiones por fecha
            self.db.sesiones_juego.create_index([("fecha_inicio", DESCENDING)])
            
            logger.info("[OK] Indices creados/verificados")
        
        except Exception as e:
            logger.error(f"[WARNING] Error al crear indices (ignorado): {e}")
            # No es fatal si falla, los índices pueden existir
    
    def get_collection(self, collection_name):
        """Obtener una colección"""
        if self.db is None:
            raise Exception("Conexión MongoDB no inicializada")
        return self.db[collection_name]
    
    @contextmanager
    def transaction(self):
        """
        Context manager para transacciones
        Nota: MongoDB requiere un cluster replica set para transacciones
        Para M0 free tier, usar sin transacciones
        """
        session = self.client.start_session()
        try:
            yield session
        except Exception as e:
            logger.error(f"Error en transacción: {e}")
            raise
        finally:
            session.end_session()
    
    def insert_one(self, collection_name, document):
        """Insertar un documento"""
        try:
            collection = self.get_collection(collection_name)
            result = collection.insert_one(document)
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error al insertar en {collection_name}: {e}")
            raise
    
    def insert_many(self, collection_name, documents):
        """Insertar múltiples documentos"""
        try:
            collection = self.get_collection(collection_name)
            result = collection.insert_many(documents)
            return result.inserted_ids
        except Exception as e:
            logger.error(f"Error al insertar múltiples en {collection_name}: {e}")
            raise
    
    def find_one(self, collection_name, filter_dict):
        """Buscar un documento"""
        try:
            collection = self.get_collection(collection_name)
            return collection.find_one(filter_dict)
        except Exception as e:
            logger.error(f"Error al buscar en {collection_name}: {e}")
            raise
    
    def find(self, collection_name, filter_dict=None, sort=None, limit=None):
        """
        Buscar múltiples documentos
        sort ejemplo: [("puntos", -1)] para descendente
        """
        try:
            collection = self.get_collection(collection_name)
            query = collection.find(filter_dict or {})
            
            if sort:
                query = query.sort(sort)
            if limit:
                query = query.limit(limit)
            
            return list(query)
        except Exception as e:
            logger.error(f"Error al buscar en {collection_name}: {e}")
            raise
    
    def update_one(self, collection_name, filter_dict, update_dict):
        """Actualizar un documento"""
        try:
            collection = self.get_collection(collection_name)
            result = collection.update_one(filter_dict, {"$set": update_dict})
            return result.modified_count
        except Exception as e:
            logger.error(f"Error al actualizar {collection_name}: {e}")
            raise
    
    def update_many(self, collection_name, filter_dict, update_dict):
        """Actualizar múltiples documentos"""
        try:
            collection = self.get_collection(collection_name)
            result = collection.update_many(filter_dict, {"$set": update_dict})
            return result.modified_count
        except Exception as e:
            logger.error(f"Error al actualizar múltiples en {collection_name}: {e}")
            raise
    
    def delete_one(self, collection_name, filter_dict):
        """Eliminar un documento"""
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_one(filter_dict)
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error al eliminar en {collection_name}: {e}")
            raise
    
    def count(self, collection_name, filter_dict=None):
        """Contar documentos"""
        try:
            collection = self.get_collection(collection_name)
            return collection.count_documents(filter_dict or {})
        except Exception as e:
            logger.error(f"Error al contar en {collection_name}: {e}")
            raise
    
    def aggregate(self, collection_name, pipeline):
        """
        Ejecutar agregación MongoDB
        pipeline: lista de etapas de agregación
        """
        try:
            collection = self.get_collection(collection_name)
            return list(collection.aggregate(pipeline))
        except Exception as e:
            logger.error(f"Error en agregación de {collection_name}: {e}")
            raise
    
    def close(self):
        """Cerrar conexión"""
        if self.client is not None:
            self.client.close()
            logger.info("Conexión MongoDB cerrada")
    
    def initialize_database(self):
        """Crear colecciones (MongoDB las crea automáticamente en el primer insert)"""
        try:
            # En MongoDB, las colecciones se crean automáticamente
            # Solo verificamos que se puede acceder a ellas
            logger.info("[OK] Base de datos MongoDB lista para usar")
            logger.info("   Colecciones: puntuaciones, sesiones_juego")
        except Exception as e:
            logger.error(f"Error al inicializar base de datos: {e}")
            raise


# Instancia global (se inicializa en app.py)
db = None


def init_db(config):
    """Inicializar database MongoDB con configuración"""
    global db
    db = MongoDatabase(config)
    db.initialize_database()
    return db

"""
Modelos de datos y lógica del juego
"""
import random
import secrets
from datetime import datetime
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

# Inicializar db como None, será asignado por app.py
db = None


class BuckshotGame:
    """Lógica principal del juego Buckshot Roulette"""
    
    def __init__(self, config):
        self.config = config
    
    def cargar_escopeta(self):
        """
        Cargar escopeta con balas aleatorias
        Returns: (escopeta, num_reales, num_fogueo)
        """
        num_reales = random.randint(
            self.config.MIN_BALAS_REALES,
            self.config.MAX_BALAS_REALES
        )
        num_fogueo = random.randint(
            self.config.MIN_BALAS_FOGUEO,
            self.config.MAX_BALAS_FOGUEO
        )
        
        # 1 = real, 0 = fogueo
        escopeta = [1] * num_reales + [0] * num_fogueo
        random.shuffle(escopeta)
        
        return escopeta, num_reales, num_fogueo
    
    def generar_session_id(self):
        """Generar ID único de sesión"""
        return secrets.token_urlsafe(32)
    
    def procesar_disparo(self, bala, objetivo, turno_jugador):
        """
        Procesar resultado de disparo
        Returns: dict con resultado
        """
        resultado = {
            'bala_real': bala == 1,
            'dano': 0,
            'puntos_ganados': 0,
            'cambiar_turno': False,
            'mensaje': ''
        }
        
        if turno_jugador:
            if objetivo == 'bot':
                if bala == 1:
                    resultado['dano'] = 1
                    resultado['puntos_ganados'] = self.config.PUNTOS_BALA_REAL
                    resultado['mensaje'] = "¡BANG! Bala REAL al bot"
                else:
                    resultado['mensaje'] = "Click - Fogueo al bot"
                resultado['cambiar_turno'] = True
            
            else:  # jugador se dispara a sí mismo
                if bala == 1:
                    resultado['dano'] = 1
                    resultado['mensaje'] = "¡BANG! Te disparaste con bala REAL"
                    resultado['cambiar_turno'] = True
                else:
                    resultado['puntos_ganados'] = self.config.PUNTOS_FOGUEO_SELF
                    resultado['mensaje'] = "Fogueo - Sigues jugando"
                    resultado['cambiar_turno'] = False
        
        else:  # turno del bot
            # Bot decide: 70% disparar al jugador, 30% a sí mismo
            if random.random() < 0.7:
                objetivo = 'jugador'
            else:
                objetivo = 'bot'
            
            if objetivo == 'jugador':
                if bala == 1:
                    resultado['dano'] = 1
                    resultado['mensaje'] = "El bot te disparó con bala REAL"
                else:
                    resultado['mensaje'] = "El bot te disparó - Fogueo"
                resultado['cambiar_turno'] = True
            else:
                if bala == 1:
                    resultado['dano'] = -1  # Daño al bot
                    resultado['mensaje'] = "El bot se disparó con bala REAL"
                else:
                    resultado['mensaje'] = "El bot se disparó - Fogueo, sigue"
                    resultado['cambiar_turno'] = False
        
        return resultado


class Puntuacion:
    """Modelo para manejar puntuaciones en MongoDB"""
    
    @staticmethod
    def guardar(nombre, puntos, session_id=None):
        """
        Guardar puntuación en MongoDB
        Returns: ID del documento insertado
        """
        try:
            documento = {
                'nombre': nombre,
                'puntos': puntos,
                'session_id': session_id,
                'fecha': datetime.now()
            }
            
            result_id = db.insert_one('puntuaciones', documento)
            logger.info(f"Puntuación guardada: {nombre} - {puntos} pts")
            return str(result_id)
        
        except Exception as e:
            logger.error(f"Error al guardar puntuación: {e}")
            raise
    
    @staticmethod
    def obtener_ranking(limite=10):
        """
        Obtener top puntuaciones ordenadas por puntos descendentes
        """
        try:
            # MongoDB query con sort
            resultados = db.find(
                'puntuaciones',
                filter_dict={},
                sort=[("puntos", -1), ("fecha", -1)],
                limit=limite
            )
            
            # Formatear resultados
            ranking = [
                {
                    'nombre': doc['nombre'],
                    'puntos': doc['puntos'],
                    'fecha': doc['fecha'].strftime('%Y-%m-%d %H:%M:%S') if doc.get('fecha') else None
                }
                for doc in resultados
            ]
            
            return ranking
        
        except Exception as e:
            logger.error(f"Error al obtener ranking: {e}")
            raise
    
    @staticmethod
    def obtener_ranking_por_fecha(limite=10, fecha_desde=None):
        """
        Obtener ranking filtrado por fecha
        """
        try:
            if fecha_desde:
                # Filtro MongoDB para documentos con fecha >= fecha_desde
                filter_dict = {'fecha': {'$gte': fecha_desde}}
            else:
                filter_dict = {}
            
            resultados = db.find(
                'puntuaciones',
                filter_dict=filter_dict,
                sort=[("puntos", -1), ("fecha", -1)],
                limit=limite
            )
            
            ranking = [
                {
                    'nombre': doc['nombre'],
                    'puntos': doc['puntos'],
                    'fecha': doc['fecha'].strftime('%Y-%m-%d %H:%M:%S') if doc.get('fecha') else None
                }
                for doc in resultados
            ]
            
            return ranking
        
        except Exception as e:
            logger.error(f"Error al obtener ranking por fecha: {e}")
            raise
    
    @staticmethod
    def obtener_estadisticas():
        """
        Obtener estadísticas globales del juego usando agregación
        """
        try:
            # Pipeline de agregación MongoDB
            pipeline = [
                {
                    '$group': {
                        '_id': None,
                        'total_partidas': {'$sum': 1},
                        'promedio_puntos': {'$avg': '$puntos'},
                        'max_puntos': {'$max': '$puntos'},
                        'min_puntos': {'$min': '$puntos'}
                    }
                }
            ]
            
            resultado = db.aggregate('puntuaciones', pipeline)
            
            if resultado:
                doc = resultado[0]
                return {
                    'total_partidas': doc.get('total_partidas', 0),
                    'promedio_puntos': round(doc.get('promedio_puntos', 0), 2),
                    'max_puntos': doc.get('max_puntos', 0),
                    'min_puntos': doc.get('min_puntos', 0)
                }
            
            return {
                'total_partidas': 0,
                'promedio_puntos': 0,
                'max_puntos': 0,
                'min_puntos': 0
            }
        
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            raise


class SesionJuego:
    """Modelo para manejar sesiones de juego en MongoDB"""
    
    @staticmethod
    def crear(session_id, nombre_jugador):
        """Crear nueva sesión"""
        try:
            documento = {
                'session_id': session_id,
                'nombre_jugador': nombre_jugador,
                'fecha_inicio': datetime.now(),
                'fecha_fin': None,
                'puntos_finales': None,
                'balas_disparadas': 0
            }
            
            result_id = db.insert_one('sesiones_juego', documento)
            logger.info(f"Sesión creada: {nombre_jugador} - {session_id[:8]}...")
            return str(result_id)
        
        except Exception as e:
            logger.error(f"Error al crear sesión: {e}")
            raise
    
    @staticmethod
    def finalizar(session_id, puntos_finales, balas_disparadas):
        """Finalizar sesión"""
        try:
            update_dict = {
                'fecha_fin': datetime.now(),
                'puntos_finales': puntos_finales,
                'balas_disparadas': balas_disparadas
            }
            
            db.update_one(
                'sesiones_juego',
                filter_dict={'session_id': session_id},
                update_dict=update_dict
            )
            
            logger.info(f"Sesión finalizada: {session_id[:8]}... - {puntos_finales} pts")
        
        except Exception as e:
            logger.error(f"Error al finalizar sesión: {e}")
            raise



class Puntuacion:
    """Modelo para manejar puntuaciones"""
    
    @staticmethod
    def guardar(nombre, puntos, session_id=None):
        """
        Guardar puntuación en base de datos
        """
        try:
            documento = {
                'nombre': nombre,
                'puntos': puntos,
                'session_id': session_id,
                'fecha': datetime.now()
            }
            
            result = db.insert_one('puntuaciones', documento)
            
            if result is not None:
                logger.info(f"Puntuación guardada: {nombre} - {puntos} pts")
                return str(result)
            
            return None
        
        except Exception as e:
            logger.error(f"Error al guardar puntuación: {e}")
            raise
    
    @staticmethod
    def obtener_ranking(limite=10):
        """
        Obtener top puntuaciones
        """
        try:
            resultados = db.find(
                'puntuaciones',
                sort=[('puntos', -1)],
                limit=limite
            )
            
            # Formatear resultados
            ranking = [
                {
                    'nombre': doc.get('nombre'),
                    'puntos': doc.get('puntos'),
                    'fecha': doc.get('fecha').strftime('%Y-%m-%d %H:%M:%S') if doc.get('fecha') else None
                }
                for doc in resultados
            ]
            
            return ranking
        
        except Exception as e:
            logger.error(f"Error al obtener ranking: {e}")
            raise
    
    @staticmethod
    def obtener_ranking_por_fecha(limite=10, fecha_desde=None):
        """
        Obtener ranking filtrado por fecha
        """
        try:
            query_filter = {}
            if fecha_desde:
                query_filter = {'fecha': {'$gte': fecha_desde}}
            
            resultados = db.find(
                'puntuaciones',
                query_filter,
                sort=[('puntos', -1)],
                limit=limite
            )
            
            ranking = [
                {
                    'nombre': doc.get('nombre'),
                    'puntos': doc.get('puntos'),
                    'fecha': doc.get('fecha').strftime('%Y-%m-%d %H:%M:%S') if doc.get('fecha') else None
                }
                for doc in resultados
            ]
            
            return ranking
        
        except Exception as e:
            logger.error(f"Error al obtener ranking por fecha: {e}")
            raise
    
    @staticmethod
    def obtener_estadisticas():
        """
        Obtener estadísticas globales del juego
        """
        try:
            pipeline = [
                {
                    '$group': {
                        '_id': None,
                        'total_partidas': {'$sum': 1},
                        'promedio_puntos': {'$avg': '$puntos'},
                        'max_puntos': {'$max': '$puntos'},
                        'min_puntos': {'$min': '$puntos'}
                    }
                }
            ]
            
            resultado = list(db.aggregate('puntuaciones', pipeline))
            
            if resultado:
                doc = resultado[0]
                return {
                    'total_partidas': doc.get('total_partidas', 0),
                    'promedio_puntos': round(float(doc.get('promedio_puntos', 0)), 2),
                    'max_puntos': doc.get('max_puntos', 0),
                    'min_puntos': doc.get('min_puntos', 0)
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            raise


class SesionJuego:
    """Modelo para manejar sesiones de juego"""
    
    @staticmethod
    def crear(session_id, nombre_jugador):
        """Crear nueva sesión"""
        try:
            documento = {
                'session_id': session_id,
                'nombre_jugador': nombre_jugador,
                'fecha_inicio': datetime.now()
            }
            
            result = db.insert_one('sesiones_juego', documento)
            return str(result) if result is not None else None
        
        except Exception as e:
            logger.error(f"Error al crear sesión: {e}")
            raise
    
    @staticmethod
    def finalizar(session_id, puntos_finales, balas_disparadas):
        """Finalizar sesión"""
        try:
            db.update_one(
                'sesiones_juego',
                {'session_id': session_id},
                {
                    'fecha_fin': datetime.now(),
                    'puntos_finales': puntos_finales,
                    'balas_disparadas': balas_disparadas
                }
            )
        
        except Exception as e:
            logger.error(f"Error al finalizar sesión: {e}")
            raise

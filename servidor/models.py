"""
Modelos de datos y logica del juego.
"""
import random
import secrets
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Inicializado por app.py durante el arranque
db = None


class BuckshotGame:
    """Logica principal del juego Buckshot Roulette."""

    def __init__(self, config):
        self.config = config

    def cargar_escopeta(self):
        """
        Cargar escopeta con balas aleatorias.
        Returns: (escopeta, num_reales, num_fogueo)
        """
        num_reales = random.randint(
            self.config.MIN_BALAS_REALES,
            self.config.MAX_BALAS_REALES,
        )
        num_fogueo = random.randint(
            self.config.MIN_BALAS_FOGUEO,
            self.config.MAX_BALAS_FOGUEO,
        )

        # 1 = real, 0 = fogueo
        escopeta = [1] * num_reales + [0] * num_fogueo
        random.shuffle(escopeta)

        return escopeta, num_reales, num_fogueo

    def generar_session_id(self):
        """Generar ID unico de sesion."""
        return secrets.token_urlsafe(32)

    def procesar_disparo(self, bala, objetivo, turno_jugador):
        """
        Procesar resultado de disparo.
        Returns: dict con resultado.
        """
        resultado = {
            "bala_real": bala == 1,
            "dano": 0,
            "puntos_ganados": 0,
            "cambiar_turno": False,
            "mensaje": "",
        }

        if turno_jugador:
            if objetivo == "bot":
                if bala == 1:
                    resultado["dano"] = 1
                    resultado["puntos_ganados"] = self.config.PUNTOS_BALA_REAL
                    resultado["mensaje"] = "!BANG! Bala REAL al bot"
                else:
                    resultado["mensaje"] = "Click - Fogueo al bot"
                resultado["cambiar_turno"] = True
            else:
                # Jugador se dispara a si mismo
                if bala == 1:
                    resultado["dano"] = 1
                    resultado["mensaje"] = "!BANG! Te disparaste con bala REAL"
                    resultado["cambiar_turno"] = True
                else:
                    resultado["puntos_ganados"] = self.config.PUNTOS_FOGUEO_SELF
                    resultado["mensaje"] = "Fogueo - Sigues jugando"
                    resultado["cambiar_turno"] = False
        else:
            # Turno del bot: 70% al jugador, 30% a si mismo
            objetivo_bot = "jugador" if random.random() < 0.7 else "bot"

            if objetivo_bot == "jugador":
                if bala == 1:
                    resultado["dano"] = 1
                    resultado["mensaje"] = "El bot te disparo con bala REAL"
                else:
                    resultado["mensaje"] = "El bot te disparo - Fogueo"
                resultado["cambiar_turno"] = True
            else:
                if bala == 1:
                    resultado["dano"] = -1
                    resultado["mensaje"] = "El bot se disparo con bala REAL"
                else:
                    resultado["mensaje"] = "El bot se disparo - Fogueo, sigue"
                    resultado["cambiar_turno"] = False

        return resultado


class Puntuacion:
    """Modelo para manejar puntuaciones en MongoDB."""

    @staticmethod
    def guardar(nombre, puntos, session_id=None):
        """Guardar puntuacion en MongoDB."""
        try:
            documento = {
                "nombre": nombre,
                "puntos": puntos,
                "session_id": session_id,
                "fecha": datetime.now(),
            }

            result_id = db.insert_one("puntuaciones", documento)
            logger.info(f"Puntuacion guardada: {nombre} - {puntos} pts")
            return str(result_id)
        except Exception as e:
            logger.error(f"Error al guardar puntuacion: {e}")
            raise

    @staticmethod
    def obtener_ranking(limite=10):
        """Obtener top puntuaciones ordenadas por puntos y fecha."""
        try:
            resultados = db.find(
                "puntuaciones",
                filter_dict={},
                sort=[("puntos", -1), ("fecha", -1)],
                limit=limite,
            )

            return [
                {
                    "nombre": doc.get("nombre"),
                    "puntos": doc.get("puntos", 0),
                    "fecha": (
                        doc.get("fecha").strftime("%Y-%m-%d %H:%M:%S")
                        if doc.get("fecha")
                        else None
                    ),
                }
                for doc in resultados
            ]
        except Exception as e:
            logger.error(f"Error al obtener ranking: {e}")
            raise

    @staticmethod
    def obtener_ranking_por_fecha(limite=10, fecha_desde=None):
        """Obtener ranking filtrado por fecha."""
        try:
            query_filter = {"fecha": {"$gte": fecha_desde}} if fecha_desde else {}
            resultados = db.find(
                "puntuaciones",
                filter_dict=query_filter,
                sort=[("puntos", -1), ("fecha", -1)],
                limit=limite,
            )

            return [
                {
                    "nombre": doc.get("nombre"),
                    "puntos": doc.get("puntos", 0),
                    "fecha": (
                        doc.get("fecha").strftime("%Y-%m-%d %H:%M:%S")
                        if doc.get("fecha")
                        else None
                    ),
                }
                for doc in resultados
            ]
        except Exception as e:
            logger.error(f"Error al obtener ranking por fecha: {e}")
            raise

    @staticmethod
    def obtener_estadisticas():
        """Obtener estadisticas globales del juego usando agregacion."""
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "total_partidas": {"$sum": 1},
                        "promedio_puntos": {"$avg": "$puntos"},
                        "max_puntos": {"$max": "$puntos"},
                        "min_puntos": {"$min": "$puntos"},
                    }
                }
            ]

            resultado = db.aggregate("puntuaciones", pipeline)
            if resultado:
                doc = resultado[0]
                return {
                    "total_partidas": doc.get("total_partidas", 0),
                    "promedio_puntos": round(float(doc.get("promedio_puntos", 0)), 2),
                    "max_puntos": doc.get("max_puntos", 0),
                    "min_puntos": doc.get("min_puntos", 0),
                }

            return {
                "total_partidas": 0,
                "promedio_puntos": 0,
                "max_puntos": 0,
                "min_puntos": 0,
            }
        except Exception as e:
            logger.error(f"Error al obtener estadisticas: {e}")
            raise


class SesionJuego:
    """Modelo para manejar sesiones de juego en MongoDB."""

    @staticmethod
    def crear(session_id, nombre_jugador):
        """Crear nueva sesion."""
        try:
            documento = {
                "session_id": session_id,
                "nombre_jugador": nombre_jugador,
                "fecha_inicio": datetime.now(),
                "fecha_fin": None,
                "puntos_finales": None,
                "balas_disparadas": 0,
            }

            result_id = db.insert_one("sesiones_juego", documento)
            logger.info(f"Sesion creada: {nombre_jugador} - {session_id[:8]}...")
            return str(result_id)
        except Exception as e:
            logger.error(f"Error al crear sesion: {e}")
            raise

    @staticmethod
    def finalizar(session_id, puntos_finales, balas_disparadas):
        """Finalizar sesion."""
        try:
            update_dict = {
                "fecha_fin": datetime.now(),
                "puntos_finales": puntos_finales,
                "balas_disparadas": balas_disparadas,
            }

            db.update_one(
                "sesiones_juego",
                filter_dict={"session_id": session_id},
                update_dict=update_dict,
            )
            logger.info(f"Sesion finalizada: {session_id[:8]}... - {puntos_finales} pts")
        except Exception as e:
            logger.error(f"Error al finalizar sesion: {e}")
            raise

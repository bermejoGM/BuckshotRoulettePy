"""
Pantallas del juego - Inicio, Juego, Ranking
"""
import pygame
import sys

class Button:
    """Clase para botones interactivos"""
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.current_color = color
        self.font = pygame.font.Font(None, 32)
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 3, border_radius=10)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def check_hover(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            return True
        else:
            self.current_color = self.color
            return False
    
    def check_click(self, mouse_pos, mouse_pressed):
        if self.rect.collidepoint(mouse_pos) and mouse_pressed[0]:
            return True
        return False


class InputBox:
    """Caja de texto para input"""
    def __init__(self, x, y, width, height, placeholder=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.color_inactive = pygame.Color('#2a2a2a')
        self.color_active = pygame.Color('#ff0000')
        self.color = self.color_inactive
        self.text = ''
        self.placeholder = placeholder
        self.font = pygame.font.Font(None, 36)
        self.active = False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True
            elif len(self.text) < 20:
                self.text += event.unicode
        
        return False
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (255, 0, 0), self.rect, 2, border_radius=8)
        
        display_text = self.text if self.text else self.placeholder
        text_color = (255, 255, 255) if self.text else (100, 100, 100)
        text_surface = self.font.render(display_text, True, text_color)
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))


class PantallaInicio:
    """Pantalla de inicio con input de nombre"""
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font_titulo = pygame.font.Font(None, 72)
        self.font_texto = pygame.font.Font(None, 28)
        
        # Input box para nombre
        self.input_box = InputBox(200, 300, 400, 50, "Ingresa tu nombre")
        
        # Botón iniciar
        self.btn_iniciar = Button(250, 400, 300, 60, "COMENZAR", 
                                   (200, 0, 0), (255, 0, 0))
        self.btn_ver_puntuaciones = Button(250, 480, 300, 50, "VER PUNTUACIONES",
                           (60, 60, 60), (100, 100, 100))
    
    def render(self, events):
        # Fondo degradado
        self.screen.fill((30, 0, 0))
        
        # Título
        titulo = self.font_titulo.render("BUCKSHOT ROULETTE", True, (255, 0, 0))
        titulo_rect = titulo.get_rect(center=(self.width // 2, 100))
        self.screen.blit(titulo, titulo_rect)
        
        # Instrucciones
        instrucciones = [
            "¡Bienvenido al juego más peligroso!",
            "Tienes 3 vidas. Pierdes si recibes 3 balas reales.",
            "Dispara al bot o arríesgate disparándote a ti mismo."
        ]
        
        y = 180
        for linea in instrucciones:
            texto = self.font_texto.render(linea, True, (200, 200, 200))
            texto_rect = texto.get_rect(center=(self.width // 2, y))
            self.screen.blit(texto, texto_rect)
            y += 35
        
        # Input box
        self.input_box.draw(self.screen)
        
        # Botón
        self.btn_iniciar.draw(self.screen)
        self.btn_ver_puntuaciones.draw(self.screen)
        self.btn_iniciar.check_hover(pygame.mouse.get_pos())
        self.btn_ver_puntuaciones.check_hover(pygame.mouse.get_pos())
        
        # Procesar eventos
        click_pos = None
        for event in events:
            enter_pressed = self.input_box.handle_event(event)
            if enter_pressed and self.input_box.text.strip():
                return {'tipo': 'iniciar_juego', 'nombre': self.input_box.text.strip()}
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click_pos = event.pos
        
        # Click en botón
        if click_pos and self.btn_iniciar.rect.collidepoint(click_pos):
            if self.input_box.text.strip():
                return {'tipo': 'iniciar_juego', 'nombre': self.input_box.text.strip()}

        if click_pos and self.btn_ver_puntuaciones.rect.collidepoint(click_pos):
            return {'tipo': 'ver_puntuaciones'}
        
        return None


class PantallaJuego:
    """Pantalla principal del juego"""
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font_stat = pygame.font.Font(None, 36)
        self.font_label = pygame.font.Font(None, 24)
        self.font_mensaje = pygame.font.Font(None, 28)
        
        # Datos del juego
        self.vidas_jugador = 3
        self.vidas_bot = 3
        self.puntos = 0
        self.balas_restantes = 0
        self.mensaje = "Prepárate para jugar..."
        self.turno_jugador = True
        
        # Botones
        self.btn_disparar_bot = Button(150, 400, 500, 60, "Disparar al BOT",
                                        (180, 50, 50), (220, 70, 70))
        self.btn_disparar_self = Button(150, 480, 500, 60, "Dispararte a TI",
                                         (180, 120, 0), (220, 150, 0))
        self.btn_turno_bot = Button(150, 440, 500, 60, "Turno del Bot",
                                     (100, 100, 100), (150, 150, 150))
    
    def actualizar_datos(self, datos):
        """Actualizar datos desde API"""
        self.vidas_jugador = datos.get('vidas_jugador', self.vidas_jugador)
        self.vidas_bot = datos.get('vidas_bot', self.vidas_bot)
        self.puntos = datos.get('puntos', self.puntos)
        self.balas_restantes = datos.get('balas_restantes', self.balas_restantes)
        self.mensaje = datos.get('mensaje', self.mensaje)
        if 'turno_jugador' in datos:
            self.turno_jugador = bool(datos.get('turno_jugador'))
        elif 'cambiar_turno' in datos:
            if datos.get('cambiar_turno'):
                self.turno_jugador = not self.turno_jugador
    
    def dibujar_stat_box(self, x, y, label, valor, color=(255, 0, 0)):
        """Dibujar caja de estadística"""
        rect = pygame.Rect(x, y, 180, 100)
        pygame.draw.rect(self.screen, (40, 40, 40), rect, border_radius=10)
        pygame.draw.rect(self.screen, color, rect, 3, border_radius=10)
        
        label_surf = self.font_label.render(label, True, (150, 150, 150))
        label_rect = label_surf.get_rect(center=(x + 90, y + 30))
        self.screen.blit(label_surf, label_rect)
        
        valor_surf = self.font_stat.render(str(valor), True, color)
        valor_rect = valor_surf.get_rect(center=(x + 90, y + 65))
        self.screen.blit(valor_surf, valor_rect)
    
    def render(self, events):
        # Fondo
        self.screen.fill((20, 20, 20))
        
        # Título
        titulo = pygame.font.Font(None, 48).render("BUCKSHOT ROULETTE", True, (255, 0, 0))
        titulo_rect = titulo.get_rect(center=(self.width // 2, 40))
        self.screen.blit(titulo, titulo_rect)
        
        # Stats
        self.dibujar_stat_box(50, 90, "Tus Vidas", self.vidas_jugador)
        self.dibujar_stat_box(240, 90, "Vidas Bot", self.vidas_bot)
        self.dibujar_stat_box(430, 90, "Puntos", self.puntos, (0, 200, 0))
        self.dibujar_stat_box(50, 210, "Balas", self.balas_restantes, (255, 150, 0))
        
        # Mensaje
        mensaje_rect = pygame.Rect(50, 330, 700, 50)
        pygame.draw.rect(self.screen, (40, 40, 40), mensaje_rect, border_radius=8)
        pygame.draw.rect(self.screen, (255, 0, 0), mensaje_rect, 2, border_radius=8)
        
        # Dividir mensaje en líneas si es muy largo
        palabras = self.mensaje.split()
        lineas = []
        linea_actual = ""
        
        for palabra in palabras:
            test_linea = linea_actual + " " + palabra if linea_actual else palabra
            if self.font_mensaje.size(test_linea)[0] < 680:
                linea_actual = test_linea
            else:
                lineas.append(linea_actual)
                linea_actual = palabra
        if linea_actual:
            lineas.append(linea_actual)
        
        y_offset = 340 if len(lineas) == 1 else 333
        for linea in lineas[:2]:  # Máximo 2 líneas
            mensaje_surf = self.font_mensaje.render(linea, True, (255, 255, 255))
            self.screen.blit(mensaje_surf, (60, y_offset))
            y_offset += 25
        
        # Botones según turno
        accion = None
        
        click_pos = None
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click_pos = event.pos

        if self.turno_jugador:
            self.btn_disparar_bot.draw(self.screen)
            self.btn_disparar_self.draw(self.screen)
            
            self.btn_disparar_bot.check_hover(pygame.mouse.get_pos())
            self.btn_disparar_self.check_hover(pygame.mouse.get_pos())
            
            if click_pos and self.btn_disparar_bot.rect.collidepoint(click_pos):
                accion = {'tipo': 'disparar', 'objetivo': 'bot'}
            elif click_pos and self.btn_disparar_self.rect.collidepoint(click_pos):
                accion = {'tipo': 'disparar', 'objetivo': 'jugador'}
        else:
            self.btn_turno_bot.draw(self.screen)
            self.btn_turno_bot.check_hover(pygame.mouse.get_pos())
            
            if click_pos and self.btn_turno_bot.rect.collidepoint(click_pos):
                accion = {'tipo': 'turno_bot'}
        
        return accion


class PantallaRanking:
    """Pantalla de ranking global"""
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font_titulo = pygame.font.Font(None, 56)
        self.font_item = pygame.font.Font(None, 28)
        self.font_score = pygame.font.Font(None, 32)
        
        self.ranking = []
        self.puntos_jugador = 0
        self.nombre_jugador = ""
        
        # Botones
        self.btn_reiniciar = Button(250, 520, 300, 50, "MENU PRINCIPAL",
                                     (0, 150, 0), (0, 200, 0))
    
    def actualizar_ranking(self, ranking, puntos, nombre):
        """Actualizar datos de ranking"""
        self.ranking = ranking
        self.puntos_jugador = puntos
        self.nombre_jugador = nombre
    
    def render(self, events):
        # Fondo
        self.screen.fill((20, 20, 20))
        
        # Título
        titulo = self.font_titulo.render("GAME OVER", True, (255, 0, 0))
        titulo_rect = titulo.get_rect(center=(self.width // 2, 50))
        self.screen.blit(titulo, titulo_rect)
        
        # Tu puntuación
        tu_score = self.font_score.render(f"Tu puntuación: {self.puntos_jugador} pts", 
                                          True, (255, 200, 0))
        tu_score_rect = tu_score.get_rect(center=(self.width // 2, 110))
        self.screen.blit(tu_score, tu_score_rect)
        
        # Título ranking
        ranking_titulo = pygame.font.Font(None, 36).render("TOP 10 GLOBAL", True, (255, 200, 0))
        ranking_titulo_rect = ranking_titulo.get_rect(center=(self.width // 2, 160))
        self.screen.blit(ranking_titulo, ranking_titulo_rect)
        
        # Lista de ranking
        y = 200
        for i, item in enumerate(self.ranking[:10], 1):
            # Extraer datos del diccionario retornado por la API
            nombre = item.get('nombre', 'Unknown') if isinstance(item, dict) else item[0]
            puntos = item.get('puntos', 0) if isinstance(item, dict) else item[1]
            fecha = item.get('fecha', '') if isinstance(item, dict) else item[2]
            
            # Fondo item
            item_rect = pygame.Rect(100, y, 600, 30)
            color_fondo = (50, 50, 50) if i % 2 == 0 else (40, 40, 40)
            
            # Resaltar jugador actual
            if nombre == self.nombre_jugador and puntos == self.puntos_jugador:
                color_fondo = (80, 30, 30)
            
            pygame.draw.rect(self.screen, color_fondo, item_rect, border_radius=5)
            
            # Posición y nombre
            pos_texto = self.font_item.render(f"{i}. {nombre}", True, (255, 255, 255))
            self.screen.blit(pos_texto, (110, y + 5))
            
            # Fecha
            fecha_texto = self.font_item.render(fecha, True, (150, 150, 150))
            self.screen.blit(fecha_texto, (320, y + 5))
            
            # Puntos
            puntos_texto = self.font_item.render(f"{puntos} pts", True, (255, 200, 0))
            self.screen.blit(puntos_texto, (600, y + 5))
            
            y += 32
        
        # Botón reiniciar
        self.btn_reiniciar.draw(self.screen)
        self.btn_reiniciar.check_hover(pygame.mouse.get_pos())
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_reiniciar.rect.collidepoint(event.pos):
                    return {'tipo': 'reiniciar'}
        
        return None


class PantallaPuntuaciones:
    """Pantalla de puntuaciones finales"""
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.font_titulo = pygame.font.Font(None, 56)
        self.font_item = pygame.font.Font(None, 28)

        self.ranking = []

        # Botón para volver al menú principal
        self.btn_volver_menu = Button(220, 520, 360, 50, "VOLVER AL MENU PRINCIPAL",
                                      (60, 60, 60), (100, 100, 100))

    def actualizar_ranking(self, ranking):
        """Actualizar lista de puntuaciones"""
        self.ranking = ranking

    def render(self, events):
        # Fondo
        self.screen.fill((20, 20, 20))

        # Título
        titulo = self.font_titulo.render("PUNTUACIONES FINALES", True, (255, 200, 0))
        titulo_rect = titulo.get_rect(center=(self.width // 2, 60))
        self.screen.blit(titulo, titulo_rect)

        # Lista de puntuaciones
        y = 120
        for i, item in enumerate(self.ranking[:10], 1):
            nombre = item.get('nombre', 'Unknown') if isinstance(item, dict) else item[0]
            puntos = item.get('puntos', 0) if isinstance(item, dict) else item[1]
            fecha = item.get('fecha', '') if isinstance(item, dict) else item[2]

            item_rect = pygame.Rect(100, y, 600, 34)
            color_fondo = (50, 50, 50) if i % 2 == 0 else (40, 40, 40)
            pygame.draw.rect(self.screen, color_fondo, item_rect, border_radius=5)

            pos_texto = self.font_item.render(f"{i}. {nombre}", True, (255, 255, 255))
            self.screen.blit(pos_texto, (110, y + 7))

            fecha_texto = self.font_item.render(fecha, True, (150, 150, 150))
            self.screen.blit(fecha_texto, (320, y + 7))

            puntos_texto = self.font_item.render(f"{puntos} pts", True, (255, 200, 0))
            self.screen.blit(puntos_texto, (600, y + 7))

            y += 36

        # Botón volver
        self.btn_volver_menu.draw(self.screen)
        self.btn_volver_menu.check_hover(pygame.mouse.get_pos())

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_volver_menu.rect.collidepoint(event.pos):
                    return {'tipo': 'volver_inicio'}

        return None

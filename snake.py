import pygame
import random
import time
import math
from enum import Enum
from collections import namedtuple

# Inicialización de pygame y configuración de fuente
pygame.init()
font = pygame.font.Font('arial.ttf', 25)
title_font = pygame.font.Font('arial.ttf', 40)

# Configuración global del juego
BLOCK_SIZE = 20
SPEED_OPTIONS = [10, 15, 20, 25, 30]  # Opciones de velocidad (dificultad)
SPEED = SPEED_OPTIONS[2]  # Velocidad por defecto (nivel medio)
TIMER_SECONDS = 3
MAX_ATTEMPTS = 6  # Máximo número de intentos

# Definición de direcciones como enum para mejor legibilidad
class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    
Point = namedtuple('Point', 'x, y')

# Definición de colores para usar en el juego
WHITE = (255, 255, 255)
RED = (200, 0, 0)
LIGHT_RED = (255, 100, 100)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
GRID_COLOR = (20, 20, 20)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)

# Lista de colores disponibles para la serpiente
SNAKE_COLORS = [
    {"name": "Azul", "primary": BLUE1, "secondary": BLUE2},
    {"name": "Verde", "primary": (0, 200, 0), "secondary": (0, 255, 0)},
    {"name": "Rojo", "primary": (200, 0, 0), "secondary": (255, 0, 0)},
    {"name": "Morado", "primary": (128, 0, 128), "secondary": (180, 0, 180)},
    {"name": "Naranja", "primary": (255, 140, 0), "secondary": (255, 165, 0)},
    {"name": "Cian", "primary": (0, 180, 180), "secondary": (0, 255, 255)},
]

# Estados del juego
class GameState(Enum):
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    DIFFICULTY = 3
    COLOR_SELECT = 4

class Button:
    """
    Clase para crear botones interactivos con efectos de hover.
    Proporciona métodos para dibujar, detectar hover y clicks.
    """
    def __init__(self, x, y, width, height, text, color):
        """Inicializa un botón con posición, tamaño, texto y color."""
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        # Color más claro para el efecto hover
        self.hover_color = (min(color[0] + 50, 255), min(color[1] + 50, 255), min(color[2] + 50, 255))
        self.is_hovered = False
        
    def draw(self, surface):
        """
        Dibuja el botón en la superficie especificada, 
        con efecto de hover si el ratón está encima.
        """
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)  # Borde blanco
        
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def check_hover(self, pos):
        """
        Verifica si la posición del ratón está sobre el botón y
        actualiza el estado de hover.
        """
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, click):
        """
        Verifica si el botón ha sido clickeado.
        Requiere la posición del ratón y el estado del click.
        """
        return self.rect.collidepoint(pos) and click

class SnakeGame:
    """
    Clase principal que implementa el juego Snake con interfaz gráfica
    y efectos visuales.
    """
    
    def __init__(self, w=640, h=480):
        """
        Inicializa el juego con la ventana y todos los elementos necesarios.
        
        Args:
            w (int): Ancho de la ventana del juego
            h (int): Alto de la ventana del juego
        """
        self.w = w
        self.h = h
        # Inicializar la ventana de juego
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        
        # Estado del juego y número de intentos
        self.game_state = GameState.MENU
        self.attempts_remaining = MAX_ATTEMPTS
        self.selected_speed_index = 2  # Índice medio por defecto
        self.selected_color_index = 0  # Color por defecto (Azul)
        
        # Crear fondo con cuadrícula
        self.background = pygame.Surface((self.w, self.h))
        self.draw_background_grid()
        
        # Variable para los efectos de animación
        self.time = 0
        
        # Inicializar el juego y crear botones
        self.reset_game()
        self.create_buttons()
        
    def create_buttons(self):
        """
        Crea todos los botones necesarios para las diferentes pantallas.
        """
        button_width, button_height = 200, 50
        button_x = self.w // 2 - button_width // 2
        
        # Botones del menú principal
        self.play_button = Button(button_x, 150, button_width, button_height, "Jugar", GREEN)
        self.difficulty_button = Button(button_x, 220, button_width, button_height, "Dificultad", BLUE1)
        self.color_button = Button(button_x, 290, button_width, button_height, "Cambiar Color", PURPLE)
        self.quit_button = Button(button_x, 360, button_width, button_height, "Salir", RED)
        
        # Botones para la pantalla de game over
        self.restart_button = Button(button_x, self.h // 2 + 50, button_width, button_height, "Reiniciar", GREEN)
        self.menu_button = Button(button_x, self.h // 2 + 110, button_width, button_height, "Menú Principal", BLUE1)
        
        # Botones para la pantalla de dificultad
        self.back_button = Button(button_x, 360, button_width, button_height, "Volver", ORANGE)
        
        # Botones de dificultad
        self.difficulty_buttons = []
        for i, speed in enumerate(SPEED_OPTIONS):
            difficulty_text = f"{'Muy fácil' if i == 0 else 'Fácil' if i == 1 else 'Normal' if i == 2 else 'Difícil' if i == 3 else 'Muy difícil'}"
            button_color = (int(50 + (i * 40)), int(200 - (i * 30)), 50)
            self.difficulty_buttons.append(
                Button(button_x, 120 + (i * 60), button_width, button_height, difficulty_text, button_color)
            )
            
        # Botones para selección de color
        self.color_buttons = []
        for i, color_data in enumerate(SNAKE_COLORS):
            button_color = color_data["primary"]
            self.color_buttons.append(
                Button(button_x, 120 + (i * 40), button_width, 30, color_data["name"], button_color)
            )
        
    def draw_background_grid(self):
        """
        Crea un fondo con patrón de cuadrícula sutil para mejorar
        la visibilidad del área de juego.
        """
        self.background.fill(BLACK)
        for x in range(0, self.w, BLOCK_SIZE):
            pygame.draw.line(self.background, GRID_COLOR, (x, 0), (x, self.h))
        for y in range(0, self.h, BLOCK_SIZE):
            pygame.draw.line(self.background, GRID_COLOR, (0, y), (self.w, y))
    
    def reset_game(self):
        """
        Reinicia todos los elementos del juego a su estado inicial.
        Se usa tanto al iniciar el juego como al reiniciarlo tras game over.
        """
        # Inicializar estado del juego
        self.direction = Direction.RIGHT
        self.last_direction = Direction.RIGHT
        
        # Crear la serpiente inicial (cabeza + 2 segmentos)
        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head, 
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        
        # Reiniciar puntuación y comida
        self.score = 0
        self.food = None
        self.generate_food()
        
        # Reiniciar temporizador y animaciones
        self.game_started = False
        self.start_time = time.time()
        self.time = 0
        
        # Buffer para teclas presionadas
        self.key_buffer = []
        
        # Resetear game_over
        self.game_over = False
        
    def generate_food(self):
        """
        Genera una nueva pieza de comida en una posición aleatoria.
        Evita que la comida aparezca donde está la serpiente.
        """
        x = random.randint(0, (self.w-BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE 
        y = random.randint(0, (self.h-BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self.generate_food()  # Recursión si la comida apareció en la serpiente
    
    def is_valid_direction(self, new_direction):
        """
        Verifica si la dirección solicitada es válida 
        (evita que la serpiente pueda girar 180 grados sobre sí misma).
        
        Args:
            new_direction (Direction): La nueva dirección propuesta
            
        Returns:
            bool: True si la dirección es válida, False si no lo es
        """
        # Verificar que la nueva dirección no sea opuesta a la dirección actual
        if (new_direction == Direction.LEFT and self.last_direction == Direction.RIGHT) or \
           (new_direction == Direction.RIGHT and self.last_direction == Direction.LEFT) or \
           (new_direction == Direction.UP and self.last_direction == Direction.DOWN) or \
           (new_direction == Direction.DOWN and self.last_direction == Direction.UP):
            return False
        return True
    
    def handle_input(self):
        """
        Procesa las entradas del usuario (teclado y ratón).
        Maneja las teclas de dirección y los clicks en botones.
        
        Returns:
            tuple: (cerrar_juego, click_del_raton)
        """
        self.key_buffer = []  # Reiniciar el buffer en cada frame
        mouse_click = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True, False
            
            # Procesar entradas de teclado durante el juego
            if self.game_state == GameState.PLAYING:
                if event.type == pygame.KEYDOWN:
                    if not self.game_started or self.game_over:
                        continue  # Ignorar entradas de dirección durante el temporizador o game over
                    
                    # Almacenar la tecla en el buffer
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.key_buffer.append(Direction.LEFT)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.key_buffer.append(Direction.RIGHT)
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.key_buffer.append(Direction.UP)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.key_buffer.append(Direction.DOWN)
                    # Tecla ESC para volver al menú principal
                    elif event.key == pygame.K_ESCAPE:
                        self.game_state = GameState.MENU
            
            # En cualquier estado, procesar clicks de ratón
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_click = True
                
        return False, mouse_click
    
    def process_direction_input(self):
        """
        Procesa el buffer de teclas y establece la dirección actual
        basándose en la última tecla válida presionada.
        """
        if self.key_buffer:
            # Tomar la última tecla presionada que sea válida
            for direction in reversed(self.key_buffer):
                if self.is_valid_direction(direction):
                    self.direction = direction
                    break
    
    def render_menu(self, mouse_pos, mouse_click):
        """
        Renderiza la pantalla del menú principal con todos los botones
        y maneja las interacciones.
        
        Args:
            mouse_pos (tuple): Posición actual del ratón
            mouse_click (bool): Si se ha hecho click en este frame
        """
        # Dibujar el fondo con cuadrícula
        self.display.blit(self.background, (0, 0))
        
        # Mostrar título del juego
        title_text = title_font.render("SNAKE GAME", True, WHITE)
        title_shadow = title_font.render("SNAKE GAME", True, (50, 50, 50))
        title_rect = title_text.get_rect(center=(self.w // 2, 60))
        shadow_rect = title_text.get_rect(center=(self.w // 2 + 2, 62))
        
        self.display.blit(title_shadow, shadow_rect)
        self.display.blit(title_text, title_rect)
        
        # Mostrar información de intentos restantes
        attempts_text = font.render(f"Intentos restantes: {self.attempts_remaining}", True, WHITE)
        attempts_rect = attempts_text.get_rect(center=(self.w // 2, 100))
        self.display.blit(attempts_text, attempts_rect)
        
        # Verificar interacciones con botones
        self.play_button.check_hover(mouse_pos)
        self.difficulty_button.check_hover(mouse_pos)
        self.color_button.check_hover(mouse_pos)
        self.quit_button.check_hover(mouse_pos)
        
        # Dibujar botones
        self.play_button.draw(self.display)
        self.difficulty_button.draw(self.display)
        self.color_button.draw(self.display)
        self.quit_button.draw(self.display)
        
        # Procesar clicks
        if mouse_click:
            if self.play_button.is_clicked(mouse_pos, True):
                if self.attempts_remaining > 0:
                    self.reset_game()
                    self.game_state = GameState.PLAYING
                else:
                    # No hay intentos restantes
                    pass  # Podríamos mostrar un mensaje o deshabilitar el botón
            elif self.difficulty_button.is_clicked(mouse_pos, True):
                self.game_state = GameState.DIFFICULTY
            elif self.color_button.is_clicked(mouse_pos, True):
                self.game_state = GameState.COLOR_SELECT
            elif self.quit_button.is_clicked(mouse_pos, True):
                return True  # Señal para salir del juego
        
        pygame.display.flip()
        return False
    
    def render_difficulty_screen(self, mouse_pos, mouse_click):
        """
        Renderiza la pantalla de selección de dificultad y maneja
        las interacciones con los botones.
        
        Args:
            mouse_pos (tuple): Posición actual del ratón
            mouse_click (bool): Si se ha hecho click en este frame
        """
        # Dibujar el fondo con cuadrícula
        self.display.blit(self.background, (0, 0))
        
        # Mostrar título
        title_text = title_font.render("DIFICULTAD", True, WHITE)
        title_rect = title_text.get_rect(center=(self.w // 2, 60))
        self.display.blit(title_text, title_rect)
        
        # Verificar interacciones con botones de dificultad
        for i, button in enumerate(self.difficulty_buttons):
            button.check_hover(mouse_pos)
            button.draw(self.display)
            
            if mouse_click and button.is_clicked(mouse_pos, True):
                self.selected_speed_index = i
                global SPEED
                SPEED = SPEED_OPTIONS[i]
        
        # Verificar interacción con botón de volver
        self.back_button.check_hover(mouse_pos)
        self.back_button.draw(self.display)
        
        if mouse_click and self.back_button.is_clicked(mouse_pos, True):
            self.game_state = GameState.MENU
        
        # Mostrar la dificultad actual seleccionada
        current_difficulty = f"{'Muy fácil' if self.selected_speed_index == 0 else 'Fácil' if self.selected_speed_index == 1 else 'Normal' if self.selected_speed_index == 2 else 'Difícil' if self.selected_speed_index == 3 else 'Muy difícil'}"
        difficulty_text = font.render(f"Dificultad actual: {current_difficulty}", True, WHITE)
        difficulty_rect = difficulty_text.get_rect(center=(self.w // 2, 410))
        self.display.blit(difficulty_text, difficulty_rect)
        
        pygame.display.flip()
    
    def render_color_select_screen(self, mouse_pos, mouse_click):
        """
        Renderiza la pantalla de selección de color para la serpiente
        y maneja las interacciones con los botones.
        
        Args:
            mouse_pos (tuple): Posición actual del ratón
            mouse_click (bool): Si se ha hecho click en este frame
        """
        # Dibujar el fondo con cuadrícula
        self.display.blit(self.background, (0, 0))
        
        # Mostrar título
        title_text = title_font.render("COLOR DE SERPIENTE", True, WHITE)
        title_rect = title_text.get_rect(center=(self.w // 2, 60))
        self.display.blit(title_text, title_rect)
        
        # Verificar interacciones con botones de color
        for i, button in enumerate(self.color_buttons):
            button.check_hover(mouse_pos)
            button.draw(self.display)
            
            # Marcar el color seleccionado
            if i == self.selected_color_index:
                pygame.draw.rect(self.display, WHITE, button.rect, 3, border_radius=10)
                
            if mouse_click and button.is_clicked(mouse_pos, True):
                self.selected_color_index = i
        
        # Verificar interacción con botón de volver
        self.back_button.check_hover(mouse_pos)
        self.back_button.draw(self.display)
        
        if mouse_click and self.back_button.is_clicked(mouse_pos, True):
            self.game_state = GameState.MENU
            
        # Dibujar una vista previa de la serpiente con el color seleccionado
        self.render_snake_preview()
        
        pygame.display.flip()
    
    def render_snake_preview(self):
        """
        Renderiza una vista previa de la serpiente con el color seleccionado
        a la derecha de los botones de selección de color.
        """
        # Posición para la vista previa - ahora más a la derecha
        preview_x = self.w * 0.85  # 75% del ancho de la pantalla
        preview_y = self.h * 0.5   # Mitad de la altura de la pantalla
        
        # Obtener colores seleccionados
        color_primary = SNAKE_COLORS[self.selected_color_index]["primary"]
        color_secondary = SNAKE_COLORS[self.selected_color_index]["secondary"]
        
        # Dibujar texto de vista previa
        preview_text = font.render("Vista previa:", True, WHITE)
        preview_rect = preview_text.get_rect(center=(preview_x, preview_y - 40))
        self.display.blit(preview_text, preview_rect)
        
        # Dibujar segmentos de la serpiente para la vista previa
        for i in range(5):  # 5 segmentos para la vista previa
            x = preview_x - (i * BLOCK_SIZE)
            y = preview_y
            
            # Calcular intensidad de color basada en la posición
            intensity = 1 - (i / (5 * 1.5))
            if intensity < 0.3:
                intensity = 0.3
                
            # Crear color con gradiente
            color = (int(color_primary[0] * intensity), int(color_primary[1] * intensity), int(color_primary[2] * intensity))
            inner_color = (int(color_secondary[0] * intensity), int(color_secondary[1] * intensity), int(color_secondary[2] * intensity))
            
            # Dibujar segmentos con bordes redondeados
            pygame.draw.rect(self.display, color, pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE), border_radius=3)
            pygame.draw.rect(self.display, inner_color, pygame.Rect(x+4, y+4, 12, 12), border_radius=2)
            
            # Añadir ojos a la cabeza
            if i == 0:
                eye_radius = 2
                eye_offset_x = 5
                eye_offset_y = 8
                pygame.draw.circle(self.display, WHITE, (x + BLOCK_SIZE - eye_offset_x, y + eye_offset_y), eye_radius)
                pygame.draw.circle(self.display, WHITE, (x + BLOCK_SIZE - eye_offset_x, y + BLOCK_SIZE - eye_offset_y), eye_radius)
        
        # Opcionalmente, añadir un marco alrededor de la vista previa
        preview_frame = pygame.Rect(preview_x - 60, preview_y - 70, 120, 110)
        pygame.draw.rect(self.display, GRID_COLOR, preview_frame, 1, border_radius=5)
    
    def check_timer(self):
        """
        Verifica si el temporizador inicial ha terminado.
        Actualiza el estado del juego y la UI correspondiente.
        
        Returns:
            bool: True si el temporizador sigue activo, False si ya terminó
        """
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        
        if not self.game_started:
            if elapsed_time >= TIMER_SECONDS:
                self.game_started = True
                return False
            
            # Actualizar UI para el temporizador
            self.render_timer_screen(TIMER_SECONDS - int(elapsed_time))
            self.clock.tick(60)  # FPS durante el temporizador
            return True
            
        return False
    
    def update_game_state(self):
        """
        Actualiza el estado del juego en cada frame:
        - Mueve la serpiente
        - Verifica colisiones
        - Maneja la comida
        
        Returns:
            bool: True si el juego ha terminado, False si continúa
        """
        # Mover la cabeza de la serpiente
        self.move_snake(self.direction)
        self.last_direction = self.direction  # Actualizar la última dirección
        self.snake.insert(0, self.head)
        
        # Verificar colisiones
        if self.check_collision():
            self.game_over = True
            self.game_state = GameState.GAME_OVER
            self.attempts_remaining -= 1  # Reducir el número de intentos
            self.render_game_over_screen()
            return True
            
        # Verificar si se comió la comida
        if self.head == self.food:
            self.score += 1
            self.generate_food()
        else:
            self.snake.pop()  # Solo eliminar la cola si no comió
        
        return False
        
    def check_collision(self):
        """
        Verifica si la serpiente ha colisionado con los bordes
        o consigo misma.
        
        Returns:
            bool: True si hay colisión, False si no hay
        """
        # Colisión con los bordes
        if self.head.x > self.w - BLOCK_SIZE or self.head.x < 0 or self.head.y > self.h - BLOCK_SIZE or self.head.y < 0:
            return True
        # Colisión con la propia serpiente
        if self.head in self.snake[1:]:
            return True
        
        return False
    
    def move_snake(self, direction):
        """
        Mueve la cabeza de la serpiente en la dirección especificada.
        
        Args:
            direction (Direction): La dirección en la que mover la serpiente
        """
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
            
        self.head = Point(x, y)
    
    def render_timer_screen(self, seconds_left):
        """
        Renderiza la pantalla del temporizador inicial con
        la serpiente estática y cuenta regresiva.
        
        Args:
            seconds_left (int): Segundos restantes para iniciar
        """
        # Dibujar el fondo con cuadrícula
        self.display.blit(self.background, (0, 0))
        
        # Dibujar la serpiente estática con efecto de gradiente
        self.render_snake_with_gradient()
        
        # Dibujar la comida con efectos
        self.render_food_with_effects()
        
        # Mostrar el temporizador en el centro de la pantalla con efecto de sombra
        self.render_text_with_shadow(
            f"El juego comienza en: {seconds_left}", 
            position=(self.w/2, self.h/2),
            is_centered=True
        )
        
        # Mostrar instrucciones de control con efecto de sombra
        self.render_text_with_shadow(
            "Controles: Flechas o WASD", 
            position=(self.w/2, self.h/2 + 40),
            is_centered=True
        )
        
        pygame.display.flip()
        
    def render_game_over_screen(self):
        """
        Renderiza la pantalla de game over con el mensaje
        y botones de reinicio y menú principal.
        """
        # Dibujar el fondo con cuadrícula
        self.display.blit(self.background, (0, 0))
        
        # Mostrar mensaje de fin de juego con efecto de sombra
        self.render_text_with_shadow(
            f"¡Juego terminado! Puntuación: {self.score}", 
            position=(self.w/2, self.h/2 - 60),
            is_centered=True
        )
        
        # Mostrar intentos restantes
        self.render_text_with_shadow(
            f"Intentos restantes: {self.attempts_remaining}", 
            position=(self.w/2, self.h/2 - 20),
            is_centered=True
        )
        
        # Dibujar botones
        self.restart_button.draw(self.display)
        self.menu_button.draw(self.display)
        
        pygame.display.flip()
    
    def handle_game_over(self, mouse_pos, mouse_click):
        """
        Maneja la pantalla de game over, procesa interacciones
        con botones de reinicio y menú principal.
        
        Args:
            mouse_pos (tuple): Posición actual del ratón
            mouse_click (bool): Si se ha hecho click en este frame
            
        Returns:
            bool: True para continuar, False para cambiar de estado
        """
        # Verificar interacciones con botones
        self.restart_button.check_hover(mouse_pos)
        self.menu_button.check_hover(mouse_pos)
        
        # Dibujar la pantalla de game over
        self.render_game_over_screen()
        
        # Procesar clicks
        if mouse_click:
            if self.attempts_remaining > 0 and self.restart_button.is_clicked(mouse_pos, True):
                self.reset_game()
                self.game_state = GameState.PLAYING
                return False
            elif self.menu_button.is_clicked(mouse_pos, True):
                self.game_state = GameState.MENU
                return False
                
        return True
        
    def render_game_screen(self):
        """
        Renderiza la pantalla principal del juego con la serpiente,
        comida y puntuación.
        """
        # Dibujar el fondo con cuadrícula
        self.display.blit(self.background, (0, 0))
        
        # Dibujar la serpiente con gradiente y ojos
        self.render_snake_with_gradient_and_eyes()
        
        # Dibujar la comida con efectos
        self.render_food_with_effects()
        
        # Mostrar puntuación con efecto de sombra
        self.render_text_with_shadow(
            f"Score: {self.score}", 
            position=(0, 0),
            is_centered=False
        )
        
        # Mostrar intentos restantes en la esquina superior derecha
        attempts_text = f"Intentos: {self.attempts_remaining}"
        text_width = font.size(attempts_text)[0]
        self.render_text_with_shadow(
            attempts_text,
            position=(self.w - text_width - 10, 0),
            is_centered=False
        )
        
        pygame.display.flip()
        
    def render_snake_with_gradient(self):
        """
        Renderiza la serpiente con un efecto de gradiente
        pero sin ojos (para la pantalla de temporizador).
        """
        # Obtener colores seleccionados
        color_primary = SNAKE_COLORS[self.selected_color_index]["primary"]
        color_secondary = SNAKE_COLORS[self.selected_color_index]["secondary"]
        
        for i, pt in enumerate(self.snake):
            # Calcular intensidad de color basada en la posición
            intensity = 1 - (i / (len(self.snake) * 1.5))
            if intensity < 0.3:
                intensity = 0.3
                
            # Crear color con gradiente
            color = (int(color_primary[0] * intensity), int(color_primary[1] * intensity), int(color_primary[2] * intensity))
            inner_color = (int(color_secondary[0] * intensity), int(color_secondary[1] * intensity), int(color_secondary[2] * intensity))
            
            # Dibujar segmento con bordes redondeados
            pygame.draw.rect(self.display, color, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE), border_radius=3)
            pygame.draw.rect(self.display, inner_color, pygame.Rect(pt.x+4, pt.y+4, 12, 12), border_radius=2)
    
    def render_snake_with_gradient_and_eyes(self):
        """
        Renderiza la serpiente con efecto de gradiente y ojos
        en la cabeza que siguen la dirección del movimiento.
        """
        # Obtener colores seleccionados
        color_primary = SNAKE_COLORS[self.selected_color_index]["primary"]
        color_secondary = SNAKE_COLORS[self.selected_color_index]["secondary"]
        
        for i, pt in enumerate(self.snake):
            # Calcular intensidad de color basada en la posición
            intensity = 1 - (i / (len(self.snake) * 1.5))
            if intensity < 0.3:
                intensity = 0.3
                
            # Crear color con gradiente
            color = (int(color_primary[0] * intensity), int(color_primary[1] * intensity), int(color_primary[2] * intensity))
            inner_color = (int(color_secondary[0] * intensity), int(color_secondary[1] * intensity), int(color_secondary[2] * intensity))
            
            # Dibujar segmento con bordes redondeados
            pygame.draw.rect(self.display, color, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE), border_radius=3)
            pygame.draw.rect(self.display, inner_color, pygame.Rect(pt.x+4, pt.y+4, 12, 12), border_radius=2)
            
            # Añadir ojos solo a la cabeza
            if i == 0:
                self.render_snake_eyes(pt)
    
    def render_snake_eyes(self, head_position):
        """
        Renderiza los ojos en la cabeza de la serpiente según la dirección.
        
        Args:
            head_position (Point): La posición de la cabeza
        """
        eye_radius = 2
        eye_offset_x = 5
        eye_offset_y = 8
        
        if self.direction == Direction.RIGHT:
            pygame.draw.circle(self.display, WHITE, (head_position.x + BLOCK_SIZE - eye_offset_x, head_position.y + eye_offset_y), eye_radius)
            pygame.draw.circle(self.display, WHITE, (head_position.x + BLOCK_SIZE - eye_offset_x, head_position.y + BLOCK_SIZE - eye_offset_y), eye_radius)
        elif self.direction == Direction.LEFT:
            pygame.draw.circle(self.display, WHITE, (head_position.x + eye_offset_x, head_position.y + eye_offset_y), eye_radius)
            pygame.draw.circle(self.display, WHITE, (head_position.x + eye_offset_x, head_position.y + BLOCK_SIZE - eye_offset_y), eye_radius)
        elif self.direction == Direction.UP:
            pygame.draw.circle(self.display, WHITE, (head_position.x + eye_offset_y, head_position.y + eye_offset_x), eye_radius)
            pygame.draw.circle(self.display, WHITE, (head_position.x + BLOCK_SIZE - eye_offset_y, head_position.y + eye_offset_x), eye_radius)
        elif self.direction == Direction.DOWN:
            pygame.draw.circle(self.display, WHITE, (head_position.x + eye_offset_y, head_position.y + BLOCK_SIZE - eye_offset_x), eye_radius)
            pygame.draw.circle(self.display, WHITE, (head_position.x + BLOCK_SIZE - eye_offset_y, head_position.y + BLOCK_SIZE - eye_offset_x), eye_radius)
    
    def render_food_with_effects(self):
        """
        Renderiza la comida con efectos de pulsación, brillo y reflejos.
        """
        # Calcular efecto de pulsación
        pulse = (math.sin(self.time * 5) + 1) / 4 + 0.75  # Valor entre 0.75 y 1.25
        food_color = (int(RED[0] * pulse), int(RED[1] * pulse), int(RED[2] * pulse))
        
        # Dibujar brillo alrededor de la comida
        glow_radius = int(BLOCK_SIZE * (1 + 0.3 * math.sin(self.time * 3)))
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*LIGHT_RED, 40), (glow_radius, glow_radius), glow_radius)
        self.display.blit(glow_surf, (self.food.x + BLOCK_SIZE//2 - glow_radius, self.food.y + BLOCK_SIZE//2 - glow_radius))
        
        # Dibujar la comida con bordes redondeados
        pygame.draw.rect(self.display, food_color, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE), border_radius=BLOCK_SIZE//2)
        pygame.draw.rect(self.display, LIGHT_RED, pygame.Rect(self.food.x+2, self.food.y+2, BLOCK_SIZE-4, BLOCK_SIZE-4), border_radius=BLOCK_SIZE//2-1)
        
        # Añadir reflejo a la comida
        highlight_pos = (self.food.x + 5, self.food.y + 5)
        highlight_size = 3
        pygame.draw.circle(self.display, WHITE, highlight_pos, highlight_size)
    
    def render_text_with_shadow(self, text, position, is_centered=False):
        """
        Renderiza texto con efecto de sombra.
        
        Args:
            text (str): El texto a mostrar
            position (tuple): Posición (x, y) donde mostrar el texto
            is_centered (bool): Si el texto debe centrarse en la posición
        """
        text_shadow = font.render(text, True, (30, 30, 30))
        text_surface = font.render(text, True, WHITE)
        
        if is_centered:
            shadow_rect = text_shadow.get_rect(center=(position[0] + 2, position[1] + 2))
            text_rect = text_surface.get_rect(center=position)
        else:
            shadow_rect = (position[0] + 2, position[1] + 2)
            text_rect = position
            
        self.display.blit(text_shadow, shadow_rect)
        self.display.blit(text_surface, text_rect)
    
    def play_step(self):
        """
        Ejecuta un paso del juego, gestionando entrada, lógica y renderizado.
        Maneja los diferentes estados del juego.
        
        Returns:
            bool: True para continuar ejecutando el juego, False para terminar
        """
        # Incrementar tiempo para animaciones
        self.time += 0.1
        
        # Obtener entradas del usuario
        quit_game, mouse_click = self.handle_input()
        if quit_game:
            return False
            
        mouse_pos = pygame.mouse.get_pos()
        
        # Manejar el estado actual del juego
        if self.game_state == GameState.MENU:
            quit_requested = self.render_menu(mouse_pos, mouse_click)
            if quit_requested:
                return False
                
        elif self.game_state == GameState.DIFFICULTY:
            self.render_difficulty_screen(mouse_pos, mouse_click)
            
        elif self.game_state == GameState.COLOR_SELECT:
            self.render_color_select_screen(mouse_pos, mouse_click)
            
        elif self.game_state == GameState.GAME_OVER:
            self.handle_game_over(mouse_pos, mouse_click)
            
        elif self.game_state == GameState.PLAYING:
            # Comprobar si hay intentos disponibles
            if self.attempts_remaining <= 0:
                self.game_state = GameState.MENU
                return True
                
            # Procesar entradas de dirección
            self.process_direction_input()
            
            # Verificar temporizador inicial
            if self.check_timer():
                return True
                
            # Actualizar estado del juego
            game_ended = self.update_game_state()
            if not game_ended:
                # Renderizar pantalla de juego
                self.render_game_screen()
            
            # Ajustar velocidad según la dificultad seleccionada
            self.clock.tick(SPEED)
        
        return True


if __name__ == '__main__':
    game = SnakeGame()
    
    # Bucle principal del juego
    running = True
    while running:
        running = game.play_step()
        
    pygame.quit()
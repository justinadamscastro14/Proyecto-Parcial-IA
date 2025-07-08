"""
Núcleo del juego - Manejo de estados y lógica principal

Autor: [Tu nombre]
Matrícula: [Tu matrícula]
"""

import pygame
import sys
from enum import Enum
from scripts.player import Player
from scripts.map import GameMap
from scripts.enemy import EnemyManager, EnemyType
from scripts.input import InputManager
from scripts.audio import AudioManager
from scripts.utils import image_loader

class GameState(Enum):
    """Estados del juego"""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    VICTORY = "victory"

class Game:
    """Clase principal del juego"""
    
    def __init__(self):
        pygame.init()
        
        # Configuración de pantalla
        self.screen_width = 800
        self.screen_height = 600
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("The Legend of Zelda - Proyecto Final")
        
        # Cargar icono
        try:
            icon = image_loader.get_image('icon.svg', (32, 32))
            pygame.display.set_icon(icon)
        except:
            pass  # Si no se puede cargar el icono, continuamos sin él
        
        # Configuración del juego
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.running = True
        self.state = GameState.MENU
        
        # Managers
        self.input_manager = InputManager()
        self.audio_manager = AudioManager()
        
        # Juego
        self.game_map = None
        self.player = None
        self.enemy_manager = None
        
        # Cámara
        self.camera_x = 0
        self.camera_y = 0
        
        # UI
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Inicializar juego
        self.new_game()
    
    def new_game(self):
        """Inicializar un nuevo juego"""
        # Crear mapa
        self.game_map = GameMap()
        
        # Crear jugador en posición de spawn
        self.player = Player(self.game_map)
        
        # Crear enemigos
        self.enemy_manager = EnemyManager(self.game_map, self.player)
        
        # Reproducir música de fondo
        self.audio_manager.play_music("background")
    
    def handle_events(self):
        """Manejar eventos del juego"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Actualizar input manager
            self.input_manager.handle_event(event)
            
            # Manejar eventos específicos del estado
            if self.state == GameState.MENU:
                self._handle_menu_events(event)
            elif self.state == GameState.PLAYING:
                self._handle_playing_events(event)
            elif self.state == GameState.PAUSED:
                self._handle_paused_events(event)
            elif self.state in [GameState.GAME_OVER, GameState.VICTORY]:
                self._handle_end_events(event)
    
    def _handle_menu_events(self, event):
        """Manejar eventos del menú"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.state = GameState.PLAYING
    
    def _handle_playing_events(self, event):
        """Manejar eventos durante el juego"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.PAUSED
    
    def _handle_paused_events(self, event):
        """Manejar eventos durante la pausa"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = GameState.PLAYING
            elif event.key == pygame.K_r:
                self.new_game()
                self.state = GameState.PLAYING
    
    def _handle_end_events(self, event):
        """Manejar eventos en pantallas de fin"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.new_game()
                self.state = GameState.PLAYING
            elif event.key == pygame.K_ESCAPE:
                self.state = GameState.MENU
    
    def update(self, dt):
        """Actualizar lógica del juego"""
        if self.state == GameState.PLAYING:
            # Actualizar input manager
            self.input_manager.update()
            
            # Actualizar jugador
            self.player.update(dt, self.input_manager)
            
            # Actualizar enemigos
            self.enemy_manager.update(dt)
            
            # Verificar colisiones jugador-enemigo
            for enemy in self.enemy_manager.enemies:
                if not enemy.is_dead and self.player.get_rect().colliderect(enemy.get_rect()):
                    if self.player.take_damage(enemy.attack_damage):
                        self.audio_manager.play_sound("hurt")
            
            # Verificar ataques del jugador
            attack_rect = self.player.get_attack_rect()
            if attack_rect and attack_rect.width > 0:
                for enemy in self.enemy_manager.enemies:
                    if not enemy.is_dead and attack_rect.colliderect(enemy.get_rect()):
                        if enemy.take_damage(self.player.attack_damage):
                            self.audio_manager.play_sound("enemy_death")
            
            # Actualizar cámara
            self._update_camera()
            
            # Verificar condiciones de fin
            if self.player.health <= 0:
                self.state = GameState.GAME_OVER
            elif self.enemy_manager.all_enemies_defeated():
                self.state = GameState.VICTORY
    
    def _update_camera(self):
        """Actualizar posición de la cámara"""
        # Centrar cámara en el jugador
        target_x = self.player.x - self.screen_width // 2
        target_y = self.player.y - self.screen_height // 2
        
        # Límites del mapa
        max_camera_x = self.game_map.width * self.game_map.tile_size - self.screen_width
        max_camera_y = self.game_map.height * self.game_map.tile_size - self.screen_height
        
        # Aplicar límites
        self.camera_x = max(0, min(target_x, max_camera_x))
        self.camera_y = max(0, min(target_y, max_camera_y))
    
    def render(self):
        """Renderizar el juego"""
        self.screen.fill((0, 0, 0))
        
        if self.state == GameState.MENU:
            self._render_menu()
        elif self.state == GameState.PLAYING:
            self._render_game()
        elif self.state == GameState.PAUSED:
            self._render_game()
            self._render_pause_overlay()
        elif self.state == GameState.GAME_OVER:
            self._render_game_over()
        elif self.state == GameState.VICTORY:
            self._render_victory()
        
        pygame.display.flip()
    
    def _render_menu(self):
        """Renderizar menú principal"""
        title = self.font.render("The Legend of Zelda", True, (255, 255, 255))
        subtitle = self.small_font.render("Proyecto Final", True, (200, 200, 200))
        start_text = self.small_font.render("Presiona SPACE para comenzar", True, (255, 255, 255))
        
        title_rect = title.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 20))
        start_rect = start_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
        
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)
        self.screen.blit(start_text, start_rect)
    
    def _render_game(self):
        """Renderizar el juego"""
        # Dibujar mapa
        self.game_map.draw(self.screen, self.camera_x, self.camera_y, self.screen_width, self.screen_height)
        
        # Dibujar jugador
        self.player.render(self.screen, self.camera_x, self.camera_y)
        
        # Dibujar enemigos
        self.enemy_manager.render(self.screen, self.camera_x, self.camera_y)
        
        # Dibujar UI
        self._render_ui()
    
    def _render_ui(self):
        """Renderizar interfaz de usuario"""
        # Barra de vida
        health_ratio = self.player.health / self.player.max_health
        health_bar_width = 200
        health_bar_height = 20
        
        # Fondo de la barra
        pygame.draw.rect(self.screen, (100, 0, 0), 
                        (10, 10, health_bar_width, health_bar_height))
        
        # Vida actual
        current_health_width = int(health_bar_width * health_ratio)
        pygame.draw.rect(self.screen, (255, 0, 0), 
                        (10, 10, current_health_width, health_bar_height))
        
        # Texto de vida
        health_text = self.small_font.render(f"Vida: {self.player.health}/{self.player.max_health}", 
                                           True, (255, 255, 255))
        self.screen.blit(health_text, (10, 35))
        
        # Contador de enemigos
        alive_enemies = sum(1 for enemy in self.enemy_manager.enemies if not enemy.is_dead)
        enemy_text = self.small_font.render(f"Enemigos: {alive_enemies}", True, (255, 255, 255))
        self.screen.blit(enemy_text, (10, 55))
    
    def _render_pause_overlay(self):
        """Renderizar overlay de pausa"""
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.font.render("PAUSA", True, (255, 255, 255))
        resume_text = self.small_font.render("ESC - Continuar | R - Reiniciar", True, (255, 255, 255))
        
        pause_rect = pause_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 20))
        resume_rect = resume_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
        
        self.screen.blit(pause_text, pause_rect)
        self.screen.blit(resume_text, resume_rect)
    
    def _render_game_over(self):
        """Renderizar pantalla de game over"""
        self.screen.fill((50, 0, 0))
        
        game_over = self.font.render("GAME OVER", True, (255, 255, 255))
        restart_text = self.small_font.render("R - Reiniciar | ESC - Menú", True, (255, 255, 255))
        
        game_over_rect = game_over.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 20))
        restart_rect = restart_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
        
        self.screen.blit(game_over, game_over_rect)
        self.screen.blit(restart_text, restart_rect)
    
    def _render_victory(self):
        """Renderizar pantalla de victoria"""
        self.screen.fill((0, 50, 0))
        
        victory = self.font.render("¡VICTORIA!", True, (255, 255, 255))
        restart_text = self.small_font.render("R - Reiniciar | ESC - Menú", True, (255, 255, 255))
        
        victory_rect = victory.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 20))
        restart_rect = restart_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
        
        self.screen.blit(victory, victory_rect)
        self.screen.blit(restart_text, restart_rect)
    
    def run(self):
        """Ejecutar el bucle principal del juego"""
        while self.running:
            # clock.tick() devuelve milisegundos, convertir a segundos
            dt = self.clock.tick(self.fps) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.render()
        
        pygame.quit()
        sys.exit() 
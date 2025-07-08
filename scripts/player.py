"""
Sistema del jugador - Manejo del personaje Link

Autor: [Tu nombre]
Matrícula: [Tu matrícula]
"""

import pygame
import math
from typing import Tuple, Optional
from scripts.input import InputManager, InputType
from .utils import image_loader

class Player:
    """Clase del jugador (Link)"""
    
    def __init__(self, game_map):
        """Inicializar el jugador"""
        self.game_map = game_map
        
        # Posición en el mundo
        spawn_x, spawn_y = game_map.get_spawn_position()
        self.x = spawn_x
        self.y = spawn_y
        
        # Posición anterior para colisiones
        self.prev_x = self.x
        self.prev_y = self.y
        
        # Estadísticas
        self.max_health = 100
        self.health = self.max_health
        self.speed = 150.0  # Píxeles por segundo
        self.attack_damage = 25
        self.attack_range = 40
        
        # Estado del jugador
        self.facing_direction = 0  # 0=abajo, 1=derecha, 2=arriba, 3=izquierda
        self.is_attacking = False
        self.attack_timer = 0.0
        self.attack_duration = 0.3
        
        # Invencibilidad temporal tras recibir daño
        self.invulnerable = False
        self.invulnerable_timer = 0.0
        self.invulnerable_duration = 1.0
        
        # Tamaño del sprite
        self.width = 24
        self.height = 24
        
        # Colores para el sprite
        self.color = (0, 255, 0)  # Verde para Link
        self.hurt_color = (255, 100, 100)  # Rojo cuando recibe daño
        
        # Items/inventario
        self.items = []
        self.selected_item = None
        
        # Efectos visuales
        self.blink_timer = 0.0
        self.blink_interval = 0.1
        
        # Cargar sprite
        self.sprite = image_loader.get_image('link.svg', (self.width, self.height))
        
        # Sword sprite for attack animation
        self.sword_sprite = image_loader.get_image('sword.svg', (40, 40))
    
    def update(self, dt: float, input_manager: InputManager):
        """Actualizar el jugador"""
        # Actualizar timers
        self.attack_timer -= dt
        if self.attack_timer <= 0:
            self.is_attacking = False
        
        self.invulnerable_timer -= dt
        if self.invulnerable_timer <= 0:
            self.invulnerable = False
        
        self.blink_timer += dt
        
        # Manejar input
        self._handle_input(input_manager, dt)
        
        # Actualizar posición
        self._update_movement(dt, input_manager)
        
        # Verificar colisiones con tiles especiales
        self._check_tile_interactions()
    
    def _handle_input(self, input_manager: InputManager, dt: float):
        """Manejar input del jugador"""
        # Ataque
        if input_manager.is_just_pressed(InputType.ATTACK) and not self.is_attacking:
            self.attack()
        
        # Usar item
        if input_manager.is_just_pressed(InputType.USE_ITEM):
            self.use_item()
    
    def _update_movement(self, dt: float, input_manager: InputManager):
        """Actualizar movimiento del jugador"""
        # Guardar posición anterior
        self.prev_x = self.x
        self.prev_y = self.y
        
        # Obtener vector de movimiento
        move_x, move_y = input_manager.get_movement_vector()
        
        # Normalizar movimiento diagonal
        if move_x != 0 and move_y != 0:
            move_x *= 0.707  # 1/sqrt(2)
            move_y *= 0.707
        
        # Actualizar dirección de facing
        if move_x > 0:
            self.facing_direction = 1  # Derecha
        elif move_x < 0:
            self.facing_direction = 3  # Izquierda
        elif move_y > 0:
            self.facing_direction = 0  # Abajo
        elif move_y < 0:
            self.facing_direction = 2  # Arriba
        
        # Calcular nueva posición
        new_x = self.x + move_x * self.speed * dt
        new_y = self.y + move_y * self.speed * dt
        
        # Verificar colisiones
        if self._can_move_to(new_x, self.y):
            self.x = new_x
        
        if self._can_move_to(self.x, new_y):
            self.y = new_y
    
    def _can_move_to(self, x: float, y: float) -> bool:
        """Verificar si el jugador puede moverse a una posición"""
        # Calcular las esquinas del jugador
        left = x - self.width // 2
        right = x + self.width // 2
        top = y - self.height // 2
        bottom = y + self.height // 2
        
        # Convertir a coordenadas de grid
        grid_left = int(left // self.game_map.tile_size)
        grid_right = int(right // self.game_map.tile_size)
        grid_top = int(top // self.game_map.tile_size)
        grid_bottom = int(bottom // self.game_map.tile_size)
        
        # Verificar todos los tiles que el jugador ocupa
        for grid_y in range(grid_top, grid_bottom + 1):
            for grid_x in range(grid_left, grid_right + 1):
                if not self.game_map.is_walkable(grid_x, grid_y):
                    return False
        
        return True
    
    def _check_tile_interactions(self):
        """Verificar interacciones con tiles especiales"""
        grid_x, grid_y = self.game_map.world_to_grid(self.x, self.y)
        tile_type = self.game_map.get_tile(grid_x, grid_y)
        
        # Interacción con cofres
        if tile_type == 5:  # CHEST
            self.collect_item(grid_x, grid_y)
            # Reemplazar cofre con pasto
            if hasattr(self.game_map, 'tiles') and 0 <= grid_y < len(self.game_map.tiles) and 0 <= grid_x < len(self.game_map.tiles[grid_y]):
                self.game_map.tiles[grid_y][grid_x] = 0  # GRASS
    
    def attack(self):
        """Ejecutar ataque"""
        if not self.is_attacking:
            self.is_attacking = True
            self.attack_timer = self.attack_duration
            
            # Reproducir sonido de ataque
            # self.audio_manager.play_sound("sword")  # Se manejará desde el juego principal
    
    def use_item(self):
        """Usar item seleccionado"""
        if self.selected_item:
            # Implementar uso de items
            pass
    
    def collect_item(self, grid_x: int, grid_y: int):
        """Recolectar un item"""
        self.items.append("health_potion")  # Item de ejemplo
        # Reproducir sonido de pickup
        # self.audio_manager.play_sound("pickup")
    
    def take_damage(self, damage: int):
        """Recibir daño"""
        if not self.invulnerable:
            self.health -= damage
            self.health = max(0, self.health)
            
            # Activar invencibilidad temporal
            self.invulnerable = True
            self.invulnerable_timer = self.invulnerable_duration
            
            # Reproducir sonido de daño
            # self.audio_manager.play_sound("hurt")
            return True
        return False
    
    def heal(self, amount: int):
        """Curarse"""
        self.health += amount
        self.health = min(self.max_health, self.health)
    
    def get_position(self) -> Tuple[float, float]:
        """Obtener posición del jugador"""
        return self.x, self.y
    
    def get_rect(self) -> pygame.Rect:
        """Obtener el rectángulo de colisión del jugador"""
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)
    
    def get_grid_position(self) -> Tuple[int, int]:
        """Obtener posición en grid del jugador"""
        return self.game_map.world_to_grid(self.x, self.y)
    
    def get_attack_rect(self) -> pygame.Rect:
        """Obtener rectángulo de ataque"""
        if not self.is_attacking:
            return pygame.Rect(0, 0, 0, 0)
        
        # Calcular posición del ataque según la dirección
        attack_x = self.x
        attack_y = self.y
        
        if self.facing_direction == 0:  # Abajo
            attack_y += self.height // 2 + self.attack_range // 2
        elif self.facing_direction == 1:  # Derecha
            attack_x += self.width // 2 + self.attack_range // 2
        elif self.facing_direction == 2:  # Arriba
            attack_y -= self.height // 2 + self.attack_range // 2
        elif self.facing_direction == 3:  # Izquierda
            attack_x -= self.width // 2 + self.attack_range // 2
        
        return pygame.Rect(attack_x - self.attack_range // 2, 
                          attack_y - self.attack_range // 2,
                          self.attack_range, self.attack_range)
    
    def render(self, screen: pygame.Surface, camera_x: int = 0, camera_y: int = 0):
        """Renderizar el jugador"""
        # Calcular posición en pantalla
        screen_x = int(self.x - camera_x - self.width // 2)
        screen_y = int(self.y - camera_y - self.height // 2)
        
        # Determinar color (parpadeo cuando está invulnerable)
        current_color = self.color
        if self.invulnerable:
            if int(self.blink_timer / self.blink_interval) % 2 == 0:
                current_color = self.hurt_color
        
        # Dibujar cuerpo del jugador
        pygame.draw.rect(screen, current_color, 
                        (screen_x, screen_y, self.width, self.height))
        
        # Dibujar dirección de facing
        center_x = screen_x + self.width // 2
        center_y = screen_y + self.height // 2
        
        # Dibujar una línea indicando la dirección
        if self.facing_direction == 0:  # Abajo
            pygame.draw.line(screen, (0, 0, 0), 
                           (center_x, center_y), 
                           (center_x, center_y + self.height // 2), 3)
        elif self.facing_direction == 1:  # Derecha
            pygame.draw.line(screen, (0, 0, 0), 
                           (center_x, center_y), 
                           (center_x + self.width // 2, center_y), 3)
        elif self.facing_direction == 2:  # Arriba
            pygame.draw.line(screen, (0, 0, 0), 
                           (center_x, center_y), 
                           (center_x, center_y - self.height // 2), 3)
        elif self.facing_direction == 3:  # Izquierda
            pygame.draw.line(screen, (0, 0, 0), 
                           (center_x, center_y), 
                           (center_x - self.width // 2, center_y), 3)
        
        # Dibujar área de ataque si está atacando
        if self.is_attacking:
            attack_rect = self.get_attack_rect()
            attack_screen_x = int(attack_rect.x - camera_x)
            attack_screen_y = int(attack_rect.y - camera_y)
            pygame.draw.rect(screen, (255, 255, 0), 
                           (attack_screen_x, attack_screen_y, 
                            attack_rect.width, attack_rect.height), 2)
        
        # Dibujar sprite
        screen.blit(self.sprite, (screen_x, screen_y))
        
        # Dibujar sword durante ataque
        if self.is_attacking:
            sword_x = screen_x
            sword_y = screen_y
            
            # Posicionar sword según dirección de ataque
            if abs(self.facing_direction - 1) % 4 == 0:  # Derecha
                sword_x += self.width
            elif abs(self.facing_direction - 3) % 4 == 0:  # Izquierda
                sword_x -= 40
            elif abs(self.facing_direction - 0) % 4 == 0:  # Abajo
                sword_y += self.height
            elif abs(self.facing_direction - 2) % 4 == 0:  # Arriba
                sword_y -= 40
            
            screen.blit(self.sword_sprite, (sword_x, sword_y))
    
    def reset(self):
        """Resetear el jugador"""
        spawn_x, spawn_y = self.game_map.get_spawn_position()
        self.x = spawn_x
        self.y = spawn_y
        self.prev_x = self.x
        self.prev_y = self.y
        
        self.health = self.max_health
        self.facing_direction = 0
        self.is_attacking = False
        self.attack_timer = 0.0
        self.invulnerable = False
        self.invulnerable_timer = 0.0
        self.items = []
        self.selected_item = None
        self.blink_timer = 0.0 
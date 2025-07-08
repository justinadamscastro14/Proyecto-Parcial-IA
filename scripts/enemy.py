"""
Sistema de enemigos - IA usando A* y Árbol de Comportamiento

Autor: [Tu nombre]
Matrícula: [Tu matrícula]
"""

import pygame
import random
import math
from typing import List, Tuple, Optional, Dict
from enum import Enum
from scripts.ai.astar import AStar
from scripts.ai.behavior_tree import (
    BehaviorTree, SelectorNode, SequenceNode, LeafNode, BlackBoard,
    NodeStatus
)
from .utils import image_loader

class EnemyType(Enum):
    """Tipos de enemigos"""
    GOBLIN = "goblin"
    SKELETON = "skeleton"
    SPIDER = "spider"

class EnemyState(Enum):
    """Estados del enemigo"""
    PATROL = "patrol"
    CHASE = "chase"
    ATTACK = "attack"
    FLEE = "flee"
    DEAD = "dead"

class Enemy:
    """Clase base para enemigos"""
    
    def __init__(self, x: int, y: int, game_map, player, enemy_type: EnemyType = EnemyType.GOBLIN):
        """Inicializar enemigo"""
        self.game_map = game_map
        self.player = player
        self.enemy_type = enemy_type
        
        # Posición
        world_x, world_y = game_map.grid_to_world(x, y)
        self.x = world_x
        self.y = world_y
        self.grid_x = x
        self.grid_y = y
        
        # Posición anterior
        self.prev_x = self.x
        self.prev_y = self.y
        
        # Estadísticas base
        self.max_health = 50
        self.health = self.max_health
        self.speed = 80.0  # Píxeles por segundo
        self.attack_damage = 15
        self.attack_range = 35
        self.vision_range = 150
        self.flee_threshold = 15  # Huir cuando la vida esté por debajo de este valor
        
        # Configurar según el tipo
        self._setup_enemy_type()
        
        # Estado
        self.state = EnemyState.PATROL
        self.facing_direction = 0  # 0=abajo, 1=derecha, 2=arriba, 3=izquierda
        self.is_attacking = False
        self.attack_timer = 0.0
        self.attack_duration = 0.5
        
        # Patrulla
        self.patrol_center = (x, y)
        self.patrol_radius = 3
        self.patrol_target = None
        self.patrol_wait_timer = 0.0
        self.patrol_wait_duration = 2.0
        
        # Pathfinding
        self.pathfinder = AStar(game_map)
        self.current_path = []
        self.path_index = 0
        self.recalculate_path_timer = 0.0
        self.recalculate_path_interval = 1.0  # Recalcular cada segundo
        
        # Sistema anti-atasco
        self.stuck_timer = 0.0
        self.stuck_threshold = 2.0  # Si no se mueve por 2 segundos
        self.last_position = (self.x, self.y)
        self.stuck_recovery_timer = 0.0
        
        # Tamaño del sprite
        self.width = 20
        self.height = 20
        
        # Efectos visuales
        self.blink_timer = 0.0
        self.blink_interval = 0.1
        self.invulnerable = False
        self.invulnerable_timer = 0.0
        self.invulnerable_duration = 0.5
        
        # IA - Crear árbol de comportamiento
        self.behavior_tree = self._create_behavior_tree()
        
        # Colores
        self.color = (255, 0, 0)  # Rojo base
        self.hurt_color = (255, 100, 100)
        self._setup_colors()
        
        # Flags
        self.is_dead = False
        self.can_see_player = False
        self.distance_to_player = 0.0
        
        # Configuración por tipo
        configs = {
            "goblin": {
                "health": 40,
                "damage": 12,
                "speed": 70,
                "size": 20,
                "detection_range": 120,
                "attack_range": 25,
                "sprite": "goblin.svg"
            },
            "skeleton": {
                "health": 60,
                "damage": 18,
                "speed": 90,
                "size": 20,
                "detection_range": 180,
                "attack_range": 80,
                "sprite": "skeleton.svg"
            },
            "spider": {
                "health": 30,
                "damage": 10,
                "speed": 100,
                "size": 20,
                "detection_range": 100,
                "attack_range": 20,
                "sprite": "spider.svg"
            }
        }
        
        config = configs.get(enemy_type.value, configs["goblin"])
        self.max_health = config["health"]
        self.health = self.max_health
        self.attack_damage = config["damage"]
        self.speed = config["speed"]
        self.width = config["size"]
        self.height = config["size"]
        self.vision_range = config["detection_range"]
        self.attack_range = config["attack_range"]
        
        # Cargar sprite
        self.sprite = image_loader.get_image(config["sprite"], (self.width, self.height))
        
        # Estado
        self.target_x = x
        self.target_y = y
        self.last_attack_time = 0
        self.attack_cooldown = 1000  # ms
        
        # Patrulla
        self.patrol_center_x = x
        self.patrol_center_y = y
        self.patrol_radius = 100
        self.patrol_target_x = x
        self.patrol_target_y = y
        
        # IA
        self.blackboard = BlackBoard()
        
        # Configurar comportamientos específicos por tipo
        if enemy_type == EnemyType.GOBLIN:
            self.behavior_tree = self._create_aggressive_behavior()
        elif enemy_type == EnemyType.SKELETON:
            self.behavior_tree = self._create_ranged_behavior()
        else:  # spider
            self.behavior_tree = self._create_ambush_behavior()
    
    def _setup_enemy_type(self):
        """Configurar enemigo según su tipo"""
        if self.enemy_type == EnemyType.GOBLIN:
            self.max_health = 40
            self.health = self.max_health
            self.speed = 70.0
            self.attack_damage = 12
            self.vision_range = 120
            self.flee_threshold = 10
        
        elif self.enemy_type == EnemyType.SKELETON:
            self.max_health = 60
            self.health = self.max_health
            self.speed = 90.0
            self.attack_damage = 18
            self.vision_range = 180
            self.flee_threshold = 5
        
        elif self.enemy_type == EnemyType.SPIDER:
            self.max_health = 30
            self.health = self.max_health
            self.speed = 100.0
            self.attack_damage = 10
            self.vision_range = 100
            self.flee_threshold = 8
    
    def _setup_colors(self):
        """Configurar colores según el tipo"""
        if self.enemy_type == EnemyType.GOBLIN:
            self.color = (0, 150, 0)  # Verde
        elif self.enemy_type == EnemyType.SKELETON:
            self.color = (200, 200, 200)  # Gris
        elif self.enemy_type == EnemyType.SPIDER:
            self.color = (100, 50, 0)  # Marrón
    
    def _create_behavior_tree(self) -> BehaviorTree:
        """Crear el árbol de comportamiento del enemigo"""
        # Usar comportamiento específico según el tipo de enemigo
        if self.enemy_type == EnemyType.GOBLIN:
            return self._create_aggressive_behavior()
        elif self.enemy_type == EnemyType.SKELETON:
            return self._create_ranged_behavior()
        else:  # spider
            return self._create_ambush_behavior()
    
    def update(self, dt: float):
        """Actualizar el enemigo"""
        if self.is_dead:
            return
        
        # Guardar dt para uso en métodos de movimiento
        self.current_dt = dt
        
        # Actualizar blackboard para comportamientos
        self.blackboard.set("player", self.player)
        self.blackboard.set("game_map", self.game_map)
        
        # Actualizar timers
        self.attack_timer -= dt
        if self.attack_timer <= 0:
            self.is_attacking = False
        
        self.invulnerable_timer -= dt
        if self.invulnerable_timer <= 0:
            self.invulnerable = False
        
        self.blink_timer += dt
        self.patrol_wait_timer -= dt
        self.recalculate_path_timer -= dt
        self.stuck_recovery_timer -= dt
        
        # Sistema anti-atasco
        self._check_stuck_status(dt)
        
        # Actualizar información del jugador
        self._update_player_info()
        
        # Ejecutar árbol de comportamiento
        self.behavior_tree.update()
        
        # Actualizar posición en grid
        self.grid_x, self.grid_y = self.game_map.world_to_grid(self.x, self.y)
    
    def _check_stuck_status(self, dt: float):
        """Verificar si el enemigo está atascado y aplicar medidas correctivas"""
        current_position = (self.x, self.y)
        
        # Calcular distancia movida desde la última posición
        distance_moved = math.sqrt(
            (current_position[0] - self.last_position[0]) ** 2 + 
            (current_position[1] - self.last_position[1]) ** 2
        )
        
        # Si se movió muy poco, incrementar timer de atasco
        if distance_moved < 2.0:  # Menos de 2 píxeles de movimiento
            self.stuck_timer += dt
        else:
            self.stuck_timer = 0.0  # Resetear timer si se está moviendo
        
        # Si está atascado por demasiado tiempo, aplicar medidas correctivas
        if self.stuck_timer > self.stuck_threshold and self.stuck_recovery_timer <= 0:
            self._unstuck_recovery()
            self.stuck_recovery_timer = 1.0  # Evitar aplicar recuperación muy frecuentemente
        
        # Actualizar última posición
        self.last_position = current_position
    
    def _unstuck_recovery(self):
        """Aplicar medidas correctivas cuando el enemigo está atascado"""
        # Intentar moverse en una dirección aleatoria
        angle = random.uniform(0, 2 * math.pi)
        distance = 32  # Un tile de distancia
        
        new_x = self.x + math.cos(angle) * distance
        new_y = self.y + math.sin(angle) * distance
        
        # Verificar si la nueva posición es válida
        if self._can_move_to(new_x, new_y):
            self.x = new_x
            self.y = new_y
        else:
            # Si no puede moverse aleatoriamente, intentar volver al centro de patrulla
            center_x, center_y = self.game_map.grid_to_world(
                self.patrol_center[0], self.patrol_center[1]
            )
            
            # Mover hacia el centro de patrulla
            dx = center_x - self.x
            dy = center_y - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance > 0:
                dx /= distance
                dy /= distance
                
                # Intentar moverse un poco hacia el centro
                test_distance = 16  # Medio tile
                test_x = self.x + dx * test_distance
                test_y = self.y + dy * test_distance
                
                if self._can_move_to(test_x, test_y):
                    self.x = test_x
                    self.y = test_y
        
        # Limpiar pathfinding para forzar recálculo
        self.current_path = []
        self.path_index = 0
        self.recalculate_path_timer = 0.0
        
        # Resetear timer de atasco
        self.stuck_timer = 0.0
    
    def _update_player_info(self):
        """Actualizar información sobre el jugador"""
        player_x, player_y = self.player.get_position()
        
        # Calcular distancia
        dx = player_x - self.x
        dy = player_y - self.y
        self.distance_to_player = math.sqrt(dx * dx + dy * dy)
        
        # Verificar línea de visión
        player_grid_x, player_grid_y = self.player.get_grid_position()
        self.can_see_player = (
            self.distance_to_player <= self.vision_range and
            self.game_map.has_line_of_sight((self.x, self.y), (player_x, player_y))
        )
    
    def _should_flee(self) -> bool:
        """Verificar si debe huir"""
        return self.health <= self.flee_threshold and self.can_see_player
    
    def _can_attack(self) -> bool:
        """Verificar si puede atacar"""
        return (self.distance_to_player <= self.attack_range and 
                self.can_see_player and 
                not self.is_attacking)
    
    def _can_see_player(self) -> bool:
        """Verificar si puede ver al jugador"""
        return self.can_see_player
    
    def _flee_action(self) -> bool:
        """Acción de huida"""
        self.state = EnemyState.FLEE
        
        # Obtener posición del jugador
        player_grid_x, player_grid_y = self.player.get_grid_position()
        
        # Buscar una posición alejada del jugador
        best_position = None
        best_distance = 0
        
        for _ in range(10):  # Intentar 10 posiciones aleatorias
            test_x = random.randint(max(0, self.grid_x - 5), min(self.game_map.width - 1, self.grid_x + 5))
            test_y = random.randint(max(0, self.grid_y - 5), min(self.game_map.height - 1, self.grid_y + 5))
            
            if self.game_map.is_valid_position(test_x, test_y):
                distance = self.game_map.get_distance(test_x, test_y, player_grid_x, player_grid_y)
                if distance > best_distance:
                    best_distance = distance
                    best_position = (test_x, test_y)
        
        if best_position:
            self._move_to_position(best_position, getattr(self, 'current_dt', 1.0 / 60.0))
            return True
        
        return False
    
    def _attack_action(self) -> bool:
        """Acción de ataque"""
        self.state = EnemyState.ATTACK
        
        if not self.is_attacking:
            self.is_attacking = True
            self.attack_timer = self.attack_duration
            
            # Calcular dirección del ataque
            player_x, player_y = self.player.get_position()
            dx = player_x - self.x
            dy = player_y - self.y
            
            if abs(dx) > abs(dy):
                self.facing_direction = 1 if dx > 0 else 3
            else:
                self.facing_direction = 0 if dy > 0 else 2
            
            return True
        
        return False
    
    def _chase_action(self) -> bool:
        """Acción de persecución"""
        self.state = EnemyState.CHASE
        
        # Recalcular camino periódicamente
        if self.recalculate_path_timer <= 0:
            player_grid_x, player_grid_y = self.player.get_grid_position()
            self.current_path = self.pathfinder.find_path(
                (self.grid_x, self.grid_y), 
                (player_grid_x, player_grid_y)
            )
            self.path_index = 0
            self.recalculate_path_timer = self.recalculate_path_interval
        
        # Seguir el camino
        if self.current_path and self.path_index < len(self.current_path):
            target_pos = self.current_path[self.path_index]
            if self._move_to_position(target_pos, getattr(self, 'current_dt', 1.0 / 60.0)):
                self.path_index += 1
            return True
        
        return False
    
    def _patrol_action(self) -> bool:
        """Acción de patrulla"""
        self.state = EnemyState.PATROL
        
        # Si no tiene objetivo de patrulla o llegó al objetivo
        if not self.patrol_target or self._reached_position(self.patrol_target):
            if self.patrol_wait_timer <= 0:
                # Elegir nuevo objetivo de patrulla
                self.patrol_target = self._get_random_patrol_position()
                self.patrol_wait_timer = self.patrol_wait_duration
            return True
        
        # Moverse hacia el objetivo de patrulla
        if self.patrol_target:
            self._move_to_position(self.patrol_target, getattr(self, 'current_dt', 1.0 / 60.0))
            return True
        
        return False
    
    def _get_random_patrol_position(self) -> Tuple[int, int]:
        """Obtener posición aleatoria para patrulla"""
        attempts = 0
        while attempts < 20:
            # Generar posición aleatoria dentro del radio de patrulla
            dx = random.randint(-self.patrol_radius, self.patrol_radius)
            dy = random.randint(-self.patrol_radius, self.patrol_radius)
            
            new_x = self.patrol_center[0] + dx
            new_y = self.patrol_center[1] + dy
            
            if self.game_map.is_valid_position(new_x, new_y):
                return (new_x, new_y)
            
            attempts += 1
        
        # Si no se encuentra posición válida, regresar al centro
        return self.patrol_center
    
    def _move_to_position(self, target_pos: Tuple[int, int], dt: float = None) -> bool:
        """Mover hacia una posición específica"""
        target_x, target_y = self.game_map.grid_to_world(target_pos[0], target_pos[1])
        
        # Calcular dirección
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < 5:  # Llegó al objetivo
            return True
        
        # Normalizar dirección
        dx /= distance
        dy /= distance
        
        # Actualizar dirección de facing
        if abs(dx) > abs(dy):
            self.facing_direction = 1 if dx > 0 else 3
        else:
            self.facing_direction = 0 if dy > 0 else 2
        
        # Usar dt real o asumir 60 FPS como fallback
        if dt is None:
            dt = 1.0 / 60.0
        
        # Mover
        move_distance = self.speed * dt
        new_x = self.x + dx * move_distance
        new_y = self.y + dy * move_distance
        
        # Verificar colisión con el rectángulo completo del enemigo
        if self._can_move_to(new_x, new_y):
            self.prev_x = self.x
            self.prev_y = self.y
            self.x = new_x
            self.y = new_y
        else:
            # Si no puede moverse directamente, intentar moverse en solo una dirección
            # Primero intentar movimiento horizontal
            test_x = self.x + dx * move_distance
            if self._can_move_to(test_x, self.y):
                self.prev_x = self.x
                self.x = test_x
            else:
                # Luego intentar movimiento vertical
                test_y = self.y + dy * move_distance
                if self._can_move_to(self.x, test_y):
                    self.prev_y = self.y
                    self.y = test_y
        
        return False
    
    def _can_move_to(self, x: float, y: float) -> bool:
        """Verificar si puede moverse a una posición considerando el tamaño completo del enemigo"""
        # Calcular las esquinas del enemigo
        left = x - self.width // 2
        right = x + self.width // 2  
        top = y - self.height // 2
        bottom = y + self.height // 2
        
        # Convertir a coordenadas de grid
        grid_left = int(left // self.game_map.tile_size)
        grid_right = int(right // self.game_map.tile_size)
        grid_top = int(top // self.game_map.tile_size)
        grid_bottom = int(bottom // self.game_map.tile_size)
        
        # Verificar todos los tiles que el enemigo ocuparía
        for grid_y in range(grid_top, grid_bottom + 1):
            for grid_x in range(grid_left, grid_right + 1):
                if not self.game_map.is_walkable(grid_x, grid_y):
                    return False
        
        return True
    
    def _reached_position(self, target_pos: Tuple[int, int]) -> bool:
        """Verificar si llegó a una posición"""
        target_x, target_y = self.game_map.grid_to_world(target_pos[0], target_pos[1])
        distance = math.sqrt((target_x - self.x) ** 2 + (target_y - self.y) ** 2)
        return distance < 10
    
    def take_damage(self, damage: int):
        """Recibir daño"""
        if not self.invulnerable and not self.is_dead:
            self.health -= damage
            self.health = max(0, self.health)
            
            # Activar invencibilidad temporal
            self.invulnerable = True
            self.invulnerable_timer = self.invulnerable_duration
            
            # Verificar muerte
            if self.health <= 0:
                self.is_dead = True
                self.state = EnemyState.DEAD
    
    def get_position(self) -> Tuple[float, float]:
        """Obtener posición del enemigo"""
        return self.x, self.y
    
    def get_grid_position(self) -> Tuple[int, int]:
        """Obtener posición en grid"""
        return self.grid_x, self.grid_y
    
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
        """Renderizar el enemigo"""
        if self.is_dead:
            return
        
        # Calcular posición en pantalla
        screen_x = int(self.x - camera_x - self.width // 2)
        screen_y = int(self.y - camera_y - self.height // 2)
        
        # Determinar color (parpadeo cuando está herido)
        current_color = self.color
        if self.invulnerable:
            if int(self.blink_timer / self.blink_interval) % 2 == 0:
                current_color = self.hurt_color
        
        # Dibujar cuerpo del enemigo
        pygame.draw.rect(screen, current_color, 
                        (screen_x, screen_y, self.width, self.height))
        
        # Dibujar borde
        pygame.draw.rect(screen, (0, 0, 0), 
                        (screen_x, screen_y, self.width, self.height), 2)
        
        # Dibujar dirección de facing
        center_x = screen_x + self.width // 2
        center_y = screen_y + self.height // 2
        
        if self.facing_direction == 0:  # Abajo
            pygame.draw.line(screen, (0, 0, 0), 
                           (center_x, center_y), 
                           (center_x, center_y + self.height // 2), 2)
        elif self.facing_direction == 1:  # Derecha
            pygame.draw.line(screen, (0, 0, 0), 
                           (center_x, center_y), 
                           (center_x + self.width // 2, center_y), 2)
        elif self.facing_direction == 2:  # Arriba
            pygame.draw.line(screen, (0, 0, 0), 
                           (center_x, center_y), 
                           (center_x, center_y - self.height // 2), 2)
        elif self.facing_direction == 3:  # Izquierda
            pygame.draw.line(screen, (0, 0, 0), 
                           (center_x, center_y), 
                           (center_x - self.width // 2, center_y), 2)
        
        # Dibujar barra de vida
        if self.health < self.max_health:
            bar_width = self.width
            bar_height = 4
            bar_x = screen_x
            bar_y = screen_y - bar_height - 2
            
            # Fondo de la barra
            pygame.draw.rect(screen, (255, 0, 0), 
                           (bar_x, bar_y, bar_width, bar_height))
            
            # Barra de vida
            health_width = int(bar_width * (self.health / self.max_health))
            pygame.draw.rect(screen, (0, 255, 0), 
                           (bar_x, bar_y, health_width, bar_height))
        
        # Dibujar área de ataque si está atacando
        if self.is_attacking:
            attack_rect = self.get_attack_rect()
            attack_screen_x = int(attack_rect.x - camera_x)
            attack_screen_y = int(attack_rect.y - camera_y)
            pygame.draw.rect(screen, (255, 0, 0), 
                           (attack_screen_x, attack_screen_y, 
                            attack_rect.width, attack_rect.height), 2)

    def _create_aggressive_behavior(self):
        """Comportamiento agresivo para goblins"""
        selector = SelectorNode("Aggressive Behavior")
        
        # Si vida baja, huir
        flee_seq = SequenceNode("Flee Sequence")
        flee_seq.add_child(LeafNode("Low Health Check", lambda: self.health < self.max_health * 0.3))
        flee_seq.add_child(LeafNode("Flee Action", self._flee_behavior))
        selector.add_child(flee_seq)
        
        # Si jugador cerca, atacar
        attack_seq = SequenceNode("Attack Sequence")
        attack_seq.add_child(LeafNode("In Range Check", lambda: self._distance_to_player() <= self.attack_range))
        attack_seq.add_child(LeafNode("Attack Action", self._attack_behavior))
        selector.add_child(attack_seq)
        
        # Si jugador detectado, perseguir
        chase_seq = SequenceNode("Chase Sequence")
        chase_seq.add_child(LeafNode("Vision Check", lambda: self._distance_to_player() <= self.vision_range))
        chase_seq.add_child(LeafNode("Chase Action", self._chase_behavior))
        selector.add_child(chase_seq)
        
        # Patrullar por defecto
        selector.add_child(LeafNode("Patrol Action", self._patrol_behavior))
        
        return BehaviorTree(selector)
    
    def _create_ranged_behavior(self):
        """Comportamiento a distancia para esqueletos"""
        selector = SelectorNode("Ranged Behavior")
        
        # Si jugador muy cerca, alejarse
        flee_seq = SequenceNode("Too Close Sequence")
        flee_seq.add_child(LeafNode("Too Close Check", lambda: self._distance_to_player() <= 40))
        flee_seq.add_child(LeafNode("Flee Action", self._flee_behavior))
        selector.add_child(flee_seq)
        
        # Si jugador en rango, atacar
        attack_seq = SequenceNode("Attack Sequence")
        attack_seq.add_child(LeafNode("In Range Check", lambda: self._distance_to_player() <= self.attack_range))
        attack_seq.add_child(LeafNode("Attack Action", self._attack_behavior))
        selector.add_child(attack_seq)
        
        # Si jugador detectado, mantener distancia
        distance_seq = SequenceNode("Maintain Distance Sequence")
        distance_seq.add_child(LeafNode("Vision Check", lambda: self._distance_to_player() <= self.vision_range))
        distance_seq.add_child(LeafNode("Maintain Distance Action", self._maintain_distance_behavior))
        selector.add_child(distance_seq)
        
        # Patrullar por defecto
        selector.add_child(LeafNode("Patrol Action", self._patrol_behavior))
        
        return BehaviorTree(selector)
    
    def _create_ambush_behavior(self):
        """Comportamiento de emboscada para arañas"""
        selector = SelectorNode("Ambush Behavior")
        
        # Si vida baja, huir
        flee_seq = SequenceNode("Low Health Sequence")
        flee_seq.add_child(LeafNode("Low Health Check", lambda: self.health < self.max_health * 0.2))
        flee_seq.add_child(LeafNode("Flee Action", self._flee_behavior))
        selector.add_child(flee_seq)
        
        # Si jugador muy cerca, atacar rápidamente
        quick_attack_seq = SequenceNode("Quick Attack Sequence")
        quick_attack_seq.add_child(LeafNode("Close Range Check", lambda: self._distance_to_player() <= self.attack_range))
        quick_attack_seq.add_child(LeafNode("Quick Attack Action", self._quick_attack_behavior))
        selector.add_child(quick_attack_seq)
        
        # Si jugador detectado, acercarse sigilosamente
        stealth_seq = SequenceNode("Stealth Sequence")
        stealth_seq.add_child(LeafNode("Vision Check", lambda: self._distance_to_player() <= self.vision_range))
        stealth_seq.add_child(LeafNode("Stealth Action", self._stealth_approach_behavior))
        selector.add_child(stealth_seq)
        
        # Patrullar por defecto
        selector.add_child(LeafNode("Patrol Action", self._patrol_behavior))
        
        return BehaviorTree(selector)
    
    def _distance_to_player(self):
        player = self.blackboard.get("player")
        if not player:
            return float('inf')
        
        dx = player.x - self.x
        dy = player.y - self.y
        return math.sqrt(dx * dx + dy * dy)
    
    def _attack_behavior(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown:
            self.last_attack_time = current_time
            
            player = self.blackboard.get("player")
            if player and self._distance_to_player() <= self.attack_range:
                # Realizar ataque
                if player.take_damage(self.attack_damage):
                    # Sonido de ataque si es necesario
                    pass
        
        return NodeStatus.SUCCESS
    
    def _quick_attack_behavior(self):
        """Ataque rápido para arañas"""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_attack_time >= self.attack_cooldown * 0.5:  # Más rápido
            self.last_attack_time = current_time
            
            player = self.blackboard.get("player")
            if player and self._distance_to_player() <= self.attack_range:
                if player.take_damage(self.attack_damage):
                    pass
        
        return NodeStatus.SUCCESS
    
    def _chase_behavior(self):
        player = self.blackboard.get("player")
        game_map = self.blackboard.get("game_map")
        
        if not player or not game_map:
            return NodeStatus.FAILURE
        
        # Usar A* para encontrar camino al jugador
        start = game_map.world_to_grid(self.x, self.y)
        goal = game_map.world_to_grid(player.x, player.y)
        
        self.current_path = self.pathfinder.find_path(start, goal, game_map)
        
        if self.current_path and len(self.current_path) > 1:
            next_pos = self.current_path[1]  # Skip current position
            world_pos = game_map.grid_to_world(next_pos[0], next_pos[1])
            self.target_x, self.target_y = world_pos
            
            return self._move_to_target(getattr(self, 'current_dt', 1.0 / 60.0))
        
        return NodeStatus.FAILURE
    
    def _flee_behavior(self):
        player = self.blackboard.get("player")
        if not player:
            return NodeStatus.FAILURE
        
        # Huir en dirección opuesta al jugador
        dx = self.x - player.x
        dy = self.y - player.y
        
        if dx != 0 or dy != 0:
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx /= length
                dy /= length
                
                self.target_x = self.x + dx * 100
                self.target_y = self.y + dy * 100
                
                return self._move_to_target(getattr(self, 'current_dt', 1.0 / 60.0))
        
        return NodeStatus.FAILURE
    
    def _maintain_distance_behavior(self):
        """Mantener distancia óptima (para esqueletos)"""
        player = self.blackboard.get("player")
        if not player:
            return NodeStatus.FAILURE
        
        optimal_distance = self.attack_range * 0.8
        current_distance = self._distance_to_player()
        
        if abs(current_distance - optimal_distance) > 10:
            dx = self.x - player.x
            dy = self.y - player.y
            
            if dx != 0 or dy != 0:
                length = math.sqrt(dx * dx + dy * dy)
                if length > 0:
                    dx /= length
                    dy /= length
                    
                    if current_distance < optimal_distance:
                        # Alejarse
                        self.target_x = self.x + dx * 50
                        self.target_y = self.y + dy * 50
                    else:
                        # Acercarse
                        self.target_x = self.x - dx * 30
                        self.target_y = self.y - dy * 30
                    
                    return self._move_to_target(getattr(self, 'current_dt', 1.0 / 60.0))
        
        return NodeStatus.SUCCESS
    
    def _stealth_approach_behavior(self):
        """Acercarse sigilosamente (para arañas)"""
        return self._chase_behavior()  # Por ahora igual que chase
    
    def _patrol_behavior(self):
        # Si estamos cerca del objetivo de patrulla, elegir uno nuevo
        dx = self.x - self.patrol_target_x
        dy = self.y - self.patrol_target_y
        if math.sqrt(dx * dx + dy * dy) < 20:
            # Elegir nuevo punto de patrulla
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(30, self.patrol_radius)
            
            self.patrol_target_x = self.patrol_center_x + math.cos(angle) * distance
            self.patrol_target_y = self.patrol_center_y + math.sin(angle) * distance
        
        self.target_x = self.patrol_target_x
        self.target_y = self.patrol_target_y
        
        return self._move_to_target(getattr(self, 'current_dt', 1.0 / 60.0))
    
    def _move_to_target(self, dt: float = None):
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 5:  # Threshold to avoid jittering
            # Normalize movement vector
            dx /= distance
            dy /= distance
            
            # Usar dt real o asumir 60 FPS como fallback
            if dt is None:
                dt = 1.0 / 60.0
            
            # Move towards target
            new_x = self.x + dx * self.speed * dt
            new_y = self.y + dy * self.speed * dt
            
            # Verificar colisión con el rectángulo completo del enemigo
            if self._can_move_to(new_x, new_y):
                self.x = new_x
                self.y = new_y
            else:
                # Si no puede moverse directamente, intentar moverse en solo una dirección
                # Primero intentar movimiento horizontal
                test_x = self.x + dx * self.speed * dt
                if self._can_move_to(test_x, self.y):
                    self.x = test_x
                else:
                    # Luego intentar movimiento vertical
                    test_y = self.y + dy * self.speed * dt
                    if self._can_move_to(self.x, test_y):
                        self.y = test_y
            
            return NodeStatus.RUNNING
        
        return NodeStatus.SUCCESS
    

    
    def take_damage(self, damage):
        if not self.is_dead:
            self.health -= damage
            if self.health <= 0:
                self.is_dead = True
                return True  # Enemy died
        return False
    
    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)
    
    def draw(self, screen, camera_x=0, camera_y=0):
        if self.is_dead:
            return
        
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Draw enemy sprite
        screen.blit(self.sprite, (screen_x, screen_y))
        
        # Draw health bar
        if self.health < self.max_health:
            bar_width = self.width
            bar_height = 4
            bar_x = screen_x
            bar_y = screen_y - 8
            
            # Background
            pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            
            # Health
            health_width = int(bar_width * (self.health / self.max_health))
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))
        
        # Debug: draw detection range (opcional)
        # pygame.draw.circle(screen, (255, 255, 0), 
        #                   (int(screen_x + self.width//2), int(screen_y + self.width//2)), 
        #                   self.vision_range, 1)

class EnemyManager:
    """Gestor de enemigos"""
    
    def __init__(self, game_map, player):
        """Inicializar gestor de enemigos"""
        self.game_map = game_map
        self.player = player
        self.enemies: List[Enemy] = []
        
        # Crear enemigos en los spawns
        self._spawn_enemies()
    
    def _spawn_enemies(self):
        """Crear enemigos en las posiciones de spawn"""
        # Crear varios enemigos en posiciones aleatorias
        for i in range(6):
            enemy_pos = self.game_map.get_random_free_position()
            enemy_type = list(EnemyType)[i % len(EnemyType)]
            enemy = Enemy(enemy_pos[0], enemy_pos[1], self.game_map, self.player, enemy_type)
            self.enemies.append(enemy)
    
    def update(self, dt: float):
        """Actualizar todos los enemigos"""
        for enemy in self.enemies:
            if not enemy.is_dead:
                enemy.update(dt)
        
        # Verificar ataques enemigos vs jugador
        self._check_enemy_attacks()
        
        # Verificar ataques jugador vs enemigos
        self._check_player_attacks()
    
    def _check_enemy_attacks(self):
        """Verificar ataques de enemigos contra el jugador"""
        for enemy in self.enemies:
            if enemy.is_attacking and not enemy.is_dead:
                enemy_attack_rect = enemy.get_attack_rect()
                player_rect = pygame.Rect(
                    self.player.x - self.player.width // 2,
                    self.player.y - self.player.height // 2,
                    self.player.width,
                    self.player.height
                )
                
                if enemy_attack_rect.colliderect(player_rect):
                    self.player.take_damage(enemy.attack_damage)
    
    def _check_player_attacks(self):
        """Verificar ataques del jugador contra enemigos"""
        if self.player.is_attacking:
            player_attack_rect = self.player.get_attack_rect()
            
            for enemy in self.enemies:
                if not enemy.is_dead:
                    enemy_rect = pygame.Rect(
                        enemy.x - enemy.width // 2,
                        enemy.y - enemy.height // 2,
                        enemy.width,
                        enemy.height
                    )
                    
                    if player_attack_rect.colliderect(enemy_rect):
                        enemy.take_damage(self.player.attack_damage)
    
    def render(self, screen: pygame.Surface, camera_x: int = 0, camera_y: int = 0):
        """Renderizar todos los enemigos"""
        for enemy in self.enemies:
            enemy.render(screen, camera_x, camera_y)
    
    def get_enemy_count(self) -> int:
        """Obtener número de enemigos vivos"""
        return len([enemy for enemy in self.enemies if not enemy.is_dead])
    
    def all_enemies_defeated(self) -> bool:
        """Verificar si todos los enemigos están derrotados"""
        return self.get_enemy_count() == 0
    
    def reset(self):
        """Resetear todos los enemigos"""
        self.enemies.clear()
        self._spawn_enemies() 
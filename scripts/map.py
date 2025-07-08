"""
Sistema de mapas - Manejo de tiles y colisiones

Autor: [Tu nombre]
Matrícula: [Tu matrícula]
"""

import pygame
import random
import math
from typing import List, Tuple, Optional
from .utils import image_loader

class TileType:
    """Tipos de tiles en el mapa"""
    GRASS = 0
    WALL = 1
    WATER = 2
    TREE = 3
    ROCK = 4
    CHEST = 5
    SPAWN = 6

class GameMap:
    """Clase para manejar el mapa del juego"""
    
    def __init__(self, width: int = 50, height: int = 50):
        """Inicializar el mapa"""
        self.width = width
        self.height = height
        self.tile_size = 32
        self.tiles = []
        self.chests = []
        self.spawn_points = []
        
        # Cargar tileset
        self.tileset = image_loader.load_tileset()
        
        # Tipos de tiles
        self.GRASS = 0
        self.WALL = 1
        self.WATER = 2
        self.TREE = 3
        self.ROCK = 4
        self.CHEST = 5
        self.SPAWN = 6
        
        # Mapeo de tipos a nombres de tiles
        self.tile_names = {
            self.GRASS: 'grass',
            self.WALL: 'wall',
            self.WATER: 'water',
            self.TREE: 'tree',
            self.ROCK: 'rock',
            self.CHEST: 'chest',
            self.SPAWN: 'spawn'
        }
        
        self.generate_map()
    
    def generate_map(self):
        """Genera un mapa procedural"""
        # Inicializar con pasto
        self.tiles = [[self.GRASS for _ in range(self.width)] for _ in range(self.height)]
        
        # Bordes del mapa
        for x in range(self.width):
            self.tiles[0][x] = self.WALL
            self.tiles[self.height-1][x] = self.WALL
        for y in range(self.height):
            self.tiles[y][0] = self.WALL
            self.tiles[y][self.width-1] = self.WALL
        
        # Generar características del mapa
        self._generate_walls()
        self._generate_water()
        self._generate_trees()
        self._generate_rocks()
        self._generate_chests()
        self._place_spawn_point()
    
    def _generate_walls(self):
        """Genera paredes interiores"""
        num_walls = random.randint(5, 10)
        
        for _ in range(num_walls):
            if random.choice([True, False]):
                # Pared horizontal
                length = random.randint(3, 8)
                start_x = random.randint(2, self.width - length - 2)
                start_y = random.randint(2, self.height - 3)
                
                for i in range(length):
                    if start_x + i < self.width - 1:
                        self.tiles[start_y][start_x + i] = self.WALL
            else:
                # Pared vertical
                length = random.randint(3, 8)
                start_x = random.randint(2, self.width - 3)
                start_y = random.randint(2, self.height - length - 2)
                
                for i in range(length):
                    if start_y + i < self.height - 1:
                        self.tiles[start_y + i][start_x] = self.WALL
    
    def _generate_water(self):
        """Genera cuerpos de agua"""
        num_water_areas = random.randint(1, 3)
        
        for _ in range(num_water_areas):
            center_x = random.randint(5, self.width - 5)
            center_y = random.randint(5, self.height - 5)
            radius = random.randint(2, 4)
            
            for y in range(max(1, center_y - radius), min(self.height - 1, center_y + radius + 1)):
                for x in range(max(1, center_x - radius), min(self.width - 1, center_x + radius + 1)):
                    if (x - center_x)**2 + (y - center_y)**2 <= radius**2:
                        if self.tiles[y][x] == self.GRASS:
                            self.tiles[y][x] = self.WATER
    
    def _generate_trees(self):
        """Genera árboles"""
        num_trees = random.randint(15, 25)
        
        for _ in range(num_trees):
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            
            if self.tiles[y][x] == self.GRASS:
                self.tiles[y][x] = self.TREE
    
    def _generate_rocks(self):
        """Genera rocas"""
        num_rocks = random.randint(10, 20)
        
        for _ in range(num_rocks):
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            
            if self.tiles[y][x] == self.GRASS:
                self.tiles[y][x] = self.ROCK
    
    def _generate_chests(self):
        """Genera cofres del tesoro"""
        num_chests = random.randint(3, 6)
        
        for _ in range(num_chests):
            attempts = 0
            while attempts < 50:
                x = random.randint(3, self.width - 4)
                y = random.randint(3, self.height - 4)
                
                # Verificar que el área esté libre
                area_clear = True
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        if self.tiles[y + dy][x + dx] != self.GRASS:
                            area_clear = False
                            break
                    if not area_clear:
                        break
                
                if area_clear:
                    self.tiles[y][x] = self.CHEST
                    self.chests.append({'x': x, 'y': y, 'opened': False})
                    break
                
                attempts += 1
    
    def _place_spawn_point(self):
        """Coloca el punto de spawn del jugador"""
        # Buscar un lugar libre cerca del centro
        center_x = self.width // 2
        center_y = self.height // 2
        
        for radius in range(1, 10):
            for angle in range(0, 360, 30):
                x = center_x + int(radius * math.cos(math.radians(angle)))
                y = center_y + int(radius * math.sin(math.radians(angle)))
                
                if (0 < x < self.width - 1 and 0 < y < self.height - 1 and 
                    self.tiles[y][x] == self.GRASS):
                    self.tiles[y][x] = self.SPAWN
                    self.spawn_points.append((x, y))
                    return
        
        # Si no se encuentra lugar, usar el centro
        if self.tiles[center_y][center_x] in [self.GRASS, self.SPAWN]:
            self.tiles[center_y][center_x] = self.SPAWN
            self.spawn_points.append((center_x, center_y))
    
    def get_spawn_position(self):
        """Retorna la posición de spawn en coordenadas del mundo"""
        if self.spawn_points:
            grid_x, grid_y = self.spawn_points[0]
            return self.grid_to_world(grid_x, grid_y)
        return (self.width * self.tile_size // 2, self.height * self.tile_size // 2)
    
    def world_to_grid(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Convertir coordenadas del mundo a coordenadas de grid"""
        grid_x = int(world_x // self.tile_size)
        grid_y = int(world_y // self.tile_size)
        return grid_x, grid_y
    
    def grid_to_world(self, grid_x: int, grid_y: int) -> Tuple[float, float]:
        """Convertir coordenadas de grid a coordenadas del mundo"""
        world_x = grid_x * self.tile_size + self.tile_size // 2
        world_y = grid_y * self.tile_size + self.tile_size // 2
        return world_x, world_y
    
    def get_tile(self, grid_x: int, grid_y: int) -> int:
        """Obtiene el tipo de tile en las coordenadas de grid"""
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            return self.tiles[grid_y][grid_x]
        return self.WALL  # Fuera de límites es pared
    
    def is_walkable(self, grid_x: int, grid_y: int) -> bool:
        """Verifica si una posición de grid es caminable"""
        tile = self.get_tile(grid_x, grid_y)
        return tile in [self.GRASS, self.SPAWN]
    
    def check_collision(self, world_x: float, world_y: float, size: float) -> bool:
        """Verifica colisión en coordenadas del mundo"""
        # Verificar las 4 esquinas del objeto
        corners = [
            (world_x, world_y),
            (world_x + size, world_y),
            (world_x, world_y + size),
            (world_x + size, world_y + size)
        ]
        
        for corner_x, corner_y in corners:
            grid_x, grid_y = self.world_to_grid(corner_x, corner_y)
            if not self.is_walkable(grid_x, grid_y):
                return True
        
        return False
    
    def has_line_of_sight(self, start_pos: Tuple[float, float], end_pos: Tuple[float, float]) -> bool:
        """Verifica si hay línea de visión entre dos puntos"""
        start_grid = self.world_to_grid(start_pos[0], start_pos[1])
        end_grid = self.world_to_grid(end_pos[0], end_pos[1])
        
        # Algoritmo de línea de Bresenham simplificado
        x0, y0 = start_grid
        x1, y1 = end_grid
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        x, y = x0, y0
        
        while True:
            if not self.is_walkable(x, y):
                return False
            
            if x == x1 and y == y1:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        
        return True
    
    def get_chest_at_position(self, world_x: float, world_y: float, range_size: float) -> Optional[Tuple[int, int]]:
        """Busca un cofre cerca de la posición dada"""
        grid_x, grid_y = self.world_to_grid(world_x, world_y)
        
        # Buscar en un área pequeña alrededor
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                check_x = grid_x + dx
                check_y = grid_y + dy
                
                if self.get_tile(check_x, check_y) == self.CHEST:
                    chest_world_x, chest_world_y = self.grid_to_world(check_x, check_y)
                    distance = math.sqrt((world_x - chest_world_x)**2 + (world_y - chest_world_y)**2)
                    
                    if distance <= range_size:
                        return (check_x, check_y)
        
        return None
    
    def open_chest(self, grid_x: int, grid_y: int) -> bool:
        """Abre un cofre"""
        for chest in self.chests:
            if chest['x'] == grid_x and chest['y'] == grid_y and not chest['opened']:
                chest['opened'] = True
                # Cambiar el tile de vuelta a pasto
                self.tiles[grid_y][grid_x] = self.GRASS
                return True
        return False
    
    def draw(self, screen: pygame.Surface, camera_x: int = 0, camera_y: int = 0, screen_width: int = 800, screen_height: int = 600):
        """Dibuja el mapa visible en pantalla"""
        # Calcular qué tiles son visibles
        start_x = max(0, int(camera_x // self.tile_size))
        start_y = max(0, int(camera_y // self.tile_size))
        end_x = min(self.width, int((camera_x + screen_width) // self.tile_size) + 1)
        end_y = min(self.height, int((camera_y + screen_height) // self.tile_size) + 1)
        
        # Dibujar tiles visibles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_type = self.tiles[y][x]
                tile_name = self.tile_names.get(tile_type, 'grass')
                
                if tile_name in self.tileset:
                    world_x = x * self.tile_size
                    world_y = y * self.tile_size
                    screen_x = world_x - camera_x
                    screen_y = world_y - camera_y
                    
                    screen.blit(self.tileset[tile_name], (screen_x, screen_y))
    
    def reset(self):
        """Resetear el mapa"""
        self.generate_map()
    
    def get_random_free_position(self) -> Tuple[int, int]:
        """Obtener una posición libre aleatoria"""
        attempts = 0
        while attempts < 100:
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            
            if self.is_walkable(x, y):
                return x, y
            
            attempts += 1
        
        # Fallback: retornar posición de spawn
        if self.spawn_points:
            return self.spawn_points[0]
        return (self.width // 2, self.height // 2) 
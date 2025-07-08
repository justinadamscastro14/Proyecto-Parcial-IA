"""
Algoritmo A* para pathfinding - Implementación desde cero

Autor: [Tu nombre]
Matrícula: [Tu matrícula]
"""

import heapq
from typing import List, Tuple, Optional, Set, Dict
import math

class Node:
    """Nodo para el algoritmo A*"""
    
    def __init__(self, position: Tuple[int, int], parent: Optional['Node'] = None):
        """Inicializar nodo"""
        self.position = position
        self.parent = parent
        
        # Costos del algoritmo A*
        self.g_cost = 0.0  # Costo desde el inicio
        self.h_cost = 0.0  # Heurística (distancia estimada al objetivo)
        self.f_cost = 0.0  # Costo total (g + h)
    
    def calculate_f_cost(self):
        """Calcular el costo total f"""
        self.f_cost = self.g_cost + self.h_cost
    
    def __lt__(self, other):
        """Comparación para la cola de prioridad"""
        return self.f_cost < other.f_cost
    
    def __eq__(self, other):
        """Comparación de igualdad"""
        return self.position == other.position
    
    def __hash__(self):
        """Hash para usar en sets"""
        return hash(self.position)

class AStar:
    """Implementación del algoritmo A*"""
    
    def __init__(self, game_map):
        """Inicializar A*"""
        self.game_map = game_map
        
        # Direcciones de movimiento (4 direcciones: arriba, abajo, izquierda, derecha)
        self.directions = [
            (0, -1),  # Arriba
            (0, 1),   # Abajo
            (-1, 0),  # Izquierda
            (1, 0)    # Derecha
        ]
        
        # Permitir movimiento diagonal (comentar para solo 4 direcciones)
        self.directions.extend([
            (-1, -1),  # Arriba-izquierda
            (1, -1),   # Arriba-derecha
            (-1, 1),   # Abajo-izquierda
            (1, 1)     # Abajo-derecha
        ])
    
    def heuristic(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calcular heurística (distancia estimada)"""
        # Distancia euclidiana
        dx = abs(pos1[0] - pos2[0])
        dy = abs(pos1[1] - pos2[1])
        return math.sqrt(dx * dx + dy * dy)
    
    def get_movement_cost(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> float:
        """Calcular costo de movimiento entre dos posiciones"""
        dx = abs(to_pos[0] - from_pos[0])
        dy = abs(to_pos[1] - from_pos[1])
        
        # Movimiento diagonal cuesta más
        if dx == 1 and dy == 1:
            return 1.414  # sqrt(2)
        else:
            return 1.0
    
    def get_neighbors(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Obtener vecinos válidos de una posición"""
        neighbors = []
        x, y = position
        
        for dx, dy in self.directions:
            new_x = x + dx
            new_y = y + dy
            
            # Verificar que esté dentro del mapa y no sea un obstáculo
            if self.game_map.is_valid_position(new_x, new_y):
                neighbors.append((new_x, new_y))
        
        return neighbors
    
    def reconstruct_path(self, node: Node) -> List[Tuple[int, int]]:
        """Reconstruir el camino desde el nodo objetivo"""
        path = []
        current = node
        
        while current is not None:
            path.append(current.position)
            current = current.parent
        
        # Invertir el camino (estaba desde objetivo a inicio)
        path.reverse()
        return path
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int], 
                  max_iterations: int = 1000) -> Optional[List[Tuple[int, int]]]:
        """
        Encontrar camino usando A*
        
        Args:
            start: Posición de inicio
            goal: Posición objetivo
            max_iterations: Máximo número de iteraciones (prevenir bucles infinitos)
            
        Returns:
            Lista de posiciones del camino, o None si no se encuentra
        """
        # Verificar que start y goal sean válidos
        if not self.game_map.is_valid_position(start[0], start[1]):
            return None
        if not self.game_map.is_valid_position(goal[0], goal[1]):
            return None
        
        # Si ya estamos en el objetivo
        if start == goal:
            return [start]
        
        # Inicializar listas
        open_set = []  # Cola de prioridad con nodos a explorar
        closed_set: Set[Tuple[int, int]] = set()  # Nodos ya explorados
        
        # Diccionario para acceso rápido a nodos
        all_nodes: Dict[Tuple[int, int], Node] = {}
        
        # Crear nodo inicial
        start_node = Node(start)
        start_node.g_cost = 0
        start_node.h_cost = self.heuristic(start, goal)
        start_node.calculate_f_cost()
        
        # Agregar nodo inicial a las estructuras
        heapq.heappush(open_set, start_node)
        all_nodes[start] = start_node
        
        iterations = 0
        
        while open_set and iterations < max_iterations:
            iterations += 1
            
            # Obtener nodo con menor f_cost
            current_node = heapq.heappop(open_set)
            current_pos = current_node.position
            
            # Si llegamos al objetivo
            if current_pos == goal:
                return self.reconstruct_path(current_node)
            
            # Mover a closed set
            closed_set.add(current_pos)
            
            # Explorar vecinos
            for neighbor_pos in self.get_neighbors(current_pos):
                # Saltar si ya fue explorado
                if neighbor_pos in closed_set:
                    continue
                
                # Calcular costo g tentativo
                tentative_g_cost = (current_node.g_cost + 
                                   self.get_movement_cost(current_pos, neighbor_pos))
                
                # Obtener o crear nodo vecino
                if neighbor_pos not in all_nodes:
                    neighbor_node = Node(neighbor_pos, current_node)
                    all_nodes[neighbor_pos] = neighbor_node
                else:
                    neighbor_node = all_nodes[neighbor_pos]
                
                # Si encontramos un mejor camino
                if neighbor_pos not in [node.position for node in open_set]:
                    # Nuevo nodo
                    neighbor_node.parent = current_node
                    neighbor_node.g_cost = tentative_g_cost
                    neighbor_node.h_cost = self.heuristic(neighbor_pos, goal)
                    neighbor_node.calculate_f_cost()
                    
                    heapq.heappush(open_set, neighbor_node)
                    
                elif tentative_g_cost < neighbor_node.g_cost:
                    # Mejor camino encontrado
                    neighbor_node.parent = current_node
                    neighbor_node.g_cost = tentative_g_cost
                    neighbor_node.calculate_f_cost()
                    
                    # Reordenar heap (no hay decreaseKey en heapq)
                    # Simplemente agregamos de nuevo (el algoritmo seguirá funcionando)
                    heapq.heappush(open_set, neighbor_node)
        
        # No se encontró camino
        return None
    
    def find_path_avoiding_entity(self, start: Tuple[int, int], goal: Tuple[int, int],
                                 avoid_positions: List[Tuple[int, int]]) -> Optional[List[Tuple[int, int]]]:
        """
        Encontrar camino evitando ciertas posiciones (por ejemplo, otros enemigos)
        
        Args:
            start: Posición de inicio
            goal: Posición objetivo
            avoid_positions: Lista de posiciones a evitar
            
        Returns:
            Lista de posiciones del camino, o None si no se encuentra
        """
        # Temporalmente marcar posiciones a evitar como sólidas
        original_tiles = {}
        for pos in avoid_positions:
            if self.game_map.is_valid_position(pos[0], pos[1]):
                original_tiles[pos] = self.game_map.get_tile_at(pos[0], pos[1])
                self.game_map.set_tile_at(pos[0], pos[1], 1)  # TileType.WALL
        
        # Encontrar camino
        path = self.find_path(start, goal)
        
        # Restaurar tiles originales
        for pos, original_tile in original_tiles.items():
            self.game_map.set_tile_at(pos[0], pos[1], original_tile)
        
        return path
    
    def get_next_step(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """
        Obtener solo el siguiente paso hacia el objetivo
        
        Args:
            start: Posición actual
            goal: Posición objetivo
            
        Returns:
            Siguiente posición a moverse, o None si no hay camino
        """
        path = self.find_path(start, goal)
        
        if path and len(path) > 1:
            return path[1]  # El primer elemento es la posición actual
        
        return None
    
    def is_path_clear(self, start: Tuple[int, int], goal: Tuple[int, int]) -> bool:
        """
        Verificar si existe un camino directo entre dos puntos
        
        Args:
            start: Posición de inicio
            goal: Posición objetivo
            
        Returns:
            True si hay un camino, False en caso contrario
        """
        path = self.find_path(start, goal, max_iterations=100)
        return path is not None
    
    def get_path_length(self, start: Tuple[int, int], goal: Tuple[int, int]) -> float:
        """
        Obtener la longitud del camino entre dos puntos
        
        Args:
            start: Posición de inicio
            goal: Posición objetivo
            
        Returns:
            Longitud del camino, o infinito si no hay camino
        """
        path = self.find_path(start, goal)
        
        if not path:
            return float('inf')
        
        total_length = 0.0
        for i in range(len(path) - 1):
            total_length += self.get_movement_cost(path[i], path[i + 1])
        
        return total_length 
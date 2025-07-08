"""
Árbol de Comportamiento para IA - Implementación desde cero

Autor: [Tu nombre]
Matrícula: [Tu matrícula]
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, List, Optional, Callable
import random

class NodeStatus(Enum):
    """Estados de los nodos del árbol"""
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RUNNING = "RUNNING"

class BlackBoard:
    """Pizarra compartida para almacenar datos entre nodos"""
    
    def __init__(self):
        """Inicializar la pizarra"""
        self.data: Dict[str, Any] = {}
    
    def set(self, key: str, value: Any):
        """Establecer un valor"""
        self.data[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtener un valor"""
        return self.data.get(key, default)
    
    def has(self, key: str) -> bool:
        """Verificar si existe una clave"""
        return key in self.data
    
    def clear(self):
        """Limpiar la pizarra"""
        self.data.clear()

class BehaviorNode(ABC):
    """Nodo base del árbol de comportamiento"""
    
    def __init__(self, name: str = ""):
        """Inicializar el nodo"""
        self.name = name
        self.status = NodeStatus.FAILURE
        self.blackboard: Optional[BlackBoard] = None
    
    def set_blackboard(self, blackboard: BlackBoard):
        """Establecer la pizarra compartida"""
        self.blackboard = blackboard
    
    @abstractmethod
    def execute(self) -> NodeStatus:
        """Ejecutar el nodo"""
        pass
    
    def reset(self):
        """Resetear el nodo"""
        self.status = NodeStatus.FAILURE

class LeafNode(BehaviorNode):
    """Nodo hoja (acción o condición)"""
    
    def __init__(self, name: str, action: Callable[[], NodeStatus]):
        """
        Inicializar nodo hoja
        
        Args:
            name: Nombre del nodo
            action: Función que ejecuta la acción
        """
        super().__init__(name)
        self.action = action
    
    def execute(self) -> NodeStatus:
        """Ejecutar la acción"""
        try:
            self.status = self.action()
            return self.status
        except Exception as e:
            print(f"Error en nodo {self.name}: {e}")
            self.status = NodeStatus.FAILURE
            return self.status

class CompositeNode(BehaviorNode):
    """Nodo compuesto (tiene hijos)"""
    
    def __init__(self, name: str):
        """Inicializar nodo compuesto"""
        super().__init__(name)
        self.children: List[BehaviorNode] = []
    
    def add_child(self, child: BehaviorNode):
        """Agregar un hijo"""
        self.children.append(child)
        if self.blackboard:
            child.set_blackboard(self.blackboard)
    
    def set_blackboard(self, blackboard: BlackBoard):
        """Establecer la pizarra compartida"""
        super().set_blackboard(blackboard)
        for child in self.children:
            child.set_blackboard(blackboard)
    
    def reset(self):
        """Resetear el nodo y sus hijos"""
        super().reset()
        for child in self.children:
            child.reset()

class SequenceNode(CompositeNode):
    """Nodo secuencia - ejecuta hijos en orden hasta que uno falle"""
    
    def __init__(self, name: str = "Sequence"):
        """Inicializar nodo secuencia"""
        super().__init__(name)
        self.current_child = 0
    
    def execute(self) -> NodeStatus:
        """Ejecutar secuencia"""
        while self.current_child < len(self.children):
            child_status = self.children[self.current_child].execute()
            
            if child_status == NodeStatus.FAILURE:
                self.current_child = 0
                self.status = NodeStatus.FAILURE
                return self.status
            
            if child_status == NodeStatus.RUNNING:
                self.status = NodeStatus.RUNNING
                return self.status
            
            # SUCCESS - continuar con el siguiente hijo
            self.current_child += 1
        
        # Todos los hijos tuvieron éxito
        self.current_child = 0
        self.status = NodeStatus.SUCCESS
        return self.status
    
    def reset(self):
        """Resetear secuencia"""
        super().reset()
        self.current_child = 0

class SelectorNode(CompositeNode):
    """Nodo selector - ejecuta hijos hasta que uno tenga éxito"""
    
    def __init__(self, name: str = "Selector"):
        """Inicializar nodo selector"""
        super().__init__(name)
        self.current_child = 0
    
    def execute(self) -> NodeStatus:
        """Ejecutar selector"""
        while self.current_child < len(self.children):
            child_status = self.children[self.current_child].execute()
            
            if child_status == NodeStatus.SUCCESS:
                self.current_child = 0
                self.status = NodeStatus.SUCCESS
                return self.status
            
            if child_status == NodeStatus.RUNNING:
                self.status = NodeStatus.RUNNING
                return self.status
            
            # FAILURE - continuar con el siguiente hijo
            self.current_child += 1
        
        # Todos los hijos fallaron
        self.current_child = 0
        self.status = NodeStatus.FAILURE
        return self.status
    
    def reset(self):
        """Resetear selector"""
        super().reset()
        self.current_child = 0

class ParallelNode(CompositeNode):
    """Nodo paralelo - ejecuta todos los hijos simultáneamente"""
    
    def __init__(self, name: str = "Parallel", success_threshold: int = 1):
        """
        Inicializar nodo paralelo
        
        Args:
            name: Nombre del nodo
            success_threshold: Número de hijos que deben tener éxito
        """
        super().__init__(name)
        self.success_threshold = success_threshold
    
    def execute(self) -> NodeStatus:
        """Ejecutar paralelo"""
        success_count = 0
        failure_count = 0
        running_count = 0
        
        for child in self.children:
            child_status = child.execute()
            
            if child_status == NodeStatus.SUCCESS:
                success_count += 1
            elif child_status == NodeStatus.FAILURE:
                failure_count += 1
            elif child_status == NodeStatus.RUNNING:
                running_count += 1
        
        # Verificar condiciones de éxito/fallo
        if success_count >= self.success_threshold:
            self.status = NodeStatus.SUCCESS
        elif failure_count > len(self.children) - self.success_threshold:
            self.status = NodeStatus.FAILURE
        else:
            self.status = NodeStatus.RUNNING
        
        return self.status

class DecoratorNode(BehaviorNode):
    """Nodo decorador - modifica el comportamiento de un hijo"""
    
    def __init__(self, name: str):
        """Inicializar decorador"""
        super().__init__(name)
        self.child: Optional[BehaviorNode] = None
    
    def set_child(self, child: BehaviorNode):
        """Establecer el hijo"""
        self.child = child
        if self.blackboard:
            child.set_blackboard(self.blackboard)
    
    def set_blackboard(self, blackboard: BlackBoard):
        """Establecer la pizarra compartida"""
        super().set_blackboard(blackboard)
        if self.child:
            self.child.set_blackboard(blackboard)
    
    def reset(self):
        """Resetear decorador"""
        super().reset()
        if self.child:
            self.child.reset()

class InverterNode(DecoratorNode):
    """Nodo inversor - invierte el resultado del hijo"""
    
    def __init__(self, name: str = "Inverter"):
        """Inicializar inversor"""
        super().__init__(name)
    
    def execute(self) -> NodeStatus:
        """Ejecutar inversor"""
        if not self.child:
            self.status = NodeStatus.FAILURE
            return self.status
        
        child_status = self.child.execute()
        
        if child_status == NodeStatus.SUCCESS:
            self.status = NodeStatus.FAILURE
        elif child_status == NodeStatus.FAILURE:
            self.status = NodeStatus.SUCCESS
        else:  # RUNNING
            self.status = NodeStatus.RUNNING
        
        return self.status

class RepeatNode(DecoratorNode):
    """Nodo repetidor - repite el hijo N veces"""
    
    def __init__(self, name: str = "Repeat", repeat_count: int = 1):
        """
        Inicializar repetidor
        
        Args:
            name: Nombre del nodo
            repeat_count: Número de repeticiones (-1 para infinito)
        """
        super().__init__(name)
        self.repeat_count = repeat_count
        self.current_count = 0
    
    def execute(self) -> NodeStatus:
        """Ejecutar repetidor"""
        if not self.child:
            self.status = NodeStatus.FAILURE
            return self.status
        
        while self.current_count < self.repeat_count or self.repeat_count == -1:
            child_status = self.child.execute()
            
            if child_status == NodeStatus.RUNNING:
                self.status = NodeStatus.RUNNING
                return self.status
            
            if child_status == NodeStatus.FAILURE:
                self.current_count = 0
                self.status = NodeStatus.FAILURE
                return self.status
            
            # SUCCESS - continuar o terminar
            self.current_count += 1
            if self.repeat_count != -1 and self.current_count >= self.repeat_count:
                break
            
            self.child.reset()
        
        self.current_count = 0
        self.status = NodeStatus.SUCCESS
        return self.status
    
    def reset(self):
        """Resetear repetidor"""
        super().reset()
        self.current_count = 0

class BehaviorTree:
    """Árbol de comportamiento completo"""
    
    def __init__(self, root: BehaviorNode):
        """
        Inicializar árbol de comportamiento
        
        Args:
            root: Nodo raíz del árbol
        """
        self.root = root
        self.blackboard = BlackBoard()
        self.root.set_blackboard(self.blackboard)
    
    def update(self) -> NodeStatus:
        """Actualizar el árbol"""
        return self.root.execute()
    
    def reset(self):
        """Resetear el árbol"""
        self.root.reset()
    
    def get_blackboard(self) -> BlackBoard:
        """Obtener la pizarra"""
        return self.blackboard
    
    def set_blackboard_value(self, key: str, value: Any):
        """Establecer valor en la pizarra"""
        self.blackboard.set(key, value)
    
    def get_blackboard_value(self, key: str, default: Any = None) -> Any:
        """Obtener valor de la pizarra"""
        return self.blackboard.get(key, default)

# Funciones de ayuda para crear nodos comunes
def create_condition_node(name: str, condition: Callable[[], bool]) -> LeafNode:
    """Crear nodo de condición"""
    def condition_action():
        return NodeStatus.SUCCESS if condition() else NodeStatus.FAILURE
    
    return LeafNode(name, condition_action)

def create_action_node(name: str, action: Callable[[], bool]) -> LeafNode:
    """Crear nodo de acción"""
    def action_wrapper():
        return NodeStatus.SUCCESS if action() else NodeStatus.FAILURE
    
    return LeafNode(name, action_wrapper)

def create_wait_node(name: str, duration: float) -> LeafNode:
    """Crear nodo de espera"""
    start_time = None
    
    def wait_action():
        nonlocal start_time
        import time
        
        if start_time is None:
            start_time = time.time()
        
        elapsed = time.time() - start_time
        if elapsed >= duration:
            start_time = None
            return NodeStatus.SUCCESS
        else:
            return NodeStatus.RUNNING
    
    return LeafNode(name, wait_action) 
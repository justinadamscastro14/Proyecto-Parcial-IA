"""
Sistema de manejo de input - Soporte para teclado y gamepad

Autor: [Tu nombre]
Matrícula: [Tu matrícula]
"""

import pygame
from enum import Enum

class InputType(Enum):
    """Tipos de input disponibles"""
    MOVE_UP = 0
    MOVE_DOWN = 1
    MOVE_LEFT = 2
    MOVE_RIGHT = 3
    ATTACK = 4
    USE_ITEM = 5
    PAUSE = 6
    QUIT = 7

class InputManager:
    """Gestor de input para teclado y gamepad"""
    
    def __init__(self):
        """Inicializar el gestor de input"""
        self.keys_current = pygame.key.get_pressed()
        self.keys_previous = None
        self.joystick = None
        self.joystick_buttons_current = {}
        self.joystick_buttons_previous = {}
        
        # Inicializar joystick si está disponible
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"Gamepad conectado: {self.joystick.get_name()}")
        else:
            print("No se encontró gamepad, usando teclado")
        
        # Mapeo de teclas
        self.key_mapping = {
            InputType.MOVE_UP: [pygame.K_UP, pygame.K_w],
            InputType.MOVE_DOWN: [pygame.K_DOWN, pygame.K_s],
            InputType.MOVE_LEFT: [pygame.K_LEFT, pygame.K_a],
            InputType.MOVE_RIGHT: [pygame.K_RIGHT, pygame.K_d],
            InputType.ATTACK: [pygame.K_z, pygame.K_SPACE],
            InputType.USE_ITEM: [pygame.K_x, pygame.K_LSHIFT],
            InputType.PAUSE: [pygame.K_RETURN, pygame.K_p],
            InputType.QUIT: [pygame.K_ESCAPE]
        }
        
        # Mapeo de botones de gamepad
        self.gamepad_mapping = {
            InputType.ATTACK: [0],  # Botón A
            InputType.USE_ITEM: [1],  # Botón B
            InputType.PAUSE: [7],  # Start
            InputType.QUIT: [6]  # Select
        }
        
        # Deadzone para joystick analógico
        self.deadzone = 0.3
    
    def update(self):
        """Actualizar el estado del input"""
        # Guardar estado anterior
        self.keys_previous = self.keys_current
        self.joystick_buttons_previous = self.joystick_buttons_current.copy()
        
        # Actualizar estado actual
        self.keys_current = pygame.key.get_pressed()
        
        # Actualizar estado del gamepad
        if self.joystick:
            self.joystick_buttons_current = {}
            for i in range(self.joystick.get_numbuttons()):
                self.joystick_buttons_current[i] = self.joystick.get_button(i)
    
    def handle_event(self, event):
        """Manejar eventos de pygame"""
        if event.type == pygame.JOYDEVICEADDED:
            # Gamepad conectado
            if not self.joystick:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                print(f"Gamepad conectado: {self.joystick.get_name()}")
        
        elif event.type == pygame.JOYDEVICEREMOVED:
            # Gamepad desconectado
            if self.joystick:
                self.joystick.quit()
                self.joystick = None
                print("Gamepad desconectado")
    
    def is_pressed(self, input_type):
        """Verificar si un input está presionado"""
        return self._is_key_pressed(input_type) or self._is_gamepad_pressed(input_type)
    
    def is_just_pressed(self, input_type):
        """Verificar si un input acaba de ser presionado"""
        return self._is_key_just_pressed(input_type) or self._is_gamepad_just_pressed(input_type)
    
    def is_just_released(self, input_type):
        """Verificar si un input acaba de ser liberado"""
        return self._is_key_just_released(input_type) or self._is_gamepad_just_released(input_type)
    
    def get_movement_vector(self):
        """Obtener vector de movimiento normalizado"""
        movement_x = 0
        movement_y = 0
        
        # Teclado
        if self.is_pressed(InputType.MOVE_LEFT):
            movement_x -= 1
        if self.is_pressed(InputType.MOVE_RIGHT):
            movement_x += 1
        if self.is_pressed(InputType.MOVE_UP):
            movement_y -= 1
        if self.is_pressed(InputType.MOVE_DOWN):
            movement_y += 1
        
        # Gamepad (joystick analógico)
        if self.joystick:
            axis_x = self.joystick.get_axis(0)
            axis_y = self.joystick.get_axis(1)
            
            # Aplicar deadzone
            if abs(axis_x) > self.deadzone:
                movement_x += axis_x
            if abs(axis_y) > self.deadzone:
                movement_y += axis_y
            
            # D-pad (verificar que exista) - solo si no hay movimiento analógico
            if self.joystick.get_numhats() > 0 and abs(movement_x) <= self.deadzone and abs(movement_y) <= self.deadzone:
                hat = self.joystick.get_hat(0)
                if hat[0] != 0:
                    movement_x = hat[0]
                if hat[1] != 0:
                    movement_y = -hat[1]  # Invertir Y para coincidir con coordenadas de pantalla
        
        return movement_x, movement_y
    
    def _is_key_pressed(self, input_type):
        """Verificar si una tecla está presionada"""
        if input_type in self.key_mapping:
            for key in self.key_mapping[input_type]:
                if self.keys_current[key]:
                    return True
        return False
    
    def _is_key_just_pressed(self, input_type):
        """Verificar si una tecla acaba de ser presionada"""
        if input_type in self.key_mapping:
            for key in self.key_mapping[input_type]:
                current_pressed = self.keys_current[key]
                previous_pressed = self.keys_previous[key] if self.keys_previous else False
                if current_pressed and not previous_pressed:
                    return True
        return False
    
    def _is_key_just_released(self, input_type):
        """Verificar si una tecla acaba de ser liberada"""
        if input_type in self.key_mapping:
            for key in self.key_mapping[input_type]:
                current_pressed = self.keys_current[key]
                previous_pressed = self.keys_previous[key] if self.keys_previous else False
                if not current_pressed and previous_pressed:
                    return True
        return False
    
    def _is_gamepad_pressed(self, input_type):
        """Verificar si un botón del gamepad está presionado"""
        if not self.joystick or input_type not in self.gamepad_mapping:
            return False
        
        for button in self.gamepad_mapping[input_type]:
            if self.joystick_buttons_current.get(button, False):
                return True
        return False
    
    def _is_gamepad_just_pressed(self, input_type):
        """Verificar si un botón del gamepad acaba de ser presionado"""
        if not self.joystick or input_type not in self.gamepad_mapping:
            return False
        
        for button in self.gamepad_mapping[input_type]:
            if (self.joystick_buttons_current.get(button, False) and 
                not self.joystick_buttons_previous.get(button, False)):
                return True
        return False
    
    def _is_gamepad_just_released(self, input_type):
        """Verificar si un botón del gamepad acaba de ser liberado"""
        if not self.joystick or input_type not in self.gamepad_mapping:
            return False
        
        for button in self.gamepad_mapping[input_type]:
            if (not self.joystick_buttons_current.get(button, False) and 
                self.joystick_buttons_previous.get(button, False)):
                return True
        return False 
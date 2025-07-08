"""
Sistema de audio - Manejo de sonidos y música

Autor: [Tu nombre]
Matrícula: [Tu matrícula]
"""

import pygame
import os
from typing import Dict, Optional

class AudioManager:
    """Gestor de audio para sonidos y música"""
    
    def __init__(self):
        """Inicializar el gestor de audio"""
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        # Diccionarios para almacenar sonidos y música
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_tracks: Dict[str, str] = {}
        
        # Estado de la música
        self.current_music = None
        self.music_volume = 0.7
        self.sound_volume = 0.8
        
        # Cargar archivos de audio
        self._load_audio_files()
        
        # Configurar volúmenes
        pygame.mixer.music.set_volume(self.music_volume)
    
    def _load_audio_files(self):
        """Cargar archivos de audio desde el directorio assets"""
        # Crear sonidos básicos si no existen archivos
        self._create_basic_sounds()
        
        # Intentar cargar archivos de sonido
        sounds_dir = os.path.join("assets", "sounds")
        if os.path.exists(sounds_dir):
            for filename in os.listdir(sounds_dir):
                if filename.endswith(('.wav', '.ogg', '.mp3')):
                    try:
                        sound_name = os.path.splitext(filename)[0]
                        sound_path = os.path.join(sounds_dir, filename)
                        self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
                        print(f"Sonido cargado: {sound_name}")
                    except pygame.error as e:
                        print(f"Error cargando sonido {filename}: {e}")
        
        # Intentar cargar archivos de música
        music_dir = os.path.join("assets", "music")
        if os.path.exists(music_dir):
            for filename in os.listdir(music_dir):
                if filename.endswith(('.wav', '.ogg', '.mp3')):
                    music_name = os.path.splitext(filename)[0]
                    music_path = os.path.join(music_dir, filename)
                    self.music_tracks[music_name] = music_path
                    print(f"Música cargada: {music_name}")
    
    def _create_basic_sounds(self):
        """Crear sonidos básicos usando generación procedural"""
        # Crear sonidos básicos si no existen archivos
        try:
            # Crear sonidos silenciosos básicos
            silent_buffer = b'\x00' * 1024
            
            self.sounds["sword"] = pygame.mixer.Sound(buffer=silent_buffer)
            self.sounds["hurt"] = pygame.mixer.Sound(buffer=silent_buffer)
            self.sounds["pickup"] = pygame.mixer.Sound(buffer=silent_buffer)
            self.sounds["game_over"] = pygame.mixer.Sound(buffer=silent_buffer)
            self.sounds["victory"] = pygame.mixer.Sound(buffer=silent_buffer)
            
            print("Sonidos básicos creados (silenciosos)")
        except Exception as e:
            print(f"Error generando sonidos: {e}")
            self.sounds = {}
    
    def _generate_sword_sound(self):
        """Generar sonido de espada"""
        try:
            import numpy as np
            duration = 0.3
            sample_rate = 22050
            t = np.linspace(0, duration, int(sample_rate * duration))
            
            # Generar ruido blanco filtrado
            frequency = 2000
            wave = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 10)
            wave = (wave * 32767).astype(np.int16)
            
            # Crear superficie de sonido estéreo
            stereo_wave = np.column_stack((wave, wave))
            stereo_wave = np.ascontiguousarray(stereo_wave)
            sound = pygame.sndarray.make_sound(stereo_wave)
            return sound
        except:
            # Crear sonido silencioso si hay error
            return pygame.mixer.Sound(buffer=b'\x00' * 1024)
    
    def _generate_hurt_sound(self):
        """Generar sonido de daño"""
        import numpy as np
        duration = 0.2
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Generar tono descendente
        frequency = 800 * (1 - t / duration)
        wave = np.sin(2 * np.pi * frequency * t) * np.exp(-t * 5)
        wave = (wave * 16383).astype(np.int16)
        
        sound = pygame.sndarray.make_sound(np.array([wave, wave]).T)
        return sound
    
    def _generate_pickup_sound(self):
        """Generar sonido de pickup"""
        import numpy as np
        duration = 0.15
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Generar tono ascendente
        frequency = 400 + 600 * (t / duration)
        wave = np.sin(2 * np.pi * frequency * t) * (1 - t / duration)
        wave = (wave * 16383).astype(np.int16)
        
        sound = pygame.sndarray.make_sound(np.array([wave, wave]).T)
        return sound
    
    def _generate_game_over_sound(self):
        """Generar sonido de game over"""
        import numpy as np
        duration = 1.0
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Generar secuencia de tonos descendentes
        wave = np.zeros_like(t)
        for i, freq in enumerate([400, 350, 300, 250]):
            start = i * len(t) // 4
            end = (i + 1) * len(t) // 4
            segment = t[start:end] - t[start]
            wave[start:end] = np.sin(2 * np.pi * freq * segment) * np.exp(-segment * 2)
        
        wave = (wave * 16383).astype(np.int16)
        sound = pygame.sndarray.make_sound(np.array([wave, wave]).T)
        return sound
    
    def _generate_victory_sound(self):
        """Generar sonido de victoria"""
        import numpy as np
        duration = 0.8
        sample_rate = 22050
        t = np.linspace(0, duration, int(sample_rate * duration))
        
        # Generar secuencia de tonos ascendentes
        wave = np.zeros_like(t)
        for i, freq in enumerate([400, 500, 600, 800]):
            start = i * len(t) // 4
            end = (i + 1) * len(t) // 4
            segment = t[start:end] - t[start]
            wave[start:end] = np.sin(2 * np.pi * freq * segment) * (1 - segment / 0.2)
        
        wave = (wave * 16383).astype(np.int16)
        sound = pygame.sndarray.make_sound(np.array([wave, wave]).T)
        return sound
    
    def play_sound(self, sound_name: str, volume: Optional[float] = None):
        """Reproducir un sonido"""
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            if volume is not None:
                sound.set_volume(volume)
            else:
                sound.set_volume(self.sound_volume)
            sound.play()
        else:
            print(f"Sonido no encontrado: {sound_name}")
    
    def play_music(self, music_name: str, loops: int = -1, volume: Optional[float] = None):
        """Reproducir música"""
        if music_name in self.music_tracks:
            if self.current_music != music_name:
                pygame.mixer.music.load(self.music_tracks[music_name])
                if volume is not None:
                    pygame.mixer.music.set_volume(volume)
                else:
                    pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(loops)
                self.current_music = music_name
        else:
            # Si no hay música específica, crear silencio
            print(f"Música no encontrada: {music_name}")
    
    def stop_music(self):
        """Detener la música"""
        pygame.mixer.music.stop()
        self.current_music = None
    
    def pause_music(self):
        """Pausar la música"""
        pygame.mixer.music.pause()
    
    def resume_music(self):
        """Reanudar la música"""
        pygame.mixer.music.unpause()
    
    def set_music_volume(self, volume: float):
        """Establecer volumen de la música (0.0 a 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def set_sound_volume(self, volume: float):
        """Establecer volumen de los sonidos (0.0 a 1.0)"""
        self.sound_volume = max(0.0, min(1.0, volume))
        # Actualizar volumen de todos los sonidos cargados
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)
    
    def cleanup(self):
        """Limpiar recursos de audio"""
        pygame.mixer.music.stop()
        pygame.mixer.quit() 
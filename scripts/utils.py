import pygame
import os
from pathlib import Path

class ImageLoader:
    """Utilidad para cargar imágenes y manejar SVGs"""
    
    def __init__(self):
        self.images = {}
        self.assets_path = Path(__file__).parent.parent / "assets" / "images"
    
    def load_svg_as_surface(self, filename, size=None):
        """
        Carga un SVG y lo convierte a Surface de pygame
        Si pygame no puede cargar SVG, crea un surface con color sólido como fallback
        """
        try:
            filepath = self.assets_path / filename
            if filepath.exists():
                # Intentar cargar como imagen normal
                surface = pygame.image.load(str(filepath))
                if size:
                    surface = pygame.transform.scale(surface, size)
                return surface
        except:
            pass
        
        # Fallback: crear surface con color
        if size is None:
            size = (32, 32)
        surface = pygame.Surface(size, pygame.SRCALPHA)
        
        # Colores de fallback basados en el nombre del archivo
        fallback_colors = {
            'link.svg': (0, 128, 0),
            'goblin.svg': (34, 139, 34),
            'skeleton.svg': (245, 245, 220),
            'spider.svg': (101, 67, 33),
            'icon.svg': (0, 128, 0)
        }
        
        color = fallback_colors.get(filename, (128, 128, 128))
        surface.fill(color)
        return surface
    
    def load_tileset(self):
        """Carga el tileset como surfaces individuales"""
        try:
            filepath = self.assets_path / "tileset.svg"
            if filepath.exists():
                # Intentar cargar el tileset completo
                tileset = pygame.image.load(str(filepath))
                
                # Extraer tiles individuales (32x32 cada uno)
                tiles = {}
                tile_names = ['grass', 'wall', 'water', 'tree', 'rock', 'chest', 'spawn']
                
                for i, name in enumerate(tile_names):
                    x = i * 32
                    tile_surface = pygame.Surface((32, 32))
                    tile_surface.blit(tileset, (0, 0), (x, 0, 32, 32))
                    tiles[name] = tile_surface
                
                return tiles
        except:
            pass
        
        # Fallback: crear tiles con colores sólidos
        tile_colors = {
            'grass': (34, 139, 34),
            'wall': (139, 69, 19),
            'water': (65, 105, 225),
            'tree': (0, 100, 0),
            'rock': (128, 128, 128),
            'chest': (218, 165, 32),
            'spawn': (255, 215, 0)
        }
        
        tiles = {}
        for name, color in tile_colors.items():
            surface = pygame.Surface((32, 32))
            surface.fill(color)
            tiles[name] = surface
        
        return tiles
    
    def get_image(self, filename, size=None):
        """Obtiene una imagen cargada, la carga si no existe"""
        key = f"{filename}_{size}"
        if key not in self.images:
            self.images[key] = self.load_svg_as_surface(filename, size)
        return self.images[key]

# Instancia global del cargador de imágenes
image_loader = ImageLoader() 
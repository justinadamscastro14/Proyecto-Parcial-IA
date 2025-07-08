#!/usr/bin/env python3
"""
The Legend of Zelda - Proyecto Final
Archivo principal del juego

Un juego completo inspirado en The Legend of Zelda (NES) que demuestra:
- Implementación de Árbol de Comportamiento desde cero
- Algoritmo A* implementado desde cero
- Sistema de audio y gráficas SVG
- Soporte completo para gamepad y teclado
"""

import sys
from scripts.game import Game

def main():
    """Función principal del juego"""
    print("🎮 Iniciando The Legend of Zelda - Proyecto Final...")
    print("📚 Demostrando: Árbol de Comportamiento + A* + Gráficas SVG")
    print("🎯 Controles: Flechas/WASD = Mover, Z = Atacar, ESC = Pausa")
    print("🎮 Gamepad: Se detecta automáticamente si está conectado")
    print("-" * 60)
    
    try:
        # Crear y ejecutar el juego
        # La clase Game ahora maneja toda la inicialización internamente
        game = Game()
        game.run()
        
    except KeyboardInterrupt:
        print("\n👋 Juego interrumpido por el usuario")
    except Exception as e:
        print(f"❌ Error en el juego: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("🏁 Cerrando juego...")

if __name__ == "__main__":
    main() 
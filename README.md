# Proyecto-parcial-IA

## Nombre: Justin Adams Castro mancebo

## Matrícula: 21-SISN-2-034

## Proyecto: The Legend of Zelda


# The Legend of Zelda

Un juego completo inspirado en The Legend of Zelda (NES) implementado en Python usando Pygame, que incluye implementaciones desde cero de un Árbol de Comportamiento y el algoritmo A* para la IA de enemigos.

## 🎮 Características del Juego

- **Árbol de Comportamiento**: Implementado desde cero para la IA de enemigos
- **Algoritmo A***: Implementado desde cero para pathfinding
- **Soporte para controles/gamepad**: Control completo con teclado y gamepad
- **Sonidos y música**: Sistema de audio completo (genera sonidos proceduralmente)
- **Sprites SVG**: Gráficas vectoriales escalables para todos los elementos
- **Sistema de menús**: Menú principal, pausa, game over y victoria
- **Estructura del proyecto**: Organización modular y limpia
- **Documentación**: README.md completo y archivos de instalación

### 🎯 Mecánicas de Juego
- **Jugador (Link)**: Movimiento fluido, sistema de ataque con espada, vida e invencibilidad temporal
- **Enemigos inteligentes**:
  - **Goblins**: Comportamiento agresivo, persiguen y atacan directamente
  - **Esqueletos**: Mantienen distancia óptima, ataques a distancia
  - **Arañas**: Emboscadas sigilosas, ataques rápidos
- **Mapa procedural**: Generación automática de terreno con obstáculos, agua, árboles y cofres
- **Sistema de colisiones**: Detección precisa entre jugador, enemigos y entorno
- **Pathfinding inteligente**: Los enemigos navegan obstáculos usando A*

## 🎨 Gráficas SVG

El juego incluye sprites vectoriales escalables:

### Personajes
- **Link**: Sprite del héroe con gorro verde, espada y escudo
- **Goblin**: Enemigo verde con garrote
- **Skeleton**: Esqueleto con arco
- **Spider**: Araña marrón con patrón distintivo

### Elementos del Mundo
- **Tileset completo**: Pasto, paredes, agua, árboles, rocas, cofres, spawn point
- **Items**: Espada brillante, corazones de vida, pociones de curación
- **Icono del juego**: Triforce dorado con fondo verde

### Sistema de Fallback
Si las imágenes SVG no se pueden cargar, el juego automáticamente usa colores sólidos como respaldo, garantizando que siempre sea jugable.

## 🤖 Inteligencia Artificial

### Árbol de Comportamiento (Implementación Propia)
Framework completo de Behavior Trees con:
- **Nodos Compuestos**: Selector, Secuencia, Paralelo
- **Nodos Decoradores**: Inversor, Repetidor, Límite de tiempo
- **Sistema de Pizarra**: Para compartir datos entre nodos
- **Condiciones y Acciones**: Nodos leaf personalizables

### Algoritmo A* (Implementación Propia)
Pathfinding optimizado con:
- **Heurística euclidiana** para distancias precisas
- **Movimiento en 8 direcciones** (incluye diagonales)
- **Optimización de rendimiento** con límites de iteración
- **Integración con el mapa** para evitar obstáculos

### Comportamientos por Enemigo
- **Goblin (Agresivo)**: Patrulla → Detecta → Persigue → Ataca → Huye si vida baja
- **Skeleton (A Distancia)**: Patrulla → Detecta → Mantiene distancia → Ataca → Huye si muy cerca
- **Spider (Emboscada)**: Patrulla → Detecta → Acecho sigiloso → Ataque rápido → Huye si vida crítica

## 🎮 Controles

### Teclado
- **Flechas**: Movimiento
- **Z**: Atacar/Interactuar
- **ESC**: Pausa/Menú
- **R**: Reiniciar (en pausa/game over)
- **SPACE**: Confirmar en menús

### Gamepad (Detección Automática)
- **Joystick izquierdo/D-pad**: Movimiento
- **Botón A**: Atacar/Interactuar
- **Botón Start**: Pausa/Menú
- **Botón Select**: Reiniciar

## 📁 Estructura del Proyecto

```
justin/
├── main.py                 # Punto de entrada del juego
├── requirements.txt        # Dependencias Python
├── README.md              # Este archivo
├── INSTALL.md             # Guía de instalación
├── test_graphics.py       # Prueba de gráficas SVG
├── scripts/               # Código fuente del juego
│   ├── __init__.py
│   ├── game.py           # Clase principal del juego
│   ├── player.py         # Sistema del jugador
│   ├── enemy.py          # Sistema de enemigos
│   ├── map.py            # Generación y manejo de mapas
│   ├── input.py          # Manejo de controles
│   ├── audio.py          # Sistema de sonidos
│   ├── utils.py          # Utilidades para cargar SVGs
│   └── ai/               # Algoritmos de IA
│       ├── __init__.py
│       ├── astar.py      # Algoritmo A* (implementación propia)
│       └── behavior_tree.py # Árbol de Comportamiento (implementación propia)
└── assets/               # Recursos del juego
    ├── images/           # Sprites SVG
    │   ├── icon.svg      # Icono del juego
    │   ├── link.svg      # Sprite del jugador
    │   ├── goblin.svg    # Sprite del goblin
    │   ├── skeleton.svg  # Sprite del esqueleto
    │   ├── spider.svg    # Sprite de la araña
    │   ├── tileset.svg   # Tiles del mapa
    │   ├── sword.svg     # Sprite de la espada
    │   ├── heart.svg     # Sprite de corazón
    │   ├── potion.svg    # Sprite de poción
    │   └── README.md     # Información sobre sprites
    ├── sounds/           # Efectos de sonido
    │   └── README.md     # Información sobre sonidos
    └── music/            # Música de fondo
        └── README.md     # Información sobre música
```

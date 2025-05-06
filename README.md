# Snake Game with AI

Este proyecto implementa un juego de Snake con una versión controlada por el usuario y otra versión con Inteligencia Artificial que aprende a jugar por sí misma mediante aprendizaje por refuerzo.

## Características

- Juego de Snake clásico con controles de teclado (versión `snake.py`)
- Versión con IA que aprende a jugar utilizando Q-Learning (versión `agent.py`)
- Interfaz gráfica mejorada con efectos visuales
- Sistema de dificultad configurable
- Personalización de colores para la serpiente

## Cómo ejecutar
Asegúrate de tener Python 3.11.9 instalado en tu sistema

1. Instala las dependencias:
```
pip install -r requirements.txt
```

2. Para jugar la versión manual:
```
python snake.py
```

3. Para ver la IA aprendiendo a jugar:
```
python agent.py
```
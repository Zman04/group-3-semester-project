# Vertical Ball Physics Simulation

A clean Python 3 physics simulation of a ball falling with realistic vertical motion, including gravity, air resistance, and bouncing.

## Features

- **Realistic Physics**: Implements gravity (9.81 m/s²), energy loss on bouncing
- **Smooth Visualization**: Pygame-based rendering with smooth camera following
- **Real-time Information**: Displays position, velocity, acceleration, and energy
- **Interactive Controls**: Reset ball, toggle info display, and quit functionality
- **Clean Architecture**: Modular design for easy extension and web adaptation

## Physics Implementation

The simulation includes:
- **Gravity**: Constant downward acceleration
- **Air Resistance**: Drag force proportional to velocity squared and cross-sectional area
- **Bouncing**: Energy loss on ground collision with damping factor
- **Fixed Time Step**: Consistent 60 FPS physics updates for stability

## Installation

1. Ensure you have Python 3.7+ installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the simulation:
```bash
python src/main.py
```

### Controls
- **SPACE**: Reset ball to initial position
- **I**: Toggle physics information display
- **ESC**: Quit simulation

## Project Structure

```
python-vertical-toss/
├── src/
│   └── main.py          # Main simulation code
├── assets/
│   └── circle.png       # Ball texture (future use)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Physics Classes

### PhysicsBall
- Handles individual ball physics
- Updates position, velocity, and acceleration
- Manages collision detection and response

### PhysicsSimulation
- Main simulation controller
- Handles rendering and user input
- Manages camera and UI

## Future Web Adaptation

The code is structured to be easily adaptable for web use:
- Physics calculations are separated from rendering
- Clean class interfaces
- No platform-specific dependencies in physics code

Potential web frameworks:
- Pygame-web (pygame compiled to WebAssembly)
- Pyodide (Python in browser)
- Rewrite physics in JavaScript/TypeScript

## Customization

You can easily modify physics parameters in the `PhysicsBall` class:
- `gravity`: Gravitational acceleration
- `air_resistance_coefficient`: Drag coefficient
- `bounce_damping`: Energy loss on bounce
- `mass` and `radius`: Ball properties

## Requirements

- Python 3.7+
- Pygame 2.5.0+ 
# Vertical Ball Physics Simulation

A clean Python 3 physics simulation of a ball falling with realistic vertical motion, including gravity, air resistance, and bouncing. The project has been refactored into a modular architecture with separated concerns.

## Features

- **Modular Architecture**: Separated concerns for better maintainability and testing
- **Physics Engine**: Dedicated physics module with proper state management
- **Rendering System**: Optimized rendering with texture caching
- **Time Control**: Advanced time management with history and stepping
- **GUI System**: Improved GUI with proper event handling
- **Comprehensive Testing**: Unit tests and integration tests
- **Error Handling**: Robust error handling and logging throughout

## Installation

1. Ensure you have Python 3.7+ installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the simulation:
```bash
python src/main_refactored.py
```

### Controls
- **Time Controls**: Play/Pause, Step, Custom Time Increments
- **Step Modes**: Frame-based or Time-based stepping
- **History**: Rewind functionality with state history
- **I**: Toggle info display
- **ESC**: Quit simulation

## Project Structure

```
project/
├── src/
│   ├── main_refactored.py  # Main orchestrator
│   ├── config.py           # Configuration constants
│   ├── physics.py          # Physics engine
│   ├── renderer.py         # Rendering system
│   ├── time_manager.py     # Time control
│   ├── gui.py             # GUI components
│   └── test_refactored.py # Test suite
├── assets/
│   └── circle.png         # Ball texture
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Architecture Overview

### Config Module
- Centralizes all configuration constants
- Makes the codebase more maintainable
- Eliminates magic numbers

### Physics Engine
- Handles ball physics calculations
- Manages state and collisions
- Independent of rendering and UI

### Renderer
- Optimized rendering system
- Texture caching for better performance
- Handles all visual elements

### Time Manager
- Controls simulation time flow
- Manages state history
- Provides stepping and rewind functionality

### GUI System
- Event-driven GUI components
- Clean separation from game logic
- Improved user interaction

## Testing

The project includes comprehensive tests:
- Unit tests for individual modules
- Integration tests for module interactions
- Import verification
- Physics engine validation
- Time management testing

## Requirements

- Python 3.7+
- Pygame 2.5.0+

## Future Enhancements

Planned improvements:
- Additional visual effects

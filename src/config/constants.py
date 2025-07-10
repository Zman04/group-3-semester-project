"""
Configuration Constants

Contains all configuration values and constants for the simulation.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class SimulationConfig:
    """Configuration for physics simulation."""
    
    # Simulation dimensions
    DEFAULT_WIDTH: int = 800
    DEFAULT_HEIGHT: int = 600
    GROUND_OFFSET: int = 50
    
    # Initial positions
    DEFAULT_SCREEN_START_Y: int = 100  # Near top of screen
    DEFAULT_PHYSICS_START_Y: int = 420  # Above ground in physics coordinates
    
    # Physics constants
    GRAVITY: float = 6000.0  # pixels/s²
    BOUNCE_DAMPING: float = 0.8
    MIN_BOUNCE_VELOCITY: float = 50.0
    
    # Time control
    TARGET_FPS: int = 144
    MAX_HISTORY_FRAMES: int = 500


@dataclass
class UIConfig:
    """Configuration for user interface."""
    
    # Layout
    CONTROL_PANEL_WIDTH: int = 250
    PANEL_PADDING: int = 10
    ELEMENT_SPACING: int = 40
    SECTION_SPACING: int = 50
    GRID_SPACING: int = 50
    
    # Font sizes
    DEFAULT_FONT_SIZE: int = 24
    SMALL_FONT_SIZE: int = 20
    
    # Colors (RGB tuples)
    BACKGROUND_COLOR: Tuple[int, int, int] = (0, 0, 0)
    TEXT_COLOR: Tuple[int, int, int] = (255, 255, 255)
    LABEL_COLOR: Tuple[int, int, int] = (200, 200, 200)
    HELPER_TEXT_COLOR: Tuple[int, int, int] = (150, 150, 150)
    
    # UI element colors
    BUTTON_COLOR: Tuple[int, int, int] = (150, 150, 150)
    BUTTON_PRESSED_COLOR: Tuple[int, int, int] = (100, 100, 100)
    BORDER_COLOR: Tuple[int, int, int] = (200, 200, 200)
    
    # Control panel
    CONTROL_PANEL_COLOR: Tuple[int, int, int] = (40, 40, 40)
    
    # Grid and ground
    GRID_COLOR: Tuple[int, int, int] = (105, 105, 105)
    GROUND_COLOR: Tuple[int, int, int] = (100, 100, 255)
    
    # Ball rendering
    BALL_COLOR: Tuple[int, int, int] = (255, 100, 100)
    BALL_HIGHLIGHT_COLOR: Tuple[int, int, int] = (255, 200, 200)
    SHADOW_COLOR: Tuple[int, int, int] = (0, 0, 0)


@dataclass
class LoggingConfig:
    """Configuration for logging system."""
    
    # Log levels
    DEFAULT_LEVEL: str = "INFO"
    CONSOLE_LEVEL: str = "INFO"
    FILE_LEVEL: str = "DEBUG"
    
    # File settings
    LOG_FILE: str = "simulation.log"
    MAX_LOG_SIZE: int = 1024 * 1024  # 1MB
    BACKUP_COUNT: int = 3
    
    # Format
    FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"

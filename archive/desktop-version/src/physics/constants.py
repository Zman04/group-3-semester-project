"""
Physics Constants

Physical constants and default values for the simulation.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class PhysicsConstants:
    """Physical constants for the simulation."""
    
    # Default ball properties
    DEFAULT_BALL_RADIUS: float = 20.0
    DEFAULT_BALL_MASS: float = 1.0
    DEFAULT_BALL_COLOR: Tuple[int, int, int] = (255, 100, 100)
    
    # Ball texture
    BALL_TEXTURE_PATH: str = "assets/circle.png"
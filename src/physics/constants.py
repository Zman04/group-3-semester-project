"""
Physics Constants

Physical constants and default values for the simulation.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PhysicsConstants:
    """Physical constants for the simulation."""
    
    # Default ball properties
    DEFAULT_BALL_RADIUS: float = 20.0
    DEFAULT_BALL_MASS: float = 1.0
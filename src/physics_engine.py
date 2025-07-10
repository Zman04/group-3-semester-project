"""
Refactored Physics Engine for Web Application

Uses the unified physics module with proper separation of concerns.
"""

from typing import Dict, Any
from physics import Ball
from simulation import PhysicsSimulation as BasePhysicsSimulation
from config import SimulationConfig, setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


class PhysicsSimulation(BasePhysicsSimulation):
    """Web-specific physics simulation that extends the base simulation."""
    
    def __init__(self, width: int = 800, height: int = 600):
        """
        Initialize the web physics simulation.
        
        Args:
            width: Simulation width
            height: Simulation height
        """
        # Use physics coordinate system for web version
        super().__init__(width, height, "physics")
        
        # Web-specific properties for viewport management
        self.viewport_padding = 50
        self.min_viewport_height = 600
        
        logger.info(f"Web PhysicsSimulation initialized: {width}x{height}")
    
    def get_viewport_bounds(self) -> Dict[str, float]:
        """Calculate optimal viewport bounds based on ball position and history."""
        max_height = max(
            self.ball.y + self.ball.radius + self.viewport_padding, 
            self.min_viewport_height
        )
        
        return {
            'min_x': 0,
            'max_x': self.width,
            'min_y': -300,  # Allow 300 units below ground
            'max_y': max_height
        }
    
    def physics_to_canvas_y(self, physics_y: float, canvas_height: float) -> float:
        """Convert physics y-coordinate to canvas y-coordinate."""
        bounds = self.get_viewport_bounds()
        # Flip y-axis: physics y=0 (ground) -> canvas bottom, physics y=max -> canvas top
        normalized_y = (physics_y - bounds['min_y']) / (bounds['max_y'] - bounds['min_y'])
        return canvas_height - (normalized_y * canvas_height)
    
    def canvas_to_physics_y(self, canvas_y: float, canvas_height: float) -> float:
        """Convert canvas y-coordinate to physics y-coordinate."""
        bounds = self.get_viewport_bounds()
        normalized_y = (canvas_height - canvas_y) / canvas_height
        return bounds['min_y'] + (normalized_y * (bounds['max_y'] - bounds['min_y']))
    
    def get_state(self) -> Dict[str, Any]:
        """Get current simulation state with viewport information."""
        state = super().get_state()
        state['viewport'] = self.get_viewport_bounds()
        return state
    
    def set_start_y(self, start_y: float = 400) -> Dict[str, Any]:
        """
        Set the ball's starting y position and reset the simulation.
        
        Args:
            start_y: Bottom position of the ball in physics coordinates
        """
        # Convert bottom position to center position
        ball_center_y = start_y - self.ball.radius
        return self.set_ball_start_position(self.width // 2, ball_center_y)
    
    def step_simulation_time(self, time_step: float) -> Dict[str, Any]:
        """Step the simulation by a specific time amount (web interface)."""
        result = super().step_simulation_time(time_step)
        logger.debug(f"Web: Stepped simulation by {time_step}s")
        return result
    
    def reset(self) -> Dict[str, Any]:
        """Reset the simulation to initial state (web interface)."""
        result = super().reset()
        logger.info("Web: Simulation reset")
        return result
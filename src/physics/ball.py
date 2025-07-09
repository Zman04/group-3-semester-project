"""
Unified Ball Physics Class

A ball object with vertical motion simulation that can work with different coordinate systems.
"""

from typing import Dict, Any, Optional, Tuple
import os

try:
    from .constants import PhysicsConstants
    from ..config.constants import SimulationConfig
    from ..config.logging_config import get_logger
except ImportError:
    # Fallback for direct execution
    from physics.constants import PhysicsConstants
    from config.constants import SimulationConfig
    from config.logging_config import get_logger

logger = get_logger(__name__)


class Ball:
    """A physics-based ball object with vertical motion simulation."""
    
    def __init__(self, x: float, y: float, radius: float = None, mass: float = None, 
                 coordinate_system: str = "screen"):
        """
        Initialize a ball object.
        
        Args:
            x: Initial x position
            y: Initial y position  
            radius: Ball radius (uses default if None)
            mass: Ball mass (uses default if None)
            coordinate_system: Either "screen" (y increases downward) or "physics" (y=0 at ground, positive up)
        """
        self.x = x
        self.y = y
        self.radius = radius or PhysicsConstants.DEFAULT_BALL_RADIUS
        self.mass = mass or PhysicsConstants.DEFAULT_BALL_MASS
        self.coordinate_system = coordinate_system
        
        # Physics properties
        self.velocity_y = 0.0
        self.acceleration_y = 0.0
        
        # Physics constants
        if coordinate_system == "physics":
            # Positive y is up, so gravity is negative
            self.gravity = -SimulationConfig.GRAVITY
        else:
            # Screen coordinates, positive y is down, so gravity is positive
            self.gravity = SimulationConfig.GRAVITY
            
        self.bounce_damping = SimulationConfig.BOUNCE_DAMPING
        self.min_bounce_velocity = SimulationConfig.MIN_BOUNCE_VELOCITY
        
        # Rendering properties (only for screen coordinate system)
        self.color = PhysicsConstants.DEFAULT_BALL_COLOR
        self.texture = None
        
        if coordinate_system == "screen":
            self._load_texture()
            
        logger.debug(f"Created Ball at ({x}, {y}) with {coordinate_system} coordinates")
    
    def _load_texture(self) -> None:
        """Load ball texture for rendering (only for screen coordinate system)."""
        try:
            # Only import pygame if we're using screen coordinates
            import pygame
            
            if os.path.exists(PhysicsConstants.BALL_TEXTURE_PATH):
                self.texture = pygame.image.load(PhysicsConstants.BALL_TEXTURE_PATH)
                scaled_size = (int(self.radius * 2), int(self.radius * 2))
                self.texture = pygame.transform.scale(self.texture, scaled_size)
                logger.debug("Ball texture loaded successfully")
            else:
                logger.warning(f"Texture file not found: {PhysicsConstants.BALL_TEXTURE_PATH}")
        except ImportError:
            logger.debug("Pygame not available, skipping texture loading")
        except Exception as e:
            logger.warning(f"Could not load ball texture: {e}")
    
    def update(self, dt: float, ground_y: Optional[float] = None) -> None:
        """
        Update ball physics for one time step.
        
        Args:
            dt: Time step in seconds
            ground_y: Ground position (only needed for screen coordinates)
        """
        # Determine if ball is at rest
        if self.coordinate_system == "physics":
            is_at_rest = self.velocity_y == 0 and self.y <= self.radius
        else:
            # Screen coordinates
            if ground_y is None:
                raise ValueError("ground_y is required for screen coordinate system")
            is_at_rest = self.velocity_y == 0 and self.y + self.radius >= ground_y
        
        # Apply gravity if not at rest
        if not is_at_rest:
            self.acceleration_y = self.gravity
        else:
            self.acceleration_y = 0
        
        # Update velocity and position using kinematic equations
        self.velocity_y += self.acceleration_y * dt
        self.y += self.velocity_y * dt
    
    def check_ground_collision(self, ground_y: Optional[float] = None) -> None:
        """
        Check and handle collision with the ground.
        
        Args:
            ground_y: Ground position (only needed for screen coordinates)
        """
        if self.coordinate_system == "physics":
            # Physics coordinates: ground is at y=0
            if self.y <= self.radius:
                self.y = self.radius
                self.velocity_y = -self.velocity_y * self.bounce_damping
                
                if abs(self.velocity_y) < self.min_bounce_velocity:
                    self.velocity_y = 0
        else:
            # Screen coordinates: ground is at ground_y
            if ground_y is None:
                raise ValueError("ground_y is required for screen coordinate system")
                
            if self.y + self.radius >= ground_y:
                self.y = ground_y - self.radius
                self.velocity_y = -self.velocity_y * self.bounce_damping
                
                if abs(self.velocity_y) < self.min_bounce_velocity:
                    self.velocity_y = 0
    
    def draw(self, screen, ground_y: Optional[float] = None) -> None:
        """
        Draw the ball on the screen (only for screen coordinate system).
        
        Args:
            screen: Pygame surface to draw on
            ground_y: Ground position for shadow calculation
        """
        if self.coordinate_system != "screen":
            raise ValueError("Drawing is only supported for screen coordinate system")
        
        try:
            import pygame
            import pygame.gfxdraw
        except ImportError:
            logger.error("Pygame not available for drawing")
            return
        
        # Draw shadow
        if ground_y is not None:
            shadow_alpha = max(0, 100 - int(abs(self.y - ground_y) / 2))
            if shadow_alpha > 0:
                shadow_color = (0, 0, 0, shadow_alpha)
                pygame.gfxdraw.filled_ellipse(screen, int(self.x), int(ground_y), 
                                            int(self.radius), 5, shadow_color)
        
        # Draw ball
        if self.texture:
            texture_rect = self.texture.get_rect()
            texture_rect.center = (int(self.x), int(self.y))
            screen.blit(self.texture, texture_rect)
        else:
            pygame.draw.circle(screen, self.color, 
                             (int(self.x), int(self.y)), int(self.radius))
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the ball."""
        return {
            'x': self.x,
            'y': self.y,
            'radius': self.radius,
            'mass': self.mass,
            'velocity_y': self.velocity_y,
            'acceleration_y': self.acceleration_y,
            'coordinate_system': self.coordinate_system
        }
    
    def set_state(self, state: Dict[str, Any]) -> None:
        """Set the ball's state from a dictionary."""
        self.x = state['x']
        self.y = state['y']
        self.velocity_y = state['velocity_y']
        self.acceleration_y = state['acceleration_y']
        
        # Update other properties if provided
        if 'radius' in state:
            self.radius = state['radius']
        if 'mass' in state:
            self.mass = state['mass']
    
    def get_energy(self, ground_y: Optional[float] = None) -> Tuple[float, float, float]:
        """
        Calculate kinetic, potential, and total energy.
        
        Args:
            ground_y: Ground position (only needed for screen coordinates)
            
        Returns:
            Tuple of (kinetic_energy, potential_energy, total_energy)
        """
        kinetic_energy = 0.5 * self.mass * self.velocity_y**2
        
        if self.coordinate_system == "physics":
            height_above_ground = max(0, self.y - self.radius)
        else:
            if ground_y is None:
                raise ValueError("ground_y is required for screen coordinate system")
            height_above_ground = max(0, ground_y - (self.y + self.radius))
        
        potential_energy = self.mass * abs(self.gravity) * height_above_ground
        total_energy = kinetic_energy + potential_energy
        
        return kinetic_energy, potential_energy, total_energy
    
    def reset_to_position(self, x: float, y: float) -> None:
        """Reset ball to a specific position with zero velocity."""
        self.x = x
        self.y = y
        self.velocity_y = 0.0
        self.acceleration_y = 0.0
        logger.debug(f"Ball reset to position ({x}, {y})")
    
    def __repr__(self) -> str:
        return (f"Ball(x={self.x:.1f}, y={self.y:.1f}, "
                f"velocity_y={self.velocity_y:.1f}, "
                f"coordinate_system='{self.coordinate_system}')") 
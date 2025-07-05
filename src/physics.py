"""Physics engine for the simulation."""

from typing import Tuple, Optional
from dataclasses import dataclass
from config import DEFAULT_GRAVITY, DEFAULT_BOUNCE_DAMPING, MIN_BOUNCE_VELOCITY

@dataclass
class PhysicsState:
    """Represents the physics state of an object."""
    x: float
    y: float
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    acceleration_x: float = 0.0
    acceleration_y: float = 0.0
    
    def copy(self) -> 'PhysicsState':
        """Create a copy of this state."""
        return PhysicsState(
            self.x, self.y, 
            self.velocity_x, self.velocity_y,
            self.acceleration_x, self.acceleration_y
        )

class PhysicsObject:
    """A physics object with mass and physics properties."""
    
    def __init__(self, x: float, y: float, mass: float = 1.0, 
                 gravity: float = DEFAULT_GRAVITY,
                 bounce_damping: float = DEFAULT_BOUNCE_DAMPING):
        self.mass = mass
        self.gravity = gravity
        self.bounce_damping = bounce_damping
        self.state = PhysicsState(x, y)
    
    def apply_gravity(self, dt: float) -> None:
        """Apply gravitational acceleration."""
        self.state.acceleration_y = self.gravity
    
    def update(self, dt: float) -> None:
        """Update physics for one time step using kinematic equations."""
        # Update velocity
        self.state.velocity_x += self.state.acceleration_x * dt
        self.state.velocity_y += self.state.acceleration_y * dt
        
        # Update position
        self.state.x += self.state.velocity_x * dt
        self.state.y += self.state.velocity_y * dt
    
    def get_state(self) -> PhysicsState:
        """Get the current physics state."""
        return self.state.copy()
    
    def set_state(self, state: PhysicsState) -> None:
        """Set the physics state."""
        self.state = state.copy()

class Ball(PhysicsObject):
    """A ball physics object with collision detection."""
    
    def __init__(self, x: float, y: float, radius: float, mass: float = 1.0,
                 gravity: float = DEFAULT_GRAVITY,
                 bounce_damping: float = DEFAULT_BOUNCE_DAMPING):
        super().__init__(x, y, mass, gravity, bounce_damping)
        self.radius = radius
    
    def update(self, dt: float, ground_y: float) -> None:
        """Update ball physics including ground collision."""
        # Only apply gravity if not at rest on ground
        is_at_rest = (self.state.velocity_y == 0 and 
                     self.state.y + self.radius >= ground_y)
        
        if not is_at_rest:
            self.apply_gravity(dt)
        else:
            self.state.acceleration_y = 0
        
        # Update physics
        super().update(dt)
        
        # Check ground collision
        self.check_ground_collision(ground_y)
    
    def check_ground_collision(self, ground_y: float) -> None:
        """Check and handle collision with the ground."""
        if self.state.y + self.radius >= ground_y:
            self.state.y = ground_y - self.radius
            self.state.velocity_y = -self.state.velocity_y * self.bounce_damping
            
            # Stop very small bounces
            if abs(self.state.velocity_y) < MIN_BOUNCE_VELOCITY:
                self.state.velocity_y = 0
    
    def get_kinetic_energy(self) -> float:
        """Calculate kinetic energy."""
        velocity_squared = (self.state.velocity_x**2 + 
                           self.state.velocity_y**2)
        return 0.5 * self.mass * velocity_squared
    
    def get_potential_energy(self, ground_y: float) -> float:
        """Calculate gravitational potential energy."""
        height_above_ground = max(0, ground_y - (self.state.y + self.radius))
        return self.mass * self.gravity * height_above_ground
    
    def get_total_energy(self, ground_y: float) -> float:
        """Calculate total mechanical energy."""
        return self.get_kinetic_energy() + self.get_potential_energy(ground_y)

class PhysicsEngine:
    """Main physics engine that manages physics objects."""
    
    def __init__(self, ground_y: float):
        self.ground_y = ground_y
        self.objects: list[PhysicsObject] = []
    
    def add_object(self, obj: PhysicsObject) -> None:
        """Add a physics object to the engine."""
        self.objects.append(obj)
    
    def remove_object(self, obj: PhysicsObject) -> None:
        """Remove a physics object from the engine."""
        if obj in self.objects:
            self.objects.remove(obj)
    
    def update(self, dt: float) -> None:
        """Update all physics objects."""
        for obj in self.objects:
            if isinstance(obj, Ball):
                obj.update(dt, self.ground_y)
            else:
                obj.update(dt)
    
    def clear(self) -> None:
        """Clear all physics objects."""
        self.objects.clear() 
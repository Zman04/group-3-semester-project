import math

class Ball:
    """A physics-based ball object with vertical motion simulation."""
    
    def __init__(self, x: float, y: float, radius: float = 20, mass: float = 1.0):
        self.x = x
        self.y = y
        self.radius = radius
        self.mass = mass
        
        # Physics properties
        self.velocity_y = 0.0
        self.acceleration_y = 0.0
        
        # Constants
        self.gravity = 6000.0  # pixels/s²
        self.bounce_damping = 0.8
        
    def update(self, dt: float, ground_y: float):
        """Update ball physics for one time step."""
        is_at_rest = self.velocity_y == 0 and self.y + self.radius >= ground_y
        if not is_at_rest:
            self.acceleration_y = self.gravity
        else:
            self.acceleration_y = 0
        
        self.velocity_y += self.acceleration_y * dt
        self.y += self.velocity_y * dt
        
    def check_ground_collision(self, ground_y: float):
        """Check and handle collision with the ground."""
        if self.y + self.radius >= ground_y:
            self.y = ground_y - self.radius
            self.velocity_y = -self.velocity_y * self.bounce_damping
            
            if abs(self.velocity_y) < 50:
                self.velocity_y = 0
                
    def get_state(self):
        """Get the current state of the ball as a tuple."""
        return {
            'x': self.x,
            'y': self.y,
            'radius': self.radius,
            'velocity_y': self.velocity_y,
            'acceleration_y': self.acceleration_y
        }
    
    def set_state(self, state):
        """Set the ball's state from a dictionary."""
        self.x = state['x']
        self.y = state['y']
        self.velocity_y = state['velocity_y']
        self.acceleration_y = state['acceleration_y']

class PhysicsSimulation:
    """Core physics simulation class."""
    
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self.ground_y = height - 50
        
        # Create ball
        self.ball = Ball(width // 2, 100)
        
        # Time control properties
        self.simulation_time = 0.0
        self.is_playing = False
        self.target_fps = 144
        self.dt = 1 / self.target_fps
        
        # State history
        self.history = []
        self.time_history = []
        self.max_history = 500
        
    def update(self):
        """Update simulation state."""
        if self.is_playing:
            self.save_state()
            self.ball.update(self.dt, self.ground_y)
            self.ball.check_ground_collision(self.ground_y)
            self.simulation_time += self.dt
            
        return self.get_state()
    
    def save_state(self):
        """Save the current state to history."""
        if len(self.history) >= self.max_history:
            self.history.pop(0)
            self.time_history.pop(0)
            
        self.history.append(self.ball.get_state())
        self.time_history.append(self.simulation_time)
    
    def get_state(self):
        """Get current simulation state."""
        return {
            'ball': self.ball.get_state(),
            'time': self.simulation_time,
            'is_playing': self.is_playing,
            'ground_y': self.ground_y,
            'width': self.width,
            'height': self.height
        }
    
    def toggle_play_pause(self):
        """Toggle between play and pause states."""
        self.is_playing = not self.is_playing
        return self.is_playing
    
    def reset(self):
        """Reset the simulation to initial state."""
        self.simulation_time = 0.0
        self.is_playing = False
        self.ball = Ball(self.width // 2, 100)
        self.history.clear()
        self.time_history.clear()
        return self.get_state()
    
    def step_simulation_time(self, time_step):
        """Step the simulation by a specific time amount."""
        if time_step > 0:
            steps = int(time_step / self.dt)
            for _ in range(steps):
                self.save_state()
                self.ball.update(self.dt, self.ground_y)
                self.ball.check_ground_collision(self.ground_y)
                self.simulation_time += self.dt
        elif time_step < 0:
            target_time = max(0, self.simulation_time + time_step)
            if target_time == 0:
                self.reset()
            else:
                self.rewind_to_time(target_time)
        
        return self.get_state()
    
    def rewind_to_time(self, target_time):
        """Rewind to the closest available time in history."""
        if not self.time_history:
            self.reset()
            return self.get_state()
        
        best_idx = 0
        best_diff = abs(self.time_history[0] - target_time)
        
        for i, t in enumerate(self.time_history):
            diff = abs(t - target_time)
            if diff < best_diff:
                best_diff = diff
                best_idx = i
        
        if best_idx < len(self.history):
            self.ball.set_state(self.history[best_idx])
            self.simulation_time = self.time_history[best_idx]
            
            # Truncate history to this point
            self.history = self.history[:best_idx + 1]
            self.time_history = self.time_history[:best_idx + 1]
        
        return self.get_state() 
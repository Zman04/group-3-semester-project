# elastic collision

import pygame
import sys
import math
import pygame.gfxdraw # For AA
#from typing import Tuple, Optional

class Ball:
    """A physics-based ball object with vertical motion simulation."""
    
    def __init__(self, x: float, y: float, radius: float = 20, mass: float = 1.0):
        self.x = x # Initial horizontal coordinates
        self.y = y # Initial vertical coordinates
        self.radius = radius # Initial radius
        self.mass = mass # Initial mass (Used for energy calculations

        # Each ball will have its own x, y, radius, and mass
        
        # Physics properties
        self.velocity_y = 0.0 # Initial y velocity
        self.acceleration_y = 0.0 # Initial vertical acceleration
        
        # Constants
        self.gravity = 6000.0  # pixels/s²
        self.bounce_damping = 0.8  # Slightly less energy loss for more bounces
        
        # Load ball texture
        try:
            self.texture = pygame.image.load("asset/circle.png")
            # Scale texture to match radius
            scaled_size = (int(radius * 2), int(radius * 2))
            self.texture = pygame.transform.scale(self.texture, scaled_size)
        except (pygame.error, FileNotFoundError, OSError):
            print("Warning: Could not load circle.png, using default circle")
            self.texture = None
        
        # Visual properties (fallback)
        self.color = (255, 100, 100)  # Red color
        
    def update(self, dt: float, ground_y: float):
        """Update ball physics for one time step."""
        # Only apply gravity if ball is not at rest on ground
        is_at_rest = self.velocity_y == 0 and self.y + self.radius >= ground_y
        if not is_at_rest: # If not at rest then
            self.acceleration_y = self.gravity # apply gravity
        else:
            self.acceleration_y = 0 # don't apply gravity
        
        # Update velocity and position using proper kinematic equations
        self.velocity_y += self.acceleration_y * dt
        self.y += self.velocity_y * dt
        
    def check_ground_collision(self, ground_y: float):
        """Check and handle collision with the ground."""
        if self.y + self.radius >= ground_y:
            self.y = ground_y - self.radius
            self.velocity_y = -self.velocity_y * self.bounce_damping
            
            # Stop very small bounces
            if abs(self.velocity_y) < 50:
                self.velocity_y = 0
                
    def draw(self, screen):
        """Draw the ball on the screen."""
        # Draw a simple shadow
        shadow_y = 600  # Ground level
        shadow_alpha = max(0, 100 - int(abs(self.y - 600) / 2))
        if shadow_alpha > 0:
            shadow_color = (0, 0, 0, shadow_alpha)
            pygame.gfxdraw.filled_ellipse(screen, int(self.x), shadow_y, int(self.radius), 5, shadow_color)
            
        # Draw the ball texture or a fallback circle
        if self.texture:
            texture_rect = self.texture.get_rect()
            texture_rect.center = (int(self.x), int(self.y))
            screen.blit(self.texture, texture_rect)
        else:
            pygame.draw.circle(screen, self.color, 
                             (int(self.x), int(self.y)), int(self.radius))



class PhysicsSimulation:
    """Main physics simulation class."""
    
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height
        self.ground_y = height - 50
        
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Vertical Ball Physics Simulation")
        self.clock = pygame.time.Clock()
        
        # Create ball
        self.ball = Ball(width // 2, 100)
        
        # UI properties
        self.font = pygame.font.Font(None, 24)
        self.show_info = True

        self.history = [] # Stores (y, velocity_y, acceleration_y) tuples
        self.MAX_HISTORY_FRAMES = 500 # Store up to 500 frames of history

        self.create_background()

    def save_state(self):
        """Save the current state of the ball to history."""
        state = (self.ball.y, self.ball.velocity_y, self.ball.acceleration_y)
        self.history.append(state)
        if len(self.history) > self.MAX_HISTORY_FRAMES:
            self.history.pop(0) # Remove the oldest state

    def restore_state(self):
        """Restore the ball to a previous state from history."""
        if self.history:
            #Pop the last state (most recent before current)
            y, velocity_y, acceleration_y = self.history.pop()
            self.ball.y = y
            self.ball.velocity_y = velocity_y
            self.ball.acceleration_y = acceleration_y

    def create_background(self):
        """Pre-render the static background for performance."""
        self.background = self.screen.copy()
        self.background.fill((0, 0, 0))  # Black background
        
        # Draw ground line
        pygame.draw.line(self.background, (100, 100, 255), 
                        (0, self.ground_y), (self.width, self.ground_y), 3)
        
        # Draw grid lines
        grid_color = (105, 105, 105)
        for i in range(0, self.width, 50):
            pygame.draw.line(self.background, grid_color, 
                           (i, 0), (i, self.ground_y), 1)
        for i in range(0, self.ground_y, 50):
            pygame.draw.line(self.background, grid_color, 
                           (0, i), (self.width, i), 1)
        
    def draw_ui(self):
        """Draw UI information."""
        if not self.show_info:
            return
            
        # Physics info
        height_above_ground = max(0, self.ground_y - (self.ball.y + self.ball.radius))
        kinetic_energy = 0.5 * self.ball.mass * self.ball.velocity_y**2
        potential_energy = self.ball.mass * self.ball.gravity * height_above_ground
        total_energy = kinetic_energy + potential_energy
        
        info_lines = [
            f"Position: ({self.ball.x:.1f}, {self.ball.y:.1f}) px",
            f"Velocity: {self.ball.velocity_y:.1f} px/s",
            f"Acceleration: {self.ball.acceleration_y:.1f} px/s²",
            f"Energy: {total_energy:.0f} J"
        ]
        
        for i, line in enumerate(info_lines):
            text = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (10, 10 + i * 25))
            
        # Controls info
        controls = [
            "Controls:",
            "SPACE: Reset ball",
            "I: Toggle info",
            "ESC: Quit"
        ]
        
        for i, line in enumerate(controls):
            text = self.font.render(line, True, (200, 200, 200))
            self.screen.blit(text, (10, self.height - 100 + i * 20))
    
    def reset_ball(self):
        """Reset the ball to initial position."""
        self.ball.y = 100
        self.ball.velocity_y = 0
        self.ball.acceleration_y = 0
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE:
                    self.reset_ball()
                elif event.key == pygame.K_i:
                    self.show_info = not self.show_info
        return True
    
    def run(self):
        """Main simulation loop."""
        running = True
        target_fps = 144
        dt = 1 / target_fps  # Fixed time step for consistent physics

        while running:
            # Handle events
            running = self.handle_events()
            
            # Update physics
            self.ball.update(dt, self.ground_y)
            self.ball.check_ground_collision(self.ground_y)
            
            # Draw everything
            self.screen.blit(self.background, (0, 0))
            self.ball.draw(self.screen)
            self.draw_ui()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(target_fps)
        
        pygame.quit()
        sys.exit()


    def save_state(self):
        """Save the state of the ball after each frame"""

    def restore_state(self):
        """Restore the state of the ball when needed"""
def main():
    """Main function to run the simulation."""
    print("Starting Vertical Ball Physics Simulation...")
    print("Controls:")
    print("  SPACE - Reset ball")
    print("  I - Toggle info display")
    print("  ESC - Quit")
    print()
    
    simulation = PhysicsSimulation()
    simulation.run()

if __name__ == "__main__":
    main()

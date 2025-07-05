# elastic collision

import pygame
import sys
import math
import pygame.gfxdraw # For AA
from collections import deque
#from typing import Tuple, Optional

class GUIElement:
    """Base class for GUI elements."""
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.active = False
        self.visible = True
    
    def handle_event(self, event):
        """Handle pygame events. Return True if event was consumed."""
        return False
    
    def update(self, dt):
        """Update the element."""
        pass
    
    def draw(self, screen):
        """Draw the element."""
        pass

class Button(GUIElement):
    """
    A clickable button that can be drawn with custom images or default styling.

    To use custom images, provide a dictionary for the `images` parameter, e.g.:
    {
        'normal': 'path/to/normal_image.png',
        'hover': 'path/to/hover_image.png',
        'pressed': 'path/to/pressed_image.png'
    }
    """
    def __init__(self, x, y, width, height, text, callback=None, images=None):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, 24)
        self.pressed = False
        self.hover = False
        
        # Load images if provided
        self.images = {}
        if images:
            for key, path in images.items():
                try:
                    self.images[key] = pygame.image.load(path).convert_alpha()
                except pygame.error:
                    print(f"Warning: Could not load image for button state '{key}' at {path}")
        
    def handle_event(self, event):
        if not self.visible:
            return False
        
        # Check for hover state
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        
        # Check for clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed and self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                self.pressed = False
                return True
            self.pressed = False
            
        # Update hover state if mouse leaves the button area without moving
        if not self.rect.collidepoint(pygame.mouse.get_pos()):
            self.hover = False
            
        return False
    
    def draw(self, screen):
        if not self.visible:
            return
        
        # Determine which image to use
        current_image = None
        if self.pressed and 'pressed' in self.images:
            current_image = self.images['pressed']
        elif self.hover and 'hover' in self.images:
            current_image = self.images['hover']
        elif 'normal' in self.images:
            current_image = self.images['normal']

        # Draw with image or with default style
        if current_image:
            # Scale image to fit button dimensions
            scaled_image = pygame.transform.scale(current_image, (self.rect.width, self.rect.height))
            screen.blit(scaled_image, self.rect.topleft)
        else:
            # Fallback to procedural drawing with hover effect
            if self.pressed:
                color = (100, 100, 100) # Darker grey when pressed
            elif self.hover:
                color = (170, 170, 170) # Lighter grey on hover
            else:
                color = (150, 150, 150) # Default grey
            
            border_color = (200, 200, 200)
            
            pygame.draw.rect(screen, color, self.rect)
            pygame.draw.rect(screen, border_color, self.rect, 2)
        
        # Center text on the button
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class InputField(GUIElement):
    """A text input field."""
    def __init__(self, x, y, width, height, placeholder="", max_length=20):
        super().__init__(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.max_length = max_length
        self.font = pygame.font.Font(None, 20)
        self.cursor_pos = 0
        self.cursor_visible = True
        self.cursor_timer = 0
        
    def handle_event(self, event):
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            return self.active
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
            elif event.key == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif event.key == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.text)
            elif len(self.text) < self.max_length:
                char = event.unicode
                if char.isprintable():
                    self.text = self.text[:self.cursor_pos] + char + self.text[self.cursor_pos:]
                    self.cursor_pos += 1
            return True
        return False
    
    def update(self, dt):
        # Cursor blinking
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, screen):
        if not self.visible:
            return
            
        # Background
        bg_color = (255, 255, 255) if self.active else (230, 230, 230)
        border_color = (100, 150, 255) if self.active else (150, 150, 150)
        
        pygame.draw.rect(screen, bg_color, self.rect)
        pygame.draw.rect(screen, border_color, self.rect, 2)
        
        # Text
        display_text = self.text if self.text else self.placeholder
        text_color = (0, 0, 0) if self.text else (128, 128, 128)
        
        text_surface = self.font.render(display_text, True, text_color)
        text_rect = text_surface.get_rect()
        text_rect.centery = self.rect.centery
        text_rect.x = self.rect.x + 5
        
        # Clip text to field
        clip_rect = self.rect.copy()
        clip_rect.width -= 10
        screen.set_clip(clip_rect)
        screen.blit(text_surface, text_rect)
        screen.set_clip(None)
        
        # Cursor
        if self.active and self.cursor_visible and self.text:
            cursor_text = self.text[:self.cursor_pos]
            cursor_width = self.font.size(cursor_text)[0]
            cursor_x = self.rect.x + 5 + cursor_width
            cursor_y1 = self.rect.y + 3
            cursor_y2 = self.rect.y + self.rect.height - 3
            pygame.draw.line(screen, (0, 0, 0), (cursor_x, cursor_y1), (cursor_x, cursor_y2), 1)

class Checkbox(GUIElement):
    """A checkbox element."""
    def __init__(self, x, y, size, text, checked=False, callback=None):
        super().__init__(x, y, size, size)
        self.text = text
        self.checked = checked
        self.callback = callback
        self.font = pygame.font.Font(None, 20)
        
    def handle_event(self, event):
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                if self.callback:
                    self.callback(self.checked)
                return True
        return False
    
    def draw(self, screen):
        if not self.visible:
            return
            
        # Checkbox
        color = (255, 255, 255)
        border_color = (150, 150, 150)
        
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, border_color, self.rect, 2)
        
        # Checkmark
        if self.checked:
            points = [
                (self.rect.x + 3, self.rect.y + self.rect.height // 2),
                (self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height - 4),
                (self.rect.x + self.rect.width - 3, self.rect.y + 3)
            ]
            pygame.draw.lines(screen, (0, 150, 0), False, points, 3)
        
        # Text
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.centery = self.rect.centery
        text_rect.x = self.rect.right + 10
        screen.blit(text_surface, text_rect)

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
            self.texture = pygame.image.load("assets/circle.png")
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

    def get_state(self):
        """Get the current state of the ball as a tuple."""
        return (self.x, self.y, self.velocity_y, self.acceleration_y)
    
    def set_state(self, state):
        """Set the ball's state from a tuple."""
        self.x, self.y, self.velocity_y, self.acceleration_y = state


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
        self.small_font = pygame.font.Font(None, 20)
        self.show_info = True

        # Time control properties
        self.simulation_time = 0.0  # Simulation time in seconds
        self.is_playing = False
        self.target_fps = 144
        self.dt = 1 / self.target_fps  # Fixed time step for consistent physics
        self.auto_pause_after_step = False

        # State management - using deque for efficient operations at both ends
        self.history = deque(maxlen=500)  # Store up to 500 frames of history (about 3.5 seconds at 144 FPS)
        self.time_history = deque(maxlen=500)  # Store corresponding time values
        self.rewind_speed = 5  # Number of frames to rewind per button press

        # GUI elements
        self.gui_elements = []
        self.setup_gui()

        self.create_background()

    def setup_gui(self):
        """Initialize GUI elements."""
        # Control panel area (right side)
        panel_x = self.width - 250
        y_offset = 20
        
        # Play/Pause button
        self.play_pause_btn = Button(panel_x, y_offset, 100, 30, "Play", self.toggle_play_pause)
        self.gui_elements.append(self.play_pause_btn)
        y_offset += 40
        
        # Reset button
        reset_btn = Button(panel_x, y_offset, 100, 30, "Reset", self.reset_simulation)
        self.gui_elements.append(reset_btn)
        y_offset += 40
        
        # Time step +1s button
        step_btn = Button(panel_x, y_offset, 100, 30, "Step +1s", self.step_one_second)
        self.gui_elements.append(step_btn)
        y_offset += 45
        
        # Step unit toggle (frames vs seconds)
        self.step_by_frames = False
        self.step_unit_btn = Button(panel_x, y_offset, 120, 25, "Step: Seconds", self.toggle_step_unit)
        self.gui_elements.append(self.step_unit_btn)
        y_offset += 35
        
        # Custom increment input
        increment_label = self.create_label("Step Value:", panel_x, y_offset)
        y_offset += 25
        self.increment_input = InputField(panel_x, y_offset, 120, 25, "1.0", 15)
        self.gui_elements.append(self.increment_input)
        y_offset += 30
        
        # Custom increment step button
        custom_step_btn = Button(panel_x, y_offset, 100, 30, "Step", self.step_custom_increment)
        self.gui_elements.append(custom_step_btn)
        y_offset += 50
        
        # Set time input
        time_label = self.create_label("Set Time (s):", panel_x, y_offset)
        y_offset += 25
        self.time_input = InputField(panel_x, y_offset, 120, 25, "0.0", 15)
        self.gui_elements.append(self.time_input)
        y_offset += 30
        
        # Set time button
        set_time_btn = Button(panel_x, y_offset, 100, 30, "Set Time", self.set_specific_time)
        self.gui_elements.append(set_time_btn)
        y_offset += 50
        
        # Auto-pause checkbox
        self.auto_pause_checkbox = Checkbox(panel_x, y_offset, 20, "Auto-pause after step", 
                                          self.auto_pause_after_step, self.toggle_auto_pause)
        self.gui_elements.append(self.auto_pause_checkbox)

    def create_label(self, text, x, y):
        """Helper to create text labels (not interactive)."""
        # Labels are drawn in draw_ui, not as GUI elements
        return None

    def toggle_play_pause(self):
        """Toggle between play and pause states."""
        self.is_playing = not self.is_playing
        self.play_pause_btn.text = "Pause" if self.is_playing else "Play"

    def toggle_step_unit(self):
        """Toggle between frame-based and time-based stepping."""
        self.step_by_frames = not self.step_by_frames
        self.step_unit_btn.text = "Step: Frames" if self.step_by_frames else "Step: Seconds"
        # Update placeholder text in increment input
        if self.step_by_frames:
            self.increment_input.placeholder = "144"  # Suggest 144 frames (1 second)
        else:
            self.increment_input.placeholder = "1.0"  # Suggest 1 second

    def reset_simulation(self):
        """Reset the simulation to initial state."""
        self.simulation_time = 0.0
        self.is_playing = False
        self.play_pause_btn.text = "Play"
        self.reset_ball()

    def step_one_second(self):
        """Step the simulation forward by 1 second."""
        if self.step_by_frames:
            self.step_simulation_frames(self.target_fps)  # 144 frames = 1 second
        else:
            self.step_simulation_time(1.0)

    def step_custom_increment(self):
        """Step the simulation by the custom increment value."""
        try:
            increment = float(self.increment_input.text)
            if self.step_by_frames:
                # Stepping by frames (can be negative)
                self.step_simulation_frames(int(increment))
            else:
                # Stepping by time (can be negative)
                self.step_simulation_time(increment)
        except ValueError:
            print("Invalid step value")

    def step_simulation_frames(self, frame_count):
        """Step the simulation by a specific number of frames (positive or negative)."""
        if frame_count > 0:
            # Step forward
            for _ in range(frame_count):
                self.save_state()
                self.ball.update(self.dt, self.ground_y)
                self.ball.check_ground_collision(self.ground_y)
                self.simulation_time += self.dt
        elif frame_count < 0:
            # Step backward (rewind)
            frames_to_rewind = min(abs(frame_count), len(self.history))
            for _ in range(frames_to_rewind):
                if self.history and self.time_history:
                    self.history.pop()
                    self.time_history.pop()
            
            # Apply the rewound state
            if self.history and self.time_history:
                self.ball.set_state(self.history[-1])
                self.simulation_time = self.time_history[-1]
            else:
                # If we've exhausted history, reset to initial state
                self.reset_simulation()
        
        if self.auto_pause_after_step:
            self.is_playing = False
            self.play_pause_btn.text = "Play"

    def step_simulation_time(self, time_step):
        """Step the simulation by a specific time amount (positive or negative)."""
        if time_step > 0:
            # Step forward in time
            steps = int(time_step / self.dt)
            for _ in range(steps):
                self.save_state()
                self.ball.update(self.dt, self.ground_y)
                self.ball.check_ground_collision(self.ground_y)
                self.simulation_time += self.dt
        elif time_step < 0:
            # Step backward in time
            target_time = max(0, self.simulation_time + time_step)  # Can't go below 0
            if target_time == 0:
                self.reset_simulation()
            else:
                self.rewind_to_time(target_time)
        
        if self.auto_pause_after_step:
            self.is_playing = False
            self.play_pause_btn.text = "Play"

    def set_specific_time(self):
        """Set the simulation to a specific time."""
        try:
            target_time = float(self.time_input.text)
            if target_time >= 0:
                self.jump_to_time(target_time)
            else:
                print("Invalid time: must be non-negative")
        except ValueError:
            print("Invalid time value")

    def toggle_auto_pause(self, checked):
        """Toggle auto-pause functionality."""
        self.auto_pause_after_step = checked

    def jump_to_time(self, target_time):
        """Jump to a specific time in the simulation."""
        if target_time < self.simulation_time:
            # Need to rewind or reset
            if target_time == 0:
                self.reset_simulation()
            else:
                # Try to find the closest time in history
                self.rewind_to_time(target_time)
        elif target_time > self.simulation_time:
            # Step forward to target time
            time_diff = target_time - self.simulation_time
            self.step_simulation_time(time_diff)
        
        if self.auto_pause_after_step:
            self.is_playing = False
            self.play_pause_btn.text = "Play"

    def rewind_to_time(self, target_time):
        """Rewind to the closest available time in history."""
        if not self.time_history:
            self.reset_simulation()
            return
        
        # Find the closest time in history
        best_idx = 0
        best_diff = abs(self.time_history[0] - target_time)
        
        for i, t in enumerate(self.time_history):
            diff = abs(t - target_time)
            if diff < best_diff:
                best_diff = diff
                best_idx = i
        
        # Rewind to that state
        frames_to_rewind = len(self.history) - best_idx - 1
        if frames_to_rewind > 0:
            for _ in range(frames_to_rewind):
                if self.history and self.time_history:
                    self.history.pop()
                    self.time_history.pop()
        
        if self.history and self.time_history:
            self.ball.set_state(self.history[-1])
            self.simulation_time = self.time_history[-1]

    def save_state(self):
        """Save the current state of the ball to history."""
        state = self.ball.get_state()
        self.history.append(state)
        self.time_history.append(self.simulation_time)

    def can_rewind(self):
        """Check if there are states available for rewinding."""
        return len(self.history) > 1

    def get_history_info(self):
        """Get information about the current history state."""
        return {
            'frames_stored': len(self.history),
            'max_frames': self.history.maxlen,
            'time_stored_seconds': len(self.history) / self.target_fps,
            'can_rewind': self.can_rewind()
        }

    def create_background(self):
        """Pre-render the static background for performance."""
        self.background = self.screen.copy()
        self.background.fill((0, 0, 0))  # Black background
        
        # Draw ground line
        pygame.draw.line(self.background, (100, 100, 255), 
                        (0, self.ground_y), (self.width, self.ground_y), 3)
        
        # Draw grid lines
        grid_color = (105, 105, 105)
        for i in range(0, self.width - 250, 50):  # Don't draw grid under control panel
            pygame.draw.line(self.background, grid_color, 
                           (i, 0), (i, self.ground_y), 1)
        for i in range(0, self.ground_y, 50):
            pygame.draw.line(self.background, grid_color, 
                           (0, i), (self.width - 250, i), 1)
        
        # Draw control panel background
        panel_rect = pygame.Rect(self.width - 250, 0, 250, self.height)
        pygame.draw.rect(self.background, (40, 40, 40), panel_rect)
        pygame.draw.line(self.background, (100, 100, 100), 
                        (self.width - 250, 0), (self.width - 250, self.height), 2)
        
    def draw_ui(self):
        """Draw UI information."""
        if not self.show_info:
            return
            
        # Physics info (left side)
        height_above_ground = max(0, self.ground_y - (self.ball.y + self.ball.radius))
        kinetic_energy = 0.5 * self.ball.mass * self.ball.velocity_y**2
        potential_energy = self.ball.mass * self.ball.gravity * height_above_ground
        total_energy = kinetic_energy + potential_energy
        
        # Get history info
        history_info = self.get_history_info()
        
        info_lines = [
            f"Time: {self.simulation_time:.3f} s",
            f"Position: ({self.ball.x:.1f}, {self.ball.y:.1f}) px",
            f"Velocity: {self.ball.velocity_y:.1f} px/s",
            f"Acceleration: {self.ball.acceleration_y:.1f} px/s²",
            f"Energy: {total_energy:.0f} J",
            f"Status: {'Playing' if self.is_playing else 'Paused'}",
            f"Step Mode: {'Frames' if self.step_by_frames else 'Seconds'}",
            f"History: {history_info['frames_stored']}/{history_info['max_frames']} frames"
        ]
        
        for i, line in enumerate(info_lines):
            text = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (10, 10 + i * 25))
        
        # Control panel labels
        panel_x = self.width - 240
        
        # Step value label with unit indication
        step_unit = "frames" if self.step_by_frames else "seconds"
        step_label_text = f"Step Value ({step_unit}):"
        label = self.small_font.render(step_label_text, True, (200, 200, 200))
        self.screen.blit(label, (panel_x, 145))
        
        # Helper text for negative values
        helper_text = "(+/- values allowed)"
        helper_label = self.small_font.render(helper_text, True, (150, 150, 150))
        self.screen.blit(helper_label, (panel_x, 165))
        
        # Set time label
        label = self.small_font.render("Set Time (s):", True, (200, 200, 200))
        self.screen.blit(label, (panel_x, 275))
        
        # Controls info (bottom left)
        controls = [
            "Keyboard Controls:",
            "I: Toggle info",
            "ESC: Quit",
            "",
            "Step Controls:",
            "• Use +/- values to go forward/back",
            f"• Current mode: {step_unit}",
            "• Toggle mode with Step button"
        ]
        
        for i, line in enumerate(controls):
            color = (200, 200, 200) if line else (100, 100, 100)
            if line.startswith("•"):
                color = (180, 180, 180)
            text = self.small_font.render(line, True, color)
            self.screen.blit(text, (10, self.height - 160 + i * 18))
    
    def reset_ball(self):
        """Reset the ball to initial position and clear history."""
        self.ball.x = self.width // 2
        self.ball.y = 100
        self.ball.velocity_y = 0
        self.ball.acceleration_y = 0
        self.history.clear()  # Clear history when resetting
        self.time_history.clear()
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            # Check GUI elements first
            event_consumed = False
            for element in self.gui_elements:
                if element.handle_event(event):
                    event_consumed = True
                    break
            
            if event_consumed:
                continue
                
            # Handle other events
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_i:
                    self.show_info = not self.show_info
        return True
    
    def run(self):
        """Main simulation loop."""
        running = True

        while running:
            # Calculate delta time
            dt_real = self.clock.tick(self.target_fps) / 1000.0
            
            # Handle events
            running = self.handle_events()
            
            # Update GUI elements
            for element in self.gui_elements:
                element.update(dt_real)
            
            # Update physics only if playing
            if self.is_playing:
                self.save_state()
                self.ball.update(self.dt, self.ground_y)
                self.ball.check_ground_collision(self.ground_y)
                self.simulation_time += self.dt
            
            # Draw everything
            self.screen.blit(self.background, (0, 0))
            self.ball.draw(self.screen)
            self.draw_ui()
            
            # Draw GUI elements
            for element in self.gui_elements:
                element.draw(self.screen)
            
            # Update display
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()


def main():
    """Main function to run the simulation."""
    print("Starting Vertical Ball Physics Simulation...")
    print("Time Control Features:")
    print("  - Play/Pause button")
    print("  - Step by 1 second")
    print("  - Custom time increments")
    print("  - Set specific time")
    print("  - Auto-pause option")
    print("  - Rewind functionality")
    print()
    print("Keyboard Controls:")
    print("  I - Toggle info display")
    print("  ESC - Quit")
    print()
    
    simulation = PhysicsSimulation()
    simulation.run()

if __name__ == "__main__":
    main()
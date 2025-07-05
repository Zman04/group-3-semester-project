"""Refactored physics simulation using modular architecture."""

import pygame
import sys
import logging
from typing import Optional

# Import our new modules
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, GROUND_OFFSET,
    DEFAULT_BALL_RADIUS, DEFAULT_BALL_MASS, TARGET_FPS,
    INITIAL_BALL_X_RATIO, INITIAL_BALL_Y
)
from physics import Ball, PhysicsEngine
from renderer import Renderer
from time_manager import TimeManager, StepMode
from gui import GUIManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PhysicsSimulation:
    """Main physics simulation class using modular architecture."""
    
    def __init__(self, width: int = WINDOW_WIDTH, height: int = WINDOW_HEIGHT):
        self.width = width
        self.height = height
        self.ground_y = height - GROUND_OFFSET
        
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()
        
        # Initialize core systems
        self.physics_engine = PhysicsEngine(self.ground_y)
        self.renderer = Renderer(width, height, self.ground_y)
        self.time_manager = TimeManager(TARGET_FPS)
        self.gui_manager = GUIManager(width, height)
        
        # Create ball
        initial_x = width * INITIAL_BALL_X_RATIO
        self.ball = Ball(
            initial_x, INITIAL_BALL_Y, 
            DEFAULT_BALL_RADIUS, DEFAULT_BALL_MASS
        )
        self.physics_engine.add_object(self.ball)
        
        # UI state
        self.show_info = True
        self.running = True
        
        # GUI element references (stored by GUI manager)
        self.gui_refs = {}
        
        # Setup GUI and callbacks
        self._setup_gui()
        self._setup_time_manager_callbacks()
        
        logger.info("Physics simulation initialized")
    
    def _setup_gui(self) -> None:
        """Setup the GUI system with callbacks."""
        callbacks = {
            'toggle_play_pause': self._toggle_play_pause,
            'reset': self._reset_simulation,
            'step_one_second': self._step_one_second,
            'toggle_step_mode': self._toggle_step_mode,
            'step_custom': self._step_custom,
            'set_time': self._set_time,
            'toggle_auto_pause': self._toggle_auto_pause,
        }
        
        self.gui_manager.create_control_panel(callbacks)
        
        # Store references to GUI elements for later updates
        self.gui_refs = callbacks
        
        # Set initial GUI state
        self._update_gui_state()
        
        logger.info("GUI system initialized")
    
    def _setup_time_manager_callbacks(self) -> None:
        """Setup callbacks for time manager events."""
        self.time_manager.add_on_play_state_change_callback(self._on_play_state_changed)
        self.time_manager.add_on_time_change_callback(self._on_time_changed)
    
    def _toggle_play_pause(self) -> None:
        """Toggle play/pause state."""
        self.time_manager.toggle_play_pause()
    
    def _reset_simulation(self) -> None:
        """Reset the simulation."""
        self.time_manager.reset()
        self._reset_ball()
        logger.info("Simulation reset")
    
    def _step_one_second(self) -> None:
        """Step forward by one second."""
        if self.time_manager.step_mode == StepMode.FRAMES:
            self.time_manager.step_forward_frames(TARGET_FPS, self.ball)
        else:
            self.time_manager.step_forward_time(1.0, self.ball, self.ground_y)
    
    def _toggle_step_mode(self) -> None:
        """Toggle between frame and time step modes."""
        self.time_manager.toggle_step_mode()
        self._update_gui_state()
    
    def _step_custom(self) -> None:
        """Step by custom increment."""
        step_input = self.gui_refs.get('step_input')
        if not step_input:
            return
        
        try:
            increment = float(step_input.text)
            if self.time_manager.step_mode == StepMode.FRAMES:
                frame_count = int(increment)
                if frame_count > 0:
                    self.time_manager.step_forward_frames(frame_count, self.ball)
                else:
                    self.time_manager.step_backward_frames(abs(frame_count), self.ball)
            else:
                if increment > 0:
                    self.time_manager.step_forward_time(increment, self.ball, self.ground_y)
                else:
                    self.time_manager.step_backward_time(abs(increment), self.ball)
        except ValueError:
            logger.warning("Invalid step value entered")
    
    def _set_time(self) -> None:
        """Set simulation to specific time."""
        time_input = self.gui_refs.get('time_input')
        if not time_input:
            return
        
        try:
            target_time = float(time_input.text)
            if target_time >= 0:
                self.time_manager.jump_to_time(target_time, self.ball, self.ground_y)
            else:
                logger.warning("Time cannot be negative")
        except ValueError:
            logger.warning("Invalid time value entered")
    
    def _toggle_auto_pause(self, checked: bool) -> None:
        """Toggle auto-pause functionality."""
        self.time_manager.set_auto_pause(checked)
    
    def _on_play_state_changed(self, is_playing: bool) -> None:
        """Callback for when play state changes."""
        play_pause_btn = self.gui_refs.get('play_pause_button')
        if play_pause_btn:
            play_pause_btn.set_text("Pause" if is_playing else "Play")
    
    def _on_time_changed(self, new_time: float) -> None:
        """Callback for when simulation time changes."""
        # Update time input field to show current time
        time_input = self.gui_refs.get('time_input')
        if time_input and not time_input.active:  # Don't update if user is typing
            time_input.set_text(f"{new_time:.3f}")
    
    def _update_gui_state(self) -> None:
        """Update GUI elements based on current state."""
        # Update step mode button
        step_mode_btn = self.gui_refs.get('step_mode_button')
        if step_mode_btn:
            mode_text = "Step: " + self.time_manager.step_mode.value.capitalize()
            step_mode_btn.set_text(mode_text)
        
        # Update step input placeholder
        step_input = self.gui_refs.get('step_input')
        if step_input:
            step_input.placeholder = self.time_manager.get_suggested_step_value()
        
        # Update step label
        step_label = self.gui_refs.get('step_label')
        if step_label:
            unit = self.time_manager.step_mode.value
            step_label.set_text(f"Step Value ({unit}):")
        
        # Update auto-pause checkbox
        auto_pause_cb = self.gui_refs.get('auto_pause_checkbox')
        if auto_pause_cb:
            auto_pause_cb.set_checked(self.time_manager.auto_pause_after_step)
    
    def _reset_ball(self) -> None:
        """Reset ball to initial position."""
        initial_x = self.width * INITIAL_BALL_X_RATIO
        self.ball.state.x = initial_x
        self.ball.state.y = INITIAL_BALL_Y
        self.ball.state.velocity_x = 0
        self.ball.state.velocity_y = 0
        self.ball.state.acceleration_x = 0
        self.ball.state.acceleration_y = 0
    
    def _handle_events(self) -> bool:
        """Handle pygame events."""
        for event in pygame.event.get():
            # Check GUI first
            if self.gui_manager.handle_event(event):
                continue
            
            # Handle other events
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_i:
                    self.show_info = not self.show_info
                    logger.info(f"Info display {'enabled' if self.show_info else 'disabled'}")
        
        return True
    
    def _update(self, dt: float) -> None:
        """Update simulation state."""
        # Update GUI
        self.gui_manager.update(dt)
        
        # Update physics if playing
        if self.time_manager.is_playing:
            self.time_manager.save_state(self.ball)
            self.ball.update(self.time_manager.dt, self.ground_y)
            self.time_manager.step_time(self.time_manager.dt)
    
    def _get_info_data(self) -> dict:
        """Get data for the info panel."""
        history_info = self.time_manager.get_history_info()
        return {
            'time': self.time_manager.simulation_time,
            'x': self.ball.state.x,
            'y': self.ball.state.y,
            'velocity_y': self.ball.state.velocity_y,
            'acceleration_y': self.ball.state.acceleration_y,
            'total_energy': self.ball.get_total_energy(self.ground_y),
            'status': 'Playing' if self.time_manager.is_playing else 'Paused',
            'step_mode': self.time_manager.step_mode.value.capitalize(),
            'history_frames': history_info['frames_stored'],
            'max_history': history_info['max_frames']
        }
    
    def _render(self) -> None:
        """Render the frame."""
        # Render main scene
        self.renderer.render_frame(self.screen, self.ball)
        
        # Render GUI
        self.gui_manager.draw(self.screen)
        
        # Render info panels
        if self.show_info:
            info_data = self._get_info_data()
            self.gui_manager.draw_info_panel(self.screen, info_data)
            self.gui_manager.draw_controls_info(
                self.screen, 
                self.time_manager.step_mode.value
            )
        
        # Update display
        pygame.display.flip()
    
    def run(self) -> None:
        """Main simulation loop."""
        logger.info("Starting simulation loop")
        
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(TARGET_FPS) / 1000.0
            
            # Handle events
            self.running = self._handle_events()
            
            # Update simulation
            self._update(dt)
            
            # Render frame
            self._render()
        
        # Cleanup
        self._cleanup()
        logger.info("Simulation ended")
    
    def _cleanup(self) -> None:
        """Clean up resources."""
        self.renderer.cleanup()
        pygame.quit()
        sys.exit()

def main():
    """Main function to run the simulation."""
    
    print("Controls:")
    print("  I - Toggle info display")
    print("  ESC - Quit")
    print("  Use GUI controls for time manipulation")
    print()
    
    try:
        simulation = PhysicsSimulation()
        simulation.run()
    except Exception as e:
        logger.error(f"Simulation failed: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main() 
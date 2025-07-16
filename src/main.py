"""
Refactored Main Application

Physics ball simulation with modular design and clean separation of concerns.
"""

import pygame
import sys
from typing import List

from ui import Button, InputField, Checkbox
from simulation import PhysicsSimulation, Renderer
from config import SimulationConfig, UIConfig, setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


class PhysicsSimulationApp:
    """Main application class that coordinates all components."""
    
    def __init__(self, width: int = None, height: int = None):
        """Initialize the physics simulation application."""
        self.width = width or SimulationConfig.DEFAULT_WIDTH
        self.height = height or SimulationConfig.DEFAULT_HEIGHT
        
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Vertical Ball Physics Simulation")
        self.clock = pygame.time.Clock()
        
        # Create core components
        self.simulation = PhysicsSimulation(self.width, self.height, "screen")
        self.renderer = Renderer(self.width, self.height)
        
        # UI state
        self.show_info = True
        self.gui_elements: List = []
        
        # Setup GUI
        self.setup_gui()
        
        logger.info(f"PhysicsSimulationApp initialized: {self.width}x{self.height}")
    
    def setup_gui(self) -> None:
        """Initialize GUI elements."""
        panel_x = self.width - UIConfig.CONTROL_PANEL_WIDTH + UIConfig.PANEL_PADDING
        y_offset = UIConfig.PANEL_PADDING
        
        # Play/Pause button
        self.play_pause_btn = Button(
            panel_x, y_offset, 100, 30, "Play", 
            self.on_play_pause_clicked
        )
        self.gui_elements.append(self.play_pause_btn)
        y_offset += UIConfig.ELEMENT_SPACING
        
        # Reset button
        reset_btn = Button(
            panel_x, y_offset, 100, 30, "Reset", 
            self.on_reset_clicked
        )
        self.gui_elements.append(reset_btn)
        y_offset += UIConfig.ELEMENT_SPACING
        
        # Step +1s button
        step_btn = Button(
            panel_x, y_offset, 100, 30, "Step +1s", 
            self.on_step_one_second_clicked
        )
        self.gui_elements.append(step_btn)
        y_offset += 45
        
        # Step unit toggle
        self.step_unit_btn = Button(
            panel_x, y_offset, 120, 25, "Step: Seconds", 
            self.on_toggle_step_unit_clicked
        )
        self.gui_elements.append(self.step_unit_btn)
        y_offset += 60
        
        # Custom increment input
        self.increment_input = InputField(
            panel_x, y_offset, 120, 25, "1.0", 15
        )
        self.gui_elements.append(self.increment_input)
        y_offset += 30
        
        # Custom increment step button
        custom_step_btn = Button(
            panel_x, y_offset, 100, 30, "Step", 
            self.on_custom_step_clicked
        )
        self.gui_elements.append(custom_step_btn)
        y_offset += 50
        
        # Set time input
        self.time_input = InputField(
            panel_x, y_offset, 120, 25, "0.0", 15
        )
        self.gui_elements.append(self.time_input)
        y_offset += 30
        
        # Set time button
        set_time_btn = Button(
            panel_x, y_offset, 100, 30, "Set Time", 
            self.on_set_time_clicked
        )
        self.gui_elements.append(set_time_btn)
        y_offset += 50
        
        # Auto-pause checkbox
        self.auto_pause_checkbox = Checkbox(
            panel_x, y_offset, 20, "Auto-pause after step", 
            False, self.on_auto_pause_toggled
        )
        self.gui_elements.append(self.auto_pause_checkbox)
    
    def on_play_pause_clicked(self) -> None:
        """Handle play/pause button click."""
        is_playing = self.simulation.toggle_play_pause()
        self.play_pause_btn.text = "Pause" if is_playing else "Play"
        logger.debug(f"Play/pause toggled: {'playing' if is_playing else 'paused'}")
    
    def on_reset_clicked(self) -> None:
        """Handle reset button click."""
        self.simulation.reset()
        self.play_pause_btn.text = "Play"
        logger.debug("Simulation reset")
    
    def on_step_one_second_clicked(self) -> None:
        """Handle step +1s button click."""
        state = self.simulation.get_state()
        if state['step_by_frames']:
            self.simulation.step_simulation_frames(self.simulation.target_fps)
        else:
            self.simulation.step_simulation_time(1.0)
        self._update_play_pause_button()
    
    def on_toggle_step_unit_clicked(self) -> None:
        """Handle step unit toggle button click."""
        unit = self.simulation.toggle_step_unit()
        self.step_unit_btn.text = f"Step: {unit.title()}"
        
        # Update placeholder text
        if unit == "frames":
            self.increment_input.placeholder = "144"
        else:
            self.increment_input.placeholder = "1.0"
    
    def on_custom_step_clicked(self) -> None:
        """Handle custom step button click."""
        try:
            increment = float(self.increment_input.text)
            state = self.simulation.get_state()
            
            if state['step_by_frames']:
                self.simulation.step_simulation_frames(int(increment))
            else:
                self.simulation.step_simulation_time(increment)
            
            self._update_play_pause_button()
        except ValueError:
            logger.warning("Invalid step value entered")
    
    def on_set_time_clicked(self) -> None:
        """Handle set time button click."""
        try:
            target_time = float(self.time_input.text)
            self.simulation.jump_to_time(target_time)
            self._update_play_pause_button()
        except ValueError:
            logger.warning("Invalid time value entered")
    
    def on_auto_pause_toggled(self, checked: bool) -> None:
        """Handle auto-pause checkbox toggle."""
        self.simulation.set_auto_pause(checked)
    
    def _update_play_pause_button(self) -> None:
        """Update play/pause button text based on simulation state."""
        state = self.simulation.get_state()
        self.play_pause_btn.text = "Pause" if state['is_playing'] else "Play"
    
    def handle_events(self) -> bool:
        """Handle pygame events. Returns False if app should quit."""
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
                    logger.debug(f"Info display {'enabled' if self.show_info else 'disabled'}")
        
        return True
    
    def update(self, dt: float) -> None:
        """Update application state."""
        # Update GUI elements
        for element in self.gui_elements:
            element.update(dt)
        
        # Update simulation
        self.simulation.update()
    
    def draw(self) -> None:
        """Draw the complete application."""
        # Get current simulation state
        state = self.simulation.get_state()
        
        # Draw simulation
        self.renderer.draw_simulation(self.screen, state, self.show_info)
        
        # Draw GUI elements
        self.renderer.draw_gui_elements(self.screen, self.gui_elements)
        
        # Update display
        pygame.display.flip()
    
    def run(self) -> None:
        """Main application loop."""
        logger.info("Starting physics simulation...")
        
        running = True
        while running:
            # Calculate delta time
            dt_real = self.clock.tick(self.simulation.target_fps) / 1000.0
            
            # Handle events
            running = self.handle_events()
            
            # Update
            self.update(dt_real)
            
            # Draw
            self.draw()
        
        logger.info("Physics simulation ended")
        pygame.quit()
        sys.exit()


def main():
    """Main function to run the simulation."""
    print("Starting Vertical Ball Physics Simulation...")
    print("Features:")
    print("  - Modular design with separated concerns")
    print("  - Play/Pause control")
    print("  - Time stepping (frames or seconds)")
    print("  - Custom time increments") 
    print("  - Set specific time")
    print("  - Auto-pause option")
    print("  - Rewind functionality")
    print("  - Comprehensive logging")
    print()
    print("Keyboard Controls:")
    print("  I - Toggle info display")
    print("  ESC - Quit")
    print()
    
    try:
        app = PhysicsSimulationApp()
        app.run()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
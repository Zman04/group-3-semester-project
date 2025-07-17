"""
Renderer Module

Handles all rendering operations for the physics simulation.
"""

import pygame
from typing import Dict, Any, List, Optional

try:
    from ..config.constants import UIConfig, SimulationConfig
    from ..config.logging_config import get_logger
except ImportError:
    # Fallback for direct execution
    from config.constants import UIConfig, SimulationConfig
    from config.logging_config import get_logger

logger = get_logger(__name__)


class SimulationRenderer:
    """Handles rendering of the physics simulation."""
    
    def __init__(self, width: int, height: int):
        """
        Initialize the renderer.
        
        Args:
            width: Screen width
            height: Screen height
        """
        self.width = width
        self.height = height
        
        # Fonts
        self.font = pygame.font.Font(None, UIConfig.DEFAULT_FONT_SIZE)
        self.small_font = pygame.font.Font(None, UIConfig.SMALL_FONT_SIZE)
        
        # Pre-render static background for performance
        self.background = None
        self.create_background()
        
        logger.debug(f"Renderer initialized for {width}x{height}")
    
    def create_background(self) -> None:
        """Pre-render the static background for performance."""
        self.background = pygame.Surface((self.width, self.height))
        self.background.fill(UIConfig.BACKGROUND_COLOR)
        
        # Calculate control panel and simulation area
        control_panel_width = UIConfig.CONTROL_PANEL_WIDTH
        sim_width = self.width - control_panel_width
        ground_y = self.height - SimulationConfig.GROUND_OFFSET
        
        # Draw grid lines in simulation area only
        grid_color = UIConfig.GRID_COLOR
        for i in range(0, sim_width, UIConfig.GRID_SPACING):
            pygame.draw.line(self.background, grid_color, 
                           (i, 0), (i, ground_y), 1)
        for i in range(0, ground_y, UIConfig.GRID_SPACING):
            pygame.draw.line(self.background, grid_color, 
                           (0, i), (sim_width, i), 1)
        
        # Draw ground line
        pygame.draw.line(self.background, UIConfig.GROUND_COLOR, 
                        (0, ground_y), (sim_width, ground_y), 3)
        
        # Draw control panel background
        panel_rect = pygame.Rect(sim_width, 0, control_panel_width, self.height)
        pygame.draw.rect(self.background, UIConfig.CONTROL_PANEL_COLOR, panel_rect)
        pygame.draw.line(self.background, UIConfig.BORDER_COLOR, 
                        (sim_width, 0), (sim_width, self.height), 2)
        
        logger.debug("Background pre-rendered")
    
    def draw_simulation_info(self, screen: pygame.Surface, state: Dict[str, Any], 
                           show_info: bool = True) -> None:
        """
        Draw simulation information on the screen.
        
        Args:
            screen: Pygame surface to draw on
            state: Current simulation state
            show_info: Whether to show detailed info
        """
        if not show_info:
            return
        
        ball = state['ball']
        energy = state['energy']
        
        # Calculate height above ground
        if state['coordinate_system'] == "screen":
            height_above_ground = max(0, state['ground_y'] - (ball['y'] + ball['radius']))
        else:
            height_above_ground = max(0, ball['y'] - ball['radius'])
        
        # Main info lines
        info_lines = [
            f"Time: {state['time']:.3f} s",
            f"Position: ({ball['x']:.1f}, {ball['y']:.1f}) px",
            f"Velocity: {ball['velocity_y']:.1f} px/s",
            f"Acceleration: {ball['acceleration_y']:.1f} px/s²",
            f"Energy: {energy['total']:.0f} J",
            f"Status: {'Playing' if state['is_playing'] else 'Paused'}",
            f"Step Mode: {'Frames' if state.get('step_by_frames', False) else 'Seconds'}"
        ]
        
        # Draw info lines
        for i, line in enumerate(info_lines):
            text = self.font.render(line, True, UIConfig.TEXT_COLOR)
            screen.blit(text, (10, 10 + i * 25))
    
    def draw_control_labels(self, screen: pygame.Surface) -> None:
        """Draw static labels for control panel."""
        panel_x = self.width - UIConfig.CONTROL_PANEL_WIDTH + 10
        
        # Step value label
        label = self.small_font.render("Step Value:", True, UIConfig.LABEL_COLOR)
        screen.blit(label, (panel_x, 145))
        
        # Helper text
        helper_text = "(+/- values allowed)"
        helper_label = self.small_font.render(helper_text, True, UIConfig.HELPER_TEXT_COLOR)
        screen.blit(label, (panel_x, 165))
        
        # Set time label
        label = self.small_font.render("Set Time (s):", True, UIConfig.LABEL_COLOR)
        screen.blit(label, (panel_x, 275))
    
    def draw_controls_info(self, screen: pygame.Surface, state: Dict[str, Any]) -> None:
        """Draw controls information at bottom of screen."""
        step_unit = "frames" if state.get('step_by_frames', False) else "seconds"
        
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
            if not line:
                continue
            color = UIConfig.LABEL_COLOR if line.startswith("•") else UIConfig.TEXT_COLOR
            if line.endswith(":"):
                color = UIConfig.TEXT_COLOR
            text = self.small_font.render(line, True, color)
            screen.blit(text, (10, self.height - 160 + i * 18))
    
    def draw_ball_with_shadow(self, screen: pygame.Surface, ball_data: Dict[str, Any], 
                            ground_y: float) -> None:
        """
        Draw the ball with shadow effect.
        
        Args:
            screen: Pygame surface to draw on
            ball_data: Ball state data
            ground_y: Ground position for shadow
        """
        x, y = int(ball_data['x']), int(ball_data['y'])
        radius = int(ball_data['radius'])
        
        # Draw shadow
        shadow_alpha = max(0, 100 - int(abs(y - ground_y) / 2))
        if shadow_alpha > 0:
            shadow_color = (*UIConfig.SHADOW_COLOR, shadow_alpha)
            try:
                import pygame.gfxdraw
                pygame.gfxdraw.filled_ellipse(screen, x, int(ground_y), radius, 5, shadow_color)
            except ImportError:
                # Fallback without alpha
                pygame.draw.ellipse(screen, UIConfig.SHADOW_COLOR[:3], 
                                  (x - radius, int(ground_y) - 5, radius * 2, 10))
        
        # Draw ball
        import pygame as pg
        pg.draw.circle(screen, UIConfig.BALL_COLOR, (x, y), radius)
        
        # Add highlight for 3D effect
        highlight_offset = radius // 3
        highlight_pos = (x - highlight_offset, y - highlight_offset)
        highlight_radius = radius // 2
        pg.draw.circle(screen, UIConfig.BALL_HIGHLIGHT_COLOR, highlight_pos, highlight_radius)
    
    def render_frame(self, screen: pygame.Surface, state: Dict[str, Any], 
                    gui_elements: List = None, show_info: bool = True) -> None:
        """
        Render a complete frame of the simulation.
        
        Args:
            screen: Pygame surface to draw on
            state: Current simulation state
            gui_elements: List of GUI elements to draw
            show_info: Whether to show simulation info
        """
        # Draw background
        screen.blit(self.background, (0, 0))
        
        # Draw ball
        self.draw_ball_with_shadow(screen, state['ball'], state['ground_y'])
        
        # Draw simulation info
        self.draw_simulation_info(screen, state, show_info)
        
        # Draw control labels
        self.draw_control_labels(screen)
        
        # Draw controls info
        self.draw_controls_info(screen, state)
        
        # Draw GUI elements
        if gui_elements:
            for element in gui_elements:
                element.draw(screen)
    
    def get_background(self) -> pygame.Surface:
        """Get the pre-rendered background surface."""
        return self.background.copy()
    
    def draw_simulation(self, screen: pygame.Surface, state: Dict[str, Any], 
                       show_info: bool = True) -> None:
        """
        Draw the complete simulation (compatibility method).
        
        Args:
            screen: Pygame surface to draw on
            state: Current simulation state
            show_info: Whether to show simulation info
        """
        # This is a wrapper around render_frame for backward compatibility
        self.render_frame(screen, state, None, show_info)
    
    def draw_gui_elements(self, screen: pygame.Surface, gui_elements: List) -> None:
        """
        Draw GUI elements on the screen.
        
        Args:
            screen: Pygame surface to draw on
            gui_elements: List of GUI elements to draw
        """
        for element in gui_elements:
            element.draw(screen)


class WebSimulationRenderer:
    """Simplified renderer for web-based simulation (coordinate conversion only)."""
    
    def __init__(self, width: int = 800, height: int = 600):
        """
        Initialize web renderer.
        
        Args:
            width: Canvas width
            height: Canvas height
        """
        self.width = width
        self.height = height
        logger.debug(f"Web renderer initialized for {width}x{height}")
    
    def physics_to_canvas_y(self, physics_y: float, canvas_height: int) -> float:
        """
        Convert physics y-coordinate to canvas y-coordinate.
        
        Args:
            physics_y: Y coordinate in physics space
            canvas_height: Height of the canvas
            
        Returns:
            Y coordinate in canvas space
        """
        # In physics coordinates: y=0 is ground, positive is up
        # In canvas coordinates: y=0 is top, positive is down
        ground_offset = 100  # Pixels from bottom of canvas
        physics_height = canvas_height - ground_offset
        
        # Flip and offset
        return canvas_height - ground_offset - physics_y
    
    def canvas_to_physics_y(self, canvas_y: float, canvas_height: int) -> float:
        """
        Convert canvas y-coordinate to physics y-coordinate.
        
        Args:
            canvas_y: Y coordinate in canvas space
            canvas_height: Height of the canvas
            
        Returns:
            Y coordinate in physics space
        """
        ground_offset = 100  # Pixels from bottom of canvas
        return (canvas_height - ground_offset) - canvas_y 
"""Rendering system for the physics simulation."""

import pygame
import pygame.gfxdraw
from typing import Optional, Tuple
from pathlib import Path
import logging

from config import (
    BALL_TEXTURE_PATH, DEFAULT_BALL_COLOR, SHADOW_COLOR, 
    SHADOW_MAX_ALPHA, SHADOW_HEIGHT, BACKGROUND_COLOR,
    GROUND_COLOR, GRID_COLOR, GRID_SPACING, GROUND_LINE_THICKNESS,
    CONTROL_PANEL_WIDTH, CONTROL_PANEL_BACKGROUND, CONTROL_PANEL_BORDER
)
from physics import Ball, PhysicsState

logger = logging.getLogger(__name__)

class TextureManager:
    """Manages loading and caching of textures."""
    
    def __init__(self):
        self._textures: dict[str, Optional[pygame.Surface]] = {}
    
    def load_texture(self, path: str, size: Optional[Tuple[int, int]] = None) -> Optional[pygame.Surface]:
        """Load a texture from file, with optional resizing."""
        cache_key = f"{path}_{size}"
        
        if cache_key in self._textures:
            return self._textures[cache_key]
        
        try:
            texture = pygame.image.load(path)
            if size:
                texture = pygame.transform.scale(texture, size)
            self._textures[cache_key] = texture
            logger.info(f"Loaded texture: {path}")
            return texture
        except (pygame.error, FileNotFoundError, OSError) as e:
            logger.warning(f"Could not load texture {path}: {e}")
            self._textures[cache_key] = None
            return None
    
    def clear_cache(self) -> None:
        """Clear the texture cache."""
        self._textures.clear()

class BallRenderer:
    """Renders ball objects."""
    
    def __init__(self, texture_manager: TextureManager):
        self.texture_manager = texture_manager
        self._cached_textures: dict[int, Optional[pygame.Surface]] = {}
    
    def _get_ball_texture(self, radius: float) -> Optional[pygame.Surface]:
        """Get cached ball texture for the given radius."""
        radius_key = int(radius * 2)  # Use diameter as key
        
        if radius_key not in self._cached_textures:
            size = (radius_key, radius_key)
            texture = self.texture_manager.load_texture(BALL_TEXTURE_PATH, size)
            self._cached_textures[radius_key] = texture
        
        return self._cached_textures[radius_key]
    
    def draw_shadow(self, screen: pygame.Surface, ball: Ball, ground_y: float) -> None:
        """Draw a shadow for the ball."""
        shadow_alpha = max(0, SHADOW_MAX_ALPHA - int(abs(ball.state.y - ground_y) / 2))
        if shadow_alpha > 0:
            shadow_color = (*SHADOW_COLOR, shadow_alpha)
            try:
                pygame.gfxdraw.filled_ellipse(
                    screen, 
                    int(ball.state.x), 
                    int(ground_y), 
                    int(ball.radius), 
                    SHADOW_HEIGHT, 
                    shadow_color
                )
            except pygame.error:
                # Fallback if gfxdraw fails
                pass
    
    def draw_ball(self, screen: pygame.Surface, ball: Ball) -> None:
        """Draw a ball on the screen."""
        texture = self._get_ball_texture(ball.radius)
        
        if texture:
            # Draw with texture
            texture_rect = texture.get_rect()
            texture_rect.center = (int(ball.state.x), int(ball.state.y))
            screen.blit(texture, texture_rect)
        else:
            # Fallback to simple circle
            pygame.draw.circle(
                screen, 
                DEFAULT_BALL_COLOR, 
                (int(ball.state.x), int(ball.state.y)), 
                int(ball.radius)
            )
    
    def draw(self, screen: pygame.Surface, ball: Ball, ground_y: float) -> None:
        """Draw ball with shadow."""
        self.draw_shadow(screen, ball, ground_y)
        self.draw_ball(screen, ball)

class BackgroundRenderer:
    """Renders the static background elements."""
    
    def __init__(self, width: int, height: int, ground_y: float):
        self.width = width
        self.height = height
        self.ground_y = ground_y
        self.background: Optional[pygame.Surface] = None
    
    def create_background(self, screen: pygame.Surface) -> pygame.Surface:
        """Create and cache the background surface."""
        if self.background is None:
            self.background = screen.copy()
            self._render_background()
        return self.background
    
    def _render_background(self) -> None:
        """Render the background elements."""
        if self.background is None:
            return
        
        # Fill background
        self.background.fill(BACKGROUND_COLOR)
        
        # Draw ground line
        pygame.draw.line(
            self.background, 
            GROUND_COLOR, 
            (0, self.ground_y), 
            (self.width, self.ground_y), 
            GROUND_LINE_THICKNESS
        )
        
        # Draw grid lines
        self._draw_grid()
        
        # Draw control panel background
        self._draw_control_panel()
    
    def _draw_grid(self) -> None:
        """Draw the grid lines."""
        if self.background is None:
            return
        
        # Vertical lines (don't draw under control panel)
        for x in range(0, self.width - CONTROL_PANEL_WIDTH, GRID_SPACING):
            pygame.draw.line(
                self.background, 
                GRID_COLOR, 
                (x, 0), 
                (x, self.ground_y), 
                1
            )
        
        # Horizontal lines
        for y in range(0, int(self.ground_y), GRID_SPACING):
            pygame.draw.line(
                self.background, 
                GRID_COLOR, 
                (0, y), 
                (self.width - CONTROL_PANEL_WIDTH, y), 
                1
            )
    
    def _draw_control_panel(self) -> None:
        """Draw the control panel background."""
        if self.background is None:
            return
        
        panel_rect = pygame.Rect(
            self.width - CONTROL_PANEL_WIDTH, 
            0, 
            CONTROL_PANEL_WIDTH, 
            self.height
        )
        pygame.draw.rect(self.background, CONTROL_PANEL_BACKGROUND, panel_rect)
        pygame.draw.line(
            self.background, 
            CONTROL_PANEL_BORDER, 
            (self.width - CONTROL_PANEL_WIDTH, 0), 
            (self.width - CONTROL_PANEL_WIDTH, self.height), 
            2
        )
    
    def invalidate(self) -> None:
        """Invalidate the cached background."""
        self.background = None

class Renderer:
    """Main rendering system."""
    
    def __init__(self, width: int, height: int, ground_y: float):
        self.width = width
        self.height = height
        self.ground_y = ground_y
        
        # Initialize components
        self.texture_manager = TextureManager()
        self.ball_renderer = BallRenderer(self.texture_manager)
        self.background_renderer = BackgroundRenderer(width, height, ground_y)
    
    def render_frame(self, screen: pygame.Surface, ball: Ball) -> None:
        """Render a complete frame."""
        # Draw background
        background = self.background_renderer.create_background(screen)
        screen.blit(background, (0, 0))
        
        # Draw ball
        self.ball_renderer.draw(screen, ball, self.ground_y)
    
    def cleanup(self) -> None:
        """Clean up renderer resources."""
        self.texture_manager.clear_cache()
        self.background_renderer.invalidate() 
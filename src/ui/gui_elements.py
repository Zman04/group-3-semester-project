"""
GUI Elements Module

Contains all GUI element classes for the physics simulation.
"""

import pygame
from abc import ABC, abstractmethod
from typing import Optional, Callable

try:
    from ..config.constants import UIConfig
    from ..config.logging_config import get_logger
except ImportError:
    # Fallback for direct execution
    from config.constants import UIConfig
    from config.logging_config import get_logger

logger = get_logger(__name__)


class GUIElement(ABC):
    """Base class for GUI elements."""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.active = False
        self.visible = True
        logger.debug(f"Created {self.__class__.__name__} at ({x}, {y})")
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events. Return True if event was consumed."""
        pass
    
    def update(self, dt: float) -> None:
        """Update the element."""
        pass
    
    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the element."""
        pass


class Button(GUIElement):
    """A clickable button."""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 callback: Optional[Callable[[], None]] = None):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.font = pygame.font.Font(None, UIConfig.DEFAULT_FONT_SIZE)
        self.pressed = False
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                logger.debug(f"Button '{self.text}' pressed")
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed and self.rect.collidepoint(event.pos):
                if self.callback:
                    logger.debug(f"Button '{self.text}' clicked")
                    self.callback()
                self.pressed = False
                return True
            self.pressed = False
        return False
    
    def draw(self, screen: pygame.Surface) -> None:
        if not self.visible:
            return
            
        # Button color based on state
        color = UIConfig.BUTTON_PRESSED_COLOR if self.pressed else UIConfig.BUTTON_COLOR
        
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, UIConfig.BORDER_COLOR, self.rect, 2)
        
        # Center text
        text_surface = self.font.render(self.text, True, UIConfig.TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)


class InputField(GUIElement):
    """A text input field."""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 placeholder: str = "", max_length: int = 20):
        super().__init__(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.max_length = max_length
        self.font = pygame.font.Font(None, UIConfig.SMALL_FONT_SIZE)
        self.cursor_pos = 0
        self.cursor_visible = True
        self.cursor_timer = 0.0
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            was_active = self.active
            self.active = self.rect.collidepoint(event.pos)
            if self.active and not was_active:
                logger.debug("Input field activated")
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
    
    def update(self, dt: float) -> None:
        # Cursor blinking
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0.0
    
    def draw(self, screen: pygame.Surface) -> None:
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
    
    def __init__(self, x: int, y: int, size: int, text: str, 
                 checked: bool = False, callback: Optional[Callable[[bool], None]] = None):
        super().__init__(x, y, size, size)
        self.text = text
        self.checked = checked
        self.callback = callback
        self.font = pygame.font.Font(None, UIConfig.SMALL_FONT_SIZE)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                logger.debug(f"Checkbox '{self.text}' toggled to {self.checked}")
                if self.callback:
                    self.callback(self.checked)
                return True
        return False
    
    def draw(self, screen: pygame.Surface) -> None:
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
        text_surface = self.font.render(self.text, True, UIConfig.TEXT_COLOR)
        text_rect = text_surface.get_rect()
        text_rect.centery = self.rect.centery
        text_rect.x = self.rect.right + 10
        screen.blit(text_surface, text_rect) 
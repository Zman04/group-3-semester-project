"""GUI system for the physics simulation."""

import pygame
from typing import Optional, List, Callable, Any
from abc import ABC, abstractmethod
import logging

from config import (
    BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_SPACING, INPUT_WIDTH, INPUT_HEIGHT,
    BUTTON_COLOR, BUTTON_PRESSED_COLOR, BUTTON_BORDER_COLOR,
    INPUT_ACTIVE_COLOR, INPUT_INACTIVE_COLOR, INPUT_BORDER_ACTIVE, INPUT_BORDER_INACTIVE,
    TEXT_COLOR, TEXT_PLACEHOLDER_COLOR, TEXT_LABEL_COLOR, TEXT_HELPER_COLOR,
    FONT_SIZE_NORMAL, FONT_SIZE_SMALL, CONTROL_PANEL_WIDTH,
    CURSOR_BLINK_RATE, INFO_PANEL_X, INFO_PANEL_Y, INFO_LINE_HEIGHT,
    CONTROLS_INFO_Y_OFFSET
)

logger = logging.getLogger(__name__)

class GUIElement(ABC):
    """Base class for GUI elements."""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.active = False
        self.visible = True
        self.enabled = True
    
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
    
    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the element."""
        self.enabled = enabled
    
    def set_visible(self, visible: bool) -> None:
        """Show or hide the element."""
        self.visible = visible

class Button(GUIElement):
    """A clickable button."""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 text: str, callback: Optional[Callable] = None):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.pressed = False
        self._font = pygame.font.Font(None, FONT_SIZE_NORMAL)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed and self.rect.collidepoint(event.pos):
                if self.callback:
                    try:
                        self.callback()
                    except Exception as e:
                        logger.error(f"Error in button callback: {e}")
                self.pressed = False
                return True
            self.pressed = False
        return False
    
    def draw(self, screen: pygame.Surface) -> None:
        if not self.visible:
            return
            
        # Button color based on state
        if not self.enabled:
            color = (100, 100, 100)
            border_color = (150, 150, 150)
        elif self.pressed:
            color = BUTTON_PRESSED_COLOR
            border_color = BUTTON_BORDER_COLOR
        else:
            color = BUTTON_COLOR
            border_color = BUTTON_BORDER_COLOR
        
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, border_color, self.rect, 2)
        
        # Center text
        text_color = TEXT_COLOR if self.enabled else (150, 150, 150)
        text_surface = self._font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def set_text(self, text: str) -> None:
        """Update button text."""
        self.text = text

class InputField(GUIElement):
    """A text input field."""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 placeholder: str = "", max_length: int = 20):
        super().__init__(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.max_length = max_length
        self.cursor_pos = 0
        self.cursor_visible = True
        self.cursor_timer = 0.0
        self._font = pygame.font.Font(None, FONT_SIZE_SMALL)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            was_active = self.active
            self.active = self.rect.collidepoint(event.pos)
            return self.active or was_active
        elif event.type == pygame.KEYDOWN and self.active:
            return self._handle_key_event(event)
        return False
    
    def _handle_key_event(self, event: pygame.event.Event) -> bool:
        """Handle keyboard input."""
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
    
    def update(self, dt: float) -> None:
        """Update cursor blinking."""
        self.cursor_timer += dt
        if self.cursor_timer >= CURSOR_BLINK_RATE:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0.0
    
    def draw(self, screen: pygame.Surface) -> None:
        if not self.visible:
            return
            
        # Background
        if not self.enabled:
            bg_color = (200, 200, 200)
            border_color = (150, 150, 150)
        elif self.active:
            bg_color = INPUT_ACTIVE_COLOR
            border_color = INPUT_BORDER_ACTIVE
        else:
            bg_color = INPUT_INACTIVE_COLOR
            border_color = INPUT_BORDER_INACTIVE
        
        pygame.draw.rect(screen, bg_color, self.rect)
        pygame.draw.rect(screen, border_color, self.rect, 2)
        
        # Text
        display_text = self.text if self.text else self.placeholder
        text_color = (0, 0, 0) if self.text else TEXT_PLACEHOLDER_COLOR
        if not self.enabled:
            text_color = (150, 150, 150)
        
        text_surface = self._font.render(display_text, True, text_color)
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
        if self.active and self.cursor_visible and self.enabled:
            cursor_text = self.text[:self.cursor_pos] if self.text else ""
            cursor_width = self._font.size(cursor_text)[0]
            cursor_x = self.rect.x + 5 + cursor_width
            cursor_y1 = self.rect.y + 3
            cursor_y2 = self.rect.y + self.rect.height - 3
            pygame.draw.line(screen, (0, 0, 0), (cursor_x, cursor_y1), (cursor_x, cursor_y2), 1)
    
    def set_text(self, text: str) -> None:
        """Set the input text."""
        self.text = text[:self.max_length]
        self.cursor_pos = len(self.text)
    
    def clear(self) -> None:
        """Clear the input field."""
        self.text = ""
        self.cursor_pos = 0

class Checkbox(GUIElement):
    """A checkbox element."""
    
    def __init__(self, x: int, y: int, size: int, text: str, 
                 checked: bool = False, callback: Optional[Callable[[bool], None]] = None):
        super().__init__(x, y, size, size)
        self.text = text
        self.checked = checked
        self.callback = callback
        self._font = pygame.font.Font(None, FONT_SIZE_SMALL)
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.visible or not self.enabled:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                if self.callback:
                    try:
                        self.callback(self.checked)
                    except Exception as e:
                        logger.error(f"Error in checkbox callback: {e}")
                return True
        return False
    
    def draw(self, screen: pygame.Surface) -> None:
        if not self.visible:
            return
            
        # Checkbox
        bg_color = (255, 255, 255) if self.enabled else (200, 200, 200)
        border_color = (150, 150, 150)
        
        pygame.draw.rect(screen, bg_color, self.rect)
        pygame.draw.rect(screen, border_color, self.rect, 2)
        
        # Checkmark
        if self.checked:
            checkmark_color = (0, 150, 0) if self.enabled else (100, 100, 100)
            points = [
                (self.rect.x + 3, self.rect.y + self.rect.height // 2),
                (self.rect.x + self.rect.width // 2, self.rect.y + self.rect.height - 4),
                (self.rect.x + self.rect.width - 3, self.rect.y + 3)
            ]
            pygame.draw.lines(screen, checkmark_color, False, points, 3)
        
        # Text
        text_color = TEXT_COLOR if self.enabled else (150, 150, 150)
        text_surface = self._font.render(self.text, True, text_color)
        text_rect = text_surface.get_rect()
        text_rect.centery = self.rect.centery
        text_rect.x = self.rect.right + 10
        screen.blit(text_surface, text_rect)
    
    def set_checked(self, checked: bool) -> None:
        """Set the checkbox state."""
        self.checked = checked

class Label:
    """A simple text label (not interactive)."""
    
    def __init__(self, x: int, y: int, text: str, color: tuple = TEXT_LABEL_COLOR, 
                 font_size: int = FONT_SIZE_SMALL):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.visible = True
        self._font = pygame.font.Font(None, font_size)
    
    def draw(self, screen: pygame.Surface) -> None:
        if self.visible:
            text_surface = self._font.render(self.text, True, self.color)
            screen.blit(text_surface, (self.x, self.y))
    
    def set_text(self, text: str) -> None:
        """Update label text."""
        self.text = text

class GUIManager:
    """Manages the GUI system."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.elements: List[GUIElement] = []
        self.labels: List[Label] = []
        self._font = pygame.font.Font(None, FONT_SIZE_NORMAL)
        self._small_font = pygame.font.Font(None, FONT_SIZE_SMALL)
        
    def add_element(self, element: GUIElement) -> None:
        """Add a GUI element."""
        self.elements.append(element)
    
    def add_label(self, label: Label) -> None:
        """Add a label."""
        self.labels.append(label)
    
    def remove_element(self, element: GUIElement) -> None:
        """Remove a GUI element."""
        if element in self.elements:
            self.elements.remove(element)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events for all elements. Returns True if consumed."""
        for element in self.elements:
            if element.handle_event(event):
                return True
        return False
    
    def update(self, dt: float) -> None:
        """Update all elements."""
        for element in self.elements:
            element.update(dt)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw all elements."""
        for element in self.elements:
            element.draw(screen)
        for label in self.labels:
            label.draw(screen)
    
    def create_control_panel(self, callbacks: dict) -> None:
        """Create the control panel GUI."""
        panel_x = self.width - CONTROL_PANEL_WIDTH + 10
        y_offset = 20
        
        # Play/Pause button
        play_pause_btn = Button(
            panel_x, y_offset, BUTTON_WIDTH, BUTTON_HEIGHT, 
            "Play", callbacks.get('toggle_play_pause')
        )
        self.add_element(play_pause_btn)
        callbacks['play_pause_button'] = play_pause_btn  # Store reference
        y_offset += BUTTON_SPACING
        
        # Reset button
        reset_btn = Button(
            panel_x, y_offset, BUTTON_WIDTH, BUTTON_HEIGHT, 
            "Reset", callbacks.get('reset')
        )
        self.add_element(reset_btn)
        y_offset += BUTTON_SPACING
        
        # Step button
        step_btn = Button(
            panel_x, y_offset, BUTTON_WIDTH, BUTTON_HEIGHT, 
            "Step +1s", callbacks.get('step_one_second')
        )
        self.add_element(step_btn)
        y_offset += BUTTON_SPACING + 5
        
        # Step mode toggle
        step_mode_btn = Button(
            panel_x, y_offset, INPUT_WIDTH, INPUT_HEIGHT, 
            "Step: Seconds", callbacks.get('toggle_step_mode')
        )
        self.add_element(step_mode_btn)
        callbacks['step_mode_button'] = step_mode_btn  # Store reference
        y_offset += BUTTON_SPACING - 5
        
        # Step value input
        step_label = Label(panel_x, y_offset, "Step Value (seconds):", TEXT_LABEL_COLOR)
        self.add_label(step_label)
        callbacks['step_label'] = step_label  # Store reference
        y_offset += 20
        
        helper_label = Label(panel_x, y_offset, "(+/- values allowed)", TEXT_HELPER_COLOR)
        self.add_label(helper_label)
        y_offset += 20
        
        step_input = InputField(panel_x, y_offset, INPUT_WIDTH, INPUT_HEIGHT, "1.0", 15)
        self.add_element(step_input)
        callbacks['step_input'] = step_input  # Store reference
        y_offset += 35
        
        # Custom step button
        custom_step_btn = Button(
            panel_x, y_offset, BUTTON_WIDTH, BUTTON_HEIGHT, 
            "Step", callbacks.get('step_custom')
        )
        self.add_element(custom_step_btn)
        y_offset += BUTTON_SPACING + 10
        
        # Set time input
        time_label = Label(panel_x, y_offset, "Set Time (s):", TEXT_LABEL_COLOR)
        self.add_label(time_label)
        y_offset += 20
        
        time_input = InputField(panel_x, y_offset, INPUT_WIDTH, INPUT_HEIGHT, "0.0", 15)
        self.add_element(time_input)
        callbacks['time_input'] = time_input  # Store reference
        y_offset += 35
        
        # Set time button
        set_time_btn = Button(
            panel_x, y_offset, BUTTON_WIDTH, BUTTON_HEIGHT, 
            "Set Time", callbacks.get('set_time')
        )
        self.add_element(set_time_btn)
        y_offset += BUTTON_SPACING + 10
        
        # Auto-pause checkbox
        auto_pause_cb = Checkbox(
            panel_x, y_offset, 20, "Auto-pause after step", 
            False, callbacks.get('toggle_auto_pause')
        )
        self.add_element(auto_pause_cb)
        callbacks['auto_pause_checkbox'] = auto_pause_cb  # Store reference
    
    def draw_info_panel(self, screen: pygame.Surface, info_data: dict) -> None:
        """Draw the information panel."""
        info_lines = [
            f"Time: {info_data.get('time', 0):.3f} s",
            f"Position: ({info_data.get('x', 0):.1f}, {info_data.get('y', 0):.1f}) px",
            f"Velocity: {info_data.get('velocity_y', 0):.1f} px/s",
            f"Acceleration: {info_data.get('acceleration_y', 0):.1f} px/s²",
            f"Energy: {info_data.get('total_energy', 0):.0f} J",
            f"Status: {info_data.get('status', 'Unknown')}",
            f"Step Mode: {info_data.get('step_mode', 'Unknown')}",
            f"History: {info_data.get('history_frames', 0)}/{info_data.get('max_history', 0)} frames"
        ]
        
        for i, line in enumerate(info_lines):
            text_surface = self._font.render(line, True, TEXT_COLOR)
            screen.blit(text_surface, (INFO_PANEL_X, INFO_PANEL_Y + i * INFO_LINE_HEIGHT))
    
    def draw_controls_info(self, screen: pygame.Surface, step_mode: str) -> None:
        """Draw the controls information."""
        controls = [
            "Keyboard Controls:",
            "I: Toggle info",
            "ESC: Quit",
            "",
            "Step Controls:",
            "• Use +/- values to go forward/back",
            f"• Current mode: {step_mode}",
            "• Toggle mode with Step button"
        ]
        
        for i, line in enumerate(controls):
            color = TEXT_LABEL_COLOR if line else (100, 100, 100)
            if line.startswith("•"):
                color = (180, 180, 180)
            text_surface = self._small_font.render(line, True, color)
            screen.blit(text_surface, (
                INFO_PANEL_X, 
                self.height - CONTROLS_INFO_Y_OFFSET + i * 18
            ))
    
    def clear(self) -> None:
        """Clear all elements."""
        self.elements.clear()
        self.labels.clear() 
"""Time control and state management for the simulation."""

from typing import Optional, Dict, Any
from collections import deque
from enum import Enum
import logging

from config import TARGET_FPS, HISTORY_MAX_FRAMES, DEFAULT_REWIND_SPEED
from physics import PhysicsState, Ball

logger = logging.getLogger(__name__)

class StepMode(Enum):
    """Step mode enumeration."""
    FRAMES = "frames"
    SECONDS = "seconds"

class TimeManager:
    """Manages simulation time, history, and time control operations."""
    
    def __init__(self, target_fps: int = TARGET_FPS):
        self.target_fps = target_fps
        self.dt = 1.0 / target_fps  # Fixed time step
        self.simulation_time = 0.0
        self.is_playing = False
        self.step_mode = StepMode.SECONDS
        self.auto_pause_after_step = False
        
        # History management
        self.history: deque[PhysicsState] = deque(maxlen=HISTORY_MAX_FRAMES)
        self.time_history: deque[float] = deque(maxlen=HISTORY_MAX_FRAMES)
        
        # Callbacks
        self._on_time_change_callbacks: list[callable] = []
        self._on_play_state_change_callbacks: list[callable] = []
    
    def add_on_time_change_callback(self, callback: callable) -> None:
        """Add a callback to be called when time changes."""
        self._on_time_change_callbacks.append(callback)
    
    def add_on_play_state_change_callback(self, callback: callable) -> None:
        """Add a callback to be called when play state changes."""
        self._on_play_state_change_callbacks.append(callback)
    
    def _notify_time_change(self) -> None:
        """Notify all time change callbacks."""
        for callback in self._on_time_change_callbacks:
            try:
                callback(self.simulation_time)
            except Exception as e:
                logger.error(f"Error in time change callback: {e}")
    
    def _notify_play_state_change(self) -> None:
        """Notify all play state change callbacks."""
        for callback in self._on_play_state_change_callbacks:
            try:
                callback(self.is_playing)
            except Exception as e:
                logger.error(f"Error in play state change callback: {e}")
    
    def save_state(self, ball: Ball) -> None:
        """Save the current state to history."""
        state = ball.get_state()
        self.history.append(state)
        self.time_history.append(self.simulation_time)
    
    def step_time(self, dt: float) -> None:
        """Step simulation time forward by dt."""
        self.simulation_time += dt
        self._notify_time_change()
    
    def toggle_play_pause(self) -> None:
        """Toggle between play and pause states."""
        self.is_playing = not self.is_playing
        self._notify_play_state_change()
        logger.info(f"Simulation {'playing' if self.is_playing else 'paused'}")
    
    def pause(self) -> None:
        """Pause the simulation."""
        if self.is_playing:
            self.is_playing = False
            self._notify_play_state_change()
    
    def play(self) -> None:
        """Start the simulation."""
        if not self.is_playing:
            self.is_playing = True
            self._notify_play_state_change()
    
    def reset(self) -> None:
        """Reset time and history."""
        self.simulation_time = 0.0
        self.is_playing = False
        self.history.clear()
        self.time_history.clear()
        self._notify_time_change()
        self._notify_play_state_change()
        logger.info("Simulation reset")
    
    def step_forward_frames(self, frame_count: int, ball: Ball) -> None:
        """Step forward by a specific number of frames."""
        if frame_count <= 0:
            return
        
        for _ in range(frame_count):
            self.save_state(ball)
            ball.update(self.dt, ball.state.y)  # This needs the ground_y from context
            self.step_time(self.dt)
        
        if self.auto_pause_after_step:
            self.pause()
        
        logger.info(f"Stepped forward {frame_count} frames")
    
    def step_forward_time(self, time_amount: float, ball: Ball, ground_y: float) -> None:
        """Step forward by a specific time amount."""
        if time_amount <= 0:
            return
        
        steps = int(time_amount / self.dt)
        for _ in range(steps):
            self.save_state(ball)
            ball.update(self.dt, ground_y)
            self.step_time(self.dt)
        
        if self.auto_pause_after_step:
            self.pause()
        
        logger.info(f"Stepped forward {time_amount:.3f} seconds")
    
    def step_backward_frames(self, frame_count: int, ball: Ball) -> None:
        """Step backward by a specific number of frames."""
        if frame_count <= 0:
            return
        
        frames_to_rewind = min(frame_count, len(self.history))
        for _ in range(frames_to_rewind):
            if self.history and self.time_history:
                self.history.pop()
                self.time_history.pop()
        
        # Apply the rewound state
        if self.history and self.time_history:
            ball.set_state(self.history[-1])
            self.simulation_time = self.time_history[-1]
        else:
            # If we've exhausted history, reset to initial state
            self.reset()
        
        self._notify_time_change()
        if self.auto_pause_after_step:
            self.pause()
        
        logger.info(f"Stepped backward {frames_to_rewind} frames")
    
    def step_backward_time(self, time_amount: float, ball: Ball) -> None:
        """Step backward by a specific time amount."""
        if time_amount <= 0:
            return
        
        target_time = max(0, self.simulation_time - time_amount)
        if target_time == 0:
            self.reset()
        else:
            self.rewind_to_time(target_time, ball)
        
        if self.auto_pause_after_step:
            self.pause()
        
        logger.info(f"Stepped backward {time_amount:.3f} seconds")
    
    def jump_to_time(self, target_time: float, ball: Ball, ground_y: float) -> None:
        """Jump to a specific time in the simulation."""
        if target_time < 0:
            logger.warning("Target time cannot be negative")
            return
        
        if target_time < self.simulation_time:
            # Need to rewind
            if target_time == 0:
                self.reset()
            else:
                self.rewind_to_time(target_time, ball)
        elif target_time > self.simulation_time:
            # Step forward
            time_diff = target_time - self.simulation_time
            self.step_forward_time(time_diff, ball, ground_y)
        
        if self.auto_pause_after_step:
            self.pause()
        
        logger.info(f"Jumped to time {target_time:.3f} seconds")
    
    def rewind_to_time(self, target_time: float, ball: Ball) -> None:
        """Rewind to the closest available time in history."""
        if not self.time_history:
            self.reset()
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
            ball.set_state(self.history[-1])
            self.simulation_time = self.time_history[-1]
            self._notify_time_change()
    
    def can_rewind(self) -> bool:
        """Check if there are states available for rewinding."""
        return len(self.history) > 1
    
    def get_history_info(self) -> Dict[str, Any]:
        """Get information about the current history state."""
        return {
            'frames_stored': len(self.history),
            'max_frames': self.history.maxlen,
            'time_stored_seconds': len(self.history) / self.target_fps,
            'can_rewind': self.can_rewind(),
            'current_time': self.simulation_time,
            'is_playing': self.is_playing,
            'step_mode': self.step_mode.value
        }
    
    def set_step_mode(self, mode: StepMode) -> None:
        """Set the step mode."""
        self.step_mode = mode
        logger.info(f"Step mode changed to {mode.value}")
    
    def toggle_step_mode(self) -> None:
        """Toggle between frame and time step modes."""
        if self.step_mode == StepMode.FRAMES:
            self.set_step_mode(StepMode.SECONDS)
        else:
            self.set_step_mode(StepMode.FRAMES)
    
    def set_auto_pause(self, enabled: bool) -> None:
        """Set auto-pause after step functionality."""
        self.auto_pause_after_step = enabled
        logger.info(f"Auto-pause after step {'enabled' if enabled else 'disabled'}")
    
    def get_suggested_step_value(self) -> str:
        """Get the suggested step value for the current mode."""
        if self.step_mode == StepMode.FRAMES:
            return str(self.target_fps)  # 1 second worth of frames
        else:
            return "1.0"  # 1 second 
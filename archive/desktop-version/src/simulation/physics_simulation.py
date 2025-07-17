"""
Physics Simulation Module

Core simulation logic separated from rendering and UI concerns.
"""

from typing import Dict, Any, List, Tuple, Optional
from collections import deque

try:
    from ..physics import Ball
    from ..config.constants import SimulationConfig
    from ..config.logging_config import get_logger
except ImportError:
    # Fallback for direct execution
    from physics import Ball
    from config.constants import SimulationConfig
    from config.logging_config import get_logger

logger = get_logger(__name__)


class PhysicsSimulation:
    """Core physics simulation class responsible for time control and state management."""
    
    def __init__(self, width: int = None, height: int = None, coordinate_system: str = "screen"):
        """
        Initialize the physics simulation.
        
        Args:
            width: Simulation width
            height: Simulation height
            coordinate_system: Either "screen" or "physics"
        """
        self.width = width or SimulationConfig.DEFAULT_WIDTH
        self.height = height or SimulationConfig.DEFAULT_HEIGHT
        self.coordinate_system = coordinate_system
        
        # Calculate ground position
        if coordinate_system == "screen":
            self.ground_y = self.height - SimulationConfig.GROUND_OFFSET
            initial_ball_y = SimulationConfig.DEFAULT_SCREEN_START_Y  # Near top of screen
        else:
            self.ground_y = 0  # Physics coordinates
            initial_ball_y = SimulationConfig.DEFAULT_PHYSICS_START_Y  # Above ground in physics coordinates
        
        # Create ball
        self.ball = Ball(self.width // 2, initial_ball_y, coordinate_system=coordinate_system)
        
        # Time control properties
        self.simulation_time = 0.0
        self.is_playing = False
        self.target_fps = SimulationConfig.TARGET_FPS
        self.dt = 1 / self.target_fps
        self.auto_pause_after_step = False
        
        # State management
        self.history = deque(maxlen=SimulationConfig.MAX_HISTORY_FRAMES)
        self.time_history = deque(maxlen=SimulationConfig.MAX_HISTORY_FRAMES)
        
        # Step control
        self.step_by_frames = False
        
        logger.info(f"Created PhysicsSimulation: {self.width}x{self.height}, {coordinate_system} coordinates")
    
    def update(self) -> Dict[str, Any]:
        """Update simulation by one time step."""
        if self.is_playing:
            self.save_state()
            
            if self.coordinate_system == "screen":
                self.ball.update(self.dt, self.ground_y)
                self.ball.check_ground_collision(self.ground_y)
            else:
                self.ball.update(self.dt)
                self.ball.check_ground_collision()
            
            self.simulation_time += self.dt
            
        return self.get_state()
    
    def save_state(self) -> None:
        """Save the current state to history."""
        self.history.append(self.ball.get_state())
        self.time_history.append(self.simulation_time)
    
    def get_state(self) -> Dict[str, Any]:
        """Get current simulation state."""
        state = {
            'ball': self.ball.get_state(),
            'time': self.simulation_time,
            'is_playing': self.is_playing,
            'width': self.width,
            'height': self.height,
            'ground_y': self.ground_y,
            'coordinate_system': self.coordinate_system,
            'step_by_frames': self.step_by_frames,
            'auto_pause_after_step': self.auto_pause_after_step
        }
        
        # Add energy information
        if self.coordinate_system == "screen":
            kinetic, potential, total = self.ball.get_energy(self.ground_y)
        else:
            kinetic, potential, total = self.ball.get_energy()
        
        state['energy'] = {
            'kinetic': kinetic,
            'potential': potential,
            'total': total
        }
        
        return state
    
    def toggle_play_pause(self) -> bool:
        """Toggle between play and pause states."""
        self.is_playing = not self.is_playing
        logger.debug(f"Simulation {'playing' if self.is_playing else 'paused'}")
        return self.is_playing
    
    def reset(self) -> Dict[str, Any]:
        """Reset the simulation to initial state."""
        self.simulation_time = 0.0
        self.is_playing = False
        
        if self.coordinate_system == "screen":
            initial_y = SimulationConfig.DEFAULT_SCREEN_START_Y
        else:
            initial_y = SimulationConfig.DEFAULT_PHYSICS_START_Y
        
        self.ball.reset_to_position(self.width // 2, initial_y)
        self.history.clear()
        self.time_history.clear()
        
        logger.info("Simulation reset")
        return self.get_state()
    
    def step_simulation_time(self, time_step: float) -> Dict[str, Any]:
        """Step the simulation by a specific time amount."""
        if time_step > 0:
            # Step forward
            target_time = self.simulation_time + time_step
            while self.simulation_time < target_time:
                # Don't overshoot the target time
                remaining_time = target_time - self.simulation_time
                current_dt = min(self.dt, remaining_time)
                
                self.save_state()
                if self.coordinate_system == "screen":
                    self.ball.update(current_dt, self.ground_y)
                    self.ball.check_ground_collision(self.ground_y)
                else:
                    self.ball.update(current_dt)
                    self.ball.check_ground_collision()
                self.simulation_time += current_dt
        elif time_step < 0:
            # Step backward
            target_time = max(0, self.simulation_time + time_step)
            if target_time == 0:
                self.reset()
            else:
                self.rewind_to_time(target_time)
        
        if self.auto_pause_after_step:
            self.is_playing = False
        
        logger.debug(f"Stepped simulation by {time_step}s to time {self.simulation_time:.3f}s")
        return self.get_state()
    
    def step_simulation_frames(self, frame_count: int) -> Dict[str, Any]:
        """Step the simulation by a specific number of frames."""
        if frame_count > 0:
            # Step forward
            for _ in range(frame_count):
                self.save_state()
                if self.coordinate_system == "screen":
                    self.ball.update(self.dt, self.ground_y)
                    self.ball.check_ground_collision(self.ground_y)
                else:
                    self.ball.update(self.dt)
                    self.ball.check_ground_collision()
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
                self.reset()
        
        if self.auto_pause_after_step:
            self.is_playing = False
        
        logger.debug(f"Stepped simulation by {frame_count} frames to time {self.simulation_time:.3f}s")
        return self.get_state()
    
    def jump_to_time(self, target_time: float) -> Dict[str, Any]:
        """Jump to a specific time in the simulation."""
        if target_time < 0:
            target_time = 0
        
        if target_time < self.simulation_time:
            # Need to rewind
            if target_time == 0:
                self.reset()
            else:
                self.rewind_to_time(target_time)
        elif target_time > self.simulation_time:
            # Step forward
            time_diff = target_time - self.simulation_time
            self.step_simulation_time(time_diff)
        
        if self.auto_pause_after_step:
            self.is_playing = False
        
        logger.debug(f"Jumped to time {target_time:.3f}s")
        return self.get_state()
    
    def rewind_to_time(self, target_time: float) -> None:
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
            self.ball.set_state(self.history[-1])
            self.simulation_time = self.time_history[-1]
    
    def set_ball_start_position(self, x: float, y: float) -> Dict[str, Any]:
        """Set the ball's starting position and reset."""
        self.simulation_time = 0.0
        self.is_playing = False
        self.ball.reset_to_position(x, y)
        self.history.clear()
        self.time_history.clear()
        
        logger.debug(f"Set ball start position to ({x}, {y})")
        return self.get_state()
    
    def can_rewind(self) -> bool:
        """Check if there are states available for rewinding."""
        return len(self.history) > 1
    
    def get_history_info(self) -> Dict[str, Any]:
        """Get information about the current history state."""
        return {
            'frames_stored': len(self.history),
            'max_frames': self.history.maxlen,
            'time_stored_seconds': len(self.history) / self.target_fps,
            'can_rewind': self.can_rewind()
        }
    
    def toggle_step_unit(self) -> str:
        """Toggle between frame-based and time-based stepping."""
        self.step_by_frames = not self.step_by_frames
        unit = "frames" if self.step_by_frames else "seconds"
        logger.debug(f"Step unit changed to {unit}")
        return unit
    
    def set_auto_pause(self, enabled: bool) -> None:
        """Set auto-pause functionality."""
        self.auto_pause_after_step = enabled
        logger.debug(f"Auto-pause {'enabled' if enabled else 'disabled'}")
    
    def get_ball_position(self) -> Tuple[float, float]:
        """Get current ball position."""
        return self.ball.x, self.ball.y
    
    def get_ball_velocity(self) -> float:
        """Get current ball velocity."""
        return self.ball.velocity_y 
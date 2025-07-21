"""
Test suite for the physics_engine module.

Tests the web-specific PhysicsSimulation class that extends BasePhysicsSimulation.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from physics_engine import PhysicsSimulation


class TestPhysicsSimulation(unittest.TestCase):
    """Test cases for the PhysicsSimulation class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock the logging setup to avoid import issues during testing
        with patch('physics_engine.setup_logging'), \
             patch('physics_engine.get_logger'):
            self.simulation = PhysicsSimulation(width=800, height=600)
    
    def test_initialization_default_values(self):
        """Test that PhysicsSimulation initializes with default values correctly."""
        with patch('physics_engine.setup_logging'), \
             patch('physics_engine.get_logger'):
            sim = PhysicsSimulation()
            
            # Should use default dimensions from config
            self.assertIsNotNone(sim.width)
            self.assertIsNotNone(sim.height)
            self.assertEqual(sim.viewport_padding, 50)
            self.assertEqual(sim.min_viewport_height, 600)
    
    def test_initialization_custom_values(self):
        """Test that PhysicsSimulation initializes with custom values correctly."""
        with patch('physics_engine.setup_logging'), \
             patch('physics_engine.get_logger'):
            sim = PhysicsSimulation(width=1024, height=768)
            
            self.assertEqual(sim.width, 1024)
            self.assertEqual(sim.height, 768)
            self.assertEqual(sim.viewport_padding, 50)
            self.assertEqual(sim.min_viewport_height, 600)
    
    def test_get_viewport_bounds_basic(self):
        """Test basic viewport bounds calculation."""
        # Mock ball with known position
        self.simulation.ball = Mock()
        self.simulation.ball.y = 100
        self.simulation.ball.radius = 20
        
        bounds = self.simulation.get_viewport_bounds()
        
        self.assertEqual(bounds['min_x'], 0)
        self.assertEqual(bounds['max_x'], 800)
        self.assertEqual(bounds['min_y'], -300)
        # max_y should be max of (ball.y + radius + padding, min_viewport_height)
        expected_max_y = max(100 + 20 + 50, 600)
        self.assertEqual(bounds['max_y'], expected_max_y)
    
    def test_get_viewport_bounds_high_ball(self):
        """Test viewport bounds when ball is very high."""
        # Mock ball at high position
        self.simulation.ball = Mock()
        self.simulation.ball.y = 1000
        self.simulation.ball.radius = 20
        
        bounds = self.simulation.get_viewport_bounds()
        
        # When ball is high, max_y should accommodate the ball
        expected_max_y = 1000 + 20 + 50  # ball.y + radius + padding
        self.assertEqual(bounds['max_y'], expected_max_y)
    
    def test_get_viewport_bounds_low_ball(self):
        """Test viewport bounds when ball is low."""
        # Mock ball at low position
        self.simulation.ball = Mock()
        self.simulation.ball.y = 50
        self.simulation.ball.radius = 20
        
        bounds = self.simulation.get_viewport_bounds()
        
        # When ball is low, should use min_viewport_height
        expected_max_y = max(50 + 20 + 50, 600)  # Should be 600 (min_viewport_height)
        self.assertEqual(bounds['max_y'], expected_max_y)


if __name__ == '__main__':
    # Run the tests
    unittest.main() 
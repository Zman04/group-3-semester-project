#!/usr/bin/env python3
"""Simple test to verify the refactored modules work correctly."""

import sys
import os
import time
import logging

# Add the src directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all modules can be imported."""
    logger.info("Testing imports...")
    
    try:
        import config
        logger.info("✅ config module imported successfully")
        
        from physics import Ball, PhysicsEngine, PhysicsState
        logger.info("✅ physics module imported successfully")
        
        from time_manager import TimeManager, StepMode
        logger.info("✅ time_manager module imported successfully")
        
        # Note: renderer and gui modules require pygame, which might not be available in all environments
        try:
            import pygame
            pygame.init()
            
            from renderer import Renderer
            logger.info("✅ renderer module imported successfully")
            
            from gui import GUIManager
            logger.info("✅ gui module imported successfully")
            
            pygame.quit()
            
        except ImportError as e:
            logger.warning(f"⚠️  Could not import pygame modules: {e}")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        return False

def test_physics_engine():
    """Test the physics engine functionality."""
    logger.info("Testing physics engine...")
    
    try:
        from physics import Ball, PhysicsEngine
        from config import DEFAULT_BALL_RADIUS, DEFAULT_BALL_MASS
        
        # Create physics engine
        engine = PhysicsEngine(ground_y=550)
        
        # Create ball
        ball = Ball(x=100, y=100, radius=DEFAULT_BALL_RADIUS, mass=DEFAULT_BALL_MASS)
        engine.add_object(ball)
        
        # Test initial state
        initial_state = ball.get_state()
        assert initial_state.x == 100
        assert initial_state.y == 100
        assert initial_state.velocity_y == 0
        
        # Test physics update
        dt = 1.0 / 60  # 60 FPS
        ball.update(dt, engine.ground_y)
        
        # Ball should have moved due to gravity
        new_state = ball.get_state()
        assert new_state.y > initial_state.y, "Ball should fall due to gravity"
        assert new_state.velocity_y > 0, "Ball should have downward velocity"
        
        # Test energy calculations
        ke = ball.get_kinetic_energy()
        pe = ball.get_potential_energy(engine.ground_y)
        total = ball.get_total_energy(engine.ground_y)
        
        assert ke >= 0, "Kinetic energy should be non-negative"
        assert pe >= 0, "Potential energy should be non-negative"
        assert abs(total - (ke + pe)) < 1e-10, "Total energy should equal KE + PE"
        
        logger.info("✅ Physics engine test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Physics engine test failed: {e}")
        return False

def test_time_manager():
    """Test the time manager functionality."""
    logger.info("Testing time manager...")
    
    try:
        from time_manager import TimeManager, StepMode
        from physics import Ball
        from config import DEFAULT_BALL_RADIUS, DEFAULT_BALL_MASS
        
        # Create time manager and ball
        time_manager = TimeManager(target_fps=60)
        ball = Ball(x=100, y=100, radius=DEFAULT_BALL_RADIUS, mass=DEFAULT_BALL_MASS)
        
        # Test initial state
        assert time_manager.simulation_time == 0.0
        assert not time_manager.is_playing
        assert time_manager.step_mode == StepMode.SECONDS
        
        # Test time stepping
        time_manager.step_forward_time(1.0, ball, 550)
        assert time_manager.simulation_time > 0, "Time should advance"
        
        # Test history
        history_info = time_manager.get_history_info()
        assert history_info['frames_stored'] > 0, "History should contain frames"
        
        # Test mode switching
        time_manager.toggle_step_mode()
        assert time_manager.step_mode == StepMode.FRAMES
        
        # Test reset
        time_manager.reset()
        assert time_manager.simulation_time == 0.0
        assert not time_manager.is_playing
        
        logger.info("✅ Time manager test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Time manager test failed: {e}")
        return False

def test_configuration():
    """Test the configuration module."""
    logger.info("Testing configuration...")
    
    try:
        import config
        
        # Test that key constants exist
        assert hasattr(config, 'WINDOW_WIDTH')
        assert hasattr(config, 'WINDOW_HEIGHT')
        assert hasattr(config, 'DEFAULT_GRAVITY')
        assert hasattr(config, 'DEFAULT_BALL_RADIUS')
        assert hasattr(config, 'TARGET_FPS')
        
        # Test that values are reasonable
        assert config.WINDOW_WIDTH > 0
        assert config.WINDOW_HEIGHT > 0
        assert config.DEFAULT_GRAVITY > 0
        assert config.DEFAULT_BALL_RADIUS > 0
        assert config.TARGET_FPS > 0
        
        logger.info("✅ Configuration test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return False

def test_modular_integration():
    """Test that the modules work together correctly."""
    logger.info("Testing modular integration...")
    
    try:
        from physics import Ball, PhysicsEngine
        from time_manager import TimeManager
        from config import DEFAULT_BALL_RADIUS, DEFAULT_BALL_MASS, TARGET_FPS
        
        # Create integrated system
        engine = PhysicsEngine(ground_y=550)
        time_manager = TimeManager(target_fps=TARGET_FPS)
        ball = Ball(x=100, y=100, radius=DEFAULT_BALL_RADIUS, mass=DEFAULT_BALL_MASS)
        
        engine.add_object(ball)
        
        # Test integrated simulation step
        initial_y = ball.state.y
        time_manager.save_state(ball)
        ball.update(time_manager.dt, engine.ground_y)
        time_manager.step_time(time_manager.dt)
        
        # Verify state changed
        assert ball.state.y != initial_y, "Ball position should change"
        assert time_manager.simulation_time > 0, "Time should advance"
        
        # Test that history was saved
        history_info = time_manager.get_history_info()
        assert history_info['frames_stored'] > 0, "History should be saved"
        
        logger.info("✅ Modular integration test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Modular integration test failed: {e}")
        return False

def run_all_tests():
    """Run all tests and report results."""
    logger.info("Starting refactored code tests...")
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Physics Engine Test", test_physics_engine),
        ("Time Manager Test", test_time_manager),
        ("Integration Test", test_modular_integration),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} ---")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            failed += 1
    
    logger.info(f"\n--- Test Results ---")
    logger.info(f"✅ Passed: {passed}")
    logger.info(f"❌ Failed: {failed}")
    logger.info(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        logger.info("🎉 All tests passed! The refactored code is working correctly.")
        return True
    else:
        logger.error(f"💥 {failed} test(s) failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 
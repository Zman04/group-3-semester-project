#!/usr/bin/env python3
"""
Test runner for the physics simulation project.

Run this script to execute all test cases.
"""

import sys
import os
import unittest

# Add the src directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

def run_tests():
    """Discover and run all tests in the tests directory."""
    # Get the tests directory
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Discover all test files
    loader = unittest.TestLoader()
    suite = loader.discover(tests_dir, pattern='test_*.py')
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code based on test results
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code) 
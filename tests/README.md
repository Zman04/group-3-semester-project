# Tests

This directory contains test cases for the physics simulation project.

## Running Tests

### Option 1: Using the test runner script
```bash
cd tests
python run_tests.py
```

### Option 2: Using unittest directly
```bash
# Run all tests
python -m unittest discover tests -v

# Run specific test file
python -m unittest tests.test_physics_engine -v

# Run from the project root
cd /path/to/project
python -m unittest discover tests -v
```

### Option 3: Run individual test file directly
```bash
cd tests
python test_physics_engine.py
```

## Test Structure

- `test_physics_engine.py`: Comprehensive tests for the PhysicsSimulation class
- `run_tests.py`: Test runner script
- `__init__.py`: Makes tests directory a Python package

## Test Coverage

The tests cover:

### Core Functionality
- Initialization with default and custom values
- Viewport bounds calculation
- Coordinate system conversions (physics ↔ canvas)
- State management
- Ball positioning
- Simulation stepping and resetting

### Edge Cases
- Zero/negative canvas dimensions
- Extreme ball positions
- Large coordinate values
- Below-ground positions

### Mocking Strategy
The tests use `unittest.mock` to:
- Mock the logging system to avoid import dependencies
- Mock the Ball object for predictable test conditions
- Mock parent class methods to isolate testing of web-specific functionality

## Adding New Tests

When adding new tests:
1. Follow the naming convention `test_*.py`
2. Use descriptive test method names starting with `test_`
3. Include docstrings explaining what each test validates
4. Use mocking appropriately to isolate units under test
5. Test both happy path and edge cases 
"""
Refactored Flask Server

Uses the new modular physics engine with improved error handling and logging.
"""

from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO, emit
import os
import threading
import time
from typing import Dict

# Import from physics engine
from physics_engine import PhysicsSimulation
from config import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

# Store simulations for each client
simulations: Dict[str, PhysicsSimulation] = {}


@app.route('/')
def index():
    """Serve the main HTML page."""
    return send_from_directory('static', 'index.html')


@app.route('/<path:path>')
def static_files(path):
    """Serve static files."""
    return send_from_directory('static', path)


@socketio.on('connect')
def handle_connect():
    """Create a new simulation instance for the client."""
    try:
        simulation = PhysicsSimulation()
        simulations[request.sid] = simulation
        emit('simulation_state', simulation.get_state())
        logger.info(f"Client {request.sid} connected, simulation created")
    except Exception as e:
        logger.error(f"Error creating simulation for client {request.sid}: {e}")
        emit('error', {'message': 'Failed to create simulation'})


@socketio.on('disconnect')
def handle_disconnect():
    """Clean up simulation when client disconnects."""
    if request.sid in simulations:
        del simulations[request.sid]
        logger.info(f"Client {request.sid} disconnected, simulation cleaned up")


@socketio.on('toggle_play')
def handle_toggle_play():
    """Toggle play/pause state."""
    if request.sid in simulations:
        try:
            simulation = simulations[request.sid]
            is_playing = simulation.toggle_play_pause()
            emit('simulation_state', simulation.get_state())
            logger.debug(f"Client {request.sid}: play/pause toggled to {is_playing}")
        except Exception as e:
            logger.error(f"Error toggling play/pause for client {request.sid}: {e}")
            emit('error', {'message': 'Failed to toggle play/pause'})


@socketio.on('reset')
def handle_reset():
    """Reset the simulation."""
    if request.sid in simulations:
        try:
            simulation = simulations[request.sid]
            state = simulation.reset()
            emit('simulation_state', state)
            logger.debug(f"Client {request.sid}: simulation reset")
        except Exception as e:
            logger.error(f"Error resetting simulation for client {request.sid}: {e}")
            emit('error', {'message': 'Failed to reset simulation'})


@socketio.on('step')
def handle_step(data):
    """Step the simulation by a specific time amount."""
    if request.sid in simulations:
        try:
            simulation = simulations[request.sid]
            time_step = float(data.get('time_step', 1.0))
            state = simulation.step_simulation_time(time_step)
            emit('simulation_state', state)
            logger.debug(f"Client {request.sid}: stepped by {time_step}s")
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid time step from client {request.sid}: {data}")
            emit('error', {'message': 'Invalid time step value'})
        except Exception as e:
            logger.error(f"Error stepping simulation for client {request.sid}: {e}")
            emit('error', {'message': 'Failed to step simulation'})


@socketio.on('set_start_y')
def handle_set_start_y(data):
    """Set the ball's starting y position."""
    if request.sid in simulations:
        try:
            simulation = simulations[request.sid]
            start_y = float(data.get('start_y', 400))
            state = simulation.set_start_y(start_y)
            emit('simulation_state', state)
            logger.debug(f"Client {request.sid}: start Y set to {start_y}")
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid start Y from client {request.sid}: {data}")
            emit('error', {'message': 'Invalid start Y position'})
        except Exception as e:
            logger.error(f"Error setting start Y for client {request.sid}: {e}")
            emit('error', {'message': 'Failed to set start position'})


def update_simulations():
    """Update all active simulations."""
    logger.info("Starting simulation update loop")
    
    while True:
        try:
            for sid, simulation in list(simulations.items()):
                try:
                    if simulation.is_playing:
                        state = simulation.update()
                        socketio.emit('simulation_state', state, room=sid)
                except Exception as e:
                    logger.error(f"Error updating simulation for client {sid}: {e}")
                    # Remove problematic simulation
                    if sid in simulations:
                        del simulations[sid]
            
            time.sleep(1/144)  # Target 144 FPS
        except Exception as e:
            logger.error(f"Error in simulation update loop: {e}")
            time.sleep(0.1)  # Brief pause before retrying


if __name__ == '__main__':
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    # Start the simulation update loop in a background thread
    update_thread = threading.Thread(target=update_simulations, daemon=True)
    update_thread.start()
    
    print("Starting server at http://localhost:5001")
    print("Features:")
    print("  - Modular physics engine")
    print("  - Improved error handling")
    print("  - Comprehensive logging")
    print("  - Clean separation of concerns")
    
    # Start the server
    try:
        socketio.run(app, host='0.0.0.0', port=5001, debug=True)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise
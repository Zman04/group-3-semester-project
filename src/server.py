from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO, emit
from physics_engine import PhysicsSimulation
import os
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')

# Store simulations for each client
simulations = {}

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

@socketio.on('connect')
def handle_connect():
    """Create a new simulation instance for the client."""
    simulation = PhysicsSimulation()
    simulations[request.sid] = simulation
    emit('simulation_state', simulation.get_state())

@socketio.on('disconnect')
def handle_disconnect():
    """Clean up simulation when client disconnects."""
    if request.sid in simulations:
        del simulations[request.sid]

@socketio.on('toggle_play')
def handle_toggle_play():
    """Toggle play/pause state."""
    if request.sid in simulations:
        simulation = simulations[request.sid]
        is_playing = simulation.toggle_play_pause()
        emit('simulation_state', simulation.get_state())

@socketio.on('reset')
def handle_reset():
    """Reset the simulation."""
    if request.sid in simulations:
        simulation = simulations[request.sid]
        emit('simulation_state', simulation.reset())

@socketio.on('step')
def handle_step(data):
    """Step the simulation by a specific time amount."""
    if request.sid in simulations:
        simulation = simulations[request.sid]
        time_step = float(data.get('time_step', 1.0))
        emit('simulation_state', simulation.step_simulation_time(time_step))

def update_simulations():
    """Update all active simulations."""
    while True:
        for sid, simulation in list(simulations.items()):
            if simulation.is_playing:
                state = simulation.update()
                socketio.emit('simulation_state', state, room=sid)
        time.sleep(1/144)  # Target 144 FPS

if __name__ == '__main__':
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    # Start the simulation update loop in a background thread
    update_thread = threading.Thread(target=update_simulations, daemon=True)
    update_thread.start()
    
    print("Starting server at http://localhost:5001")
    # Start the server
    socketio.run(app, host='0.0.0.0', port=5001, debug=True) 
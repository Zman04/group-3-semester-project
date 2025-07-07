# Physics Ball Simulation Web App

A web-based physics simulation of a bouncing ball with time control features. This application uses Python with Flask for the backend physics engine and HTML5 Canvas with WebSocket for the frontend rendering.

## Features

- Real-time physics simulation
- Play/Pause control
- Step-by-step simulation
- Custom time stepping
- Time travel (jump to specific time)
- Energy and motion information display
- Smooth animations with HTML5 Canvas
- Responsive design

## Requirements

- Python 3.8+
- Flask
- Flask-SocketIO
- Modern web browser with WebSocket support

## Installation

1. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. Start the server:
   ```bash
   cd src
   python server.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5001
   ```

## Controls

- **Play/Pause**: Toggle simulation playback
- **Reset**: Return ball to initial position
- **Step +1s**: Advance simulation by one second
- **Custom Step**: Enter a custom time value (positive or negative) to step forward or backward
- **Set Time**: Jump to a specific time in the simulation

## Technical Details

- Backend: Python Flask with WebSocket support
- Frontend: HTML5, CSS3, JavaScript
- Real-time Communication: Socket.IO
- Graphics: HTML5 Canvas
- Physics Engine: Custom implementation with gravity and elastic collisions

## Project Structure

```
src/
├── physics_engine.py  # Core physics simulation
├── server.py         # Flask server and WebSocket handling
└── static/
    ├── index.html    # Frontend interface
    ├── styles.css    # Styling
    └── app.js        # Frontend logic and rendering
```

## Contributing

Feel free to submit issues and enhancement requests! 
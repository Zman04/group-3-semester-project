# StarkSims

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
├── config/
│   ├── __init__.py
│   ├── constants.py
│   └── logging_config.py
├── physics/
│   ├── __init__.py
│   ├── ball.py
│   └── constants.py
├── physics_engine.py       # Web-specific physics simulation
├── physics_simulation.py   # Core physics simulation logic
├── server.py              # Flask server with WebSocket support
└── static/
    ├── app.js            # Frontend JavaScript
    ├── index.html        # Main web interface
    └── styles.css        # Styling
```

## Archived Desktop Version

The original pygame-based desktop version has been archived to `archive/desktop-version/` for reference. The project now focuses exclusively on the web-based simulation.

## Contributing

You can make recommendations and requests and stuff if you want

## License

This project is licensed under the [MIT License](./LICENSE).  
Feel free to use, modify, or build on this project for educational or commercial purposes.  
Credit is appreciated but not required.

All code was developed by Zachary Austin.


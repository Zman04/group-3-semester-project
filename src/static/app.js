class PhysicsSimulationUI {
    constructor() {
        this.canvas = document.getElementById('simulationCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.socket = io();
        
        // UI elements
        this.playPauseBtn = document.getElementById('playPauseBtn');
        this.resetBtn = document.getElementById('resetBtn');
        this.stepBtn = document.getElementById('stepBtn');
        this.customStepBtn = document.getElementById('customStepBtn');
        this.setTimeBtn = document.getElementById('setTimeBtn');
        this.stepValue = document.getElementById('stepValue');
        this.timeValue = document.getElementById('timeValue');
        this.infoPanel = document.getElementById('simulationInfo');
        
        // Simulation state
        this.state = null;
        
        this.setupEventListeners();
        this.setupWebSocket();
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
    }
    
    setupEventListeners() {
        this.playPauseBtn.addEventListener('click', () => {
            this.socket.emit('toggle_play');
        });
        
        this.resetBtn.addEventListener('click', () => {
            this.socket.emit('reset');
        });
        
        this.stepBtn.addEventListener('click', () => {
            this.socket.emit('step', { time_step: 1.0 });
        });
        
        this.customStepBtn.addEventListener('click', () => {
            const stepTime = parseFloat(this.stepValue.value) || 0;
            this.socket.emit('step', { time_step: stepTime });
        });
        
        this.setTimeBtn.addEventListener('click', () => {
            const targetTime = parseFloat(this.timeValue.value) || 0;
            const currentTime = this.state ? this.state.time : 0;
            const timeStep = targetTime - currentTime;
            this.socket.emit('step', { time_step: timeStep });
        });
    }
    
    setupWebSocket() {
        this.socket.on('simulation_state', (state) => {
            this.state = state;
            this.updateUI();
            this.draw();
        });
    }
    
    resizeCanvas() {
        const container = this.canvas.parentElement;
        this.canvas.width = container.clientWidth;
        this.canvas.height = container.clientHeight;
        this.draw();
    }
    
    updateUI() {
        if (!this.state) return;
        
        // Update play/pause button text
        this.playPauseBtn.textContent = this.state.is_playing ? 'Pause' : 'Play';
        
        // Update info panel
        const ball = this.state.ball;
        const height_above_ground = Math.max(0, this.state.ground_y - (ball.y + ball.radius));
        const kinetic_energy = 0.5 * ball.velocity_y * ball.velocity_y;
        const potential_energy = 6000.0 * height_above_ground;  // Using gravity constant
        const total_energy = kinetic_energy + potential_energy;
        
        this.infoPanel.innerHTML = `
            <div>Time: ${this.state.time.toFixed(3)} s</div>
            <div>Position: (${ball.x.toFixed(1)}, ${ball.y.toFixed(1)}) px</div>
            <div>Velocity: ${ball.velocity_y.toFixed(1)} px/s</div>
            <div>Acceleration: ${ball.acceleration_y.toFixed(1)} px/s²</div>
            <div>Energy: ${total_energy.toFixed(0)} J</div>
            <div>Status: ${this.state.is_playing ? 'Playing' : 'Paused'}</div>
        `;
    }
    
    draw() {
        if (!this.state) return;
        
        const ctx = this.ctx;
        const width = this.canvas.width;
        const height = this.canvas.height;
        
        // Clear canvas
        ctx.fillStyle = '#000000';
        ctx.fillRect(0, 0, width, height);
        
        // Draw grid
        ctx.strokeStyle = '#1a1a1a';
        ctx.lineWidth = 1;
        
        // Vertical grid lines
        for (let x = 0; x < width; x += 50) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, this.state.ground_y);
            ctx.stroke();
        }
        
        // Horizontal grid lines
        for (let y = 0; y < this.state.ground_y; y += 50) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(width, y);
            ctx.stroke();
        }
        
        // Draw ground line
        ctx.strokeStyle = '#6464ff';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(0, this.state.ground_y);
        ctx.lineTo(width, this.state.ground_y);
        ctx.stroke();
        
        // Draw ball shadow
        const ball = this.state.ball;
        const shadowAlpha = Math.max(0, 100 - Math.abs(ball.y - this.state.ground_y) / 2) / 255;
        ctx.fillStyle = `rgba(0, 0, 0, ${shadowAlpha})`;
        ctx.beginPath();
        ctx.ellipse(ball.x, this.state.ground_y, ball.radius, 5, 0, 0, Math.PI * 2);
        ctx.fill();
        
        // Draw ball
        const gradient = ctx.createRadialGradient(
            ball.x - ball.radius/3, ball.y - ball.radius/3,
            ball.radius/10,
            ball.x, ball.y,
            ball.radius
        );
        gradient.addColorStop(0, '#ff8080');
        gradient.addColorStop(1, '#ff0000');
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
        ctx.fill();
    }
}

// Start the simulation when the page loads
window.addEventListener('load', () => {
    new PhysicsSimulationUI();
}); 
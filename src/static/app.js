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
        this.setStartYBtn = document.getElementById('setStartYBtn');
        this.stepValue = document.getElementById('stepValue');
        this.timeValue = document.getElementById('timeValue');
        this.startYValue = document.getElementById('startYValue');
        this.infoPanel = document.getElementById('simulationInfo');
        
        // Viewport elements
        this.viewport = document.getElementById('physicsViewport');
        this.zoomInBtn = document.getElementById('zoomInBtn');
        this.zoomOutBtn = document.getElementById('zoomOutBtn');
        this.resetViewBtn = document.getElementById('resetViewBtn');
        this.zoomLevelSpan = document.querySelector('.zoom-level');
        
        // Physics viewport settings
        this.canvasWidth = 2000;  // Back to reasonable size for performance
        this.canvasHeight = 1500; // Back to reasonable size for performance
        this.zoomLevel = 1.0;     // Current zoom level
        this.panX = 0;            // Pan offset X
        this.panY = 0;            // Pan offset Y
        this.pixelsPerUnit = 1;   // Scale factor for physics units to pixels
        
        // Pan/drag state
        this.isPanning = false;
        this.lastPanX = 0;
        this.lastPanY = 0;
        
        // Simulation state
        this.state = null;
        
        this.setupCanvas();
        this.setupEventListeners();
        this.setupWebSocket();
    }
    
    setupCanvas() {
        // Set fixed canvas size
        this.canvas.width = this.canvasWidth;
        this.canvas.height = this.canvasHeight;
        this.canvas.style.width = `${this.canvasWidth * this.zoomLevel}px`;
        this.canvas.style.height = `${this.canvasHeight * this.zoomLevel}px`;
        
        // Center the view initially
        this.resetView();
    }
    
    setupEventListeners() {
        // Simulation controls
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
        
        this.setStartYBtn.addEventListener('click', () => {
            const startY = parseFloat(this.startYValue.value) || 400;
            this.socket.emit('set_start_y', { start_y: startY });
        });
        
        // Viewport controls
        this.zoomInBtn.addEventListener('click', () => this.zoomIn());
        this.zoomOutBtn.addEventListener('click', () => this.zoomOut());
        this.resetViewBtn.addEventListener('click', () => this.resetView());
        
        // Pan functionality
        this.viewport.addEventListener('mousedown', (e) => this.startPan(e));
        this.viewport.addEventListener('mousemove', (e) => this.handlePan(e));
        this.viewport.addEventListener('mouseup', () => this.endPan());
        this.viewport.addEventListener('mouseleave', () => this.endPan());
        
        // Zoom with mouse wheel
        this.viewport.addEventListener('wheel', (e) => {
            e.preventDefault();
            if (e.deltaY < 0) {
                this.zoomIn();
            } else {
                this.zoomOut();
            }
        });
    }
    
    setupWebSocket() {
        this.socket.on('simulation_state', (state) => {
            this.state = state;
            this.updateUI();
            this.draw();
        });
    }
    
    zoomIn() {
        this.setZoom(this.zoomLevel * 1.2);
    }
    
    zoomOut() {
        this.setZoom(this.zoomLevel / 1.2);
    }
    
    setZoom(newZoom) {
        // Limit zoom out to 3x from default (1.0 / 3 = 0.33)
        this.zoomLevel = Math.max(0.58, Math.min(5.0, newZoom));
        this.canvas.style.width = `${this.canvasWidth * this.zoomLevel}px`;
        this.canvas.style.height = `${this.canvasHeight * this.zoomLevel}px`;
        this.zoomLevelSpan.textContent = `Zoom: ${Math.round(this.zoomLevel * 100)}%`;
    }
    
    resetView() {
        this.zoomLevel = 1.0;
        this.panX = 0;
        this.panY = 0;
        this.setZoom(1.0);
        
        // Align with left and bottom edges
        setTimeout(() => {
            const viewportRect = this.viewport.getBoundingClientRect();
            
            // Scroll to show the left edge
            this.viewport.scrollLeft = 0;
            
            // Scroll to show the bottom, but keep some margin for visibility
            this.viewport.scrollTop = (this.canvasHeight * this.zoomLevel) - viewportRect.height;
        }, 10);
    }
    
    startPan(e) {
        this.isPanning = true;
        this.lastPanX = e.clientX;
        this.lastPanY = e.clientY;
    }
    
    handlePan(e) {
        if (!this.isPanning) return;
        
        const deltaX = e.clientX - this.lastPanX;
        const deltaY = e.clientY - this.lastPanY;
        
        this.viewport.scrollLeft -= deltaX;
        this.viewport.scrollTop -= deltaY;
        
        this.lastPanX = e.clientX;
        this.lastPanY = e.clientY;
    }
    
    endPan() {
        this.isPanning = false;
    }
    
    updateUI() {
        if (!this.state) return;
        
        // Update play/pause button text
        this.playPauseBtn.textContent = this.state.is_playing ? 'Pause' : 'Play';
        
        // Update info panel
        const ball = this.state.ball;
        const height_above_ground = Math.max(0, ball.y - ball.radius); // Subtract radius to get bottom of ball
        // const kinetic_energy = 0.5 * ball.velocity_y * ball.velocity_y;
        // const potential_energy = 6000.0 * height_above_ground;
        // const total_energy = kinetic_energy + potential_energy;
        
        this.infoPanel.innerHTML = `
            <div>Time: ${this.state.time.toFixed(3)} s</div>
            <div>Y Position: ${height_above_ground.toFixed(1)} units</div>
            <div>Velocity: ${ball.velocity_y.toFixed(1)} units/s</div>
            <div>Acceleration: ${ball.acceleration_y.toFixed(1)} units/s²</div>
            <div>Status: ${this.state.is_playing ? 'Playing' : 'Paused'}</div>
        `;
    }
    
    // Transform physics coordinates to canvas coordinates
    physicsToCanvas(physicsX, physicsY) {
        // Fixed coordinate system: 1 physics unit = 1 pixel
        // Ground at y=0 physics -> 100px from bottom of canvas
        return {
            x: physicsX * this.pixelsPerUnit,
            y: (this.canvasHeight - 100) - (physicsY * this.pixelsPerUnit)
        };
    }
    
    draw() {
        if (!this.state) return;
        
        const ctx = this.ctx;
        
        // Clear canvas
        ctx.fillStyle = '#000000';
        ctx.fillRect(0, 0, this.canvasWidth, this.canvasHeight);
        
        // Draw grid
        this.drawGrid(ctx);
        
        // Draw axes
        this.drawAxes(ctx);
        
        // Draw ground line - dynamic based on visible area
        const viewportRect = this.viewport.getBoundingClientRect();
        const visibleWidth = viewportRect.width / this.zoomLevel;
        const scrollLeft = this.viewport.scrollLeft / this.zoomLevel;
        const groundWidth = Math.max(this.canvasWidth, scrollLeft + visibleWidth + 1000);
        
        ctx.strokeStyle = '#6464ff';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(0, this.canvasHeight - 100);
        ctx.lineTo(groundWidth, this.canvasHeight - 100);
        ctx.stroke();
        
        // Transform ball coordinates
        const ball = this.state.ball;
        const ballCanvas = this.physicsToCanvas(ball.x, ball.y);
        const groundCanvas = this.physicsToCanvas(ball.x, 0);
        
        // Draw ball shadow
        const shadowAlpha = Math.max(0, 0.3 - (ball.y / 1000));
        if (shadowAlpha > 0) {
            ctx.fillStyle = `rgba(0, 0, 0, ${shadowAlpha})`;
            ctx.beginPath();
            ctx.ellipse(groundCanvas.x, groundCanvas.y, ball.radius * 0.8, 5, 0, 0, Math.PI * 2);
            ctx.fill();
        }
        
        // Draw ball
        const gradient = ctx.createRadialGradient(
            ballCanvas.x - ball.radius/3, ballCanvas.y - ball.radius/3,
            ball.radius/10,
            ballCanvas.x, ballCanvas.y,
            ball.radius
        );
        gradient.addColorStop(0, '#ffffff');
        //gradient.addColorStop(1, '#ff0000'); // shading
        
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(ballCanvas.x, ballCanvas.y, ball.radius, 0, Math.PI * 2);
        ctx.fill();
    }
    
    drawGrid(ctx) {
        const majorGridSpacing = 100; // 100 physics units
        const minorGridSpacing = 25;  // 25 physics units
        
        // Calculate visible area based on zoom level
        const viewportRect = this.viewport.getBoundingClientRect();
        const visibleWidth = viewportRect.width / this.zoomLevel;
        const visibleHeight = viewportRect.height / this.zoomLevel;
        const scrollLeft = this.viewport.scrollLeft / this.zoomLevel;
        const scrollTop = this.viewport.scrollTop / this.zoomLevel;
        
        // Calculate buffer based on zoom level - more buffer when zoomed out
        const buffer = Math.max(2000, 1000 / this.zoomLevel);
        
        // Extend grid to cover visible area plus buffer
        const gridWidth = Math.max(this.canvasWidth, scrollLeft + visibleWidth + buffer);
        const gridHeight = Math.max(this.canvasHeight, scrollTop + visibleHeight + buffer);
        
        // Calculate the actual range we need to draw, with some padding
        const leftBound = Math.max(0, scrollLeft - buffer);
        const rightBound = Math.min(gridWidth, scrollLeft + visibleWidth + buffer);
        const topBound = Math.max(-300, scrollTop - buffer);
        const bottomBound = Math.min(gridHeight, scrollTop + visibleHeight + buffer);
        
        // Draw minor grid
        ctx.strokeStyle = '#0f0f0f';
        ctx.lineWidth = 0.5;
        
        // Vertical lines
        const startX = Math.floor(leftBound / minorGridSpacing) * minorGridSpacing;
        const endX = Math.ceil(rightBound / minorGridSpacing) * minorGridSpacing;
        for (let x = startX; x <= endX; x += minorGridSpacing) {
            if (x >= 0 && x <= gridWidth) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, gridHeight);
                ctx.stroke();
            }
        }
        
        // Horizontal lines
        const startY = Math.floor(topBound / minorGridSpacing) * minorGridSpacing;
        const endY = Math.ceil(bottomBound / minorGridSpacing) * minorGridSpacing;
        for (let y = startY; y <= endY; y += minorGridSpacing) {
            if (y >= -300 && y <= gridHeight) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(gridWidth, y);
                ctx.stroke();
            }
        }
        
        // Draw major grid
        ctx.strokeStyle = '#1f1f1f';
        ctx.lineWidth = 1;
        
        // Vertical lines
        const startMajorX = Math.floor(leftBound / majorGridSpacing) * majorGridSpacing;
        const endMajorX = Math.ceil(rightBound / majorGridSpacing) * majorGridSpacing;
        for (let x = startMajorX; x <= endMajorX; x += majorGridSpacing) {
            if (x >= 0 && x <= gridWidth) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, gridHeight);
                ctx.stroke();
            }
        }
        
        // Horizontal lines
        const startMajorY = Math.floor(topBound / majorGridSpacing) * majorGridSpacing;
        const endMajorY = Math.ceil(bottomBound / majorGridSpacing) * majorGridSpacing;
        for (let y = startMajorY; y <= endMajorY; y += majorGridSpacing) {
            if (y >= -300 && y <= gridHeight) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(gridWidth, y);
                ctx.stroke();
            }
        }
    }
    
    drawAxes(ctx) {
        const axisX = 100; // Fixed position from left edge
        
        // Draw vertical axis
        ctx.strokeStyle = '#4a4a4a';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(axisX, 0);
        ctx.lineTo(axisX, this.canvasHeight);
        ctx.stroke();
        
        // Draw tick marks and labels
        ctx.fillStyle = '#cccccc';
        ctx.font = '12px monospace';
        ctx.textAlign = 'right';
        ctx.textBaseline = 'middle';
        
        const labelSpacing = 100; // Every 100 physics units
        const maxPhysicsY = this.canvasHeight / this.pixelsPerUnit;
        
        for (let physicsY = 0; physicsY <= maxPhysicsY; physicsY += labelSpacing) {
            const canvasPos = this.physicsToCanvas(0, physicsY);
            
            // Draw tick mark
            ctx.strokeStyle = '#4a4a4a';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(axisX - 8, canvasPos.y);
            ctx.lineTo(axisX + 8, canvasPos.y);
            ctx.stroke();
            
            // Draw label
            ctx.fillStyle = '#cccccc';
            ctx.fillText(`${physicsY}`, axisX - 12, canvasPos.y);
        }
        
        // Add axis label
        ctx.save();
        ctx.translate(30, this.canvasHeight / 2);
        ctx.rotate(-Math.PI / 2);
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 14px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('Height (units)', 0, 0);
        ctx.restore();
        
        // Add ground level indicator
        ctx.fillStyle = '#6464ff';
        ctx.font = 'bold 12px monospace';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'bottom';
        ctx.fillText('Ground Level (0)', axisX + 20, this.canvasHeight - 80);
    }
}

// Start the simulation when the page loads
window.addEventListener('load', () => {
    new PhysicsSimulationUI();
}); 
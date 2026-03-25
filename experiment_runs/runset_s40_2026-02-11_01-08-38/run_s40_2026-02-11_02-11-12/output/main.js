// Initialize the pathfinding visualizer when the page loads
let visualizer;

document.addEventListener('DOMContentLoaded', () => {
    // Initialize the visualizer
    visualizer = new PathfindingVisualizer('pathfinding-canvas', 30);

    // Set initial speed display
    visualizer.updateSpeedDisplay();

    console.log('Pathfinding Visualizer initialized!');
    console.log('Grid size:', visualizer.getGridSize());
    console.log('Start position:', visualizer.getStartPosition());
    console.log('End position:', visualizer.getEndPosition());

    // Welcome message for users
    showWelcomeMessage();
});

function showWelcomeMessage() {
    // Create a subtle notification that disappears after a few seconds
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(255, 255, 255, 0.95);
        padding: 1rem 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
        z-index: 1000;
        max-width: 300px;
        font-family: 'Segoe UI', sans-serif;
        transition: all 0.3s ease;
    `;

    notification.innerHTML = `
        <h4 style="margin: 0 0 0.5rem 0; color: #4a5568; font-size: 0.9rem;">
            🏁 Ready to Race!
        </h4>
        <p style="margin: 0; color: #718096; font-size: 0.8rem; line-height: 1.4;">
            Draw walls, choose your algorithms, and watch them compete to find the best path!
        </p>
    `;

    document.body.appendChild(notification);

    // Fade out and remove after 4 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100px)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 4000);
}

// Utility functions that can be used by both visualization and algorithm code
function heuristic(a, b) {
    // Manhattan distance heuristic for A*
    return Math.abs(a.x - b.x) + Math.abs(a.y - b.y);
}

function getNeighbors(pos, gridSize) {
    // Get valid neighboring cells (4-directional movement)
    const neighbors = [];
    const directions = [
        { x: 0, y: -1 }, // up
        { x: 1, y: 0 },  // right
        { x: 0, y: 1 },  // down
        { x: -1, y: 0 }  // left
    ];

    directions.forEach(dir => {
        const newX = pos.x + dir.x;
        const newY = pos.y + dir.y;

        if (newX >= 0 && newX < gridSize.width && newY >= 0 && newY < gridSize.height) {
            neighbors.push({ x: newX, y: newY });
        }
    });

    return neighbors;
}

function positionsEqual(a, b) {
    return a.x === b.x && a.y === b.y;
}

// Export utilities for algorithm implementations
window.pathfindingUtils = {
    heuristic,
    getNeighbors,
    positionsEqual
};

// Make visualizer globally accessible for algorithm integration
window.visualizer = visualizer;
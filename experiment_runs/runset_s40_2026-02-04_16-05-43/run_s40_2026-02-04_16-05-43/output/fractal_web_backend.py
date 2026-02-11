"""
Interactive Fractal Explorer - Web Backend
A FastAPI server for real-time fractal generation and mathematical education

Created by Alice & Bob (Claude Code collaboration)
Date: 2026-02-04

This backend provides high-performance fractal computation with educational features:
- Real-time Mandelbrot and Julia set generation
- Progressive learning endpoints
- Mathematical insight APIs
- Optimized for web deployment
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import numpy as np
from typing import List, Dict, Any
import base64
import io
from PIL import Image
import json

app = FastAPI(
    title="Interactive Fractal Explorer",
    description="Real-time fractal generation with mathematical education",
    version="1.0.0"
)

# Enable CORS for web deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FractalEngine:
    """High-performance fractal computation engine"""

    def __init__(self):
        self.default_colormap = self._create_colormap()

    def _create_colormap(self, n_colors=256):
        """Create beautiful gradient colormap"""
        # Deep blue to bright yellow gradient
        colors = []
        for i in range(n_colors):
            t = i / (n_colors - 1)
            if t < 0.5:
                # Blue to purple
                r = int(t * 2 * 128)
                g = int(t * 2 * 64)
                b = int(128 + t * 2 * 127)
            else:
                # Purple to yellow
                t_adj = (t - 0.5) * 2
                r = int(128 + t_adj * 127)
                g = int(64 + t_adj * 191)
                b = int(255 - t_adj * 255)
            colors.append([r, g, b])
        return np.array(colors, dtype=np.uint8)

    def generate_mandelbrot(self, width=800, height=800, center_real=0.0, center_imag=0.0,
                          zoom=1.0, max_iter=100):
        """Generate Mandelbrot set with vectorized computation"""

        # Create coordinate grid
        aspect_ratio = width / height
        zoom_factor = 4.0 / zoom

        x = np.linspace(center_real - zoom_factor * aspect_ratio / 2,
                       center_real + zoom_factor * aspect_ratio / 2, width)
        y = np.linspace(center_imag - zoom_factor / 2,
                       center_imag + zoom_factor / 2, height)

        X, Y = np.meshgrid(x, y)
        C = X + 1j * Y

        # Initialize arrays
        Z = np.zeros_like(C)
        iterations = np.zeros(C.shape, dtype=int)

        # Vectorized iteration
        for i in range(max_iter):
            mask = np.abs(Z) <= 2
            Z[mask] = Z[mask]**2 + C[mask]
            iterations[mask] = i

        return iterations, X, Y

    def generate_julia(self, width=800, height=800, c_real=0.0, c_imag=0.0,
                      center_real=0.0, center_imag=0.0, zoom=1.0, max_iter=100):
        """Generate Julia set for given parameter c"""

        # Create coordinate grid
        aspect_ratio = width / height
        zoom_factor = 4.0 / zoom

        x = np.linspace(center_real - zoom_factor * aspect_ratio / 2,
                       center_real + zoom_factor * aspect_ratio / 2, width)
        y = np.linspace(center_imag - zoom_factor / 2,
                       center_imag + zoom_factor / 2, height)

        X, Y = np.meshgrid(x, y)
        Z = X + 1j * Y
        C = complex(c_real, c_imag)

        iterations = np.zeros(Z.shape, dtype=int)

        # Vectorized iteration
        for i in range(max_iter):
            mask = np.abs(Z) <= 2
            Z[mask] = Z[mask]**2 + C
            iterations[mask] = i

        return iterations, X, Y

    def iterations_to_image(self, iterations):
        """Convert iteration counts to RGB image"""
        # Normalize iterations
        max_iter = np.max(iterations)
        if max_iter == 0:
            normalized = np.zeros_like(iterations)
        else:
            normalized = (iterations * (len(self.default_colormap) - 1) / max_iter).astype(int)

        # Apply colormap
        rgb_array = self.default_colormap[normalized]
        return rgb_array

# Initialize fractal engine
fractal_engine = FractalEngine()

@app.get("/")
async def root():
    """Serve main application page"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Interactive Fractal Explorer</title>
        <style>
            body { margin: 0; padding: 20px; font-family: Arial, sans-serif; background: #1a1a1a; color: white; }
            canvas { border: 2px solid #333; cursor: crosshair; }
            .controls { margin: 20px 0; }
            button { padding: 10px 20px; margin: 5px; background: #333; color: white; border: none; cursor: pointer; }
            button:hover { background: #555; }
            .info { margin: 10px 0; padding: 10px; background: #333; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>🌀 Interactive Fractal Explorer</h1>
        <p>Built by Alice & Bob - A collaborative mathematical visualization</p>

        <canvas id="fractalCanvas" width="800" height="600"></canvas>

        <div class="controls">
            <button onclick="resetView()">Reset View</button>
            <button onclick="toggleMode()">Switch to Julia Mode</button>
            <button onclick="increaseIterations()">More Detail</button>
            <button onclick="decreaseIterations()">Less Detail</button>
        </div>

        <div class="info" id="infoPanel">
            <div>Mode: <span id="currentMode">Mandelbrot</span></div>
            <div>Zoom: <span id="currentZoom">1.0x</span></div>
            <div>Iterations: <span id="currentIterations">100</span></div>
            <div>Coordinate: <span id="currentCoord">0 + 0i</span></div>
        </div>

        <div class="info">
            <h3>How to Use:</h3>
            <ul>
                <li>Click to zoom in on any point</li>
                <li>Right-click to zoom out</li>
                <li>Switch between Mandelbrot and Julia sets</li>
                <li>In Mandelbrot mode, click to select Julia parameters</li>
                <li>Adjust detail level for performance vs. quality</li>
            </ul>
        </div>

        <script>
            // Frontend JavaScript will go here
            console.log("Fractal Explorer loaded - Ready for mathematical adventures!");
        </script>
    </body>
    </html>
    """)

@app.get("/api/mandelbrot")
async def get_mandelbrot(
    width: int = Query(800, ge=100, le=2000),
    height: int = Query(600, ge=100, le=2000),
    center_real: float = Query(0.0),
    center_imag: float = Query(0.0),
    zoom: float = Query(1.0, gt=0),
    max_iter: int = Query(100, ge=10, le=1000)
):
    """Generate Mandelbrot set data"""
    try:
        iterations, X, Y = fractal_engine.generate_mandelbrot(
            width, height, center_real, center_imag, zoom, max_iter
        )

        # Convert to RGB image
        rgb_array = fractal_engine.iterations_to_image(iterations)

        # Convert to base64 for web transmission
        img = Image.fromarray(rgb_array, 'RGB')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return {
            "success": True,
            "image_data": f"data:image/png;base64,{img_str}",
            "width": width,
            "height": height,
            "parameters": {
                "center_real": center_real,
                "center_imag": center_imag,
                "zoom": zoom,
                "max_iter": max_iter
            },
            "stats": {
                "min_iterations": int(np.min(iterations)),
                "max_iterations": int(np.max(iterations)),
                "mean_iterations": float(np.mean(iterations))
            }
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/julia")
async def get_julia(
    width: int = Query(800, ge=100, le=2000),
    height: int = Query(600, ge=100, le=2000),
    c_real: float = Query(-0.5),
    c_imag: float = Query(0.6),
    center_real: float = Query(0.0),
    center_imag: float = Query(0.0),
    zoom: float = Query(1.0, gt=0),
    max_iter: int = Query(100, ge=10, le=1000)
):
    """Generate Julia set data"""
    try:
        iterations, X, Y = fractal_engine.generate_julia(
            width, height, c_real, c_imag, center_real, center_imag, zoom, max_iter
        )

        # Convert to RGB image
        rgb_array = fractal_engine.iterations_to_image(iterations)

        # Convert to base64
        img = Image.fromarray(rgb_array, 'RGB')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()

        return {
            "success": True,
            "image_data": f"data:image/png;base64,{img_str}",
            "width": width,
            "height": height,
            "parameters": {
                "c_real": c_real,
                "c_imag": c_imag,
                "center_real": center_real,
                "center_imag": center_imag,
                "zoom": zoom,
                "max_iter": max_iter
            },
            "julia_parameter": f"{c_real:+.3f} {c_imag:+.3f}i"
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/lesson/{lesson_id}")
async def get_lesson(lesson_id: str):
    """Educational content endpoints"""
    lessons = {
        "complex_basics": {
            "title": "Complex Numbers Visualization",
            "description": "Explore how complex numbers work in the Mandelbrot set",
            "steps": [
                {"text": "A complex number has the form a + bi", "action": "highlight_axes"},
                {"text": "The Mandelbrot set uses the formula z = z² + c", "action": "show_formula"},
                {"text": "Click on the point 0 + 0i to see what happens", "action": "guide_click", "coord": [0, 0]}
            ]
        },
        "zoom_exploration": {
            "title": "Infinite Detail",
            "description": "Discover the self-similar patterns in fractals",
            "steps": [
                {"text": "Fractals have infinite detail at any zoom level", "action": "zoom_demo"},
                {"text": "Click on the boundary to explore", "action": "guide_boundary"},
                {"text": "Notice how patterns repeat at different scales", "action": "compare_scales"}
            ]
        }
    }

    return lessons.get(lesson_id, {"error": "Lesson not found"})

if __name__ == "__main__":
    import uvicorn
    print("🌀 Starting Interactive Fractal Explorer Backend...")
    print("💡 Educational mathematics made visual and interactive!")
    uvicorn.run(app, host="0.0.0.0", port=8000)
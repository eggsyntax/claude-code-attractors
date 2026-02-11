#!/usr/bin/env python3
"""
Fractal Education Platform - FastAPI Backend
============================================

A high-performance backend for serving interactive fractal visualizations
to students and educators worldwide. Supports real-time generation,
progressive enhancement, and educational tracking.

Created by: Alice & Bob (Claude Code Collaboration)
Date: 2026-02-04
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Dict, Any
import numpy as np
import io
import base64
from PIL import Image
import asyncio
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Fractal Education Platform",
    description="Interactive fractal visualization for mathematics education",
    version="1.0.0"
)

# Enable CORS for web deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests
class FractalRequest(BaseModel):
    fractal_type: Literal["mandelbrot", "julia"] = "mandelbrot"
    width: int = Field(default=800, ge=100, le=4000)
    height: int = Field(default=600, ge=100, le=3000)
    center_real: float = Field(default=-0.5, ge=-3.0, le=1.0)
    center_imag: float = Field(default=0.0, ge=-2.0, le=2.0)
    zoom: float = Field(default=1.0, ge=0.001, le=10000.0)
    max_iterations: int = Field(default=100, ge=10, le=1000)
    julia_c_real: Optional[float] = Field(default=None, ge=-2.0, le=2.0)
    julia_c_imag: Optional[float] = Field(default=None, ge=-2.0, le=2.0)
    quality: Literal["fast", "medium", "high", "ultra"] = "medium"

class AnimationRequest(BaseModel):
    frames: int = Field(default=60, ge=10, le=300)
    radius: float = Field(default=0.7885, ge=0.1, le=1.0)
    center_real: float = Field(default=-0.8, ge=-2.0, le=1.0)
    center_imag: float = Field(default=0.156, ge=-2.0, le=2.0)
    width: int = Field(default=600, ge=200, le=1200)
    height: int = Field(default=600, ge=200, le=1200)
    quality: Literal["fast", "medium", "high"] = "medium"

class LearningProgress(BaseModel):
    student_id: str
    concept: str
    difficulty_level: int = Field(ge=1, le=10)
    time_spent: float
    interactions: int
    mastery_score: float = Field(ge=0.0, le=1.0)

# Core fractal generation functions (optimized versions of our earlier work)
def generate_mandelbrot(width: int, height: int, center_real: float, center_imag: float,
                       zoom: float, max_iterations: int) -> np.ndarray:
    """Vectorized Mandelbrot set generation with educational annotations."""

    # Calculate coordinate bounds
    aspect_ratio = height / width
    zoom_factor = 3.0 / zoom
    x_min = center_real - zoom_factor
    x_max = center_real + zoom_factor
    y_min = center_imag - zoom_factor * aspect_ratio
    y_max = center_imag + zoom_factor * aspect_ratio

    # Create coordinate arrays
    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    X, Y = np.meshgrid(x, y)
    C = X + 1j * Y

    # Initialize arrays
    Z = np.zeros_like(C)
    iterations = np.zeros(C.shape, dtype=int)

    # Vectorized iteration with escape detection
    for i in range(max_iterations):
        mask = np.abs(Z) <= 2
        Z[mask] = Z[mask]**2 + C[mask]
        iterations[mask] = i

    return iterations

def generate_julia(width: int, height: int, center_real: float, center_imag: float,
                  zoom: float, max_iterations: int, c_real: float, c_imag: float) -> np.ndarray:
    """Vectorized Julia set generation."""

    # Calculate coordinate bounds
    aspect_ratio = height / width
    zoom_factor = 3.0 / zoom
    x_min = center_real - zoom_factor
    x_max = center_real + zoom_factor
    y_min = center_imag - zoom_factor * aspect_ratio
    y_max = center_imag + zoom_factor * aspect_ratio

    # Create coordinate arrays
    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    C = complex(c_real, c_imag)

    # Initialize iteration counter
    iterations = np.zeros(Z.shape, dtype=int)

    # Vectorized iteration
    for i in range(max_iterations):
        mask = np.abs(Z) <= 2
        Z[mask] = Z[mask]**2 + C
        iterations[mask] = i

    return iterations

def apply_educational_colormap(iterations: np.ndarray, fractal_type: str) -> np.ndarray:
    """Apply color mapping optimized for educational visibility."""

    # Normalize iterations
    max_iter = iterations.max()
    normalized = iterations.astype(np.float32) / max_iter if max_iter > 0 else iterations.astype(np.float32)

    if fractal_type == "mandelbrot":
        # Hot colormap for Mandelbrot - emphasizes set boundary
        colors = np.zeros((*iterations.shape, 3), dtype=np.uint8)
        colors[:,:,0] = (255 * np.clip(normalized * 2, 0, 1)).astype(np.uint8)
        colors[:,:,1] = (255 * np.clip(normalized * 2 - 0.5, 0, 1)).astype(np.uint8)
        colors[:,:,2] = (255 * np.clip(normalized * 2 - 1, 0, 1)).astype(np.uint8)
    else:
        # Plasma-like colormap for Julia sets - emphasizes structure
        colors = np.zeros((*iterations.shape, 3), dtype=np.uint8)
        colors[:,:,0] = (255 * (0.5 + 0.5 * np.sin(normalized * np.pi * 4))).astype(np.uint8)
        colors[:,:,1] = (255 * (0.5 + 0.5 * np.sin(normalized * np.pi * 6 + np.pi/3))).astype(np.uint8)
        colors[:,:,2] = (255 * (0.5 + 0.5 * np.sin(normalized * np.pi * 8 + 2*np.pi/3))).astype(np.uint8)

    # Set interior points to black for clear visualization
    interior_mask = iterations >= (max_iter * 0.95)
    colors[interior_mask] = [0, 0, 0]

    return colors

def get_quality_settings(quality: str) -> Dict[str, Any]:
    """Return optimized settings for different quality levels."""
    settings = {
        "fast": {"supersampling": 1, "max_iterations": 50},
        "medium": {"supersampling": 1, "max_iterations": 100},
        "high": {"supersampling": 2, "max_iterations": 200},
        "ultra": {"supersampling": 4, "max_iterations": 400}
    }
    return settings.get(quality, settings["medium"])

# API Endpoints
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main application interface."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Fractal Education Platform</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: 'Segoe UI', system-ui, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { text-align: center; margin-bottom: 30px; }
            .app-container {
                background: rgba(255,255,255,0.1);
                border-radius: 15px;
                padding: 30px;
                backdrop-filter: blur(10px);
            }
            .coming-soon {
                text-align: center;
                font-size: 1.2em;
                margin: 40px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌀 Fractal Education Platform</h1>
                <p>Explore the infinite beauty of mathematics</p>
            </div>
            <div class="app-container">
                <div class="coming-soon">
                    <h2>FastAPI Backend is Live! 🚀</h2>
                    <p>Interactive web interface coming next...</p>
                    <p><strong>Available Endpoints:</strong></p>
                    <ul style="text-align: left; display: inline-block;">
                        <li><code>/generate</code> - Generate fractal images</li>
                        <li><code>/animate</code> - Create animations</li>
                        <li><code>/docs</code> - API documentation</li>
                        <li><code>/health</code> - System status</li>
                    </ul>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.post("/generate")
async def generate_fractal(request: FractalRequest):
    """Generate a fractal image with educational enhancements."""
    start_time = time.time()

    try:
        quality_settings = get_quality_settings(request.quality)
        effective_iterations = min(request.max_iterations, quality_settings["max_iterations"])

        if request.fractal_type == "mandelbrot":
            iterations = generate_mandelbrot(
                request.width, request.height,
                request.center_real, request.center_imag,
                request.zoom, effective_iterations
            )
        else:  # julia
            if request.julia_c_real is None or request.julia_c_imag is None:
                raise HTTPException(status_code=400, detail="Julia set requires c parameter")

            iterations = generate_julia(
                request.width, request.height,
                request.center_real, request.center_imag,
                request.zoom, effective_iterations,
                request.julia_c_real, request.julia_c_imag
            )

        # Apply educational colormap
        colored_image = apply_educational_colormap(iterations, request.fractal_type)

        # Convert to PIL Image and then to base64
        pil_image = Image.fromarray(colored_image, 'RGB')
        img_buffer = io.BytesIO()
        pil_image.save(img_buffer, format='PNG')
        img_str = base64.b64encode(img_buffer.getvalue()).decode()

        generation_time = time.time() - start_time

        return {
            "image_data": f"data:image/png;base64,{img_str}",
            "metadata": {
                "generation_time": round(generation_time, 3),
                "iterations_used": effective_iterations,
                "fractal_type": request.fractal_type,
                "dimensions": f"{request.width}x{request.height}",
                "zoom_level": request.zoom,
                "quality": request.quality,
                "center": [request.center_real, request.center_imag]
            }
        }

    except Exception as e:
        logger.error(f"Error generating fractal: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.post("/animate")
async def generate_animation(request: AnimationRequest):
    """Generate animated Julia set sequence."""

    try:
        frames = []
        angles = np.linspace(0, 2 * np.pi, request.frames)
        quality_settings = get_quality_settings(request.quality)

        for i, angle in enumerate(angles):
            # Calculate Julia parameter on circle
            c_real = request.center_real + request.radius * np.cos(angle)
            c_imag = request.center_imag + request.radius * np.sin(angle)

            # Generate Julia set frame
            iterations = generate_julia(
                request.width, request.height,
                0.0, 0.0, 1.0,  # Fixed view for animation
                quality_settings["max_iterations"],
                c_real, c_imag
            )

            colored_image = apply_educational_colormap(iterations, "julia")
            pil_image = Image.fromarray(colored_image, 'RGB')

            img_buffer = io.BytesIO()
            pil_image.save(img_buffer, format='PNG')
            img_str = base64.b64encode(img_buffer.getvalue()).decode()

            frames.append({
                "frame": i,
                "image_data": f"data:image/png;base64,{img_str}",
                "c_parameter": [round(c_real, 6), round(c_imag, 6)]
            })

        return {
            "frames": frames,
            "metadata": {
                "frame_count": request.frames,
                "dimensions": f"{request.width}x{request.height}",
                "animation_path": f"Circle(center=[{request.center_real}, {request.center_imag}], radius={request.radius})",
                "quality": request.quality
            }
        }

    except Exception as e:
        logger.error(f"Error generating animation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Animation generation failed: {str(e)}")

@app.post("/learning/progress")
async def track_learning_progress(progress: LearningProgress):
    """Track student learning progress for adaptive education."""

    # In a real implementation, this would save to a database
    # For now, we'll return analysis and recommendations

    try:
        # Simple adaptive algorithm
        recommendations = []

        if progress.mastery_score < 0.6:
            recommendations.append({
                "type": "review",
                "message": "Consider reviewing complex number basics",
                "suggested_activity": "interactive_complex_plane"
            })

        if progress.interactions < 10:
            recommendations.append({
                "type": "explore",
                "message": "Try zooming into the boundary regions",
                "suggested_activity": "guided_exploration"
            })

        if progress.time_spent > 30 and progress.mastery_score > 0.8:
            recommendations.append({
                "type": "advance",
                "message": "Ready for Julia set exploration!",
                "suggested_activity": "julia_connection"
            })

        return {
            "student_id": progress.student_id,
            "analysis": {
                "engagement_level": "high" if progress.time_spent > 15 else "medium",
                "conceptual_understanding": "strong" if progress.mastery_score > 0.7 else "developing",
                "exploration_depth": "thorough" if progress.interactions > 20 else "surface"
            },
            "recommendations": recommendations,
            "next_concepts": ["julia_sets", "complex_dynamics", "chaos_theory"] if progress.mastery_score > 0.8 else ["complex_arithmetic", "iteration_concept"]
        }

    except Exception as e:
        logger.error(f"Error tracking progress: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Progress tracking failed: {str(e)}")

@app.get("/health")
async def health_check():
    """System health and performance metrics."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "uptime": "Just started!",
        "capabilities": [
            "mandelbrot_generation",
            "julia_set_generation",
            "animation_creation",
            "educational_tracking",
            "adaptive_learning"
        ],
        "performance": {
            "numpy_available": True,
            "pil_available": True,
            "estimated_generation_speed": "~0.5s for 800x600 medium quality"
        }
    }

if __name__ == "__main__":
    import uvicorn
    print("🌀 Starting Fractal Education Platform Backend...")
    print("📚 Visit http://localhost:8000/docs for API documentation")
    print("🚀 Visit http://localhost:8000 for the web interface")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
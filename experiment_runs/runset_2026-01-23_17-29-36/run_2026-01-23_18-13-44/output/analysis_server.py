#!/usr/bin/env python3
"""
Real-Time Collaborative Code Analysis Server
============================================

A FastAPI-powered web service that provides real-time code analysis capabilities
with team collaboration features, CI/CD integration, and interactive dashboards.

This server extends our Alice+Bob collaborative analysis system into a
production-ready platform that development teams can deploy and use together.

Features:
- Real-time analysis API endpoints
- WebSocket updates for live collaboration
- Team project management
- CI/CD webhook integration
- Interactive dashboard serving
- Analysis result persistence

Authors: Bob & Alice (Collaborative AI Development)
"""

import os
import json
import asyncio
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import tempfile
import shutil
import logging

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from ast_analyzer import CodeAnalyzer
from complexity_analyzer import ComplexityAnalyzer
from dashboard_generator import DashboardGenerator


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalysisRequest(BaseModel):
    """Request model for code analysis."""
    project_name: str
    repository_url: Optional[str] = None
    files: Optional[Dict[str, str]] = None  # filename -> content mapping


class AnalysisResult(BaseModel):
    """Response model for analysis results."""
    project_name: str
    timestamp: datetime
    analysis_id: str
    overview: Dict[str, Any]
    functions: List[Dict[str, Any]]
    classes: List[Dict[str, Any]]
    dependencies: List[Dict[str, str]]
    dashboard_url: str


class WebSocketManager:
    """Manages WebSocket connections for real-time collaboration."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.project_subscribers: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, project_name: Optional[str] = None):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

        if project_name:
            if project_name not in self.project_subscribers:
                self.project_subscribers[project_name] = []
            self.project_subscribers[project_name].append(websocket)

        logger.info(f"New WebSocket connection for project: {project_name}")

    def disconnect(self, websocket: WebSocket, project_name: Optional[str] = None):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        if project_name and project_name in self.project_subscribers:
            if websocket in self.project_subscribers[project_name]:
                self.project_subscribers[project_name].remove(websocket)

        logger.info(f"WebSocket disconnected for project: {project_name}")

    async def broadcast_to_project(self, project_name: str, message: dict):
        """Send a message to all subscribers of a specific project."""
        if project_name not in self.project_subscribers:
            return

        disconnected = []
        for websocket in self.project_subscribers[project_name]:
            try:
                await websocket.send_json(message)
            except:
                disconnected.append(websocket)

        # Clean up disconnected sockets
        for ws in disconnected:
            self.disconnect(ws, project_name)


class AnalysisDatabase:
    """SQLite database for storing analysis results and project metadata."""

    def __init__(self, db_path: str = "analysis_results.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    repository_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_analyzed TIMESTAMP,
                    total_analyses INTEGER DEFAULT 0
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_name TEXT NOT NULL,
                    analysis_id TEXT UNIQUE NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    results_json TEXT NOT NULL,
                    dashboard_path TEXT,
                    FOREIGN KEY (project_name) REFERENCES projects (name)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS analysis_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (analysis_id) REFERENCES analysis_results (analysis_id)
                )
            """)

            conn.commit()

    def save_project(self, name: str, repository_url: Optional[str] = None):
        """Save or update project information."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO projects (name, repository_url, last_analyzed, total_analyses)
                VALUES (?, ?, CURRENT_TIMESTAMP,
                    COALESCE((SELECT total_analyses + 1 FROM projects WHERE name = ?), 1))
            """, (name, repository_url, name))
            conn.commit()

    def save_analysis_result(self, result: AnalysisResult):
        """Save analysis results to database."""
        with sqlite3.connect(self.db_path) as conn:
            results_json = json.dumps({
                'overview': result.overview,
                'functions': result.functions,
                'classes': result.classes,
                'dependencies': result.dependencies
            })

            conn.execute("""
                INSERT INTO analysis_results
                (project_name, analysis_id, results_json, dashboard_path)
                VALUES (?, ?, ?, ?)
            """, (result.project_name, result.analysis_id, results_json, result.dashboard_url))

            # Save key metrics for trending
            if result.overview:
                metrics = [
                    ('total_functions', result.overview.get('total_functions', 0)),
                    ('total_classes', result.overview.get('total_classes', 0)),
                    ('avg_complexity', result.overview.get('avg_complexity', 0)),
                    ('high_complexity_functions', result.overview.get('high_complexity_functions', 0))
                ]

                for metric_name, metric_value in metrics:
                    conn.execute("""
                        INSERT INTO analysis_metrics (analysis_id, metric_name, metric_value)
                        VALUES (?, ?, ?)
                    """, (result.analysis_id, metric_name, metric_value))

            conn.commit()

    def get_project_history(self, project_name: str, limit: int = 10) -> List[Dict]:
        """Get historical analysis results for a project."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT analysis_id, timestamp, dashboard_path
                FROM analysis_results
                WHERE project_name = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (project_name, limit))

            return [dict(row) for row in cursor.fetchall()]

    def get_all_projects(self) -> List[Dict]:
        """Get all projects with their metadata."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT name, repository_url, created_at, last_analyzed, total_analyses
                FROM projects
                ORDER BY last_analyzed DESC
            """)

            return [dict(row) for row in cursor.fetchall()]


# Initialize FastAPI app
app = FastAPI(
    title="Collaborative Code Analysis Platform",
    description="Real-time code analysis with team collaboration features",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
websocket_manager = WebSocketManager()
database = AnalysisDatabase()

# Create directories for static files and dashboards
STATIC_DIR = Path("static")
DASHBOARDS_DIR = Path("dashboards")
STATIC_DIR.mkdir(exist_ok=True)
DASHBOARDS_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/dashboards", StaticFiles(directory=DASHBOARDS_DIR), name="dashboards")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main application page."""
    return """
    <html>
        <head>
            <title>Code Analysis Platform</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: 'Segoe UI', sans-serif;
                    margin: 0;
                    padding: 40px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: white;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    text-align: center;
                }
                .hero {
                    background: rgba(255,255,255,0.1);
                    padding: 40px;
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                    margin-bottom: 30px;
                }
                .features {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }
                .feature {
                    background: rgba(255,255,255,0.1);
                    padding: 20px;
                    border-radius: 10px;
                    backdrop-filter: blur(10px);
                }
                .cta {
                    margin: 40px 0;
                }
                .button {
                    display: inline-block;
                    background: rgba(255,255,255,0.2);
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 8px;
                    margin: 10px;
                    backdrop-filter: blur(10px);
                    transition: all 0.3s ease;
                }
                .button:hover {
                    background: rgba(255,255,255,0.3);
                    transform: translateY(-2px);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="hero">
                    <h1>🔍 Collaborative Code Analysis Platform</h1>
                    <h3>Built by Alice & Bob</h3>
                    <p>Real-time code analysis with interactive visualizations, team collaboration, and CI/CD integration</p>
                </div>

                <div class="features">
                    <div class="feature">
                        <h3>🎯 Smart Analysis</h3>
                        <p>AST-based parsing with sophisticated complexity metrics</p>
                    </div>
                    <div class="feature">
                        <h3>📊 Interactive Dashboards</h3>
                        <p>Beautiful visualizations with real-time updates</p>
                    </div>
                    <div class="feature">
                        <h3>👥 Team Collaboration</h3>
                        <p>Share analysis results and collaborate in real-time</p>
                    </div>
                    <div class="feature">
                        <h3>🔄 CI/CD Integration</h3>
                        <p>Automated analysis on every commit</p>
                    </div>
                </div>

                <div class="cta">
                    <a href="/docs" class="button">📚 API Documentation</a>
                    <a href="/projects" class="button">📂 View Projects</a>
                    <a href="/analyze" class="button">🚀 Start Analysis</a>
                </div>

                <div style="margin-top: 50px; opacity: 0.8;">
                    <p>Built collaboratively by Alice & Bob using FastAPI, WebSockets, and modern web technologies</p>
                </div>
            </div>
        </body>
    </html>
    """


@app.get("/projects", response_model=List[Dict])
async def get_all_projects():
    """Get all projects with their metadata."""
    return database.get_all_projects()


@app.get("/projects/{project_name}/history")
async def get_project_history(project_name: str):
    """Get analysis history for a specific project."""
    history = database.get_project_history(project_name)
    return {"project_name": project_name, "history": history}


@app.post("/analyze", response_model=AnalysisResult)
async def analyze_code(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Analyze code and return results with interactive dashboard."""
    try:
        # Generate unique analysis ID
        analysis_id = f"{request.project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Save project to database
        database.save_project(request.project_name, request.repository_url)

        # Create temporary directory for analysis
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Write files to temporary directory if provided
            if request.files:
                for filename, content in request.files.items():
                    file_path = temp_path / filename
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(content)

            # Create dashboard generator
            generator = DashboardGenerator(str(temp_path))

            # Perform analysis
            results = generator.analyze_project(str(temp_path))

            # Generate dashboard
            dashboard_filename = f"{analysis_id}_dashboard.html"
            dashboard_path = DASHBOARDS_DIR / dashboard_filename
            generator.generate_dashboard(output_filename=str(dashboard_path))

            # Create analysis result
            result = AnalysisResult(
                project_name=request.project_name,
                timestamp=datetime.now(),
                analysis_id=analysis_id,
                overview=results.get('overview', {}),
                functions=results.get('functions', []),
                classes=results.get('classes', []),
                dependencies=results.get('dependencies', []),
                dashboard_url=f"/dashboards/{dashboard_filename}"
            )

            # Save to database
            database.save_analysis_result(result)

            # Broadcast to WebSocket subscribers
            background_tasks.add_task(
                websocket_manager.broadcast_to_project,
                request.project_name,
                {
                    "type": "analysis_complete",
                    "analysis_id": analysis_id,
                    "project_name": request.project_name,
                    "dashboard_url": result.dashboard_url
                }
            )

            logger.info(f"Analysis completed for project: {request.project_name}")
            return result

    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/upload")
async def upload_project(
    project_name: str,
    files: List[UploadFile] = File(...)
):
    """Upload project files for analysis."""
    try:
        file_contents = {}

        for file in files:
            if file.filename and file.filename.endswith('.py'):
                content = await file.read()
                file_contents[file.filename] = content.decode('utf-8')

        if not file_contents:
            raise HTTPException(status_code=400, detail="No Python files found")

        # Create analysis request
        request = AnalysisRequest(
            project_name=project_name,
            files=file_contents
        )

        # Analyze the uploaded files
        result = await analyze_code(request, BackgroundTasks())

        return {
            "message": f"Uploaded and analyzed {len(file_contents)} files",
            "analysis_id": result.analysis_id,
            "dashboard_url": result.dashboard_url
        }

    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.websocket("/ws/{project_name}")
async def websocket_endpoint(websocket: WebSocket, project_name: str):
    """WebSocket endpoint for real-time collaboration."""
    await websocket_manager.connect(websocket, project_name)

    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)

            # Broadcast message to all project subscribers
            await websocket_manager.broadcast_to_project(project_name, {
                "type": "message",
                "project_name": project_name,
                "data": message,
                "timestamp": datetime.now().isoformat()
            })

    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, project_name)
        logger.info(f"Client disconnected from project: {project_name}")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "analysis_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
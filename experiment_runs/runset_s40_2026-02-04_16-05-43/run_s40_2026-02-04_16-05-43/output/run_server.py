#!/usr/bin/env python3
"""
Fractal Explorer Server Launcher
Alice & Bob Collaborative Project - 2026-02-04

Quick launch script for the Interactive Fractal Explorer web application.
This combines our FastAPI backend with the HTML5 frontend for mathematical education.
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['fastapi', 'uvicorn', 'numpy', 'PIL']
    missing_packages = []

    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("❌ Missing required packages:")
        for pkg in missing_packages:
            print(f"   • {pkg}")
        print("\n🔧 Install them with:")
        print("   pip install -r requirements.txt")
        return False

    return True

def setup_static_files():
    """Setup static file serving for the frontend"""
    current_dir = Path(__file__).parent

    # Create static directory if it doesn't exist
    static_dir = current_dir / "static"
    static_dir.mkdir(exist_ok=True)

    # Copy frontend HTML to static directory
    frontend_src = current_dir / "fractal_frontend.html"
    frontend_dst = static_dir / "index.html"

    if frontend_src.exists():
        import shutil
        shutil.copy2(frontend_src, frontend_dst)
        print(f"✅ Frontend copied to {frontend_dst}")
    else:
        print("⚠️  Frontend HTML not found!")

def update_backend_for_static():
    """Update the backend to serve static files"""
    backend_file = Path(__file__).parent / "fractal_web_backend.py"

    if not backend_file.exists():
        print("❌ Backend file not found!")
        return

    # Read the backend file
    with open(backend_file, 'r') as f:
        content = f.read()

    # Add static files mounting if not already present
    if "app.mount" not in content:
        mount_code = '''
# Mount static files
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_index():
    """Serve the main application"""
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")
'''
        # Insert after CORS setup
        cors_index = content.find('app.add_middleware(')
        if cors_index != -1:
            # Find the end of the CORS block
            cors_end = content.find(')', cors_index)
            cors_end = content.find('\n', cors_end) + 1

            # Insert the mount code
            updated_content = content[:cors_end] + mount_code + content[cors_end:]

            with open(backend_file, 'w') as f:
                f.write(updated_content)

            print("✅ Backend updated to serve static files")

def main():
    print("🌀 Interactive Fractal Explorer - Server Launcher")
    print("   A Mathematical Adventure by Alice & Bob\n")

    # Check dependencies
    if not check_dependencies():
        return 1

    # Setup static file serving
    setup_static_files()
    update_backend_for_static()

    # Get the backend file path
    backend_file = Path(__file__).parent / "fractal_web_backend.py"

    if not backend_file.exists():
        print("❌ Backend file not found!")
        return 1

    print("🚀 Starting Fractal Explorer server...")
    print("   Server will be available at: http://localhost:8000")
    print("   Press Ctrl+C to stop the server\n")

    try:
        # Launch the server
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "fractal_web_backend:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ], cwd=Path(__file__).parent)

    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
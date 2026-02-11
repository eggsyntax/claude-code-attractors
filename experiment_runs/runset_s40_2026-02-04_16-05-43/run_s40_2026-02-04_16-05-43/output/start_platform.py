#!/usr/bin/env python3
"""
Fractal Education Platform Launcher
==================================

Quick start script for the interactive fractal education platform.
Demonstrates real-time streaming and progressive enhancement capabilities.

Usage:
    python start_platform.py [--port 8000] [--host 0.0.0.0] [--dev]

Created by: Alice & Bob (Claude Code Collaboration)
"""

import asyncio
import subprocess
import sys
import webbrowser
import argparse
import time
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'fastapi', 'uvicorn', 'numpy', 'PIL', 'pydantic'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package if package != 'PIL' else 'Pillow')

    if missing_packages:
        print("❌ Missing required packages:")
        for pkg in missing_packages:
            print(f"   - {pkg}")
        print("\n🔧 Install with:")
        print(f"   pip install {' '.join(missing_packages)}")
        print("   OR")
        print("   pip install -r requirements.txt")
        return False

    return True

def print_banner():
    """Print startup banner."""
    banner = """
    ═══════════════════════════════════════════════════════════
     🌀  FRACTAL EDUCATION PLATFORM  🌀
    ═══════════════════════════════════════════════════════════

     Interactive mathematical exploration through fractals

     Features:
     ✨ Real-time Mandelbrot & Julia set generation
     🎮 Interactive zoom and pan controls
     🎬 Smooth animation system
     📊 Educational progress tracking
     🚀 High-performance vectorized computation

     A collaboration between Alice & Bob

    ═══════════════════════════════════════════════════════════
    """
    print(banner)

async def demonstrate_capabilities():
    """Show platform capabilities with sample API calls."""
    print("🔬 Platform Capabilities Demo:")
    print("──────────────────────────────")

    import json
    import aiohttp

    async with aiohttp.ClientSession() as session:
        # Health check
        try:
            async with session.get('http://localhost:8000/health') as resp:
                if resp.status == 200:
                    health = await resp.json()
                    print(f"✅ Backend Status: {health['status']}")
                    print(f"⚡ Performance: {health['performance']['estimated_generation_speed']}")
        except:
            print("⏳ Backend starting up...")

        # Sample generation (after server is ready)
        await asyncio.sleep(2)

        try:
            sample_request = {
                "fractal_type": "mandelbrot",
                "width": 400,
                "height": 300,
                "center_real": -0.5,
                "center_imag": 0.0,
                "zoom": 1.0,
                "max_iterations": 100,
                "quality": "fast"
            }

            async with session.post('http://localhost:8000/generate',
                                  json=sample_request) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    print(f"🎨 Sample Generation: {data['metadata']['generation_time']}s")
                    print(f"📐 Dimensions: {data['metadata']['dimensions']}")
        except Exception as e:
            print(f"⚠️ Sample generation: {e}")

def start_server(host='localhost', port=8000, dev_mode=False):
    """Start the FastAPI server."""

    server_file = Path(__file__).parent / 'fractal_server.py'

    if not server_file.exists():
        print(f"❌ Server file not found: {server_file}")
        return None

    cmd = [
        sys.executable, '-m', 'uvicorn',
        'fractal_server:app',
        '--host', host,
        '--port', str(port)
    ]

    if dev_mode:
        cmd.extend(['--reload', '--log-level', 'debug'])

    print(f"🚀 Starting server on http://{host}:{port}")
    print(f"📁 Serving from: {server_file.parent}")

    return subprocess.Popen(cmd, cwd=server_file.parent)

async def main():
    parser = argparse.ArgumentParser(description='Start the Fractal Education Platform')
    parser.add_argument('--port', type=int, default=8000, help='Port to run on')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--dev', action='store_true', help='Enable development mode')
    parser.add_argument('--no-browser', action='store_true', help='Don\'t open browser automatically')
    args = parser.parse_args()

    print_banner()

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Start server
    server_process = start_server(args.host, args.port, args.dev)
    if not server_process:
        sys.exit(1)

    # Wait for server to start
    print("⏳ Waiting for server to start...")
    await asyncio.sleep(3)

    # Demonstrate capabilities
    await demonstrate_capabilities()

    # Open browser
    if not args.no_browser:
        url = f"http://{args.host}:{args.port}"
        print(f"🌐 Opening {url} in browser...")
        webbrowser.open(url)

        # Also open the interactive explorer
        explorer_url = f"http://{args.host}:{args.port}/fractal_explorer.html"
        print(f"🎮 Interactive Explorer: {explorer_url}")
        time.sleep(1)
        webbrowser.open(explorer_url)

    print("\n" + "="*60)
    print("🎉 FRACTAL PLATFORM IS READY!")
    print("="*60)
    print(f"🖥️  API Documentation: http://{args.host}:{args.port}/docs")
    print(f"🎮 Interactive Explorer: http://{args.host}:{args.port}/fractal_explorer.html")
    print(f"📊 Health Check: http://{args.host}:{args.port}/health")
    print("\n💡 Usage Tips:")
    print("   • Left-click canvas to zoom in")
    print("   • Right-click canvas to zoom out")
    print("   • Press 'j' to switch between Mandelbrot/Julia modes")
    print("   • Press 'a' to create animations")
    print("   • Press 'r' to reset view")
    print("\n⌨️  Press Ctrl+C to stop the server")
    print("="*60)

    try:
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down platform...")
        server_process.terminate()
        server_process.wait()
        print("✅ Platform stopped successfully")

if __name__ == '__main__':
    # Handle the HTML file serving
    server_file = Path(__file__).parent / 'fractal_server.py'
    html_file = Path(__file__).parent / 'fractal_explorer.html'

    # Add static file serving to the FastAPI app if HTML exists
    if html_file.exists():
        # Quick patch to serve the HTML file
        with open(server_file, 'r') as f:
            content = f.read()

        if 'app.mount' not in content:
            # Add static file serving
            additional_code = '''
# Serve static files
from fastapi.staticfiles import StaticFiles

@app.get("/fractal_explorer.html", response_class=HTMLResponse)
async def serve_explorer():
    """Serve the interactive fractal explorer."""
    html_file = Path(__file__).parent / "fractal_explorer.html"
    if html_file.exists():
        return HTMLResponse(html_file.read_text())
    else:
        return HTMLResponse("<h1>Fractal Explorer not found</h1>", status_code=404)
'''

            # Insert before the main block
            content = content.replace(
                'if __name__ == "__main__":',
                additional_code + '\nif __name__ == "__main__":'
            )

            # Add Path import
            if 'from pathlib import Path' not in content:
                content = content.replace(
                    'import logging',
                    'import logging\nfrom pathlib import Path'
                )

            with open(server_file, 'w') as f:
                f.write(content)

    # Run the platform
    asyncio.run(main())
#!/usr/bin/env python3
"""
CodeMentor Startup Script

Launches the CodeMentor collaborative code review assistant with all components:
- Real-time collaboration server
- Web interface server
- Analysis engine
- Educational modules

Usage:
    python start_codementor.py [--port PORT] [--host HOST] [--dev]

Author: Bob (Claude Code Instance)
Integrates: Alice's analysis engine + Bob's collaboration features
"""

import asyncio
import argparse
import logging
import signal
import sys
import webbrowser
from pathlib import Path
import subprocess
from datetime import datetime

try:
    import websockets
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    import threading
except ImportError as e:
    print(f"Missing required dependencies: {e}")
    print("Please install requirements:")
    print("pip install websockets")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CodeMentorLauncher:
    """Main launcher for the CodeMentor application"""

    def __init__(self, host="localhost", websocket_port=8765, web_port=8000, dev_mode=False):
        self.host = host
        self.websocket_port = websocket_port
        self.web_port = web_port
        self.dev_mode = dev_mode
        self.tasks = []
        self.should_stop = False

        # Setup signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.should_stop = True

        # Cancel all running tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()

    async def start_collaboration_server(self):
        """Start the WebSocket collaboration server"""
        try:
            # Import the collaboration server
            from realtime_collaboration import RealTimeCollaborationServer

            server = RealTimeCollaborationServer(self.host, self.websocket_port)
            logger.info(f"Starting collaboration server on ws://{self.host}:{self.websocket_port}")

            # Start the server
            await server.start_server()

        except Exception as e:
            logger.error(f"Failed to start collaboration server: {e}")
            raise

    def start_web_server(self):
        """Start the HTTP server for the web interface"""
        try:
            class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    # Set the directory to serve files from
                    super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)

                def log_message(self, format, *args):
                    # Custom logging to integrate with our logger
                    logger.info(f"HTTP: {format % args}")

                def end_headers(self):
                    # Add CORS headers for development
                    if self.command == 'OPTIONS':
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                        self.send_header('Access-Control-Allow-Headers', '*')
                    super().end_headers()

            # Create and start the HTTP server
            httpd = HTTPServer((self.host, self.web_port), CustomHTTPRequestHandler)
            logger.info(f"Starting web server on http://{self.host}:{self.web_port}")

            # Run the server in a separate thread
            def run_server():
                try:
                    httpd.serve_forever()
                except Exception as e:
                    if not self.should_stop:
                        logger.error(f"Web server error: {e}")

            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()

            return httpd

        except Exception as e:
            logger.error(f"Failed to start web server: {e}")
            raise

    def check_dependencies(self):
        """Check if all required dependencies are available"""
        dependencies = [
            ('websockets', 'WebSocket support for real-time collaboration'),
            ('json', 'JSON parsing (built-in)'),
            ('asyncio', 'Asynchronous I/O (built-in)'),
            ('threading', 'Threading support (built-in)'),
            ('http.server', 'HTTP server (built-in)')
        ]

        missing = []
        for dep, description in dependencies:
            try:
                __import__(dep)
                logger.info(f"✓ {dep}: {description}")
            except ImportError:
                missing.append((dep, description))
                logger.error(f"✗ {dep}: {description} - NOT FOUND")

        if missing:
            logger.error("Missing dependencies:")
            for dep, desc in missing:
                logger.error(f"  - {dep}: {desc}")
            return False

        return True

    def create_example_files(self):
        """Create example files for demonstration"""
        examples_dir = Path(__file__).parent / "examples"
        examples_dir.mkdir(exist_ok=True)

        # Python example
        python_example = examples_dir / "example.py"
        if not python_example.exists():
            python_example.write_text('''#!/usr/bin/env python3
"""
Example Python file for CodeMentor analysis
Contains various patterns and potential issues for demonstration
"""

import os
import json
from typing import List, Dict, Optional

class DataProcessor:
    """Example class demonstrating various patterns"""

    # Singleton pattern (potential issue)
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.data_cache = {}  # Global state
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load configuration - potential security issue"""
        config_path = os.getenv('CONFIG_PATH', 'config.json')

        # No input validation
        with open(config_path, 'r') as f:
            return json.load(f)

    def process_items(self, items: List[str]) -> List[str]:
        """Process items - potential performance issue"""
        results = []

        for item in items:
            # Expensive operation in loop
            result = self._expensive_operation(item)
            results.append(result)

        return results

    def _expensive_operation(self, item: str) -> str:
        """Simulate expensive operation"""
        return item.upper() * 1000  # Memory inefficient

# Factory pattern example
class ProcessorFactory:
    """Factory for creating processors"""

    @staticmethod
    def create_processor(processor_type: str):
        if processor_type == 'data':
            return DataProcessor()
        else:
            raise ValueError(f"Unknown processor type: {processor_type}")

# Main execution
if __name__ == "__main__":
    processor = ProcessorFactory.create_processor('data')
    results = processor.process_items(['hello', 'world'])
    print(f"Processed {len(results)} items")
''')

        # JavaScript example
        js_example = examples_dir / "example.js"
        if not js_example.exists():
            js_example.write_text('''/**
 * Example JavaScript file for CodeMentor analysis
 * Contains various patterns and potential issues
 */

// Global state (potential issue)
let applicationState = {
    users: {},
    sessions: {}
};

class UserManager {
    constructor() {
        this.cache = new Map();
    }

    // Async/await without proper error handling
    async getUser(userId) {
        if (this.cache.has(userId)) {
            return this.cache.get(userId);
        }

        // Potential security issue - no input validation
        const response = await fetch(`/api/users/${userId}`);
        const user = await response.json();

        this.cache.set(userId, user);
        return user;
    }

    // Observer pattern implementation
    addUserObserver(callback) {
        if (!this.observers) {
            this.observers = [];
        }
        this.observers.push(callback);
    }

    notifyObservers(user) {
        if (this.observers) {
            this.observers.forEach(callback => {
                try {
                    callback(user);
                } catch (error) {
                    console.error('Observer error:', error);
                }
            });
        }
    }

    // Memory leak potential
    processUsers(users) {
        const results = [];

        users.forEach(user => {
            // Creating functions in loop
            const processor = () => {
                return user.name.toUpperCase();
            };
            results.push(processor());
        });

        return results;
    }
}

// Strategy pattern example
class ValidationStrategy {
    validate(data) {
        throw new Error('Must implement validate method');
    }
}

class EmailValidation extends ValidationStrategy {
    validate(email) {
        // Weak email validation
        return email.includes('@');
    }
}

class PasswordValidation extends ValidationStrategy {
    validate(password) {
        // Weak password validation
        return password.length > 6;
    }
}

// Usage with potential issues
const userManager = new UserManager();

// Missing error handling
userManager.getUser('123').then(user => {
    console.log('User:', user);
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { UserManager, ValidationStrategy };
}
''')

        logger.info(f"Created example files in {examples_dir}")

    async def run(self):
        """Run the complete CodeMentor application"""
        logger.info("🚀 Starting CodeMentor - Collaborative Code Review Assistant")
        logger.info(f"Session started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Check dependencies
        if not self.check_dependencies():
            logger.error("Missing required dependencies. Cannot start.")
            return 1

        # Create example files
        if self.dev_mode:
            self.create_example_files()

        try:
            # Start web server
            web_server = self.start_web_server()

            # Start collaboration server in background
            collaboration_task = asyncio.create_task(
                self.start_collaboration_server()
            )
            self.tasks.append(collaboration_task)

            # Open browser if in dev mode
            if self.dev_mode:
                browser_url = f"http://{self.host}:{self.web_port}/web_interface.html"
                logger.info(f"Opening browser to: {browser_url}")
                try:
                    webbrowser.open(browser_url)
                except Exception as e:
                    logger.warning(f"Could not open browser: {e}")

            # Print startup information
            self.print_startup_info()

            # Wait for tasks to complete or interruption
            try:
                await asyncio.gather(*self.tasks)
            except asyncio.CancelledError:
                logger.info("Tasks cancelled, shutting down...")

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Application error: {e}")
            return 1
        finally:
            # Cleanup
            logger.info("Shutting down...")
            if 'web_server' in locals():
                web_server.shutdown()

        logger.info("CodeMentor shutdown complete")
        return 0

    def print_startup_info(self):
        """Print helpful startup information"""
        logger.info("=" * 60)
        logger.info("🤖 CodeMentor is now running!")
        logger.info("=" * 60)
        logger.info(f"📊 Web Interface:     http://{self.host}:{self.web_port}/web_interface.html")
        logger.info(f"🔗 WebSocket Server:  ws://{self.host}:{self.websocket_port}")
        logger.info(f"🏠 Base Directory:    {Path(__file__).parent}")
        logger.info("=" * 60)
        logger.info("💡 Quick Start:")
        logger.info("   1. Open the web interface in your browser")
        logger.info("   2. Select a file from the sidebar")
        logger.info("   3. Click 'Analyze File' to start analysis")
        logger.info("   4. Review findings and collaborate with team members")
        logger.info("=" * 60)

        if self.dev_mode:
            logger.info("🔧 Development Mode:")
            logger.info("   - Example files created in ./examples/")
            logger.info("   - Browser should open automatically")
            logger.info("   - Extra logging enabled")
            logger.info("=" * 60)

        logger.info("Press Ctrl+C to stop")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="CodeMentor - Collaborative Code Review Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python start_codementor.py                    # Start with default settings
    python start_codementor.py --port 8080       # Custom web port
    python start_codementor.py --dev             # Development mode
    python start_codementor.py --host 0.0.0.0    # Listen on all interfaces
        """
    )

    parser.add_argument(
        '--host',
        default='localhost',
        help='Host to bind servers to (default: localhost)'
    )

    parser.add_argument(
        '--web-port',
        type=int,
        default=8000,
        help='Port for web interface (default: 8000)'
    )

    parser.add_argument(
        '--ws-port',
        type=int,
        default=8765,
        help='Port for WebSocket server (default: 8765)'
    )

    parser.add_argument(
        '--dev',
        action='store_true',
        help='Enable development mode (creates examples, opens browser)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create and run launcher
    launcher = CodeMentorLauncher(
        host=args.host,
        websocket_port=args.ws_port,
        web_port=args.web_port,
        dev_mode=args.dev
    )

    # Run the application
    try:
        exit_code = asyncio.run(launcher.run())
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
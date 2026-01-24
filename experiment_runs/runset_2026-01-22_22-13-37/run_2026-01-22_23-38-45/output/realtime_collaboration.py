#!/usr/bin/env python3
"""
CodeMentor Real-Time Collaboration Server

Provides WebSocket-based real-time collaboration features for the CodeMentor
collaborative code review assistant. Enables multiple developers to work
together on code analysis sessions with live updates.

Author: Bob (Claude Code Instance)
Integrates with: Alice's analysis engine and collaborative analyzer
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, asdict
import websockets
import logging

from collaborative_analyzer import CollaborativeAnalyzer, AnalysisSession


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CollaborationEvent:
    """Represents a real-time collaboration event"""
    event_type: str  # 'analysis_update', 'comment_added', 'pattern_reviewed', 'user_joined'
    session_id: str
    user_id: str
    timestamp: datetime
    data: Dict[str, Any]
    event_id: str = None

    def __post_init__(self):
        if self.event_id is None:
            self.event_id = str(uuid.uuid4())


class RealTimeCollaborationServer:
    """WebSocket server for real-time collaborative code analysis"""

    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.active_sessions: Dict[str, AnalysisSession] = {}
        self.session_participants: Dict[str, Set[websockets.WebSocketServerProtocol]] = {}
        self.user_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.event_history: Dict[str, List[CollaborationEvent]] = {}
        self.analyzer = CollaborativeAnalyzer()

    async def register_user(self, websocket, user_id: str, session_id: str):
        """Register a user for a collaboration session"""
        self.user_connections[user_id] = websocket

        if session_id not in self.session_participants:
            self.session_participants[session_id] = set()

        self.session_participants[session_id].add(websocket)

        # Notify other participants
        await self.broadcast_to_session(session_id, {
            "type": "user_joined",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "participants_count": len(self.session_participants[session_id])
        }, exclude=websocket)

        logger.info(f"User {user_id} joined session {session_id}")

    async def unregister_user(self, websocket, user_id: str, session_id: str):
        """Unregister a user from a collaboration session"""
        if user_id in self.user_connections:
            del self.user_connections[user_id]

        if session_id in self.session_participants:
            self.session_participants[session_id].discard(websocket)

            # Notify remaining participants
            await self.broadcast_to_session(session_id, {
                "type": "user_left",
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "participants_count": len(self.session_participants[session_id])
            })

        logger.info(f"User {user_id} left session {session_id}")

    async def broadcast_to_session(self, session_id: str, message: Dict, exclude=None):
        """Broadcast a message to all participants in a session"""
        if session_id not in self.session_participants:
            return

        participants = self.session_participants[session_id].copy()
        if exclude:
            participants.discard(exclude)

        if participants:
            await asyncio.gather(
                *[self.send_safe(ws, message) for ws in participants],
                return_exceptions=True
            )

    async def send_safe(self, websocket, message: Dict):
        """Safely send a message to a websocket connection"""
        try:
            await websocket.send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Attempted to send to closed connection")
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    async def handle_analysis_request(self, session_id: str, user_id: str, data: Dict):
        """Handle a collaborative analysis request"""
        file_path = data.get('file_path')
        options = data.get('options', {})

        if not file_path:
            return {"error": "file_path is required"}

        # Start analysis
        await self.broadcast_to_session(session_id, {
            "type": "analysis_started",
            "file_path": file_path,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        })

        try:
            # Run analysis using Alice's analyzer
            results = await asyncio.to_thread(
                self.analyzer.analyze_file, file_path, options
            )

            # Broadcast results
            await self.broadcast_to_session(session_id, {
                "type": "analysis_completed",
                "file_path": file_path,
                "results": [asdict(result) for result in results],
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            })

            return {"status": "success", "results_count": len(results)}

        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            await self.broadcast_to_session(session_id, {
                "type": "analysis_error",
                "file_path": file_path,
                "error": error_msg,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            })
            return {"error": error_msg}

    async def handle_comment_add(self, session_id: str, user_id: str, data: Dict):
        """Handle adding a comment to a finding"""
        finding_id = data.get('finding_id')
        comment_text = data.get('comment')

        if not finding_id or not comment_text:
            return {"error": "finding_id and comment are required"}

        comment = {
            "id": str(uuid.uuid4()),
            "finding_id": finding_id,
            "user_id": user_id,
            "text": comment_text,
            "timestamp": datetime.now().isoformat()
        }

        # Broadcast comment to all session participants
        await self.broadcast_to_session(session_id, {
            "type": "comment_added",
            "comment": comment
        })

        return {"status": "success", "comment_id": comment["id"]}

    async def handle_pattern_review(self, session_id: str, user_id: str, data: Dict):
        """Handle reviewing a detected pattern"""
        finding_id = data.get('finding_id')
        review_status = data.get('status')  # 'approved', 'rejected', 'needs_discussion'
        review_comment = data.get('comment', '')

        if not finding_id or not review_status:
            return {"error": "finding_id and status are required"}

        review = {
            "finding_id": finding_id,
            "reviewer_id": user_id,
            "status": review_status,
            "comment": review_comment,
            "timestamp": datetime.now().isoformat()
        }

        # Broadcast review to all session participants
        await self.broadcast_to_session(session_id, {
            "type": "pattern_reviewed",
            "review": review
        })

        return {"status": "success", "review": review}

    async def handle_session_command(self, session_id: str, user_id: str, data: Dict):
        """Handle session-level commands"""
        command = data.get('command')

        if command == 'get_status':
            session = self.active_sessions.get(session_id)
            if session:
                return {
                    "status": "success",
                    "session": asdict(session),
                    "participants": len(self.session_participants.get(session_id, set())),
                    "recent_events": [
                        asdict(event) for event in
                        self.event_history.get(session_id, [])[-10:]
                    ]
                }
            else:
                return {"error": "Session not found"}

        elif command == 'pause':
            if session_id in self.active_sessions:
                self.active_sessions[session_id].status = 'paused'
                await self.broadcast_to_session(session_id, {
                    "type": "session_paused",
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat()
                })
                return {"status": "success", "message": "Session paused"}

        elif command == 'resume':
            if session_id in self.active_sessions:
                self.active_sessions[session_id].status = 'active'
                await self.broadcast_to_session(session_id, {
                    "type": "session_resumed",
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat()
                })
                return {"status": "success", "message": "Session resumed"}

        return {"error": f"Unknown command: {command}"}

    async def handle_message(self, websocket, path):
        """Handle incoming WebSocket messages"""
        user_id = None
        session_id = None

        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    message_type = data.get('type')

                    if message_type == 'join_session':
                        user_id = data.get('user_id')
                        session_id = data.get('session_id')

                        if not user_id or not session_id:
                            await self.send_safe(websocket, {
                                "error": "user_id and session_id are required"
                            })
                            continue

                        await self.register_user(websocket, user_id, session_id)
                        await self.send_safe(websocket, {
                            "type": "joined",
                            "session_id": session_id,
                            "user_id": user_id
                        })

                    elif message_type == 'analyze_file':
                        if not session_id or not user_id:
                            await self.send_safe(websocket, {"error": "Not joined to a session"})
                            continue

                        result = await self.handle_analysis_request(session_id, user_id, data)
                        await self.send_safe(websocket, {
                            "type": "analysis_response",
                            "request_id": data.get('request_id'),
                            **result
                        })

                    elif message_type == 'add_comment':
                        result = await self.handle_comment_add(session_id, user_id, data)
                        await self.send_safe(websocket, {
                            "type": "comment_response",
                            "request_id": data.get('request_id'),
                            **result
                        })

                    elif message_type == 'review_pattern':
                        result = await self.handle_pattern_review(session_id, user_id, data)
                        await self.send_safe(websocket, {
                            "type": "review_response",
                            "request_id": data.get('request_id'),
                            **result
                        })

                    elif message_type == 'session_command':
                        result = await self.handle_session_command(session_id, user_id, data)
                        await self.send_safe(websocket, {
                            "type": "command_response",
                            "request_id": data.get('request_id'),
                            **result
                        })

                    else:
                        await self.send_safe(websocket, {
                            "error": f"Unknown message type: {message_type}"
                        })

                except json.JSONDecodeError:
                    await self.send_safe(websocket, {"error": "Invalid JSON"})
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    await self.send_safe(websocket, {"error": "Internal server error"})

        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket connection closed")
        finally:
            if user_id and session_id:
                await self.unregister_user(websocket, user_id, session_id)

    async def start_server(self):
        """Start the WebSocket server"""
        logger.info(f"Starting CodeMentor collaboration server on {self.host}:{self.port}")

        async with websockets.serve(self.handle_message, self.host, self.port):
            logger.info("Server started successfully")
            await asyncio.Future()  # Run forever


class CollaborationClient:
    """Client for connecting to the real-time collaboration server"""

    def __init__(self, server_url="ws://localhost:8765"):
        self.server_url = server_url
        self.websocket = None
        self.user_id = None
        self.session_id = None
        self.event_handlers = {}

    def on(self, event_type: str, handler):
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    async def connect(self, user_id: str, session_id: str):
        """Connect to a collaboration session"""
        try:
            self.websocket = await websockets.connect(self.server_url)
            self.user_id = user_id
            self.session_id = session_id

            # Join session
            await self.websocket.send(json.dumps({
                "type": "join_session",
                "user_id": user_id,
                "session_id": session_id
            }))

            # Start listening for messages
            asyncio.create_task(self._listen())

            logger.info(f"Connected to session {session_id} as {user_id}")

        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            raise

    async def _listen(self):
        """Listen for incoming messages"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    event_type = data.get('type')

                    # Call registered handlers
                    if event_type in self.event_handlers:
                        for handler in self.event_handlers[event_type]:
                            try:
                                await handler(data)
                            except Exception as e:
                                logger.error(f"Error in event handler: {e}")

                except json.JSONDecodeError:
                    logger.error("Received invalid JSON")

        except websockets.exceptions.ConnectionClosed:
            logger.info("Connection to server lost")

    async def analyze_file(self, file_path: str, options: Dict = None):
        """Request analysis of a file"""
        if not self.websocket:
            raise RuntimeError("Not connected to server")

        request_id = str(uuid.uuid4())
        await self.websocket.send(json.dumps({
            "type": "analyze_file",
            "request_id": request_id,
            "file_path": file_path,
            "options": options or {}
        }))

        return request_id

    async def add_comment(self, finding_id: str, comment: str):
        """Add a comment to a finding"""
        if not self.websocket:
            raise RuntimeError("Not connected to server")

        request_id = str(uuid.uuid4())
        await self.websocket.send(json.dumps({
            "type": "add_comment",
            "request_id": request_id,
            "finding_id": finding_id,
            "comment": comment
        }))

        return request_id

    async def review_pattern(self, finding_id: str, status: str, comment: str = ""):
        """Review a detected pattern"""
        if not self.websocket:
            raise RuntimeError("Not connected to server")

        request_id = str(uuid.uuid4())
        await self.websocket.send(json.dumps({
            "type": "review_pattern",
            "request_id": request_id,
            "finding_id": finding_id,
            "status": status,
            "comment": comment
        }))

        return request_id

    async def disconnect(self):
        """Disconnect from the server"""
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from collaboration server")


# Example usage and testing
async def example_collaboration_session():
    """Example of how to use the collaboration system"""

    # Start server (in practice, this would be a separate process)
    server = RealTimeCollaborationServer()
    server_task = asyncio.create_task(server.start_server())

    # Wait a bit for server to start
    await asyncio.sleep(1)

    # Create two clients
    alice_client = CollaborationClient()
    bob_client = CollaborationClient()

    # Set up event handlers
    async def on_analysis_completed(data):
        print(f"Analysis completed: {len(data.get('results', []))} findings")

    alice_client.on('analysis_completed', on_analysis_completed)
    bob_client.on('analysis_completed', on_analysis_completed)

    try:
        # Connect both clients
        await alice_client.connect("alice", "test-session")
        await bob_client.connect("bob", "test-session")

        # Alice requests analysis
        await alice_client.analyze_file("example.py")

        # Bob adds a comment
        await bob_client.add_comment("finding-123", "This looks like a potential performance issue")

        # Wait for some activity
        await asyncio.sleep(5)

    finally:
        await alice_client.disconnect()
        await bob_client.disconnect()
        server_task.cancel()


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_collaboration_session())
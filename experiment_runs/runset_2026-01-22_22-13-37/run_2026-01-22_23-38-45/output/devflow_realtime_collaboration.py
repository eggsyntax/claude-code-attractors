"""
DevFlow Real-Time Collaboration System
Advanced multi-user collaboration with intelligent conflict resolution
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import websockets
import difflib
from collections import defaultdict
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CollaborationEventType(Enum):
    """Types of collaboration events"""
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    CODE_CHANGE = "code_change"
    CURSOR_MOVE = "cursor_move"
    SELECTION_CHANGE = "selection_change"
    COMMENT_ADDED = "comment_added"
    CONFLICT_DETECTED = "conflict_detected"
    CONFLICT_RESOLVED = "conflict_resolved"
    SESSION_STATE = "session_state"

class ConflictType(Enum):
    """Types of conflicts that can occur"""
    CONCURRENT_EDIT = "concurrent_edit"
    MERGE_CONFLICT = "merge_conflict"
    RESOURCE_CONFLICT = "resource_conflict"
    SEMANTIC_CONFLICT = "semantic_conflict"

@dataclass
class CollaborationUser:
    """User in a collaboration session"""
    user_id: str
    username: str
    role: str
    color: str
    cursor_position: Optional[Dict[str, int]] = None
    selection: Optional[Dict[str, Any]] = None
    last_active: datetime = None
    permissions: List[str] = None

    def __post_init__(self):
        if self.last_active is None:
            self.last_active = datetime.now()
        if self.permissions is None:
            self.permissions = ["read", "write", "comment"]

@dataclass
class CodeChange:
    """Represents a code change in collaboration"""
    change_id: str
    user_id: str
    file_path: str
    start_line: int
    end_line: int
    old_content: str
    new_content: str
    timestamp: datetime
    operation_type: str  # 'insert', 'delete', 'replace'
    context_hash: str  # Hash of surrounding context for conflict detection

@dataclass
class ConflictResolution:
    """Represents a conflict and its resolution"""
    conflict_id: str
    conflict_type: ConflictType
    involved_users: List[str]
    conflicting_changes: List[CodeChange]
    resolution_strategy: str
    resolved_content: str
    resolver_user_id: str
    resolved_at: datetime

class IntelligentConflictResolver:
    """AI-powered conflict resolution system"""

    def __init__(self):
        self.resolution_strategies = {
            ConflictType.CONCURRENT_EDIT: self._resolve_concurrent_edit,
            ConflictType.MERGE_CONFLICT: self._resolve_merge_conflict,
            ConflictType.RESOURCE_CONFLICT: self._resolve_resource_conflict,
            ConflictType.SEMANTIC_CONFLICT: self._resolve_semantic_conflict
        }
        self.conflict_history = []

    async def detect_conflict(self, changes: List[CodeChange]) -> Optional[Dict[str, Any]]:
        """Detect conflicts between multiple changes"""
        if len(changes) < 2:
            return None

        # Group changes by file and analyze overlaps
        file_changes = defaultdict(list)
        for change in changes:
            file_changes[change.file_path].append(change)

        conflicts = []
        for file_path, file_change_list in file_changes.items():
            if len(file_change_list) < 2:
                continue

            # Check for overlapping line ranges
            for i in range(len(file_change_list)):
                for j in range(i + 1, len(file_change_list)):
                    change1, change2 = file_change_list[i], file_change_list[j]

                    if self._changes_overlap(change1, change2):
                        conflict_type = self._classify_conflict(change1, change2)
                        conflicts.append({
                            "conflict_id": str(uuid.uuid4()),
                            "type": conflict_type,
                            "file_path": file_path,
                            "changes": [change1, change2],
                            "severity": self._calculate_conflict_severity(change1, change2)
                        })

        return {"conflicts": conflicts} if conflicts else None

    async def resolve_conflict(self, conflict: Dict[str, Any], user_preference: Optional[str] = None) -> ConflictResolution:
        """Resolve a conflict using intelligent strategies"""
        conflict_type = ConflictType(conflict["type"])
        strategy_func = self.resolution_strategies.get(conflict_type)

        if not strategy_func:
            raise ValueError(f"No resolution strategy for conflict type: {conflict_type}")

        # Apply resolution strategy
        resolution = await strategy_func(conflict, user_preference)

        # Track resolution for learning
        self.conflict_history.append(resolution)

        logger.info(f"Resolved conflict {resolution.conflict_id} using strategy: {resolution.resolution_strategy}")
        return resolution

    def _changes_overlap(self, change1: CodeChange, change2: CodeChange) -> bool:
        """Check if two changes overlap in terms of lines"""
        return not (change1.end_line < change2.start_line or change2.end_line < change1.start_line)

    def _classify_conflict(self, change1: CodeChange, change2: CodeChange) -> ConflictType:
        """Classify the type of conflict between two changes"""
        # Simplified classification logic
        if change1.context_hash == change2.context_hash:
            return ConflictType.CONCURRENT_EDIT
        elif self._are_semantic_conflicts(change1, change2):
            return ConflictType.SEMANTIC_CONFLICT
        else:
            return ConflictType.MERGE_CONFLICT

    def _calculate_conflict_severity(self, change1: CodeChange, change2: CodeChange) -> float:
        """Calculate conflict severity (0.0 to 1.0)"""
        # Consider factors: overlapping lines, change size, operation types
        line_overlap = min(change1.end_line, change2.end_line) - max(change1.start_line, change2.start_line)
        max_lines = max(change1.end_line - change1.start_line, change2.end_line - change2.start_line)

        overlap_ratio = line_overlap / max_lines if max_lines > 0 else 0
        return min(overlap_ratio * 1.2, 1.0)  # Cap at 1.0

    def _are_semantic_conflicts(self, change1: CodeChange, change2: CodeChange) -> bool:
        """Check if changes represent semantic conflicts"""
        # Simplified semantic analysis - would use AST parsing in production
        keywords = ["function", "class", "import", "def", "interface"]
        change1_has_keywords = any(keyword in change1.new_content for keyword in keywords)
        change2_has_keywords = any(keyword in change2.new_content for keyword in keywords)
        return change1_has_keywords and change2_has_keywords

    async def _resolve_concurrent_edit(self, conflict: Dict[str, Any], user_preference: Optional[str]) -> ConflictResolution:
        """Resolve concurrent edit conflicts"""
        changes = conflict["changes"]
        strategy = "three_way_merge"

        # Perform three-way merge
        resolved_content = self._three_way_merge(changes[0], changes[1])

        return ConflictResolution(
            conflict_id=conflict["conflict_id"],
            conflict_type=ConflictType.CONCURRENT_EDIT,
            involved_users=[c.user_id for c in changes],
            conflicting_changes=changes,
            resolution_strategy=strategy,
            resolved_content=resolved_content,
            resolver_user_id="system",
            resolved_at=datetime.now()
        )

    async def _resolve_merge_conflict(self, conflict: Dict[str, Any], user_preference: Optional[str]) -> ConflictResolution:
        """Resolve merge conflicts"""
        changes = conflict["changes"]

        if user_preference == "latest":
            # Take the latest change
            latest_change = max(changes, key=lambda c: c.timestamp)
            resolved_content = latest_change.new_content
            strategy = "latest_wins"
        elif user_preference == "manual":
            # Create merge markers for manual resolution
            resolved_content = self._create_merge_markers(changes)
            strategy = "manual_resolution"
        else:
            # Intelligent merge
            resolved_content = self._intelligent_merge(changes)
            strategy = "intelligent_merge"

        return ConflictResolution(
            conflict_id=conflict["conflict_id"],
            conflict_type=ConflictType.MERGE_CONFLICT,
            involved_users=[c.user_id for c in changes],
            conflicting_changes=changes,
            resolution_strategy=strategy,
            resolved_content=resolved_content,
            resolver_user_id="system",
            resolved_at=datetime.now()
        )

    async def _resolve_resource_conflict(self, conflict: Dict[str, Any], user_preference: Optional[str]) -> ConflictResolution:
        """Resolve resource conflicts (e.g., file locking)"""
        # Simplified resource conflict resolution
        changes = conflict["changes"]
        strategy = "first_come_first_served"

        # Prioritize by timestamp
        first_change = min(changes, key=lambda c: c.timestamp)
        resolved_content = first_change.new_content

        return ConflictResolution(
            conflict_id=conflict["conflict_id"],
            conflict_type=ConflictType.RESOURCE_CONFLICT,
            involved_users=[c.user_id for c in changes],
            conflicting_changes=changes,
            resolution_strategy=strategy,
            resolved_content=resolved_content,
            resolver_user_id="system",
            resolved_at=datetime.now()
        )

    async def _resolve_semantic_conflict(self, conflict: Dict[str, Any], user_preference: Optional[str]) -> ConflictResolution:
        """Resolve semantic conflicts"""
        changes = conflict["changes"]
        strategy = "semantic_merge"

        # Attempt to merge semantic changes intelligently
        resolved_content = self._semantic_merge(changes)

        return ConflictResolution(
            conflict_id=conflict["conflict_id"],
            conflict_type=ConflictType.SEMANTIC_CONFLICT,
            involved_users=[c.user_id for c in changes],
            conflicting_changes=changes,
            resolution_strategy=strategy,
            resolved_content=resolved_content,
            resolver_user_id="system",
            resolved_at=datetime.now()
        )

    def _three_way_merge(self, change1: CodeChange, change2: CodeChange) -> str:
        """Perform three-way merge of changes"""
        # Simplified three-way merge
        diff1 = list(difflib.unified_diff(
            change1.old_content.splitlines(),
            change1.new_content.splitlines(),
            lineterm=""
        ))
        diff2 = list(difflib.unified_diff(
            change2.old_content.splitlines(),
            change2.new_content.splitlines(),
            lineterm=""
        ))

        # Merge non-conflicting changes
        merged_lines = change1.old_content.splitlines()

        # Apply changes from both diffs where possible
        # This is a simplified implementation - production would use more sophisticated algorithms
        if not self._diffs_conflict(diff1, diff2):
            # Apply both changes
            merged_lines = change2.new_content.splitlines()
        else:
            # Create conflict markers
            merged_lines = self._create_conflict_markers(change1, change2).splitlines()

        return "\n".join(merged_lines)

    def _intelligent_merge(self, changes: List[CodeChange]) -> str:
        """Perform intelligent merge of multiple changes"""
        # Sort changes by timestamp
        sorted_changes = sorted(changes, key=lambda c: c.timestamp)

        # Start with the base content
        merged_content = sorted_changes[0].old_content

        # Apply changes in order, resolving conflicts as needed
        for change in sorted_changes:
            if not self._would_conflict_with_current(change, merged_content):
                merged_content = self._apply_change_to_content(change, merged_content)
            else:
                # Attempt smart conflict resolution
                merged_content = self._smart_conflict_resolution(change, merged_content)

        return merged_content

    def _create_merge_markers(self, changes: List[CodeChange]) -> str:
        """Create merge conflict markers for manual resolution"""
        conflict_section = "<<<<<<< HEAD\n"
        conflict_section += changes[0].new_content + "\n"
        conflict_section += "=======\n"
        conflict_section += changes[1].new_content + "\n"
        conflict_section += ">>>>>>> branch\n"
        return conflict_section

    def _create_conflict_markers(self, change1: CodeChange, change2: CodeChange) -> str:
        """Create conflict markers between two changes"""
        return f"<<<<<<< {change1.user_id}\n{change1.new_content}\n=======\n{change2.new_content}\n>>>>>>> {change2.user_id}"

    def _semantic_merge(self, changes: List[CodeChange]) -> str:
        """Perform semantic-aware merge"""
        # Simplified semantic merge - would use AST analysis in production
        return self._intelligent_merge(changes)

    def _diffs_conflict(self, diff1: List[str], diff2: List[str]) -> bool:
        """Check if two diffs conflict with each other"""
        # Simplified conflict detection
        return len(diff1) > 0 and len(diff2) > 0

    def _would_conflict_with_current(self, change: CodeChange, current_content: str) -> bool:
        """Check if a change would conflict with current content"""
        # Simplified conflict detection
        return change.old_content not in current_content

    def _apply_change_to_content(self, change: CodeChange, content: str) -> str:
        """Apply a change to content"""
        # Simplified change application
        return content.replace(change.old_content, change.new_content)

    def _smart_conflict_resolution(self, change: CodeChange, current_content: str) -> str:
        """Apply smart conflict resolution strategies"""
        # Try to find similar patterns and apply change contextually
        lines = current_content.splitlines()
        change_lines = change.new_content.splitlines()

        # Find best insertion point
        best_position = self._find_best_insertion_point(change_lines, lines)

        # Insert at best position
        result_lines = lines[:best_position] + change_lines + lines[best_position:]
        return "\n".join(result_lines)

    def _find_best_insertion_point(self, new_lines: List[str], existing_lines: List[str]) -> int:
        """Find the best position to insert new lines"""
        # Simplified heuristic - find similar context
        for i, line in enumerate(existing_lines):
            if any(keyword in line for keyword in ["function", "class", "def"] if new_lines):
                if any(keyword in new_lines[0] for keyword in ["function", "class", "def"]):
                    return i + 1
        return len(existing_lines)

class RealtimeCollaborationSession:
    """Manages a real-time collaboration session"""

    def __init__(self, session_id: str, project_id: str):
        self.session_id = session_id
        self.project_id = project_id
        self.users: Dict[str, CollaborationUser] = {}
        self.active_changes: List[CodeChange] = []
        self.conflict_resolver = IntelligentConflictResolver()
        self.websocket_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.file_states: Dict[str, Dict[str, Any]] = {}
        self.change_buffer = []
        self.last_sync = datetime.now()

    async def add_user(self, user: CollaborationUser, websocket: websockets.WebSocketServerProtocol):
        """Add a user to the collaboration session"""
        self.users[user.user_id] = user
        self.websocket_connections[user.user_id] = websocket

        # Broadcast user joined event
        await self._broadcast_event({
            "type": CollaborationEventType.USER_JOINED.value,
            "user": asdict(user),
            "timestamp": datetime.now().isoformat()
        }, exclude_user=user.user_id)

        # Send current session state to new user
        await self._send_session_state(user.user_id)

        logger.info(f"User {user.username} joined collaboration session {self.session_id}")

    async def remove_user(self, user_id: str):
        """Remove a user from the collaboration session"""
        if user_id in self.users:
            user = self.users[user_id]
            del self.users[user_id]
            del self.websocket_connections[user_id]

            # Broadcast user left event
            await self._broadcast_event({
                "type": CollaborationEventType.USER_LEFT.value,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat()
            })

            logger.info(f"User {user.username} left collaboration session {self.session_id}")

    async def handle_code_change(self, change: CodeChange):
        """Handle incoming code change with conflict detection"""
        # Add change to buffer
        self.change_buffer.append(change)
        self.active_changes.append(change)

        # Check for conflicts
        recent_changes = [c for c in self.active_changes
                         if (datetime.now() - c.timestamp).seconds < 30]

        conflict_info = await self.conflict_resolver.detect_conflict(recent_changes)

        if conflict_info:
            # Handle conflict
            await self._handle_conflicts(conflict_info["conflicts"])
        else:
            # Broadcast change to other users
            await self._broadcast_change(change)

        # Update file state
        self._update_file_state(change)

    async def _handle_conflicts(self, conflicts: List[Dict[str, Any]]):
        """Handle detected conflicts"""
        for conflict in conflicts:
            logger.warning(f"Conflict detected: {conflict['conflict_id']}")

            # Attempt automatic resolution
            try:
                resolution = await self.conflict_resolver.resolve_conflict(conflict)

                # Broadcast conflict resolution
                await self._broadcast_event({
                    "type": CollaborationEventType.CONFLICT_RESOLVED.value,
                    "conflict_id": conflict["conflict_id"],
                    "resolution": asdict(resolution),
                    "timestamp": datetime.now().isoformat()
                })

                # Apply resolved content
                await self._apply_resolution(resolution)

            except Exception as e:
                # If automatic resolution fails, notify users for manual resolution
                await self._broadcast_event({
                    "type": CollaborationEventType.CONFLICT_DETECTED.value,
                    "conflict": conflict,
                    "requires_manual_resolution": True,
                    "timestamp": datetime.now().isoformat()
                })

    async def _apply_resolution(self, resolution: ConflictResolution):
        """Apply conflict resolution to file state"""
        # Update file content with resolved version
        for change in resolution.conflicting_changes:
            file_path = change.file_path
            if file_path in self.file_states:
                self.file_states[file_path]["content"] = resolution.resolved_content
                self.file_states[file_path]["last_modified"] = resolution.resolved_at
                self.file_states[file_path]["modified_by"] = resolution.resolver_user_id

        # Sync updated state to all users
        await self._sync_file_states()

    async def _broadcast_change(self, change: CodeChange):
        """Broadcast code change to all users except the author"""
        event = {
            "type": CollaborationEventType.CODE_CHANGE.value,
            "change": asdict(change),
            "timestamp": datetime.now().isoformat()
        }

        await self._broadcast_event(event, exclude_user=change.user_id)

    async def _broadcast_event(self, event: Dict[str, Any], exclude_user: Optional[str] = None):
        """Broadcast event to all connected users"""
        message = json.dumps(event)

        disconnected_users = []
        for user_id, websocket in self.websocket_connections.items():
            if exclude_user and user_id == exclude_user:
                continue

            try:
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_users.append(user_id)
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {str(e)}")
                disconnected_users.append(user_id)

        # Clean up disconnected users
        for user_id in disconnected_users:
            await self.remove_user(user_id)

    async def _send_session_state(self, user_id: str):
        """Send current session state to a specific user"""
        websocket = self.websocket_connections.get(user_id)
        if not websocket:
            return

        state = {
            "type": CollaborationEventType.SESSION_STATE.value,
            "session_id": self.session_id,
            "users": [asdict(user) for user in self.users.values()],
            "file_states": self.file_states,
            "timestamp": datetime.now().isoformat()
        }

        try:
            await websocket.send(json.dumps(state))
        except Exception as e:
            logger.error(f"Error sending session state to user {user_id}: {str(e)}")

    async def _sync_file_states(self):
        """Sync file states to all connected users"""
        await self._broadcast_event({
            "type": "file_state_update",
            "file_states": self.file_states,
            "timestamp": datetime.now().isoformat()
        })

    def _update_file_state(self, change: CodeChange):
        """Update internal file state with change"""
        file_path = change.file_path

        if file_path not in self.file_states:
            self.file_states[file_path] = {
                "content": "",
                "last_modified": datetime.now(),
                "modified_by": change.user_id,
                "version": 1
            }

        # Apply change to file state
        file_state = self.file_states[file_path]
        file_state["content"] = change.new_content
        file_state["last_modified"] = change.timestamp
        file_state["modified_by"] = change.user_id
        file_state["version"] += 1

class RealtimeCollaborationManager:
    """Manages multiple collaboration sessions"""

    def __init__(self):
        self.sessions: Dict[str, RealtimeCollaborationSession] = {}
        self.user_colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8", "#F7DC6F", "#BB8FCE"]
        self.color_index = 0

    async def create_session(self, project_id: str) -> str:
        """Create a new collaboration session"""
        session_id = str(uuid.uuid4())
        session = RealtimeCollaborationSession(session_id, project_id)
        self.sessions[session_id] = session

        logger.info(f"Created collaboration session: {session_id} for project: {project_id}")
        return session_id

    async def join_session(self, session_id: str, user_id: str, username: str, websocket: websockets.WebSocketServerProtocol):
        """Join an existing collaboration session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]

        # Create user with assigned color
        user = CollaborationUser(
            user_id=user_id,
            username=username,
            role="developer",
            color=self._get_next_color()
        )

        await session.add_user(user, websocket)
        return session

    def _get_next_color(self) -> str:
        """Get next available color for user"""
        color = self.user_colors[self.color_index % len(self.user_colors)]
        self.color_index += 1
        return color

    async def handle_websocket_message(self, session_id: str, user_id: str, message: str):
        """Handle incoming WebSocket message"""
        if session_id not in self.sessions:
            logger.error(f"Session {session_id} not found")
            return

        session = self.sessions[session_id]

        try:
            data = json.loads(message)
            message_type = data.get("type")

            if message_type == "code_change":
                change = CodeChange(
                    change_id=str(uuid.uuid4()),
                    user_id=user_id,
                    file_path=data["file_path"],
                    start_line=data["start_line"],
                    end_line=data["end_line"],
                    old_content=data["old_content"],
                    new_content=data["new_content"],
                    timestamp=datetime.now(),
                    operation_type=data.get("operation_type", "replace"),
                    context_hash=self._calculate_context_hash(data["old_content"])
                )
                await session.handle_code_change(change)

            elif message_type == "cursor_move":
                await session._broadcast_event({
                    "type": CollaborationEventType.CURSOR_MOVE.value,
                    "user_id": user_id,
                    "position": data["position"],
                    "timestamp": datetime.now().isoformat()
                }, exclude_user=user_id)

            elif message_type == "comment":
                await session._broadcast_event({
                    "type": CollaborationEventType.COMMENT_ADDED.value,
                    "user_id": user_id,
                    "comment": data["comment"],
                    "position": data.get("position"),
                    "timestamp": datetime.now().isoformat()
                })

        except Exception as e:
            logger.error(f"Error handling WebSocket message: {str(e)}")

    def _calculate_context_hash(self, content: str) -> str:
        """Calculate hash of content for conflict detection"""
        return hashlib.md5(content.encode()).hexdigest()

# Demo function
async def demo_realtime_collaboration():
    """Demonstrate the real-time collaboration system"""

    print("🤝 DevFlow Real-Time Collaboration Demo")
    print("=" * 50)

    # Initialize collaboration manager
    manager = RealtimeCollaborationManager()

    # Create a collaboration session
    session_id = await manager.create_session("devflow-demo-project")
    print(f"📋 Created collaboration session: {session_id}")

    # Simulate multiple users joining (without actual WebSocket connections)
    class MockWebSocket:
        async def send(self, message):
            data = json.loads(message)
            print(f"📨 Broadcasting: {data['type']} to users")

    # Create mock users
    users = [
        ("alice", "Alice Developer"),
        ("bob", "Bob Reviewer"),
        ("charlie", "Charlie Tester")
    ]

    session = manager.sessions[session_id]

    for user_id, username in users:
        user = CollaborationUser(
            user_id=user_id,
            username=username,
            role="developer",
            color=manager._get_next_color()
        )
        await session.add_user(user, MockWebSocket())

    print(f"👥 Added {len(users)} users to session")

    # Simulate some code changes
    changes = [
        {
            "user_id": "alice",
            "file_path": "src/main.py",
            "start_line": 10,
            "end_line": 12,
            "old_content": "def old_function():\n    return 'old'",
            "new_content": "def new_function():\n    return 'new'",
            "operation_type": "replace"
        },
        {
            "user_id": "bob",
            "file_path": "src/main.py",
            "start_line": 11,
            "end_line": 13,
            "old_content": "def old_function():\n    return 'old'",
            "new_content": "def updated_function():\n    return 'updated'",
            "operation_type": "replace"
        }
    ]

    print("\n🔧 Simulating concurrent code changes...")
    for change_data in changes:
        change = CodeChange(
            change_id=str(uuid.uuid4()),
            user_id=change_data["user_id"],
            file_path=change_data["file_path"],
            start_line=change_data["start_line"],
            end_line=change_data["end_line"],
            old_content=change_data["old_content"],
            new_content=change_data["new_content"],
            timestamp=datetime.now(),
            operation_type=change_data["operation_type"],
            context_hash=manager._calculate_context_hash(change_data["old_content"])
        )

        await session.handle_code_change(change)
        await asyncio.sleep(0.1)  # Small delay between changes

    print(f"\n📊 Session Statistics:")
    print(f"  - Active users: {len(session.users)}")
    print(f"  - Total changes: {len(session.active_changes)}")
    print(f"  - Files modified: {len(session.file_states)}")
    print(f"  - Conflicts resolved: {len(session.conflict_resolver.conflict_history)}")

    return session

if __name__ == "__main__":
    asyncio.run(demo_realtime_collaboration())
"""
Session management system for CodeMentor collaborative reviews.

This module provides the core functionality for creating, managing, and
persisting review sessions, handling participant coordination, and
integrating with the analysis engine.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from .models import (
    ReviewSession,
    Participant,
    Comment,
    ReviewStatus,
    ProjectContext
)

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages the lifecycle of collaborative review sessions.

    This class handles:
    - Creating and configuring review sessions
    - Participant management and coordination
    - Comment threading and resolution tracking
    - Integration with analysis engine results
    - Session persistence and recovery
    """

    def __init__(self, workspace_path: str = "./codementor_workspace"):
        """Initialize session manager with workspace configuration."""
        self.workspace_path = Path(workspace_path)
        self.sessions_path = self.workspace_path / "sessions"
        self.projects_path = self.workspace_path / "projects"

        # Create workspace directories
        self.workspace_path.mkdir(exist_ok=True)
        self.sessions_path.mkdir(exist_ok=True)
        self.projects_path.mkdir(exist_ok=True)

        self._active_sessions: Dict[str, ReviewSession] = {}

        # Load existing sessions
        self._load_existing_sessions()

    def create_session(
        self,
        title: str,
        project_path: str,
        description: str = "",
        reviewer_names: List[str] = None
    ) -> ReviewSession:
        """
        Create a new collaborative review session.

        Args:
            title: Human-readable title for the review
            project_path: Path to the code project being reviewed
            description: Optional detailed description
            reviewer_names: List of reviewer names to add as participants

        Returns:
            Newly created ReviewSession instance
        """
        session = ReviewSession(
            title=title,
            description=description,
            project_path=os.path.abspath(project_path)
        )

        # Add participants
        if reviewer_names:
            for name in reviewer_names:
                participant = Participant(name=name, role="reviewer")
                session.add_participant(participant)

        # Set up default review checklist
        session.review_checklist = [
            "Code follows project conventions",
            "Logic is clear and well-structured",
            "Error handling is appropriate",
            "Tests are adequate and passing",
            "Documentation is up to date",
            "Performance implications considered",
            "Security considerations addressed"
        ]

        # Store session
        self._active_sessions[session.id] = session
        self._persist_session(session)

        logger.info(f"Created review session '{title}' with ID {session.id}")
        return session

    def get_session(self, session_id: str) -> Optional[ReviewSession]:
        """Retrieve a session by ID."""
        return self._active_sessions.get(session_id)

    def list_sessions(
        self,
        status_filter: Optional[ReviewStatus] = None,
        project_filter: Optional[str] = None
    ) -> List[ReviewSession]:
        """
        List sessions with optional filtering.

        Args:
            status_filter: Only return sessions with this status
            project_filter: Only return sessions for this project path

        Returns:
            List of matching ReviewSession instances
        """
        sessions = list(self._active_sessions.values())

        if status_filter:
            sessions = [s for s in sessions if s.status == status_filter]

        if project_filter:
            sessions = [s for s in sessions if s.project_path == project_filter]

        return sorted(sessions, key=lambda s: s.updated_at, reverse=True)

    def start_session(self, session_id: str) -> bool:
        """Start a review session, moving it from draft to in-progress."""
        session = self.get_session(session_id)
        if not session:
            return False

        session.start_review()
        self._persist_session(session)

        logger.info(f"Started review session {session_id}")
        return True

    def add_comment(
        self,
        session_id: str,
        author_name: str,
        content: str,
        file_path: str,
        line_number: Optional[int] = None,
        comment_type: str = "suggestion",
        parent_comment_id: Optional[str] = None
    ) -> Optional[Comment]:
        """
        Add a comment to a review session.

        Args:
            session_id: Target session ID
            author_name: Name of the comment author
            content: Comment text content
            file_path: File being commented on
            line_number: Optional specific line number
            comment_type: Type of comment (suggestion, question, etc.)
            parent_comment_id: For threaded replies

        Returns:
            Created Comment instance or None if failed
        """
        session = self.get_session(session_id)
        if not session:
            logger.error(f"Session {session_id} not found")
            return None

        # Find or create participant for author
        author = self._get_or_create_participant(session, author_name)

        comment = Comment(
            author_id=author.id,
            content=content,
            file_path=file_path,
            line_number=line_number,
            parent_comment_id=parent_comment_id
        )

        session.add_comment(comment)
        self._persist_session(session)

        logger.info(f"Added comment to session {session_id} on {file_path}:{line_number}")
        return comment

    def resolve_comment(
        self,
        session_id: str,
        comment_id: str,
        resolver_name: str
    ) -> bool:
        """Mark a comment as resolved."""
        session = self.get_session(session_id)
        if not session:
            return False

        comment = next((c for c in session.comments if c.id == comment_id), None)
        if not comment:
            return False

        resolver = self._get_or_create_participant(session, resolver_name)
        comment.resolve(resolver.id)
        self._persist_session(session)

        logger.info(f"Resolved comment {comment_id} in session {session_id}")
        return True

    def update_analysis_results(
        self,
        session_id: str,
        analysis_data: Dict[str, Any]
    ) -> bool:
        """
        Update session with results from Alice's analysis engine.

        This method provides the integration point for the code analysis
        engine to store its findings in the collaborative session.
        """
        session = self.get_session(session_id)
        if not session:
            return False

        session.analysis_results.update(analysis_data)
        session.updated_at = datetime.now()
        self._persist_session(session)

        logger.info(f"Updated analysis results for session {session_id}")
        return True

    def add_pattern_finding(
        self,
        session_id: str,
        pattern_name: str,
        file_path: str,
        description: str,
        line_range: Optional[tuple] = None,
        severity: str = "info",
        suggestions: List[str] = None
    ) -> bool:
        """Add a pattern detection finding to the session."""
        session = self.get_session(session_id)
        if not session:
            return False

        finding = {
            "pattern_name": pattern_name,
            "file_path": file_path,
            "description": description,
            "line_range": line_range,
            "severity": severity,
            "suggestions": suggestions or [],
            "detected_at": datetime.now().isoformat()
        }

        session.pattern_findings.append(finding)
        session.updated_at = datetime.now()
        self._persist_session(session)

        return True

    def complete_session(
        self,
        session_id: str,
        approved: bool = True,
        completion_notes: str = ""
    ) -> bool:
        """Complete a review session."""
        session = self.get_session(session_id)
        if not session:
            return False

        session.complete_review(approved)

        # Add completion notes as a system comment
        if completion_notes:
            system_comment = Comment(
                author_id="system",
                content=f"Session completed: {completion_notes}",
                file_path="",
                comment_type="educational"
            )
            session.add_comment(system_comment)

        self._persist_session(session)
        logger.info(f"Completed session {session_id} with result: {'approved' if approved else 'rejected'}")
        return True

    def get_session_summary(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of session status and metrics."""
        session = self.get_session(session_id)
        if not session:
            return None

        unresolved_comments = session.get_unresolved_comments()

        return {
            "id": session.id,
            "title": session.title,
            "status": session.status.value,
            "participant_count": len(session.participants),
            "total_comments": len(session.comments),
            "unresolved_comments": len(unresolved_comments),
            "files_reviewed": len(set(c.file_path for c in session.comments if c.file_path)),
            "pattern_findings": len(session.pattern_findings),
            "created_at": session.created_at.isoformat(),
            "last_activity": session.updated_at.isoformat()
        }

    def _get_or_create_participant(self, session: ReviewSession, name: str) -> Participant:
        """Find existing participant by name or create new one."""
        for participant in session.participants:
            if participant.name == name:
                return participant

        # Create new participant
        participant = Participant(name=name, role="reviewer")
        session.add_participant(participant)
        return participant

    def _persist_session(self, session: ReviewSession) -> None:
        """Save session to disk."""
        session_file = self.sessions_path / f"{session.id}.json"

        try:
            with open(session_file, 'w') as f:
                json.dump(session.to_dict(), f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to persist session {session.id}: {e}")

    def _load_existing_sessions(self) -> None:
        """Load all existing sessions from disk."""
        if not self.sessions_path.exists():
            return

        for session_file in self.sessions_path.glob("*.json"):
            try:
                with open(session_file) as f:
                    session_data = json.load(f)
                    session = ReviewSession.from_dict(session_data)
                    self._active_sessions[session.id] = session
                    logger.info(f"Loaded session {session.id}")
            except Exception as e:
                logger.error(f"Failed to load session from {session_file}: {e}")

    def archive_session(self, session_id: str) -> bool:
        """Archive a completed session."""
        session = self.get_session(session_id)
        if not session:
            return False

        session.status = ReviewStatus.ARCHIVED
        session.updated_at = datetime.now()
        self._persist_session(session)

        # Move from active sessions to archived (could implement separate storage)
        # For now, keep in same location but update status

        logger.info(f"Archived session {session_id}")
        return True


# Convenience functions for common operations
def create_quick_session(project_path: str, title: str = None) -> ReviewSession:
    """Quick session creation with minimal configuration."""
    manager = SessionManager()
    title = title or f"Review of {Path(project_path).name}"
    return manager.create_session(title, project_path)


def list_active_sessions() -> List[ReviewSession]:
    """List all active (non-archived) sessions."""
    manager = SessionManager()
    return [s for s in manager.list_sessions() if s.status != ReviewStatus.ARCHIVED]
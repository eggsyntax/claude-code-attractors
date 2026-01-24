"""
CodeMentor Collaboration Module

This module provides the collaborative features for CodeMentor,
including session management, participant coordination, and
integration points for the analysis engine.
"""

from .models import (
    ReviewSession,
    Participant,
    Comment,
    ReviewStatus,
    CommentType,
    Priority,
    ProjectContext
)

from .session_manager import SessionManager, create_quick_session, list_active_sessions

__version__ = "0.1.0"
__all__ = [
    "ReviewSession",
    "Participant",
    "Comment",
    "ReviewStatus",
    "CommentType",
    "Priority",
    "ProjectContext",
    "SessionManager",
    "create_quick_session",
    "list_active_sessions"
]
"""
Collaboration data models for CodeMentor.

This module defines the core data structures for managing collaborative
code reviews, discussions, and project tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid
import json


class ReviewStatus(Enum):
    """Status of a code review session."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class CommentType(Enum):
    """Types of comments in a review."""
    SUGGESTION = "suggestion"
    QUESTION = "question"
    PRAISE = "praise"
    CONCERN = "concern"
    EDUCATIONAL = "educational"


class Priority(Enum):
    """Priority levels for review items."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Participant:
    """A participant in a code review session."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email: Optional[str] = None
    role: str = "reviewer"  # reviewer, author, observer
    joined_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True


@dataclass
class Comment:
    """A comment on a specific piece of code."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    author_id: str = ""
    content: str = ""
    comment_type: CommentType = CommentType.SUGGESTION
    file_path: str = ""
    line_number: Optional[int] = None
    line_range: Optional[tuple[int, int]] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    resolved: bool = False
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    thread_id: Optional[str] = None  # For threaded discussions
    parent_comment_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    priority: Priority = Priority.MEDIUM

    def resolve(self, resolver_id: str) -> None:
        """Mark this comment as resolved."""
        self.resolved = True
        self.resolved_by = resolver_id
        self.resolved_at = datetime.now()
        self.updated_at = datetime.now()

    def add_tag(self, tag: str) -> None:
        """Add a tag to this comment."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()


@dataclass
class ReviewSession:
    """A collaborative code review session."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    project_path: str = ""
    status: ReviewStatus = ReviewStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Participants and collaboration
    participants: List[Participant] = field(default_factory=list)
    comments: List[Comment] = field(default_factory=list)

    # Review configuration
    files_to_review: List[str] = field(default_factory=list)
    excluded_files: List[str] = field(default_factory=list)
    review_checklist: List[str] = field(default_factory=list)

    # Analysis integration points (for Alice's engine)
    analysis_results: Dict[str, Any] = field(default_factory=dict)
    pattern_findings: List[Dict[str, Any]] = field(default_factory=list)
    quality_metrics: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    tags: List[str] = field(default_factory=list)
    priority: Priority = Priority.MEDIUM
    estimated_duration: Optional[int] = None  # minutes

    def add_participant(self, participant: Participant) -> None:
        """Add a participant to the review session."""
        if not any(p.id == participant.id for p in self.participants):
            self.participants.append(participant)
            self.updated_at = datetime.now()

    def start_review(self) -> None:
        """Start the review session."""
        if self.status == ReviewStatus.DRAFT:
            self.status = ReviewStatus.IN_PROGRESS
            self.started_at = datetime.now()
            self.updated_at = datetime.now()

    def complete_review(self, approved: bool = True) -> None:
        """Complete the review session."""
        self.status = ReviewStatus.APPROVED if approved else ReviewStatus.REJECTED
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()

    def add_comment(self, comment: Comment) -> None:
        """Add a comment to the review."""
        self.comments.append(comment)
        self.updated_at = datetime.now()

    def get_unresolved_comments(self) -> List[Comment]:
        """Get all unresolved comments in the review."""
        return [c for c in self.comments if not c.resolved]

    def get_comments_by_file(self, file_path: str) -> List[Comment]:
        """Get all comments for a specific file."""
        return [c for c in self.comments if c.file_path == file_path]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'project_path': self.project_path,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'participants': [
                {
                    'id': p.id,
                    'name': p.name,
                    'email': p.email,
                    'role': p.role,
                    'joined_at': p.joined_at.isoformat(),
                    'is_active': p.is_active
                } for p in self.participants
            ],
            'comments': [
                {
                    'id': c.id,
                    'author_id': c.author_id,
                    'content': c.content,
                    'comment_type': c.comment_type.value,
                    'file_path': c.file_path,
                    'line_number': c.line_number,
                    'line_range': c.line_range,
                    'created_at': c.created_at.isoformat(),
                    'updated_at': c.updated_at.isoformat() if c.updated_at else None,
                    'resolved': c.resolved,
                    'resolved_by': c.resolved_by,
                    'resolved_at': c.resolved_at.isoformat() if c.resolved_at else None,
                    'thread_id': c.thread_id,
                    'parent_comment_id': c.parent_comment_id,
                    'tags': c.tags,
                    'priority': c.priority.value
                } for c in self.comments
            ],
            'files_to_review': self.files_to_review,
            'excluded_files': self.excluded_files,
            'review_checklist': self.review_checklist,
            'analysis_results': self.analysis_results,
            'pattern_findings': self.pattern_findings,
            'quality_metrics': self.quality_metrics,
            'tags': self.tags,
            'priority': self.priority.value,
            'estimated_duration': self.estimated_duration
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReviewSession':
        """Create ReviewSession from dictionary."""
        session = cls(
            id=data['id'],
            title=data['title'],
            description=data['description'],
            project_path=data['project_path'],
            status=ReviewStatus(data['status']),
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            files_to_review=data['files_to_review'],
            excluded_files=data['excluded_files'],
            review_checklist=data['review_checklist'],
            analysis_results=data['analysis_results'],
            pattern_findings=data['pattern_findings'],
            quality_metrics=data['quality_metrics'],
            tags=data['tags'],
            priority=Priority(data['priority']),
            estimated_duration=data['estimated_duration']
        )

        if data['started_at']:
            session.started_at = datetime.fromisoformat(data['started_at'])
        if data['completed_at']:
            session.completed_at = datetime.fromisoformat(data['completed_at'])

        # Reconstruct participants
        for p_data in data['participants']:
            participant = Participant(
                id=p_data['id'],
                name=p_data['name'],
                email=p_data['email'],
                role=p_data['role'],
                joined_at=datetime.fromisoformat(p_data['joined_at']),
                is_active=p_data['is_active']
            )
            session.participants.append(participant)

        # Reconstruct comments
        for c_data in data['comments']:
            comment = Comment(
                id=c_data['id'],
                author_id=c_data['author_id'],
                content=c_data['content'],
                comment_type=CommentType(c_data['comment_type']),
                file_path=c_data['file_path'],
                line_number=c_data['line_number'],
                line_range=tuple(c_data['line_range']) if c_data['line_range'] else None,
                created_at=datetime.fromisoformat(c_data['created_at']),
                resolved=c_data['resolved'],
                resolved_by=c_data['resolved_by'],
                thread_id=c_data['thread_id'],
                parent_comment_id=c_data['parent_comment_id'],
                tags=c_data['tags'],
                priority=Priority(c_data['priority'])
            )
            if c_data['updated_at']:
                comment.updated_at = datetime.fromisoformat(c_data['updated_at'])
            if c_data['resolved_at']:
                comment.resolved_at = datetime.fromisoformat(c_data['resolved_at'])
            session.comments.append(comment)

        return session


@dataclass
class ProjectContext:
    """Context information about a project being reviewed."""
    name: str = ""
    path: str = ""
    language: str = ""
    framework: Optional[str] = None
    version: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    file_count: int = 0
    line_count: int = 0
    last_modified: Optional[datetime] = None
    git_branch: Optional[str] = None
    git_commit: Optional[str] = None

    # Integration points for Alice's analysis engine
    analysis_config: Dict[str, Any] = field(default_factory=dict)
    custom_patterns: List[str] = field(default_factory=list)
    quality_gates: Dict[str, Any] = field(default_factory=dict)
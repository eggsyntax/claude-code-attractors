"""
Core data models for CodeCraft analysis results.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any
from pathlib import Path

class Severity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class IssueType(Enum):
    CODE_SMELL = "code_smell"
    PERFORMANCE = "performance"
    SECURITY = "security"
    MAINTAINABILITY = "maintainability"
    PATTERN_VIOLATION = "pattern_violation"
    REFACTORING_OPPORTUNITY = "refactoring_opportunity"

@dataclass
class SourceLocation:
    """Represents a location in source code."""
    file_path: Path
    line_start: int
    line_end: int
    column_start: Optional[int] = None
    column_end: Optional[int] = None

@dataclass
class RefactoringSuggestion:
    """Represents a suggested refactoring."""
    title: str
    description: str
    code_before: str
    code_after: str
    estimated_effort: str  # "low", "medium", "high"
    benefits: List[str]

@dataclass
class AnalysisIssue:
    """Represents a single analysis issue/finding."""
    title: str
    description: str
    issue_type: IssueType
    severity: Severity
    location: SourceLocation
    rule_id: str
    suggestion: Optional[RefactoringSuggestion] = None
    metadata: Dict[str, Any] = None

    @property
    def severity_level(self) -> int:
        return self.severity.value

@dataclass
class AnalysisResult:
    """Complete analysis results for a codebase."""
    target_path: Path
    issues: List[AnalysisIssue]
    language: str
    analysis_duration: float
    files_analyzed: int
    lines_of_code: int

    def get_issues_by_severity(self, severity: Severity) -> List[AnalysisIssue]:
        return [issue for issue in self.issues if issue.severity == severity]

    def get_issues_by_type(self, issue_type: IssueType) -> List[AnalysisIssue]:
        return [issue for issue in self.issues if issue.issue_type == issue_type]
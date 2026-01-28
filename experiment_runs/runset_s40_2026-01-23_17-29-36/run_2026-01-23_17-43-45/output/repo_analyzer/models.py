"""
Data models for repository health analysis.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class ContributorMetrics(BaseModel):
    """Metrics about repository contributors."""
    total_contributors: int
    active_contributors_30d: int
    new_contributors_30d: int
    top_contributors: List[Dict[str, Any]]


class CodeQualityMetrics(BaseModel):
    """Code quality and technical debt metrics."""
    lines_of_code: int
    test_coverage_estimate: float  # Estimated based on test files ratio
    documentation_ratio: float    # README, docs, comments ratio
    average_file_size: int
    large_files_count: int        # Files > 500 lines
    complex_files_count: int      # Rough estimate based on nesting/length


class CommunityHealthMetrics(BaseModel):
    """Community engagement and responsiveness metrics."""
    open_issues: int
    closed_issues_30d: int
    issue_response_time_hours: float
    open_pull_requests: int
    merged_pull_requests_30d: int
    pr_merge_time_hours: float
    stars: int
    forks: int
    watchers: int


class ProjectVitalityMetrics(BaseModel):
    """Project activity and maintenance indicators."""
    commits_30d: int
    commits_90d: int
    last_commit_days_ago: int
    releases_count: int
    last_release_days_ago: Optional[int]
    active_branches: int
    stale_branches: int


class TechnicalDebtMetrics(BaseModel):
    """Technical debt and maintenance indicators."""
    outdated_dependencies: int    # Estimated from package files
    security_alerts: int         # Would need GitHub API access
    todo_fixme_count: int        # Count of TODO/FIXME comments
    deprecated_usage_count: int   # Rough estimate


class RepositoryHealth(BaseModel):
    """Complete repository health analysis."""
    repository_name: str
    analyzed_at: datetime
    overall_health_score: float  # 0-100 composite score

    # Metric categories
    contributor_metrics: ContributorMetrics
    code_quality_metrics: CodeQualityMetrics
    community_health_metrics: CommunityHealthMetrics
    project_vitality_metrics: ProjectVitalityMetrics
    technical_debt_metrics: TechnicalDebtMetrics

    # Analysis insights
    strengths: List[str]
    concerns: List[str]
    recommendations: List[str]


class RepositoryComparison(BaseModel):
    """Comparison analysis between repositories."""
    repositories: List[RepositoryHealth]
    comparison_insights: List[str]
    best_practices_identified: List[str]


class HealthTrend(BaseModel):
    """Historical health trend data."""
    repository_name: str
    date: datetime
    health_score: float
    key_metrics: Dict[str, float]
"""
Repository health analysis engine.
"""
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from github_client import GitHubClient
from models import (
    RepositoryHealth, ContributorMetrics, CodeQualityMetrics,
    CommunityHealthMetrics, ProjectVitalityMetrics, TechnicalDebtMetrics
)


class RepositoryHealthAnalyzer:
    """Analyzes repository health using GitHub API data."""

    def __init__(self, github_client: GitHubClient):
        self.github_client = github_client

    def analyze_repository(self, owner: str, repo: str) -> RepositoryHealth:
        """Perform complete health analysis of a repository."""
        print(f"Analyzing repository: {owner}/{repo}")

        # Gather raw data
        repo_data = self.github_client.get_repository(owner, repo)
        contributors = self.github_client.get_contributors(owner, repo)

        # Get commits from last 90 days for activity analysis
        since_90d = datetime.now() - timedelta(days=90)
        recent_commits = self.github_client.get_commits(owner, repo, since=since_90d)

        issues = self.github_client.get_issues(owner, repo)
        pull_requests = self.github_client.get_pull_requests(owner, repo)
        releases = self.github_client.get_releases(owner, repo)
        branches = self.github_client.get_branches(owner, repo)

        # Sample repository structure for code analysis
        contents = self.github_client.get_repository_contents(owner, repo)

        # Analyze each metric category
        contributor_metrics = self._analyze_contributors(contributors, recent_commits)
        code_quality_metrics = self._analyze_code_quality(owner, repo, contents, repo_data)
        community_health_metrics = self._analyze_community_health(repo_data, issues, pull_requests)
        project_vitality_metrics = self._analyze_project_vitality(recent_commits, releases, branches)
        technical_debt_metrics = self._analyze_technical_debt(owner, repo, contents)

        # Calculate overall health score
        health_score = self._calculate_overall_health_score(
            contributor_metrics, code_quality_metrics, community_health_metrics,
            project_vitality_metrics, technical_debt_metrics
        )

        # Generate insights
        strengths, concerns, recommendations = self._generate_insights(
            contributor_metrics, code_quality_metrics, community_health_metrics,
            project_vitality_metrics, technical_debt_metrics, health_score
        )

        return RepositoryHealth(
            repository_name=f"{owner}/{repo}",
            analyzed_at=datetime.now(),
            overall_health_score=health_score,
            contributor_metrics=contributor_metrics,
            code_quality_metrics=code_quality_metrics,
            community_health_metrics=community_health_metrics,
            project_vitality_metrics=project_vitality_metrics,
            technical_debt_metrics=technical_debt_metrics,
            strengths=strengths,
            concerns=concerns,
            recommendations=recommendations
        )

    def _analyze_contributors(self, contributors: List[Dict], recent_commits: List[Dict]) -> ContributorMetrics:
        """Analyze contributor patterns and activity."""
        total_contributors = len(contributors)

        # Count active contributors in last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        active_30d_authors = set()

        for commit in recent_commits:
            commit_date = datetime.fromisoformat(
                commit['commit']['author']['date'].replace('Z', '+00:00')
            )
            if commit_date >= thirty_days_ago:
                if commit.get('author'):
                    active_30d_authors.add(commit['author']['login'])

        active_contributors_30d = len(active_30d_authors)

        # Estimate new contributors (simplified heuristic)
        new_contributors_30d = max(0, min(active_contributors_30d, total_contributors // 10))

        # Top contributors (first 5)
        top_contributors = [
            {
                'login': contrib['login'],
                'contributions': contrib['contributions'],
                'avatar_url': contrib.get('avatar_url', '')
            }
            for contrib in contributors[:5]
        ]

        return ContributorMetrics(
            total_contributors=total_contributors,
            active_contributors_30d=active_contributors_30d,
            new_contributors_30d=new_contributors_30d,
            top_contributors=top_contributors
        )

    def _analyze_code_quality(self, owner: str, repo: str, contents: List[Dict],
                            repo_data: Dict) -> CodeQualityMetrics:
        """Analyze code quality indicators."""
        # Basic metrics from repository data
        lines_of_code = repo_data.get('size', 0) * 10  # Rough estimate (KB * 10)

        # Analyze file structure
        file_analysis = self._analyze_file_structure(owner, repo, contents)

        return CodeQualityMetrics(
            lines_of_code=lines_of_code,
            test_coverage_estimate=file_analysis['test_coverage_estimate'],
            documentation_ratio=file_analysis['documentation_ratio'],
            average_file_size=file_analysis['average_file_size'],
            large_files_count=file_analysis['large_files_count'],
            complex_files_count=file_analysis['complex_files_count']
        )

    def _analyze_file_structure(self, owner: str, repo: str, contents: List[Dict]) -> Dict[str, Any]:
        """Analyze repository file structure for quality metrics."""
        total_files = 0
        test_files = 0
        doc_files = 0
        total_size = 0
        large_files = 0

        # Sample some files for analysis
        sampled_files = contents[:20] if len(contents) > 20 else contents

        for item in sampled_files:
            if item['type'] == 'file':
                total_files += 1
                file_size = item.get('size', 0)
                total_size += file_size

                filename = item['name'].lower()

                # Check for test files
                if any(pattern in filename for pattern in ['test', 'spec', '__test__']):
                    test_files += 1

                # Check for documentation files
                if any(pattern in filename for pattern in ['readme', '.md', 'doc', 'guide']):
                    doc_files += 1

                # Check for large files (> 50KB)
                if file_size > 50000:
                    large_files += 1

        test_coverage_estimate = (test_files / max(total_files, 1)) * 100
        documentation_ratio = (doc_files / max(total_files, 1)) * 100
        average_file_size = total_size // max(total_files, 1)

        # Estimate complex files (simplified heuristic)
        complex_files = large_files  # Using large files as proxy for complexity

        return {
            'test_coverage_estimate': min(100, test_coverage_estimate * 2),  # Boost estimate
            'documentation_ratio': min(100, documentation_ratio * 3),  # Boost estimate
            'average_file_size': average_file_size,
            'large_files_count': large_files,
            'complex_files_count': complex_files
        }

    def _analyze_community_health(self, repo_data: Dict, issues: List[Dict],
                                pull_requests: List[Dict]) -> CommunityHealthMetrics:
        """Analyze community engagement metrics."""
        open_issues = repo_data.get('open_issues_count', 0)
        stars = repo_data.get('stargazers_count', 0)
        forks = repo_data.get('forks_count', 0)
        watchers = repo_data.get('subscribers_count', 0)

        # Analyze recent issue activity
        thirty_days_ago = datetime.now() - timedelta(days=30)
        closed_issues_30d = 0
        issue_response_times = []

        for issue in issues:
            if issue.get('state') == 'closed':
                closed_date = datetime.fromisoformat(
                    issue['closed_at'].replace('Z', '+00:00')
                )
                if closed_date >= thirty_days_ago:
                    closed_issues_30d += 1

                # Calculate response time (simplified)
                created_date = datetime.fromisoformat(
                    issue['created_at'].replace('Z', '+00:00')
                )
                response_time = (closed_date - created_date).total_seconds() / 3600
                issue_response_times.append(response_time)

        avg_issue_response_time = sum(issue_response_times) / max(len(issue_response_times), 1)

        # Analyze pull request metrics
        open_prs = len([pr for pr in pull_requests if pr['state'] == 'open'])
        merged_prs_30d = 0
        pr_merge_times = []

        for pr in pull_requests:
            if pr.get('state') == 'closed' and pr.get('merged_at'):
                merged_date = datetime.fromisoformat(
                    pr['merged_at'].replace('Z', '+00:00')
                )
                if merged_date >= thirty_days_ago:
                    merged_prs_30d += 1

                # Calculate merge time
                created_date = datetime.fromisoformat(
                    pr['created_at'].replace('Z', '+00:00')
                )
                merge_time = (merged_date - created_date).total_seconds() / 3600
                pr_merge_times.append(merge_time)

        avg_pr_merge_time = sum(pr_merge_times) / max(len(pr_merge_times), 1)

        return CommunityHealthMetrics(
            open_issues=open_issues,
            closed_issues_30d=closed_issues_30d,
            issue_response_time_hours=avg_issue_response_time,
            open_pull_requests=open_prs,
            merged_pull_requests_30d=merged_prs_30d,
            pr_merge_time_hours=avg_pr_merge_time,
            stars=stars,
            forks=forks,
            watchers=watchers
        )

    def _analyze_project_vitality(self, recent_commits: List[Dict], releases: List[Dict],
                                branches: List[Dict]) -> ProjectVitalityMetrics:
        """Analyze project activity and maintenance."""
        now = datetime.now()
        thirty_days_ago = now - timedelta(days=30)
        ninety_days_ago = now - timedelta(days=90)

        commits_30d = 0
        commits_90d = len(recent_commits)  # These are already filtered to 90 days
        last_commit_days = float('inf')

        for commit in recent_commits:
            commit_date = datetime.fromisoformat(
                commit['commit']['author']['date'].replace('Z', '+00:00')
            )

            if commit_date >= thirty_days_ago:
                commits_30d += 1

            # Track most recent commit
            days_ago = (now - commit_date).days
            if days_ago < last_commit_days:
                last_commit_days = days_ago

        # Analyze releases
        releases_count = len(releases)
        last_release_days = None

        if releases:
            latest_release_date = datetime.fromisoformat(
                releases[0]['published_at'].replace('Z', '+00:00')
            )
            last_release_days = (now - latest_release_date).days

        # Analyze branches (simplified)
        active_branches = len(branches)
        stale_branches = max(0, active_branches - 5)  # Assume >5 branches might be stale

        return ProjectVitalityMetrics(
            commits_30d=commits_30d,
            commits_90d=commits_90d,
            last_commit_days_ago=int(last_commit_days) if last_commit_days != float('inf') else 0,
            releases_count=releases_count,
            last_release_days_ago=last_release_days,
            active_branches=active_branches,
            stale_branches=stale_branches
        )

    def _analyze_technical_debt(self, owner: str, repo: str, contents: List[Dict]) -> TechnicalDebtMetrics:
        """Analyze technical debt indicators."""
        # This is a simplified analysis - in production, we'd scan actual file contents

        outdated_dependencies = 0
        todo_fixme_count = 0
        deprecated_usage_count = 0

        # Look for dependency files
        dependency_files = ['package.json', 'requirements.txt', 'Pipfile', 'pom.xml', 'build.gradle']
        has_dependencies = any(
            item['name'] in dependency_files for item in contents if item['type'] == 'file'
        )

        if has_dependencies:
            outdated_dependencies = 3  # Placeholder estimate

        # Sample some files for TODO/FIXME analysis
        for item in contents[:10]:
            if item['type'] == 'file' and item['name'].endswith(('.py', '.js', '.java', '.cpp', '.c')):
                file_content = self.github_client.get_file_content(owner, repo, item['path'])
                if file_content:
                    todo_fixme_count += len(re.findall(r'(TODO|FIXME|XXX|HACK)', file_content, re.IGNORECASE))
                    deprecated_usage_count += len(re.findall(r'@deprecated|deprecated', file_content, re.IGNORECASE))

        return TechnicalDebtMetrics(
            outdated_dependencies=outdated_dependencies,
            security_alerts=0,  # Would need GitHub Security API
            todo_fixme_count=todo_fixme_count,
            deprecated_usage_count=deprecated_usage_count
        )

    def _calculate_overall_health_score(self, contributor_metrics: ContributorMetrics,
                                      code_quality_metrics: CodeQualityMetrics,
                                      community_health_metrics: CommunityHealthMetrics,
                                      project_vitality_metrics: ProjectVitalityMetrics,
                                      technical_debt_metrics: TechnicalDebtMetrics) -> float:
        """Calculate composite health score (0-100)."""

        # Contributor score (25% weight)
        contributor_score = min(100, (
            (contributor_metrics.active_contributors_30d / max(contributor_metrics.total_contributors, 1)) * 50 +
            min(contributor_metrics.active_contributors_30d * 10, 50)
        ))

        # Code quality score (25% weight)
        quality_score = (
            min(code_quality_metrics.test_coverage_estimate, 100) * 0.4 +
            min(code_quality_metrics.documentation_ratio, 100) * 0.3 +
            max(0, 100 - code_quality_metrics.large_files_count * 10) * 0.3
        )

        # Community health score (25% weight)
        community_score = min(100, (
            min(community_health_metrics.stars / 10, 50) +
            min(community_health_metrics.closed_issues_30d * 5, 25) +
            min(community_health_metrics.merged_pull_requests_30d * 5, 25)
        ))

        # Project vitality score (20% weight)
        vitality_score = min(100, (
            min(project_vitality_metrics.commits_30d * 2, 50) +
            max(0, 50 - project_vitality_metrics.last_commit_days_ago * 2) +
            min(project_vitality_metrics.releases_count * 5, 25)
        ))

        # Technical debt penalty (5% weight)
        debt_penalty = min(50, (
            technical_debt_metrics.outdated_dependencies * 5 +
            technical_debt_metrics.todo_fixme_count * 2 +
            technical_debt_metrics.deprecated_usage_count * 3
        ))

        # Weighted average with debt penalty
        overall_score = (
            contributor_score * 0.25 +
            quality_score * 0.25 +
            community_score * 0.25 +
            vitality_score * 0.20
        ) - (debt_penalty * 0.05)

        return max(0, min(100, overall_score))

    def _generate_insights(self, contributor_metrics: ContributorMetrics,
                         code_quality_metrics: CodeQualityMetrics,
                         community_health_metrics: CommunityHealthMetrics,
                         project_vitality_metrics: ProjectVitalityMetrics,
                         technical_debt_metrics: TechnicalDebtMetrics,
                         health_score: float) -> tuple[List[str], List[str], List[str]]:
        """Generate insights, concerns, and recommendations."""

        strengths = []
        concerns = []
        recommendations = []

        # Analyze strengths
        if contributor_metrics.active_contributors_30d > 5:
            strengths.append("Active contributor community with regular engagement")

        if code_quality_metrics.test_coverage_estimate > 70:
            strengths.append("Good test coverage indicates robust code quality")

        if community_health_metrics.stars > 100:
            strengths.append("Strong community interest with significant star count")

        if project_vitality_metrics.commits_30d > 10:
            strengths.append("Consistent development activity with regular commits")

        # Analyze concerns
        if project_vitality_metrics.last_commit_days_ago > 30:
            concerns.append("Repository appears inactive with no recent commits")

        if community_health_metrics.issue_response_time_hours > 168:  # 1 week
            concerns.append("Slow issue response time may discourage contributors")

        if technical_debt_metrics.todo_fixme_count > 20:
            concerns.append("High number of TODO/FIXME comments indicates technical debt")

        if contributor_metrics.active_contributors_30d < 2:
            concerns.append("Limited active contributors creates bus factor risk")

        # Generate recommendations
        if health_score < 50:
            recommendations.append("Focus on increasing development activity and community engagement")

        if code_quality_metrics.test_coverage_estimate < 50:
            recommendations.append("Improve test coverage to enhance code reliability")

        if community_health_metrics.open_issues > community_health_metrics.closed_issues_30d * 5:
            recommendations.append("Address backlog of open issues to improve project health")

        if project_vitality_metrics.releases_count == 0:
            recommendations.append("Consider creating releases to improve project visibility")

        return strengths, concerns, recommendations
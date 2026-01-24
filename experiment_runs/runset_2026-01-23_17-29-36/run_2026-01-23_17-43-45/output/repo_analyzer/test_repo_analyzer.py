"""
Comprehensive test suite for Repository Health Analyzer.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from github_client import GitHubClient
from health_analyzer import RepositoryHealthAnalyzer
from models import RepositoryHealth


@pytest.fixture
def mock_github_client():
    """Create a mock GitHub client with sample data."""
    client = Mock(spec=GitHubClient)

    # Mock repository data
    client.get_repository.return_value = {
        'name': 'test-repo',
        'full_name': 'owner/test-repo',
        'stargazers_count': 150,
        'forks_count': 25,
        'subscribers_count': 12,
        'open_issues_count': 8,
        'size': 1024  # KB
    }

    # Mock contributors
    client.get_contributors.return_value = [
        {'login': 'contributor1', 'contributions': 45, 'avatar_url': 'https://github.com/avatar1.png'},
        {'login': 'contributor2', 'contributions': 32, 'avatar_url': 'https://github.com/avatar2.png'},
        {'login': 'contributor3', 'contributions': 18, 'avatar_url': 'https://github.com/avatar3.png'}
    ]

    # Mock recent commits
    now = datetime.now()
    client.get_commits.return_value = [
        {
            'commit': {
                'author': {
                    'date': (now - timedelta(days=1)).isoformat() + 'Z'
                }
            },
            'author': {'login': 'contributor1'}
        },
        {
            'commit': {
                'author': {
                    'date': (now - timedelta(days=5)).isoformat() + 'Z'
                }
            },
            'author': {'login': 'contributor2'}
        },
        {
            'commit': {
                'author': {
                    'date': (now - timedelta(days=15)).isoformat() + 'Z'
                }
            },
            'author': {'login': 'contributor1'}
        }
    ]

    # Mock issues
    client.get_issues.return_value = [
        {
            'state': 'open',
            'created_at': (now - timedelta(days=3)).isoformat() + 'Z'
        },
        {
            'state': 'closed',
            'created_at': (now - timedelta(days=10)).isoformat() + 'Z',
            'closed_at': (now - timedelta(days=8)).isoformat() + 'Z'
        }
    ]

    # Mock pull requests
    client.get_pull_requests.return_value = [
        {
            'state': 'open',
            'created_at': (now - timedelta(days=2)).isoformat() + 'Z'
        },
        {
            'state': 'closed',
            'merged_at': (now - timedelta(days=5)).isoformat() + 'Z',
            'created_at': (now - timedelta(days=7)).isoformat() + 'Z'
        }
    ]

    # Mock releases
    client.get_releases.return_value = [
        {
            'tag_name': 'v1.0.0',
            'published_at': (now - timedelta(days=30)).isoformat() + 'Z'
        }
    ]

    # Mock branches
    client.get_branches.return_value = [
        {'name': 'main'},
        {'name': 'develop'},
        {'name': 'feature/new-ui'}
    ]

    # Mock repository contents
    client.get_repository_contents.return_value = [
        {'name': 'README.md', 'type': 'file', 'size': 2048, 'path': 'README.md'},
        {'name': 'main.py', 'type': 'file', 'size': 15000, 'path': 'main.py'},
        {'name': 'test_main.py', 'type': 'file', 'size': 8000, 'path': 'test_main.py'},
        {'name': 'utils.py', 'type': 'file', 'size': 60000, 'path': 'utils.py'},  # Large file
        {'name': 'docs', 'type': 'dir', 'size': 0, 'path': 'docs'}
    ]

    # Mock file content
    client.get_file_content.return_value = '''
    def example_function():
        # TODO: Optimize this function
        # FIXME: Handle edge case
        return "Hello World"

    @deprecated
    def old_function():
        pass
    '''

    return client


@pytest.fixture
def analyzer(mock_github_client):
    """Create analyzer with mocked GitHub client."""
    return RepositoryHealthAnalyzer(mock_github_client)


class TestGitHubClient:
    """Test GitHub API client functionality."""

    def test_github_client_initialization(self):
        """Test GitHub client initialization."""
        client = GitHubClient()
        assert client.base_url == 'https://api.github.com'
        assert client.session is not None

    def test_github_client_with_token(self):
        """Test GitHub client with authentication token."""
        client = GitHubClient(token='test_token')
        assert 'Authorization' in client.session.headers
        assert client.session.headers['Authorization'] == 'token test_token'


class TestRepositoryHealthAnalyzer:
    """Test repository health analysis functionality."""

    def test_analyze_repository_returns_health_object(self, analyzer, mock_github_client):
        """Test that repository analysis returns proper RepositoryHealth object."""
        result = analyzer.analyze_repository('owner', 'test-repo')

        assert isinstance(result, RepositoryHealth)
        assert result.repository_name == 'owner/test-repo'
        assert isinstance(result.overall_health_score, float)
        assert 0 <= result.overall_health_score <= 100

    def test_contributor_metrics_analysis(self, analyzer, mock_github_client):
        """Test contributor metrics calculation."""
        result = analyzer.analyze_repository('owner', 'test-repo')
        contrib_metrics = result.contributor_metrics

        assert contrib_metrics.total_contributors == 3
        assert contrib_metrics.active_contributors_30d >= 0
        assert len(contrib_metrics.top_contributors) <= 5
        assert all('login' in contrib for contrib in contrib_metrics.top_contributors)

    def test_code_quality_metrics_analysis(self, analyzer, mock_github_client):
        """Test code quality metrics calculation."""
        result = analyzer.analyze_repository('owner', 'test-repo')
        quality_metrics = result.code_quality_metrics

        assert quality_metrics.lines_of_code > 0
        assert 0 <= quality_metrics.test_coverage_estimate <= 100
        assert 0 <= quality_metrics.documentation_ratio <= 100
        assert quality_metrics.large_files_count >= 0

    def test_community_health_metrics_analysis(self, analyzer, mock_github_client):
        """Test community health metrics calculation."""
        result = analyzer.analyze_repository('owner', 'test-repo')
        community_metrics = result.community_health_metrics

        assert community_metrics.stars == 150
        assert community_metrics.forks == 25
        assert community_metrics.open_issues == 8
        assert community_metrics.issue_response_time_hours >= 0

    def test_project_vitality_metrics_analysis(self, analyzer, mock_github_client):
        """Test project vitality metrics calculation."""
        result = analyzer.analyze_repository('owner', 'test-repo')
        vitality_metrics = result.project_vitality_metrics

        assert vitality_metrics.commits_30d >= 0
        assert vitality_metrics.commits_90d >= 0
        assert vitality_metrics.releases_count >= 0
        assert vitality_metrics.active_branches >= 0

    def test_technical_debt_metrics_analysis(self, analyzer, mock_github_client):
        """Test technical debt metrics calculation."""
        result = analyzer.analyze_repository('owner', 'test-repo')
        debt_metrics = result.technical_debt_metrics

        assert debt_metrics.todo_fixme_count >= 0
        assert debt_metrics.deprecated_usage_count >= 0
        assert debt_metrics.outdated_dependencies >= 0

    def test_insights_generation(self, analyzer, mock_github_client):
        """Test that insights, concerns, and recommendations are generated."""
        result = analyzer.analyze_repository('owner', 'test-repo')

        assert isinstance(result.strengths, list)
        assert isinstance(result.concerns, list)
        assert isinstance(result.recommendations, list)

        # All insights should be non-empty strings
        for strength in result.strengths:
            assert isinstance(strength, str)
            assert len(strength.strip()) > 0

        for concern in result.concerns:
            assert isinstance(concern, str)
            assert len(concern.strip()) > 0

        for recommendation in result.recommendations:
            assert isinstance(recommendation, str)
            assert len(recommendation.strip()) > 0

    def test_health_score_calculation(self, analyzer, mock_github_client):
        """Test that health score is properly calculated."""
        result = analyzer.analyze_repository('owner', 'test-repo')

        # Health score should be between 0 and 100
        assert 0 <= result.overall_health_score <= 100

        # Should be a reasonable score for our test data
        assert result.overall_health_score > 20  # Not completely unhealthy


class TestHealthScoreCalculation:
    """Test health score calculation edge cases."""

    def test_zero_contributors_handling(self, analyzer, mock_github_client):
        """Test handling of repositories with no contributors."""
        mock_github_client.get_contributors.return_value = []
        result = analyzer.analyze_repository('owner', 'empty-repo')

        assert result.contributor_metrics.total_contributors == 0
        assert isinstance(result.overall_health_score, float)

    def test_no_recent_activity_handling(self, analyzer, mock_github_client):
        """Test handling of repositories with no recent activity."""
        mock_github_client.get_commits.return_value = []
        result = analyzer.analyze_repository('owner', 'stale-repo')

        assert result.project_vitality_metrics.commits_30d == 0
        assert result.project_vitality_metrics.commits_90d == 0


class TestErrorHandling:
    """Test error handling in various scenarios."""

    def test_api_error_handling(self, analyzer):
        """Test handling of GitHub API errors."""
        mock_github_client = Mock(spec=GitHubClient)
        mock_github_client.get_repository.side_effect = Exception("API Error")

        analyzer_with_error = RepositoryHealthAnalyzer(mock_github_client)

        with pytest.raises(Exception):
            analyzer_with_error.analyze_repository('owner', 'repo')

    def test_missing_data_handling(self, analyzer, mock_github_client):
        """Test handling of missing or None data."""
        # Mock incomplete repository data
        mock_github_client.get_repository.return_value = {
            'name': 'test-repo',
            'full_name': 'owner/test-repo'
            # Missing many fields
        }

        result = analyzer.analyze_repository('owner', 'incomplete-repo')

        # Should still return valid RepositoryHealth object
        assert isinstance(result, RepositoryHealth)
        assert result.overall_health_score >= 0


# Integration test helpers
def create_test_repository_data():
    """Helper to create realistic test repository data."""
    return {
        'name': 'awesome-project',
        'full_name': 'github-user/awesome-project',
        'stargazers_count': 1250,
        'forks_count': 180,
        'subscribers_count': 45,
        'open_issues_count': 12,
        'size': 2048
    }


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
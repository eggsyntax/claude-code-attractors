"""
GitHub API client for repository data collection.
"""
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()


class GitHubClient:
    """Client for fetching repository data from GitHub API."""

    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub client with optional authentication token."""
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.base_url = 'https://api.github.com'
        self.session = requests.Session()

        if self.token:
            self.session.headers.update({
                'Authorization': f'token {self.token}',
                'Accept': 'application/vnd.github.v3+json'
            })

    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get basic repository information."""
        url = f"{self.base_url}/repos/{owner}/{repo}"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_contributors(self, owner: str, repo: str, per_page: int = 100) -> List[Dict[str, Any]]:
        """Get repository contributors."""
        url = f"{self.base_url}/repos/{owner}/{repo}/contributors"
        params = {'per_page': per_page}
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_commits(self, owner: str, repo: str, since: Optional[datetime] = None,
                   per_page: int = 100, max_pages: int = 10) -> List[Dict[str, Any]]:
        """Get repository commits with optional date filtering."""
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {'per_page': per_page}

        if since:
            params['since'] = since.isoformat()

        commits = []
        page = 1

        while page <= max_pages:
            params['page'] = page
            response = self.session.get(url, params=params)
            response.raise_for_status()

            page_commits = response.json()
            if not page_commits:
                break

            commits.extend(page_commits)

            # Check if we have more pages
            if 'next' not in response.links:
                break

            page += 1

        return commits

    def get_issues(self, owner: str, repo: str, state: str = 'all',
                  per_page: int = 100, max_pages: int = 5) -> List[Dict[str, Any]]:
        """Get repository issues."""
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        params = {'state': state, 'per_page': per_page}

        issues = []
        page = 1

        while page <= max_pages:
            params['page'] = page
            response = self.session.get(url, params=params)
            response.raise_for_status()

            page_issues = response.json()
            if not page_issues:
                break

            # Filter out pull requests (they appear in issues endpoint)
            page_issues = [issue for issue in page_issues if 'pull_request' not in issue]
            issues.extend(page_issues)

            if 'next' not in response.links:
                break

            page += 1

        return issues

    def get_pull_requests(self, owner: str, repo: str, state: str = 'all',
                         per_page: int = 100, max_pages: int = 5) -> List[Dict[str, Any]]:
        """Get repository pull requests."""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        params = {'state': state, 'per_page': per_page}

        pulls = []
        page = 1

        while page <= max_pages:
            params['page'] = page
            response = self.session.get(url, params=params)
            response.raise_for_status()

            page_pulls = response.json()
            if not page_pulls:
                break

            pulls.extend(page_pulls)

            if 'next' not in response.links:
                break

            page += 1

        return pulls

    def get_releases(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Get repository releases."""
        url = f"{self.base_url}/repos/{owner}/{repo}/releases"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_branches(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """Get repository branches."""
        url = f"{self.base_url}/repos/{owner}/{repo}/branches"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_repository_contents(self, owner: str, repo: str, path: str = "") -> List[Dict[str, Any]]:
        """Get repository file contents (directory listing)."""
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{path}"
        response = self.session.get(url)

        if response.status_code == 404:
            return []

        response.raise_for_status()
        result = response.json()

        # Handle single file vs directory
        return result if isinstance(result, list) else [result]

    def get_file_content(self, owner: str, repo: str, path: str) -> Optional[str]:
        """Get content of a specific file."""
        try:
            contents = self.get_repository_contents(owner, repo, path)
            if contents and len(contents) == 1:
                file_info = contents[0]
                if file_info.get('type') == 'file':
                    # Get the actual file content
                    response = self.session.get(file_info['download_url'])
                    response.raise_for_status()
                    return response.text
        except Exception:
            pass
        return None
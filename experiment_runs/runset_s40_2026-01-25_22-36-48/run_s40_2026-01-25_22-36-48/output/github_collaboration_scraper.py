"""
GitHub Collaboration Scraper - Alice's Infrastructure Component
Scrapes GitHub repositories to extract collaboration patterns for analysis.
Designed to integrate with Bob's GitHubCollaborationAnalyzer.
"""

import requests
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re

class GitHubScraper:
    """
    Scrapes GitHub repositories for collaboration data.
    Handles API rate limiting, authentication, and data formatting.
    """

    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Collaboration-Pattern-Analyzer-v1.0"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"

        self.rate_limit_remaining = 5000
        self.rate_limit_reset = time.time()

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make GitHub API request with rate limiting and error handling."""
        if self.rate_limit_remaining <= 10:
            sleep_time = max(0, self.rate_limit_reset - time.time())
            if sleep_time > 0:
                print(f"Rate limit approaching, sleeping {sleep_time:.0f}s")
                time.sleep(sleep_time)

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = requests.get(url, headers=self.headers, params=params)

            # Update rate limit info
            self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 0))
            self.rate_limit_reset = int(response.headers.get('X-RateLimit-Reset', time.time()))

            if response.status_code == 200:
                return response.json()
            else:
                print(f"API Error {response.status_code}: {response.text}")
                return None

        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def scrape_repository_commits(self, repo_owner: str, repo_name: str,
                                days_back: int = 30, max_commits: int = 200) -> List[Dict]:
        """
        Scrape commits from a repository with collaboration-focused data extraction.
        Returns data in format expected by Bob's analyzer.
        """
        print(f"Scraping commits from {repo_owner}/{repo_name}...")

        # Calculate date range
        since_date = (datetime.now() - timedelta(days=days_back)).isoformat()

        commits = []
        page = 1

        while len(commits) < max_commits:
            params = {
                'since': since_date,
                'per_page': min(100, max_commits - len(commits)),
                'page': page
            }

            endpoint = f"repos/{repo_owner}/{repo_name}/commits"
            response_data = self._make_request(endpoint, params)

            if not response_data:
                break

            if len(response_data) == 0:
                break  # No more commits

            for commit_data in response_data:
                # Format for Bob's analyzer
                commit_obj = {
                    'sha': commit_data['sha'],
                    'message': commit_data['commit']['message'],
                    'author': commit_data['commit']['author']['name'],
                    'author_email': commit_data['commit']['author']['email'],
                    'timestamp': commit_data['commit']['author']['date'],
                    'url': commit_data['html_url'],
                    # Additional metadata for pattern recognition
                    'stats': self._get_commit_stats(repo_owner, repo_name, commit_data['sha']),
                    'collaboration_signals': self._extract_collaboration_signals(commit_data['commit']['message'])
                }
                commits.append(commit_obj)

            page += 1
            time.sleep(0.1)  # Be nice to the API

        print(f"Scraped {len(commits)} commits")
        return commits

    def scrape_pull_requests(self, repo_owner: str, repo_name: str,
                           days_back: int = 30, max_prs: int = 50) -> List[Dict]:
        """
        Scrape pull requests with focus on collaboration patterns.
        Returns data formatted for Bob's analyzer.
        """
        print(f"Scraping pull requests from {repo_owner}/{repo_name}...")

        # Get both open and recently closed PRs
        prs = []

        for state in ['open', 'closed']:
            page = 1
            while len(prs) < max_prs:
                params = {
                    'state': state,
                    'sort': 'updated',
                    'direction': 'desc',
                    'per_page': min(100, max_prs - len(prs)),
                    'page': page
                }

                endpoint = f"repos/{repo_owner}/{repo_name}/pulls"
                response_data = self._make_request(endpoint, params)

                if not response_data or len(response_data) == 0:
                    break

                for pr_data in response_data:
                    # Skip PRs older than our date range
                    updated_at = datetime.fromisoformat(pr_data['updated_at'].replace('Z', '+00:00'))
                    cutoff_date = datetime.now().replace(tzinfo=updated_at.tzinfo) - timedelta(days=days_back)
                    if updated_at < cutoff_date:
                        continue

                    # Get PR comments for collaboration analysis
                    comments = self._get_pr_comments(repo_owner, repo_name, pr_data['number'])
                    reviews = self._get_pr_reviews(repo_owner, repo_name, pr_data['number'])

                    pr_obj = {
                        'number': pr_data['number'],
                        'title': pr_data['title'],
                        'description': pr_data['body'] or '',
                        'author': pr_data['user']['login'],
                        'state': pr_data['state'],
                        'created_at': pr_data['created_at'],
                        'updated_at': pr_data['updated_at'],
                        'merged_at': pr_data.get('merged_at'),
                        'comments': comments,
                        'reviews': reviews,
                        'collaboration_signals': self._extract_pr_collaboration_signals(
                            pr_data['title'], pr_data['body'] or '', comments, reviews
                        )
                    }
                    prs.append(pr_obj)

                page += 1
                if state == 'closed' and page > 3:  # Limit closed PR pages
                    break

        print(f"Scraped {len(prs)} pull requests")
        return prs[:max_prs]

    def _get_commit_stats(self, repo_owner: str, repo_name: str, sha: str) -> Dict:
        """Get commit statistics for collaboration analysis."""
        endpoint = f"repos/{repo_owner}/{repo_name}/commits/{sha}"
        commit_detail = self._make_request(endpoint)

        if commit_detail and 'stats' in commit_detail:
            return {
                'additions': commit_detail['stats']['additions'],
                'deletions': commit_detail['stats']['deletions'],
                'total_changes': commit_detail['stats']['total']
            }
        return {'additions': 0, 'deletions': 0, 'total_changes': 0}

    def _get_pr_comments(self, repo_owner: str, repo_name: str, pr_number: int) -> List[Dict]:
        """Get PR comments for collaboration analysis."""
        endpoint = f"repos/{repo_owner}/{repo_name}/issues/{pr_number}/comments"
        comments_data = self._make_request(endpoint)

        if not comments_data:
            return []

        return [{
            'author': comment['user']['login'],
            'body': comment['body'],
            'created_at': comment['created_at']
        } for comment in comments_data[:20]]  # Limit to recent comments

    def _get_pr_reviews(self, repo_owner: str, repo_name: str, pr_number: int) -> List[Dict]:
        """Get PR reviews for collaboration analysis."""
        endpoint = f"repos/{repo_owner}/{repo_name}/pulls/{pr_number}/reviews"
        reviews_data = self._make_request(endpoint)

        if not reviews_data:
            return []

        return [{
            'author': review['user']['login'],
            'state': review['state'],
            'body': review['body'] or '',
            'submitted_at': review['submitted_at']
        } for review in reviews_data[:10]]  # Limit reviews

    def _extract_collaboration_signals(self, commit_message: str) -> Dict:
        """Extract collaboration signals from commit messages."""
        message_lower = commit_message.lower()

        signals = {
            'has_co_author': 'co-authored-by:' in message_lower,
            'references_issue': bool(re.search(r'#\d+|fixes|closes|resolves', message_lower)),
            'mentions_user': '@' in commit_message,
            'indicates_pair_programming': any(word in message_lower for word in
                                            ['pair', 'pairing', 'mob', 'together', 'with']),
            'indicates_review': any(word in message_lower for word in
                                  ['review', 'feedback', 'suggestions', 'requested changes']),
            'indicates_merge': any(word in message_lower for word in
                                 ['merge', 'merged', 'pull request', 'pr'])
        }

        return signals

    def _extract_pr_collaboration_signals(self, title: str, description: str,
                                        comments: List[Dict], reviews: List[Dict]) -> Dict:
        """Extract collaboration signals from PR data."""
        all_text = f"{title} {description}".lower()

        signals = {
            'has_multiple_reviewers': len(set(r['author'] for r in reviews)) > 1,
            'has_discussion': len(comments) > 2,
            'mentions_collaboration': any(word in all_text for word in
                                        ['collaborate', 'pair', 'together', 'help', 'assist']),
            'requests_feedback': any(word in all_text for word in
                                   ['feedback', 'review', 'thoughts', 'opinions', 'wdyt']),
            'references_issue': bool(re.search(r'#\d+|fixes|closes|resolves', all_text)),
            'has_code_review_comments': any('CHANGES_REQUESTED' in r['state'] for r in reviews),
            'approved_by_multiple': sum(1 for r in reviews if r['state'] == 'APPROVED') > 1
        }

        return signals

    def scrape_repository_full(self, repo_owner: str, repo_name: str,
                             days_back: int = 30) -> Dict:
        """
        Complete repository scrape for collaboration analysis.
        Returns all data formatted for Bob's analyzer.
        """
        print(f"\n=== SCRAPING REPOSITORY: {repo_owner}/{repo_name} ===")

        # Get repository metadata
        repo_data = self._make_request(f"repos/{repo_owner}/{repo_name}")

        if not repo_data:
            return {"error": "Could not access repository"}

        # Scrape commits and PRs
        commits = self.scrape_repository_commits(repo_owner, repo_name, days_back)
        pull_requests = self.scrape_pull_requests(repo_owner, repo_name, days_back)

        # Package for Bob's analyzer
        collaboration_data = {
            'repository': {
                'name': repo_data['name'],
                'full_name': repo_data['full_name'],
                'description': repo_data.get('description', ''),
                'language': repo_data.get('language', 'Unknown'),
                'stars': repo_data['stargazers_count'],
                'contributors_count': repo_data.get('size', 0)  # Approximation
            },
            'commits': commits,
            'pull_requests': pull_requests,
            'analysis_metadata': {
                'scraped_at': datetime.now().isoformat(),
                'days_analyzed': days_back,
                'total_commits': len(commits),
                'total_prs': len(pull_requests),
                'rate_limit_remaining': self.rate_limit_remaining
            }
        }

        return collaboration_data

def main():
    """Example usage of the GitHub scraper."""
    print("GitHub Collaboration Scraper - Ready for Integration!")
    print("This scraper is designed to feed data directly into Bob's GitHubCollaborationAnalyzer.")
    print("\nExample usage:")
    print("scraper = GitHubScraper()")
    print("data = scraper.scrape_repository_full('microsoft', 'vscode', days_back=7)")
    print("analyzer = GitHubCollaborationAnalyzer()  # Bob's component")
    print("results = analyzer.analyze_collaboration_data(data)")

    # Demonstrate the data format
    scraper = GitHubScraper()
    print(f"\nScraper initialized. Rate limit: {scraper.rate_limit_remaining}")
    print("Ready to scrape repository data for collaboration analysis!")

if __name__ == "__main__":
    main()
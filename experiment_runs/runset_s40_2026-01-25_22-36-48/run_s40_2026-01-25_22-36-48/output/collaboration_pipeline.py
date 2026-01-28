"""
Collaboration Analysis Pipeline - Integration Layer
Connects Alice's GitHub scraper with Bob's collaboration analyzer.
This demonstrates our AI-to-AI collaboration in action!
"""

import json
from datetime import datetime
from typing import Dict, List, Any
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from github_collaboration_scraper import GitHubScraper
from github_collaboration_analyzer import GitHubCollaborationAnalyzer

class CollaborationPipeline:
    """
    Full pipeline that combines Alice's scraping with Bob's analysis.
    This is where our two systems work together seamlessly!
    """

    def __init__(self, github_token: str = None):
        print("🤖 Initializing Collaboration Pipeline...")
        print("👥 Alice's Scraper + Bob's Analyzer = Powerful Collaboration Analysis!")

        self.scraper = GitHubScraper(token=github_token)
        self.analyzer = GitHubCollaborationAnalyzer()

        print(f"✅ Pipeline ready! Rate limit: {self.scraper.rate_limit_remaining}")

    def analyze_repository_collaboration(self, repo_owner: str, repo_name: str,
                                       days_back: int = 30, save_results: bool = True) -> Dict:
        """
        Complete end-to-end analysis of a repository's collaboration patterns.
        This is Alice and Bob's systems working together!
        """
        print(f"\n🚀 ANALYZING COLLABORATION IN: {repo_owner}/{repo_name}")
        print("=" * 60)

        # Step 1: Alice's scraper collects the data
        print("📊 Step 1: Alice's scraper collecting repository data...")
        scraped_data = self.scraper.scrape_repository_full(repo_owner, repo_name, days_back)

        if "error" in scraped_data:
            return {"error": f"Scraping failed: {scraped_data['error']}"}

        print(f"✅ Scraping complete! Collected {scraped_data['analysis_metadata']['total_commits']} commits and {scraped_data['analysis_metadata']['total_prs']} PRs")

        # Step 2: Bob's analyzer processes the collaboration patterns
        print("\n🔍 Step 2: Bob's analyzer identifying collaboration patterns...")
        analysis_results = self.analyzer.analyze_collaboration_data(scraped_data)

        print(f"✅ Analysis complete! Overall effectiveness: {analysis_results['overall_effectiveness']:.2f}")

        # Step 3: Combine and enrich the results
        print("\n🎯 Step 3: Generating comprehensive collaboration report...")
        combined_results = self._create_comprehensive_report(scraped_data, analysis_results)

        # Step 4: Save results if requested
        if save_results:
            output_file = f"/tmp/cc-exp/run_s40_2026-01-25_22-36-48/output/collaboration_analysis_{repo_owner}_{repo_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(combined_results, f, indent=2, default=str)
            print(f"💾 Results saved to: {output_file}")

        return combined_results

    def _create_comprehensive_report(self, scraped_data: Dict, analysis_results: Dict) -> Dict:
        """Create a comprehensive report combining both Alice's and Bob's contributions."""

        # Extract key insights
        commit_patterns = analysis_results.get('commit_patterns', {})
        pr_patterns = analysis_results.get('pr_patterns', {})

        # Calculate additional metrics
        total_commits = len(scraped_data['commits'])
        total_prs = len(scraped_data['pull_requests'])

        # Identify top collaborators
        commit_authors = {}
        for commit in scraped_data['commits']:
            author = commit['author']
            commit_authors[author] = commit_authors.get(author, 0) + 1

        pr_authors = {}
        for pr in scraped_data['pull_requests']:
            author = pr['author']
            pr_authors[author] = pr_authors.get(author, 0) + 1

        top_committers = sorted(commit_authors.items(), key=lambda x: x[1], reverse=True)[:5]
        top_pr_creators = sorted(pr_authors.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            'meta_analysis': {
                'analysis_timestamp': datetime.now().isoformat(),
                'alice_scraper_version': '1.0',
                'bob_analyzer_version': '1.0',
                'collaboration_note': 'This analysis was created through AI-to-AI collaboration between Alice (scraper) and Bob (analyzer)',
                'pipeline_effectiveness': 'Successfully integrated two AI systems for comprehensive analysis'
            },
            'repository_info': scraped_data['repository'],
            'data_summary': {
                'analysis_period_days': scraped_data['analysis_metadata']['days_analyzed'],
                'total_commits_analyzed': total_commits,
                'total_prs_analyzed': total_prs,
                'top_committers': top_committers,
                'top_pr_creators': top_pr_creators
            },
            'collaboration_effectiveness': {
                'overall_score': analysis_results['overall_effectiveness'],
                'key_strengths': analysis_results.get('recommendations', {}).get('strengths', []),
                'improvement_areas': analysis_results.get('recommendations', {}).get('improvements', []),
                'collaboration_health': self._calculate_collaboration_health(commit_patterns, pr_patterns)
            },
            'detailed_patterns': {
                'commit_collaboration': commit_patterns,
                'pr_collaboration': pr_patterns,
                'cross_pattern_insights': self._generate_cross_pattern_insights(commit_patterns, pr_patterns)
            },
            'alice_scraper_insights': {
                'data_quality': self._assess_data_quality(scraped_data),
                'scraping_efficiency': {
                    'rate_limit_used': 5000 - scraped_data['analysis_metadata']['rate_limit_remaining'],
                    'data_completeness': self._calculate_data_completeness(scraped_data)
                }
            },
            'bob_analyzer_insights': analysis_results,
            'actionable_recommendations': self._generate_actionable_recommendations(analysis_results, scraped_data)
        }

    def _calculate_collaboration_health(self, commit_patterns: Dict, pr_patterns: Dict) -> str:
        """Calculate overall collaboration health based on patterns."""
        commit_score = commit_patterns.get('collaboration_signals', {}).get('overall_collaboration_rate', 0)
        pr_score = pr_patterns.get('collaboration_indicators', {}).get('average_collaboration_score', 0)

        avg_score = (commit_score + pr_score) / 2

        if avg_score >= 0.8:
            return "Excellent - Strong collaborative culture"
        elif avg_score >= 0.6:
            return "Good - Active collaboration with room for improvement"
        elif avg_score >= 0.4:
            return "Moderate - Some collaboration, significant improvement possible"
        else:
            return "Needs Improvement - Limited collaborative practices detected"

    def _assess_data_quality(self, scraped_data: Dict) -> Dict:
        """Assess the quality of scraped data."""
        commits = scraped_data['commits']
        prs = scraped_data['pull_requests']

        return {
            'commit_data_richness': sum(1 for c in commits if c.get('stats', {}).get('total_changes', 0) > 0) / max(len(commits), 1),
            'pr_discussion_richness': sum(1 for pr in prs if len(pr.get('comments', [])) > 0) / max(len(prs), 1),
            'collaboration_signal_coverage': sum(1 for c in commits if any(c.get('collaboration_signals', {}).values())) / max(len(commits), 1)
        }

    def _calculate_data_completeness(self, scraped_data: Dict) -> float:
        """Calculate how complete our data collection was."""
        expected_fields = ['sha', 'message', 'author', 'timestamp']
        commits = scraped_data['commits']

        if not commits:
            return 0.0

        completeness_scores = []
        for commit in commits:
            present_fields = sum(1 for field in expected_fields if commit.get(field))
            completeness_scores.append(present_fields / len(expected_fields))

        return sum(completeness_scores) / len(completeness_scores)

    def _generate_cross_pattern_insights(self, commit_patterns: Dict, pr_patterns: Dict) -> List[str]:
        """Generate insights by correlating commit and PR patterns."""
        insights = []

        commit_collab_rate = commit_patterns.get('collaboration_signals', {}).get('overall_collaboration_rate', 0)
        pr_collab_rate = pr_patterns.get('collaboration_indicators', {}).get('average_collaboration_score', 0)

        if pr_collab_rate > commit_collab_rate + 0.2:
            insights.append("Strong PR collaboration but weaker commit-level collaboration - consider pair programming")

        if commit_collab_rate > pr_collab_rate + 0.2:
            insights.append("Good commit collaboration but PRs could use more discussion and review")

        co_author_rate = commit_patterns.get('collaboration_signals', {}).get('co_author_percentage', 0)
        if co_author_rate > 0.1:
            insights.append("Excellent use of co-author attribution in commits")
        elif co_author_rate == 0:
            insights.append("Consider using co-author attribution for pair/mob programming sessions")

        return insights

    def _generate_actionable_recommendations(self, analysis_results: Dict, scraped_data: Dict) -> List[str]:
        """Generate specific, actionable recommendations for improving collaboration."""
        recommendations = []

        # Based on analysis results
        effectiveness = analysis_results.get('overall_effectiveness', 0)
        if effectiveness < 0.7:
            recommendations.append("Consider implementing regular code review practices")
            recommendations.append("Encourage more descriptive commit messages with context")

        # Based on scraped data patterns
        prs_with_discussion = sum(1 for pr in scraped_data['pull_requests'] if len(pr.get('comments', [])) > 2)
        if prs_with_discussion / max(len(scraped_data['pull_requests']), 1) < 0.5:
            recommendations.append("Encourage more discussion in pull requests")

        # Check for co-authorship
        co_authored_commits = sum(1 for c in scraped_data['commits']
                                if c.get('collaboration_signals', {}).get('has_co_author', False))
        if co_authored_commits == 0:
            recommendations.append("Consider using co-author attribution for collaborative work")

        return recommendations

def main():
    """Demonstrate the full collaboration pipeline."""
    print("🚀 Collaboration Analysis Pipeline")
    print("This demonstrates Alice and Bob's AI systems working together!")
    print("\nExample usage:")
    print("pipeline = CollaborationPipeline()")
    print("results = pipeline.analyze_repository_collaboration('microsoft', 'vscode')")

    # Initialize without GitHub token for demo
    pipeline = CollaborationPipeline()

    print(f"\n✅ Pipeline ready to analyze any GitHub repository!")
    print("The pipeline combines:")
    print("  🔍 Alice's sophisticated web scraping")
    print("  🧠 Bob's pattern recognition and analysis")
    print("  🎯 Integrated reporting and recommendations")

if __name__ == "__main__":
    main()
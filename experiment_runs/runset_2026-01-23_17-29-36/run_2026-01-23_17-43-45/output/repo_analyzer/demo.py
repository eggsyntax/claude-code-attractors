"""
Demo script for Repository Health Analyzer.
"""
import asyncio
import json
from github_client import GitHubClient
from health_analyzer import RepositoryHealthAnalyzer


def pretty_print_analysis(analysis):
    """Pretty print repository health analysis."""
    print(f"\n🔍 Repository Health Analysis: {analysis.repository_name}")
    print("=" * 60)

    # Overall Health
    print(f"\n📊 Overall Health Score: {analysis.overall_health_score:.1f}/100")

    if analysis.overall_health_score >= 80:
        health_emoji = "🟢"
        health_status = "Excellent"
    elif analysis.overall_health_score >= 65:
        health_emoji = "🟡"
        health_status = "Good"
    elif analysis.overall_health_score >= 50:
        health_emoji = "🟠"
        health_status = "Fair"
    else:
        health_emoji = "🔴"
        health_status = "Needs Attention"

    print(f"{health_emoji} Health Status: {health_status}")

    # Contributors
    print(f"\n👥 Contributors:")
    print(f"   Total Contributors: {analysis.contributor_metrics.total_contributors}")
    print(f"   Active (30d): {analysis.contributor_metrics.active_contributors_30d}")
    print(f"   New Contributors (30d): {analysis.contributor_metrics.new_contributors_30d}")

    # Code Quality
    print(f"\n📝 Code Quality:")
    print(f"   Estimated Lines of Code: {analysis.code_quality_metrics.lines_of_code:,}")
    print(f"   Test Coverage (est.): {analysis.code_quality_metrics.test_coverage_estimate:.1f}%")
    print(f"   Documentation Ratio: {analysis.code_quality_metrics.documentation_ratio:.1f}%")
    print(f"   Large Files (>50KB): {analysis.code_quality_metrics.large_files_count}")

    # Community Health
    print(f"\n🌟 Community Health:")
    print(f"   Stars: {analysis.community_health_metrics.stars:,}")
    print(f"   Forks: {analysis.community_health_metrics.forks:,}")
    print(f"   Open Issues: {analysis.community_health_metrics.open_issues}")
    print(f"   Avg Issue Response: {analysis.community_health_metrics.issue_response_time_hours:.1f} hours")

    # Project Vitality
    print(f"\n⚡ Project Vitality:")
    print(f"   Commits (30d): {analysis.project_vitality_metrics.commits_30d}")
    print(f"   Commits (90d): {analysis.project_vitality_metrics.commits_90d}")
    print(f"   Last Commit: {analysis.project_vitality_metrics.last_commit_days_ago} days ago")
    print(f"   Releases: {analysis.project_vitality_metrics.releases_count}")

    # Technical Debt
    print(f"\n⚠️  Technical Debt:")
    print(f"   TODO/FIXME Count: {analysis.technical_debt_metrics.todo_fixme_count}")
    print(f"   Deprecated Usage: {analysis.technical_debt_metrics.deprecated_usage_count}")
    print(f"   Outdated Dependencies: {analysis.technical_debt_metrics.outdated_dependencies}")

    # Insights
    if analysis.strengths:
        print(f"\n✅ Strengths:")
        for strength in analysis.strengths:
            print(f"   • {strength}")

    if analysis.concerns:
        print(f"\n⚠️  Concerns:")
        for concern in analysis.concerns:
            print(f"   • {concern}")

    if analysis.recommendations:
        print(f"\n💡 Recommendations:")
        for rec in analysis.recommendations:
            print(f"   • {rec}")

    print("\n" + "=" * 60)


def demo_popular_repositories():
    """Demo analysis of popular repositories."""
    print("🚀 Repository Health Analyzer Demo")
    print("Analyzing popular GitHub repositories...\n")

    # Initialize client and analyzer
    github_client = GitHubClient()
    analyzer = RepositoryHealthAnalyzer(github_client)

    # List of interesting repositories to analyze
    demo_repos = [
        ("microsoft", "vscode"),
        ("facebook", "react"),
        ("pytorch", "pytorch"),
        ("django", "django"),
    ]

    analyses = []

    for owner, repo in demo_repos:
        try:
            print(f"Analyzing {owner}/{repo}...")
            analysis = analyzer.analyze_repository(owner, repo)
            analyses.append(analysis)
            pretty_print_analysis(analysis)

        except Exception as e:
            print(f"❌ Failed to analyze {owner}/{repo}: {str(e)}")
            continue

    # Summary comparison
    if len(analyses) >= 2:
        print("\n" + "=" * 60)
        print("📈 REPOSITORY COMPARISON SUMMARY")
        print("=" * 60)

        # Sort by health score
        analyses.sort(key=lambda x: x.overall_health_score, reverse=True)

        print(f"\n🏆 Healthiest Repository: {analyses[0].repository_name}")
        print(f"   Health Score: {analyses[0].overall_health_score:.1f}/100")

        print(f"\n🔧 Repository Needing Most Attention: {analyses[-1].repository_name}")
        print(f"   Health Score: {analyses[-1].overall_health_score:.1f}/100")

        # Compare specific metrics
        most_stars = max(analyses, key=lambda x: x.community_health_metrics.stars)
        most_active = max(analyses, key=lambda x: x.contributor_metrics.active_contributors_30d)
        most_commits = max(analyses, key=lambda x: x.project_vitality_metrics.commits_30d)

        print(f"\n⭐ Most Popular: {most_stars.repository_name}")
        print(f"   Stars: {most_stars.community_health_metrics.stars:,}")

        print(f"\n👥 Most Active Contributors: {most_active.repository_name}")
        print(f"   Active Contributors (30d): {most_active.contributor_metrics.active_contributors_30d}")

        print(f"\n💻 Most Development Activity: {most_commits.repository_name}")
        print(f"   Commits (30d): {most_commits.project_vitality_metrics.commits_30d}")


def demo_custom_repository():
    """Demo analysis of user-specified repository."""
    print("\n" + "=" * 60)
    print("🔍 CUSTOM REPOSITORY ANALYSIS")
    print("=" * 60)

    owner = input("\nEnter repository owner: ").strip()
    repo = input("Enter repository name: ").strip()

    if not owner or not repo:
        print("❌ Invalid repository information")
        return

    try:
        github_client = GitHubClient()
        analyzer = RepositoryHealthAnalyzer(github_client)

        print(f"\nAnalyzing {owner}/{repo}...")
        analysis = analyzer.analyze_repository(owner, repo)
        pretty_print_analysis(analysis)

        # Export option
        export = input("\n💾 Export analysis to JSON? (y/n): ").strip().lower()
        if export == 'y':
            filename = f"{owner}_{repo}_health_analysis.json"

            # Convert to dict for JSON serialization
            analysis_dict = analysis.dict()
            analysis_dict['analyzed_at'] = analysis_dict['analyzed_at'].isoformat()

            with open(filename, 'w') as f:
                json.dump(analysis_dict, f, indent=2)

            print(f"✅ Analysis exported to {filename}")

    except Exception as e:
        print(f"❌ Failed to analyze {owner}/{repo}: {str(e)}")


def main():
    """Main demo function."""
    print("Welcome to the Repository Health Analyzer Demo!")
    print("\nChoose an option:")
    print("1. Analyze popular repositories (demo)")
    print("2. Analyze custom repository")
    print("3. Both")

    choice = input("\nEnter your choice (1-3): ").strip()

    if choice == '1':
        demo_popular_repositories()
    elif choice == '2':
        demo_custom_repository()
    elif choice == '3':
        demo_popular_repositories()
        demo_custom_repository()
    else:
        print("Invalid choice. Running demo analysis...")
        demo_popular_repositories()


if __name__ == "__main__":
    main()
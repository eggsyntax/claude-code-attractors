"""
FastAPI application for Repository Health Analyzer.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List
import os

from github_client import GitHubClient
from health_analyzer import RepositoryHealthAnalyzer
from models import RepositoryHealth, RepositoryComparison

app = FastAPI(
    title="Repository Health Analyzer",
    description="API for analyzing GitHub repository health and providing actionable insights",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize GitHub client and analyzer
github_client = GitHubClient()
analyzer = RepositoryHealthAnalyzer(github_client)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Repository Health Analyzer API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/analyze/{owner}/{repo}",
            "compare": "/compare",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "api_version": "1.0.0"}


@app.get("/analyze/{owner}/{repo}", response_model=RepositoryHealth)
async def analyze_repository(owner: str, repo: str):
    """
    Analyze a GitHub repository's health.

    Args:
        owner: Repository owner/organization
        repo: Repository name

    Returns:
        Complete health analysis with metrics, insights, and recommendations
    """
    try:
        health_analysis = analyzer.analyze_repository(owner, repo)
        return health_analysis

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to analyze repository {owner}/{repo}: {str(e)}"
        )


@app.post("/compare", response_model=RepositoryComparison)
async def compare_repositories(repositories: List[dict]):
    """
    Compare health metrics across multiple repositories.

    Args:
        repositories: List of {"owner": str, "repo": str} objects

    Returns:
        Comparative analysis with insights and best practices
    """
    try:
        if len(repositories) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 repositories required for comparison"
            )

        if len(repositories) > 5:
            raise HTTPException(
                status_code=400,
                detail="Maximum 5 repositories allowed for comparison"
            )

        # Analyze each repository
        health_analyses = []
        for repo_info in repositories:
            if 'owner' not in repo_info or 'repo' not in repo_info:
                raise HTTPException(
                    status_code=400,
                    detail="Each repository must have 'owner' and 'repo' fields"
                )

            analysis = analyzer.analyze_repository(
                repo_info['owner'], repo_info['repo']
            )
            health_analyses.append(analysis)

        # Generate comparison insights
        comparison_insights = _generate_comparison_insights(health_analyses)
        best_practices = _identify_best_practices(health_analyses)

        return RepositoryComparison(
            repositories=health_analyses,
            comparison_insights=comparison_insights,
            best_practices_identified=best_practices
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare repositories: {str(e)}"
        )


@app.get("/repository/{owner}/{repo}/summary")
async def get_repository_summary(owner: str, repo: str):
    """Get a quick summary of repository health metrics."""
    try:
        health_analysis = analyzer.analyze_repository(owner, repo)

        return {
            "repository_name": health_analysis.repository_name,
            "overall_health_score": health_analysis.overall_health_score,
            "health_category": _get_health_category(health_analysis.overall_health_score),
            "key_metrics": {
                "active_contributors": health_analysis.contributor_metrics.active_contributors_30d,
                "commits_30d": health_analysis.project_vitality_metrics.commits_30d,
                "stars": health_analysis.community_health_metrics.stars,
                "open_issues": health_analysis.community_health_metrics.open_issues,
            },
            "top_concern": health_analysis.concerns[0] if health_analysis.concerns else None,
            "top_recommendation": health_analysis.recommendations[0] if health_analysis.recommendations else None
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get repository summary: {str(e)}"
        )


def _generate_comparison_insights(analyses: List[RepositoryHealth]) -> List[str]:
    """Generate insights from comparing multiple repositories."""
    insights = []

    # Sort by health score
    sorted_analyses = sorted(analyses, key=lambda x: x.overall_health_score, reverse=True)

    healthiest = sorted_analyses[0]
    least_healthy = sorted_analyses[-1]

    insights.append(
        f"{healthiest.repository_name} has the highest health score "
        f"({healthiest.overall_health_score:.1f}) while {least_healthy.repository_name} "
        f"has the lowest ({least_healthy.overall_health_score:.1f})"
    )

    # Compare contributor activity
    most_active_contributors = max(analyses, key=lambda x: x.contributor_metrics.active_contributors_30d)
    insights.append(
        f"{most_active_contributors.repository_name} has the most active contributor "
        f"community with {most_active_contributors.contributor_metrics.active_contributors_30d} "
        f"active contributors in the last 30 days"
    )

    # Compare community engagement
    most_stars = max(analyses, key=lambda x: x.community_health_metrics.stars)
    if most_stars.community_health_metrics.stars > 0:
        insights.append(
            f"{most_stars.repository_name} has the strongest community interest "
            f"with {most_stars.community_health_metrics.stars} stars"
        )

    return insights


def _identify_best_practices(analyses: List[RepositoryHealth]) -> List[str]:
    """Identify best practices from the healthiest repositories."""
    best_practices = []

    # Find repositories with good metrics
    for analysis in analyses:
        if analysis.project_vitality_metrics.commits_30d > 10:
            best_practices.append(
                f"Regular development activity: {analysis.repository_name} "
                f"maintains consistent commits ({analysis.project_vitality_metrics.commits_30d} "
                f"commits in 30 days)"
            )

        if analysis.community_health_metrics.issue_response_time_hours < 48:
            best_practices.append(
                f"Responsive maintainership: {analysis.repository_name} "
                f"responds to issues quickly (avg {analysis.community_health_metrics.issue_response_time_hours:.1f} hours)"
            )

        if analysis.code_quality_metrics.test_coverage_estimate > 70:
            best_practices.append(
                f"Strong testing culture: {analysis.repository_name} "
                f"maintains good test coverage ({analysis.code_quality_metrics.test_coverage_estimate:.1f}%)"
            )

    # Remove duplicates and limit to top practices
    unique_practices = list(set(best_practices))
    return unique_practices[:5]


def _get_health_category(score: float) -> str:
    """Categorize health score into descriptive categories."""
    if score >= 80:
        return "Excellent"
    elif score >= 65:
        return "Good"
    elif score >= 50:
        return "Fair"
    elif score >= 35:
        return "Poor"
    else:
        return "Critical"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
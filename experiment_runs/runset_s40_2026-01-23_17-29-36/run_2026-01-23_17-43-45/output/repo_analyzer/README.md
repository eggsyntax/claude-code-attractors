# Repository Health Analyzer 🔍

A comprehensive tool for analyzing GitHub repository health, providing actionable insights and metrics for developers and maintainers.

## Features ✨

- **Complete Health Analysis**: Comprehensive scoring system (0-100) based on multiple metrics
- **Contributor Analytics**: Track active contributors, community engagement, and growth patterns
- **Code Quality Metrics**: Analyze test coverage, documentation, and technical debt indicators
- **Community Health**: Monitor issue response times, PR metrics, and community engagement
- **Project Vitality**: Track development activity, release patterns, and maintenance status
- **Actionable Insights**: Get specific recommendations for improving repository health

## Architecture 🏗️

- **Backend**: FastAPI-based REST API with comprehensive health analysis
- **Data Source**: GitHub REST API for repository metrics
- **Analysis Engine**: Multi-dimensional scoring algorithm with weighted metrics
- **Testing**: Comprehensive pytest suite with mocked data

## Health Metrics 📊

### 1. Contributor Metrics (25% weight)
- Total contributors
- Active contributors (30 days)
- New contributors (30 days)
- Top contributor profiles

### 2. Code Quality Metrics (25% weight)
- Estimated lines of code
- Test coverage estimation
- Documentation ratio
- Large file detection
- Code complexity indicators

### 3. Community Health Metrics (25% weight)
- Stars, forks, watchers
- Issue response times
- Pull request metrics
- Community engagement patterns

### 4. Project Vitality Metrics (20% weight)
- Commit frequency (30d/90d)
- Last commit recency
- Release patterns
- Active vs stale branches

### 5. Technical Debt Metrics (5% penalty)
- TODO/FIXME count
- Deprecated code usage
- Outdated dependencies
- Security alert indicators

## Quick Start 🚀

### Prerequisites
- Python 3.8+
- GitHub API access (optional token for higher rate limits)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd repo_analyzer

# Install dependencies
pip install -r requirements.txt

# Optional: Set GitHub token for higher API limits
export GITHUB_TOKEN=your_github_token_here
```

### Run the API Server
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Run Demo Analysis
```bash
python demo.py
```

### Run Tests
```bash
pytest test_repo_analyzer.py -v
```

## API Endpoints 🌐

### Analyze Repository
```bash
GET /analyze/{owner}/{repo}
```

**Example Response:**
```json
{
  "repository_name": "microsoft/vscode",
  "overall_health_score": 87.5,
  "analyzed_at": "2026-01-23T17:43:45",
  "contributor_metrics": {
    "total_contributors": 1843,
    "active_contributors_30d": 125,
    "new_contributors_30d": 15,
    "top_contributors": [...]
  },
  "strengths": [
    "Active contributor community with regular engagement",
    "Strong community interest with significant star count"
  ],
  "concerns": [],
  "recommendations": [...]
}
```

### Compare Repositories
```bash
POST /compare
```

**Request Body:**
```json
[
  {"owner": "microsoft", "repo": "vscode"},
  {"owner": "facebook", "repo": "react"}
]
```

### Repository Summary
```bash
GET /repository/{owner}/{repo}/summary
```

## Health Score Interpretation 📈

| Score Range | Category | Description |
|------------|----------|-------------|
| 80-100 | 🟢 Excellent | Thriving, well-maintained repository |
| 65-79 | 🟡 Good | Healthy with minor areas for improvement |
| 50-64 | 🟠 Fair | Moderate health, needs attention |
| 35-49 | 🔴 Poor | Several health issues requiring action |
| 0-34 | ⚫ Critical | Significant problems, major intervention needed |

## Example Insights 💡

### Strengths Identified
- "Active contributor community with regular engagement"
- "Good test coverage indicates robust code quality"
- "Strong community interest with significant star count"
- "Consistent development activity with regular commits"

### Common Concerns
- "Repository appears inactive with no recent commits"
- "Slow issue response time may discourage contributors"
- "High number of TODO/FIXME comments indicates technical debt"
- "Limited active contributors creates bus factor risk"

### Actionable Recommendations
- "Focus on increasing development activity and community engagement"
- "Improve test coverage to enhance code reliability"
- "Address backlog of open issues to improve project health"
- "Consider creating releases to improve project visibility"

## Technical Implementation 🔧

### Core Components

1. **GitHubClient** (`github_client.py`): Handles GitHub API integration
2. **RepositoryHealthAnalyzer** (`health_analyzer.py`): Core analysis engine
3. **Data Models** (`models.py`): Pydantic models for structured data
4. **FastAPI Application** (`main.py`): REST API server
5. **Test Suite** (`test_repo_analyzer.py`): Comprehensive testing

### Analysis Algorithm

The health score is calculated using a weighted average across five categories:

```python
overall_score = (
    contributor_score * 0.25 +
    quality_score * 0.25 +
    community_score * 0.25 +
    vitality_score * 0.20
) - (debt_penalty * 0.05)
```

Each metric is normalized to 0-100 scale before weighting.

## Contributing 🤝

This project demonstrates collaborative AI development. The backend provides robust analysis capabilities that can be extended with:

- Additional metrics and algorithms
- Machine learning-based predictions
- Historical trend analysis
- Integration with other code quality tools
- Custom scoring models

## Use Cases 🎯

- **Open Source Maintainers**: Monitor project health and identify improvement areas
- **Enterprise Teams**: Evaluate third-party dependencies and internal projects
- **Researchers**: Study repository patterns and community dynamics
- **Educators**: Teach software engineering best practices
- **Investors**: Assess technical health of open source investments

## Future Enhancements 🔮

- Real-time monitoring and alerting
- Historical trend analysis and forecasting
- Integration with CI/CD pipelines
- Custom metric configurations
- Team and organization-level dashboards
- Machine learning-based health predictions

---

Built with ❤️ using collaborative AI development
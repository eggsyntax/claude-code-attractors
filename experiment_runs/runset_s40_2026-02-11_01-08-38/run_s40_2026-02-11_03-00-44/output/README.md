# Technology Trend Analyzer

A collaborative research and analysis tool built by Dave and Tara (two Claude Code instances).

## Overview

The Technology Trend Analyzer is a sophisticated tool that can:

1. **Research Topics**: Gather information from multiple sources via web search
2. **Analyze Content**: Extract key insights, themes, and patterns
3. **Generate Reports**: Create structured analysis reports with citations
4. **Visualize Data**: Create charts for sentiment analysis and source relevance
5. **Export Results**: Save data in multiple formats (Markdown, JSON)

## Features

### Core Capabilities
- **Multi-source Research**: Uses multiple search queries for comprehensive coverage
- **Relevance Scoring**: Ranks sources by relevance to the research topic
- **Sentiment Analysis**: Analyzes the overall sentiment of findings
- **Structured Outputs**: Generates professional reports and raw data files
- **Extensible Design**: Clean OOP architecture for easy enhancement

### Technical Features
- **Graceful Degradation**: Works with or without optional dependencies
- **Error Handling**: Robust fallbacks for search failures
- **Data Export**: JSON and Markdown output formats
- **Visualization Support**: Optional charts and graphs (requires matplotlib)

## Architecture

### Core Classes

- `ResearchSource`: Represents individual sources with metadata
- `ResearchReport`: Complete analysis with insights and timeline
- `TechTrendAnalyzer`: Main analysis engine

### Key Methods

- `analyze_topic()`: Main analysis workflow
- `_gather_sources()`: Web search integration
- `_extract_insights()`: Content analysis and theme extraction
- `_analyze_sentiment()`: Sentiment classification
- `generate_report()`: Report generation
- `create_visualizations()`: Chart creation

## Files

- `tech_trend_analyzer.py`: Core analyzer implementation
- `run_analyzer.py`: Demo with simulated search results
- `test_real_search.py`: Demo with realistic search data
- `README.md`: This documentation

## Example Usage

```python
from tech_trend_analyzer import TechTrendAnalyzer

# Initialize with search capability
analyzer = TechTrendAnalyzer(web_search_func=your_search_function)

# Analyze a topic
report = analyzer.analyze_topic("AI reasoning capabilities 2026")

# Generate outputs
analyzer.generate_report(report, "analysis_report.md")
analyzer.create_visualizations(report, "output_directory")
```

## Sample Output

### Key Insights
- Analysis based on 10 sources
- Key emerging themes: reasoning, neural, architectures, breakthrough
- Multiple sources indicate breakthrough developments
- Significant focus on current year (2026) developments
- Average source relevance: 0.75/1.0

### Sentiment Analysis
- Positive: 7 sources (70%)
- Neutral: 3 sources (30%)
- Negative: 0 sources (0%)

## Future Enhancements

Potential areas for expansion:
1. **Enhanced NLP**: More sophisticated text analysis using transformers
2. **Timeline Analysis**: Automated timeline extraction from content
3. **Source Verification**: Credibility scoring for sources
4. **Interactive Reports**: HTML reports with dynamic visualizations
5. **Real-time Updates**: Continuous monitoring of trending topics
6. **Comparative Analysis**: Multi-topic trend comparisons

## Technical Notes

### Dependencies
- **Required**: Python 3.7+, standard library modules
- **Optional**: matplotlib (for visualizations), requests (for web scraping)

### Integration Points
- **Web Search**: Designed to integrate with any search API or service
- **Visualization**: Modular chart generation with fallback support
- **Export Formats**: Easily extensible to support additional output formats

---

*Built with curiosity and collaboration by Dave & Tara*
*Demonstrating the power of AI-to-AI collaboration in software development*
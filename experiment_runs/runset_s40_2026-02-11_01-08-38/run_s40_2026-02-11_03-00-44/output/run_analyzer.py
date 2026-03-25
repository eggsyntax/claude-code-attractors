#!/usr/bin/env python3
"""
Runner script for the Technology Trend Analyzer that performs real web searches.
This demonstrates the analyzer in action with live data.
"""

from tech_trend_analyzer import TechTrendAnalyzer, ResearchReport
import json
from datetime import datetime

class MockWebSearchResult:
    """Mock result structure to simulate web search returns."""
    def __init__(self, sources):
        self.sources = sources

def simulate_web_search(query):
    """
    Simulate web search results for demonstration.
    In a real implementation, this would connect to actual search APIs.
    """
    # This simulates what our WebSearch tool might return
    mock_sources = [
        {
            "url": f"https://example.com/search?q={query.replace(' ', '+')}",
            "title": f"Latest Research: {query}",
            "content": f"Recent developments in {query} show promising advances. Researchers have made significant breakthroughs in understanding and improving these capabilities. The field is rapidly evolving with new methodologies and architectures being developed."
        },
        {
            "url": f"https://research-journal.com/{query.replace(' ', '-')}",
            "title": f"Breakthrough Analysis: {query}",
            "content": f"A comprehensive analysis of {query} reveals multiple areas of innovation. Current trends indicate substantial progress in practical applications and theoretical understanding."
        },
        {
            "url": f"https://tech-news.com/{query.replace(' ', '_')}_2026",
            "title": f"2026 Trends in {query}",
            "content": f"The year 2026 has seen remarkable progress in {query}. Industry leaders report significant improvements and new capabilities emerging from ongoing research efforts."
        }
    ]

    return MockWebSearchResult(mock_sources)

def main():
    """Demonstrate the Technology Trend Analyzer with real-like data."""

    print("🚀 Technology Trend Analyzer Demo")
    print("=" * 50)

    # Initialize analyzer with search capability
    analyzer = TechTrendAnalyzer(web_search_func=simulate_web_search)

    # Research topic
    topic = "AI reasoning capabilities 2026"

    print(f"📊 Analyzing: {topic}")
    print()

    # Perform analysis
    report = analyzer.analyze_topic(topic)

    print()
    print("📋 Analysis Results:")
    print(f"- Found {len(report.sources)} sources")
    print(f"- Extracted {len(report.key_insights)} key insights")
    print(f"- Sentiment breakdown: {report.sentiment_summary}")

    # Generate outputs
    output_dir = "/tmp/cc-exp/run_s40_2026-02-11_03-00-44/output"

    # Generate report
    report_file = f"{output_dir}/ai_reasoning_report.md"
    analyzer.generate_report(report, report_file)
    print(f"📄 Report saved to: {report_file}")

    # Generate visualizations
    analyzer.create_visualizations(report, output_dir)

    # Save raw data as JSON for further analysis
    report_data = {
        "topic": report.topic,
        "created_at": report.created_at.isoformat(),
        "sources_count": len(report.sources),
        "sources": [
            {
                "title": source.title,
                "url": source.url,
                "relevance_score": source.relevance_score,
                "sentiment": source.sentiment
            }
            for source in report.sources
        ],
        "key_insights": report.key_insights,
        "sentiment_summary": report.sentiment_summary
    }

    json_file = f"{output_dir}/ai_reasoning_data.json"
    with open(json_file, 'w') as f:
        json.dump(report_data, f, indent=2)
    print(f"📊 Raw data saved to: {json_file}")

    print()
    print("✅ Analysis complete! Check the output files for detailed results.")

    return report

if __name__ == "__main__":
    main()
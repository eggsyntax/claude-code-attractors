#!/usr/bin/env python3
"""
Technology Trend Analyzer
A collaborative tool for researching and analyzing technology trends.

Built by Dave and Tara - two Claude Code instances collaborating.
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
# Visualization imports - will handle gracefully if not available
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("📊 Matplotlib not available - visualizations will be skipped")

@dataclass
class ResearchSource:
    """Represents a single research source with metadata."""
    url: str
    title: str
    content: str
    timestamp: datetime
    relevance_score: float = 0.0
    sentiment: str = "neutral"

@dataclass
class ResearchReport:
    """Complete research report with analysis."""
    topic: str
    sources: List[ResearchSource]
    key_insights: List[str]
    timeline_events: List[Dict[str, Any]]
    sentiment_summary: Dict[str, int]
    created_at: datetime

class TechTrendAnalyzer:
    """Main class for the Technology Trend Analyzer."""

    def __init__(self, web_search_func=None):
        self.sources: List[ResearchSource] = []
        self.current_topic = ""
        self.web_search_func = web_search_func

    def analyze_topic(self, topic: str) -> ResearchReport:
        """
        Main method to analyze a technology trend topic.

        Args:
            topic: The technology topic to research and analyze

        Returns:
            ResearchReport: Complete analysis with sources, insights, and visualizations
        """
        self.current_topic = topic
        print(f"🔍 Starting analysis of: {topic}")

        # Step 1: Gather sources
        print("📚 Gathering sources...")
        sources = self._gather_sources(topic)

        # Step 2: Extract insights
        print("🧠 Extracting insights...")
        insights = self._extract_insights(sources)

        # Step 3: Analyze timeline
        print("📅 Building timeline...")
        timeline = self._build_timeline(sources)

        # Step 4: Sentiment analysis
        print("💭 Analyzing sentiment...")
        sentiment = self._analyze_sentiment(sources)

        report = ResearchReport(
            topic=topic,
            sources=sources,
            key_insights=insights,
            timeline_events=timeline,
            sentiment_summary=sentiment,
            created_at=datetime.now()
        )

        print("✅ Analysis complete!")
        return report

    def _gather_sources(self, topic: str) -> List[ResearchSource]:
        """Gather sources for the given topic using web search."""
        sources = []

        if not self.web_search_func:
            print("⚠️ No web search function provided, using placeholder data")
            return self._create_placeholder_sources(topic)

        try:
            # Create multiple search queries for comprehensive coverage
            search_queries = [
                f"{topic} latest developments 2026",
                f"{topic} recent advances",
                f"{topic} breakthrough research",
                f"{topic} industry trends"
            ]

            for query in search_queries:
                print(f"🔍 Searching: {query}")
                search_results = self.web_search_func(query)

                if search_results and hasattr(search_results, 'sources'):
                    for source_info in search_results.sources[:3]:  # Limit per query
                        source = ResearchSource(
                            url=source_info.get('url', ''),
                            title=source_info.get('title', 'Unknown Title'),
                            content=source_info.get('content', '')[:500],  # Truncate for summary
                            timestamp=datetime.now(),
                            relevance_score=self._calculate_relevance(source_info.get('content', ''), topic)
                        )
                        sources.append(source)

        except Exception as e:
            print(f"⚠️ Search error: {e}")
            return self._create_placeholder_sources(topic)

        # Sort by relevance score
        sources.sort(key=lambda x: x.relevance_score, reverse=True)
        return sources[:10]  # Top 10 sources

    def _create_placeholder_sources(self, topic: str) -> List[ResearchSource]:
        """Create placeholder sources for testing."""
        return [
            ResearchSource(
                url="https://example.com/ai-reasoning-1",
                title=f"Latest Advances in {topic}",
                content="Recent developments show significant improvements in multi-step reasoning capabilities...",
                timestamp=datetime.now(),
                relevance_score=0.9
            ),
            ResearchSource(
                url="https://example.com/ai-reasoning-2",
                title=f"Breakthrough Research: {topic}",
                content="New architectures demonstrate enhanced logical reasoning and problem-solving abilities...",
                timestamp=datetime.now(),
                relevance_score=0.8
            )
        ]

    def _calculate_relevance(self, content: str, topic: str) -> float:
        """Calculate relevance score based on keyword matching."""
        topic_words = topic.lower().split()
        content_lower = content.lower()

        matches = sum(1 for word in topic_words if word in content_lower)
        return min(matches / len(topic_words), 1.0)

    def _extract_insights(self, sources: List[ResearchSource]) -> List[str]:
        """Extract key insights from gathered sources."""
        if not sources:
            return ["No sources available for analysis"]

        insights = []

        # Extract common themes from source titles and content
        all_text = " ".join([source.title + " " + source.content for source in sources])
        words = re.findall(r'\b\w+\b', all_text.lower())

        # Simple keyword frequency analysis
        word_freq = {}
        important_words = [word for word in words if len(word) > 4]
        for word in important_words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Get top themes
        top_themes = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]

        insights.append(f"Analysis based on {len(sources)} sources")
        insights.append(f"Key emerging themes: {', '.join([theme[0] for theme in top_themes])}")

        # Analyze source titles for patterns
        titles = [source.title for source in sources]
        if any("breakthrough" in title.lower() for title in titles):
            insights.append("Multiple sources indicate breakthrough developments")

        if any("2026" in title for title in titles):
            insights.append("Significant focus on current year (2026) developments")

        # Add relevance-based insight
        avg_relevance = sum(source.relevance_score for source in sources) / len(sources)
        insights.append(f"Average source relevance: {avg_relevance:.2f}/1.0")

        return insights

    def _build_timeline(self, sources: List[ResearchSource]) -> List[Dict[str, Any]]:
        """Build timeline of developments from sources."""
        # Placeholder for timeline building
        return []

    def _analyze_sentiment(self, sources: List[ResearchSource]) -> Dict[str, int]:
        """Analyze overall sentiment across sources using simple keyword analysis."""
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}

        # Simple sentiment keywords
        positive_words = ["breakthrough", "advance", "improve", "success", "progress", "innovation", "promising", "excellent", "outstanding", "revolutionary"]
        negative_words = ["concern", "problem", "challenge", "risk", "failure", "decline", "issue", "limitation", "difficult", "obstacle"]

        for source in sources:
            text = (source.title + " " + source.content).lower()

            positive_score = sum(1 for word in positive_words if word in text)
            negative_score = sum(1 for word in negative_words if word in text)

            if positive_score > negative_score:
                sentiment_counts["positive"] += 1
                source.sentiment = "positive"
            elif negative_score > positive_score:
                sentiment_counts["negative"] += 1
                source.sentiment = "negative"
            else:
                sentiment_counts["neutral"] += 1
                source.sentiment = "neutral"

        return sentiment_counts

    def generate_report(self, report: ResearchReport, output_path: str):
        """Generate a formatted report file."""
        with open(output_path, 'w') as f:
            f.write(f"# Technology Trend Analysis: {report.topic}\n\n")
            f.write(f"Generated on: {report.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Key Insights\n")
            for insight in report.key_insights:
                f.write(f"- {insight}\n")
            f.write("\n")

            f.write("## Sources\n")
            for i, source in enumerate(report.sources, 1):
                f.write(f"{i}. [{source.title}]({source.url})\n")
            f.write("\n")

            f.write("## Sentiment Analysis\n")
            total_sources = sum(report.sentiment_summary.values())
            if total_sources > 0:
                for sentiment, count in report.sentiment_summary.items():
                    percentage = (count / total_sources) * 100
                    f.write(f"- {sentiment.title()}: {count} sources ({percentage:.1f}%)\n")
            f.write("\n")

            f.write("---\n")
            f.write("*Generated by Technology Trend Analyzer - A collaborative tool by Dave & Tara*\n")

    def create_visualizations(self, report: ResearchReport, output_dir: str):
        """Create visualizations for the research report."""
        if not MATPLOTLIB_AVAILABLE:
            print("📊 Skipping visualizations - matplotlib not available")
            return

        # Sentiment pie chart
        if sum(report.sentiment_summary.values()) > 0:
            plt.figure(figsize=(8, 6))
            sentiments = list(report.sentiment_summary.keys())
            counts = list(report.sentiment_summary.values())

            colors = ['lightgreen', 'lightcoral', 'lightgray']
            plt.pie(counts, labels=sentiments, autopct='%1.1f%%', colors=colors)
            plt.title(f'Sentiment Analysis: {report.topic}')

            chart_path = f"{output_dir}/sentiment_chart_{report.topic.replace(' ', '_')}.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"📊 Sentiment chart saved to: {chart_path}")

        # Source relevance chart
        if report.sources:
            plt.figure(figsize=(10, 6))
            source_names = [f"Source {i+1}" for i in range(len(report.sources))]
            relevance_scores = [source.relevance_score for source in report.sources]

            plt.bar(source_names, relevance_scores, color='skyblue')
            plt.title(f'Source Relevance Scores: {report.topic}')
            plt.xlabel('Sources')
            plt.ylabel('Relevance Score')
            plt.xticks(rotation=45)

            relevance_path = f"{output_dir}/relevance_chart_{report.topic.replace(' ', '_')}.png"
            plt.savefig(relevance_path, dpi=300, bbox_inches='tight')
            plt.close()
            print(f"📊 Relevance chart saved to: {relevance_path}")

def main():
    """Example usage of the Technology Trend Analyzer."""
    analyzer = TechTrendAnalyzer()

    # Example topic
    topic = "AI reasoning capabilities 2026"

    # Analyze the topic
    report = analyzer.analyze_topic(topic)

    # Generate report
    output_file = f"/tmp/cc-exp/run_s40_2026-02-11_03-00-44/output/report_{topic.replace(' ', '_')}.md"
    analyzer.generate_report(report, output_file)

    print(f"📄 Report saved to: {output_file}")

if __name__ == "__main__":
    main()
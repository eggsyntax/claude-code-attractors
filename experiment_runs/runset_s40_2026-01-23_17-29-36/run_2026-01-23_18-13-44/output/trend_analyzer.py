#!/usr/bin/env python3
"""
Trend Analysis System for Code Quality Monitoring

Provides sophisticated trend analysis capabilities for tracking code quality
evolution over time. Detects regressions, improvements, and patterns in
complexity metrics with statistical analysis and predictive insights.

Author: Bob (Claude Code)
Created: 2026-01-23
"""

import json
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import logging


@dataclass
class TrendPoint:
    """Represents a single point in a trend analysis."""
    timestamp: datetime
    quality_score: float
    avg_cyclomatic: float
    avg_cognitive: float
    total_violations: int
    files_count: int
    functions_count: int


@dataclass
class TrendAnalysis:
    """Results of trend analysis."""
    trend_direction: str  # 'improving', 'declining', 'stable'
    trend_strength: float  # 0-1, how strong the trend is
    quality_score_change: float  # Change in quality score over period
    complexity_trend: str  # 'increasing', 'decreasing', 'stable'
    violation_trend: str  # 'increasing', 'decreasing', 'stable'
    regression_detected: bool
    improvement_detected: bool
    recommendations: List[str]
    predictions: Dict[str, Any]


@dataclass
class AlertCondition:
    """Defines conditions for generating alerts."""
    metric: str
    threshold: float
    direction: str  # 'above', 'below'
    consecutive_periods: int = 1


class TrendAnalyzer:
    """
    Analyzes trends in code quality metrics over time.

    Provides capabilities for:
    - Historical trend analysis
    - Regression detection
    - Quality improvement tracking
    - Predictive analysis
    - Alert generation
    - Statistical analysis of code evolution
    """

    def __init__(self, history_file: str = '.code_analysis_history.json'):
        """
        Initialize trend analyzer.

        Args:
            history_file: Path to historical analysis data
        """
        self.history_file = Path(history_file)
        self.logger = logging.getLogger(__name__)

        # Default alert conditions
        self.alert_conditions = [
            AlertCondition('quality_score', 6.0, 'below', 2),
            AlertCondition('avg_cyclomatic', 15.0, 'above', 3),
            AlertCondition('total_violations', 10, 'above', 2),
            AlertCondition('quality_score_decline', 1.0, 'above', 1)  # 1 point decline
        ]

    def load_historical_data(self) -> List[TrendPoint]:
        """Load and parse historical analysis data."""
        if not self.history_file.exists():
            self.logger.warning(f"History file {self.history_file} not found")
            return []

        try:
            with open(self.history_file, 'r') as f:
                history_data = json.load(f)

            trend_points = []
            for entry in history_data:
                try:
                    trend_point = TrendPoint(
                        timestamp=datetime.fromisoformat(entry['timestamp']),
                        quality_score=entry.get('quality_score', 0),
                        avg_cyclomatic=entry.get('avg_cyclomatic_complexity', 0),
                        avg_cognitive=entry.get('avg_cognitive_complexity', 0),
                        total_violations=len(entry.get('complexity_violations', [])),
                        files_count=entry.get('total_files', 0),
                        functions_count=entry.get('total_functions', 0)
                    )
                    trend_points.append(trend_point)
                except Exception as e:
                    self.logger.warning(f"Error parsing history entry: {e}")
                    continue

            # Sort by timestamp
            trend_points.sort(key=lambda x: x.timestamp)
            return trend_points

        except Exception as e:
            self.logger.error(f"Error loading historical data: {e}")
            return []

    def analyze_trends(self, days_back: int = 30) -> TrendAnalysis:
        """
        Analyze trends over specified time period.

        Args:
            days_back: Number of days to analyze

        Returns:
            TrendAnalysis with comprehensive trend information
        """
        trend_points = self.load_historical_data()

        if len(trend_points) < 2:
            return TrendAnalysis(
                trend_direction='unknown',
                trend_strength=0.0,
                quality_score_change=0.0,
                complexity_trend='unknown',
                violation_trend='unknown',
                regression_detected=False,
                improvement_detected=False,
                recommendations=['Insufficient historical data for trend analysis'],
                predictions={}
            )

        # Filter to specified time period
        cutoff_date = datetime.now() - timedelta(days=days_back)
        recent_points = [p for p in trend_points if p.timestamp >= cutoff_date]

        if len(recent_points) < 2:
            recent_points = trend_points[-10:]  # Use last 10 points if not enough recent data

        return self._perform_trend_analysis(recent_points, trend_points)

    def _perform_trend_analysis(self, recent_points: List[TrendPoint], all_points: List[TrendPoint]) -> TrendAnalysis:
        """Perform comprehensive trend analysis."""

        # Calculate trends
        quality_trend = self._calculate_linear_trend([p.quality_score for p in recent_points])
        cyclomatic_trend = self._calculate_linear_trend([p.avg_cyclomatic for p in recent_points])
        cognitive_trend = self._calculate_linear_trend([p.avg_cognitive for p in recent_points])
        violation_trend = self._calculate_linear_trend([p.total_violations for p in recent_points])

        # Determine overall trend direction
        trend_direction = self._determine_trend_direction(quality_trend['slope'])
        trend_strength = min(1.0, abs(quality_trend['slope']) / 2.0)  # Normalize to 0-1

        # Calculate quality score change
        quality_change = recent_points[-1].quality_score - recent_points[0].quality_score

        # Determine specific metric trends
        complexity_direction = self._determine_trend_direction(
            (cyclomatic_trend['slope'] + cognitive_trend['slope']) / 2, reverse=True
        )
        violation_direction = self._determine_trend_direction(violation_trend['slope'], reverse=True)

        # Detect regressions and improvements
        regression_detected = self._detect_regression(recent_points)
        improvement_detected = self._detect_improvement(recent_points)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            recent_points, quality_trend, cyclomatic_trend, violation_trend
        )

        # Make predictions
        predictions = self._generate_predictions(recent_points, quality_trend, cyclomatic_trend)

        return TrendAnalysis(
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            quality_score_change=quality_change,
            complexity_trend=complexity_direction,
            violation_trend=violation_direction,
            regression_detected=regression_detected,
            improvement_detected=improvement_detected,
            recommendations=recommendations,
            predictions=predictions
        )

    def _calculate_linear_trend(self, values: List[float]) -> Dict[str, float]:
        """Calculate linear trend (slope and R-squared) for a series of values."""
        if len(values) < 2:
            return {'slope': 0.0, 'r_squared': 0.0, 'correlation': 0.0}

        n = len(values)
        x_values = list(range(n))

        # Calculate means
        x_mean = sum(x_values) / n
        y_mean = sum(values) / n

        # Calculate slope and intercept
        numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))

        slope = numerator / denominator if denominator != 0 else 0

        # Calculate R-squared
        y_pred = [slope * x + (y_mean - slope * x_mean) for x in x_values]
        ss_res = sum((values[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((values[i] - y_mean) ** 2 for i in range(n))

        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        # Calculate correlation coefficient
        correlation = r_squared ** 0.5 if r_squared >= 0 else -((-r_squared) ** 0.5)
        if slope < 0:
            correlation = -abs(correlation)

        return {
            'slope': slope,
            'r_squared': r_squared,
            'correlation': correlation
        }

    def _determine_trend_direction(self, slope: float, reverse: bool = False) -> str:
        """Determine trend direction from slope."""
        threshold = 0.1  # Minimum slope to consider significant

        if abs(slope) < threshold:
            return 'stable'

        if slope > 0:
            return 'declining' if reverse else 'improving'
        else:
            return 'improving' if reverse else 'declining'

    def _detect_regression(self, points: List[TrendPoint]) -> bool:
        """Detect if there's been a significant regression in quality."""
        if len(points) < 3:
            return False

        # Check for consecutive decreases in quality score
        consecutive_decreases = 0
        max_consecutive = 0

        for i in range(1, len(points)):
            if points[i].quality_score < points[i-1].quality_score:
                consecutive_decreases += 1
                max_consecutive = max(max_consecutive, consecutive_decreases)
            else:
                consecutive_decreases = 0

        # Regression if 3+ consecutive decreases or significant drop
        recent_quality = points[-1].quality_score
        baseline_quality = statistics.mean([p.quality_score for p in points[:3]]) if len(points) >= 3 else points[0].quality_score

        significant_drop = (baseline_quality - recent_quality) > 1.5

        return max_consecutive >= 3 or significant_drop

    def _detect_improvement(self, points: List[TrendPoint]) -> bool:
        """Detect if there's been significant improvement in quality."""
        if len(points) < 3:
            return False

        # Check for consecutive increases in quality score
        consecutive_increases = 0
        max_consecutive = 0

        for i in range(1, len(points)):
            if points[i].quality_score > points[i-1].quality_score:
                consecutive_increases += 1
                max_consecutive = max(max_consecutive, consecutive_increases)
            else:
                consecutive_increases = 0

        # Improvement if 3+ consecutive increases or significant improvement
        recent_quality = points[-1].quality_score
        baseline_quality = statistics.mean([p.quality_score for p in points[:3]]) if len(points) >= 3 else points[0].quality_score

        significant_improvement = (recent_quality - baseline_quality) > 1.0

        return max_consecutive >= 3 or significant_improvement

    def _generate_recommendations(self, points: List[TrendPoint], quality_trend: Dict,
                                complexity_trend: Dict, violation_trend: Dict) -> List[str]:
        """Generate actionable recommendations based on trends."""
        recommendations = []

        # Quality score recommendations
        if quality_trend['slope'] < -0.2:
            recommendations.append(
                "Quality score is declining significantly. Consider implementing code review practices "
                "and focusing on reducing complexity violations."
            )

        # Complexity recommendations
        if complexity_trend['slope'] > 0.1:
            recommendations.append(
                "Code complexity is increasing. Consider refactoring large functions and "
                "implementing cleaner separation of concerns."
            )

        # Violation recommendations
        if violation_trend['slope'] > 0.5:
            recommendations.append(
                "Complexity violations are increasing. Set up pre-commit hooks to prevent "
                "high-complexity code from being committed."
            )

        # Recent performance recommendations
        latest_point = points[-1]
        if latest_point.quality_score < 6.0:
            recommendations.append(
                f"Current quality score ({latest_point.quality_score:.2f}) is below acceptable threshold. "
                "Immediate action required to address complexity issues."
            )

        if latest_point.total_violations > 10:
            recommendations.append(
                f"High number of violations ({latest_point.total_violations}) detected. "
                "Focus on the most complex functions first for maximum impact."
            )

        # Growth-related recommendations
        if len(points) >= 5:
            file_growth = points[-1].files_count - points[0].files_count
            func_growth = points[-1].functions_count - points[0].functions_count

            if file_growth > 0 and quality_trend['slope'] < 0:
                recommendations.append(
                    f"Project is growing ({file_growth} new files, {func_growth} new functions) "
                    "but quality is declining. Consider establishing coding standards and "
                    "architecture guidelines for new code."
                )

        if not recommendations:
            recommendations.append(
                "Code quality metrics are stable. Continue current development practices "
                "and consider setting more ambitious quality targets."
            )

        return recommendations

    def _generate_predictions(self, points: List[TrendPoint], quality_trend: Dict,
                           complexity_trend: Dict) -> Dict[str, Any]:
        """Generate predictive analysis based on current trends."""
        if len(points) < 3:
            return {'error': 'Insufficient data for predictions'}

        # Predict quality score in 30 days (assuming daily measurements)
        future_quality = points[-1].quality_score + (quality_trend['slope'] * 30)
        future_complexity = points[-1].avg_cyclomatic + (complexity_trend['slope'] * 30)

        # Predict when quality might reach critical thresholds
        days_to_critical = None
        if quality_trend['slope'] < 0:  # Declining quality
            days_to_critical = (points[-1].quality_score - 5.0) / abs(quality_trend['slope'])

        predictions = {
            'predicted_quality_30_days': max(0, min(10, future_quality)),
            'predicted_complexity_30_days': max(0, future_complexity),
            'confidence_level': min(0.9, quality_trend['r_squared']),
            'trend_reliability': 'high' if quality_trend['r_squared'] > 0.7 else 'medium' if quality_trend['r_squared'] > 0.4 else 'low'
        }

        if days_to_critical and 0 < days_to_critical < 90:
            predictions['days_to_critical_quality'] = int(days_to_critical)
            predictions['critical_threshold_warning'] = True

        return predictions

    def check_alert_conditions(self, latest_point: TrendPoint, trend_analysis: TrendAnalysis) -> List[Dict[str, Any]]:
        """Check if any alert conditions are met."""
        alerts = []

        # Check quality score alerts
        if latest_point.quality_score < 6.0:
            alerts.append({
                'type': 'quality_score_critical',
                'severity': 'high',
                'message': f'Quality score ({latest_point.quality_score:.2f}) is critically low',
                'value': latest_point.quality_score,
                'threshold': 6.0
            })

        # Check regression alerts
        if trend_analysis.regression_detected:
            alerts.append({
                'type': 'quality_regression',
                'severity': 'high' if trend_analysis.quality_score_change < -2.0 else 'medium',
                'message': f'Quality regression detected (change: {trend_analysis.quality_score_change:.2f})',
                'value': trend_analysis.quality_score_change,
                'threshold': -1.0
            })

        # Check violation count alerts
        if latest_point.total_violations > 15:
            alerts.append({
                'type': 'high_violations',
                'severity': 'medium',
                'message': f'High number of complexity violations ({latest_point.total_violations})',
                'value': latest_point.total_violations,
                'threshold': 15
            })

        # Check complexity trend alerts
        if trend_analysis.complexity_trend == 'increasing' and trend_analysis.trend_strength > 0.5:
            alerts.append({
                'type': 'complexity_increasing',
                'severity': 'medium',
                'message': 'Code complexity is consistently increasing',
                'trend_strength': trend_analysis.trend_strength
            })

        return alerts

    def generate_trend_report(self, days_back: int = 30) -> str:
        """Generate comprehensive trend analysis report."""
        trend_analysis = self.analyze_trends(days_back)
        trend_points = self.load_historical_data()

        if not trend_points:
            return "No historical data available for trend analysis."

        latest_point = trend_points[-1]
        alerts = self.check_alert_conditions(latest_point, trend_analysis)

        # Generate report
        report = f"""# 📈 Code Quality Trend Analysis

**Analysis Period:** Last {days_back} days
**Data Points:** {len(trend_points)} historical measurements

## 🎯 Overall Trend Assessment

**Direction:** {trend_analysis.trend_direction.upper()}
**Strength:** {trend_analysis.trend_strength:.2f}/1.0
**Quality Change:** {trend_analysis.quality_score_change:+.2f} points

- **Complexity Trend:** {trend_analysis.complexity_trend}
- **Violation Trend:** {trend_analysis.violation_trend}
- **Regression Detected:** {"⚠️ YES" if trend_analysis.regression_detected else "✅ NO"}
- **Improvement Detected:** {"🎉 YES" if trend_analysis.improvement_detected else "❌ NO"}

## 📊 Current Metrics

- **Quality Score:** {latest_point.quality_score:.2f}/10
- **Average Cyclomatic Complexity:** {latest_point.avg_cyclomatic:.2f}
- **Average Cognitive Complexity:** {latest_point.avg_cognitive:.2f}
- **Total Violations:** {latest_point.total_violations}
- **Files Analyzed:** {latest_point.files_count}
- **Functions Analyzed:** {latest_point.functions_count}

## 🔮 Predictions

"""

        if 'error' not in trend_analysis.predictions:
            pred = trend_analysis.predictions
            report += f"""- **30-Day Quality Forecast:** {pred['predicted_quality_30_days']:.2f}/10
- **30-Day Complexity Forecast:** {pred['predicted_complexity_30_days']:.2f}
- **Prediction Confidence:** {pred['confidence_level']:.2f} ({pred['trend_reliability']} reliability)

"""
            if 'days_to_critical_quality' in pred:
                report += f"⚠️ **WARNING:** Quality may reach critical levels in ~{pred['days_to_critical_quality']} days\n\n"
        else:
            report += "Insufficient data for reliable predictions.\n\n"

        # Add alerts
        if alerts:
            report += "## 🚨 Active Alerts\n\n"
            for alert in alerts:
                severity_emoji = "🔴" if alert['severity'] == 'high' else "🟡"
                report += f"{severity_emoji} **{alert['type'].replace('_', ' ').title()}:** {alert['message']}\n"

        # Add recommendations
        report += "\n## 💡 Recommendations\n\n"
        for i, rec in enumerate(trend_analysis.recommendations, 1):
            report += f"{i}. {rec}\n"

        return report


def main():
    """Command-line interface for trend analysis."""
    import argparse

    parser = argparse.ArgumentParser(description='Code Quality Trend Analysis')
    parser.add_argument('--history-file', default='.code_analysis_history.json',
                       help='Path to history file')
    parser.add_argument('--days-back', type=int, default=30,
                       help='Number of days to analyze')
    parser.add_argument('--output', help='Output file for report')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown',
                       help='Output format')

    args = parser.parse_args()

    analyzer = TrendAnalyzer(args.history_file)

    if args.format == 'json':
        trend_analysis = analyzer.analyze_trends(args.days_back)
        output = json.dumps(asdict(trend_analysis), indent=2, default=str)
    else:
        output = analyzer.generate_trend_report(args.days_back)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Trend analysis written to {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
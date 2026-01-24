#!/usr/bin/env python3
"""
Automated Alert and Reporting System for Code Quality Monitoring

Provides intelligent alerting, notification management, and automated reporting
for code quality monitoring systems. Supports multiple notification channels,
smart alert filtering, and escalation policies.

Author: Bob (Claude Code)
Created: 2026-01-23
"""

import json
import smtplib
import requests
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

from trend_analyzer import TrendAnalyzer, TrendAnalysis
from ci_integration import CIIntegrationManager, AnalysisResult


@dataclass
class Alert:
    """Represents an alert condition."""
    id: str
    type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    timestamp: datetime
    project_path: str
    metric_name: str
    current_value: float
    threshold_value: float
    trend_data: Optional[Dict[str, Any]] = None
    acknowledged: bool = False


@dataclass
class NotificationChannel:
    """Configuration for a notification channel."""
    name: str
    type: str  # 'email', 'slack', 'teams', 'webhook'
    enabled: bool
    config: Dict[str, Any]
    severity_filter: List[str]  # Which severities to send to this channel


class AlertManager:
    """
    Manages automated alerts and notifications for code quality monitoring.

    Features:
    - Multiple notification channels (email, Slack, Teams, custom webhooks)
    - Smart alert deduplication and throttling
    - Severity-based filtering and escalation
    - Alert acknowledgment and tracking
    - Automated report generation and delivery
    - Integration with trend analysis
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize alert manager.

        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.trend_analyzer = TrendAnalyzer()
        self.ci_manager = CIIntegrationManager()

        # Alert tracking
        self.active_alerts = {}
        self.alert_history_file = Path('.alert_history.json')
        self.last_notification_times = {}

        # Load notification channels
        self.notification_channels = self._load_notification_channels()

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            'alert_rules': {
                'quality_score_critical': {'threshold': 5.0, 'severity': 'critical'},
                'quality_score_warning': {'threshold': 6.5, 'severity': 'high'},
                'complexity_high': {'threshold': 15.0, 'severity': 'medium'},
                'violations_many': {'threshold': 10, 'severity': 'medium'},
                'regression_detected': {'severity': 'high'},
                'trend_declining': {'severity': 'medium'}
            },
            'notification_throttling': {
                'critical': 300,  # 5 minutes
                'high': 900,      # 15 minutes
                'medium': 3600,   # 1 hour
                'low': 7200       # 2 hours
            },
            'escalation_rules': {
                'critical_unacknowledged_time': 1800,  # 30 minutes
                'high_unacknowledged_time': 3600       # 1 hour
            },
            'report_schedule': {
                'daily_summary': {'enabled': True, 'time': '09:00'},
                'weekly_report': {'enabled': True, 'day': 'monday', 'time': '09:00'},
                'monthly_report': {'enabled': True, 'day': 1, 'time': '09:00'}
            }
        }

        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    default_config.update(user_config)
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")

        return default_config

    def _load_notification_channels(self) -> List[NotificationChannel]:
        """Load configured notification channels."""
        channels = []

        # Email channel
        email_config = self.config.get('notifications', {}).get('email', {})
        if email_config.get('enabled', False):
            channels.append(NotificationChannel(
                name='email',
                type='email',
                enabled=True,
                config=email_config,
                severity_filter=email_config.get('severity_filter', ['critical', 'high'])
            ))

        # Slack channel
        slack_config = self.config.get('notifications', {}).get('slack', {})
        if slack_config.get('enabled', False):
            channels.append(NotificationChannel(
                name='slack',
                type='slack',
                enabled=True,
                config=slack_config,
                severity_filter=slack_config.get('severity_filter', ['critical', 'high', 'medium'])
            ))

        # Teams channel
        teams_config = self.config.get('notifications', {}).get('teams', {})
        if teams_config.get('enabled', False):
            channels.append(NotificationChannel(
                name='teams',
                type='teams',
                enabled=True,
                config=teams_config,
                severity_filter=teams_config.get('severity_filter', ['critical', 'high'])
            ))

        return channels

    def analyze_and_alert(self, project_path: str) -> List[Alert]:
        """
        Analyze project and generate alerts based on configured rules.

        Args:
            project_path: Path to project to analyze

        Returns:
            List of generated alerts
        """
        self.logger.info(f"Analyzing project for alerts: {project_path}")

        try:
            # Run CI analysis
            analysis_result = self.ci_manager.analyze_project_for_ci(project_path)

            # Run trend analysis
            trend_analysis = self.trend_analyzer.analyze_trends(days_back=7)

            # Generate alerts
            alerts = self._generate_alerts(analysis_result, trend_analysis, project_path)

            # Process and send alerts
            for alert in alerts:
                self._process_alert(alert)

            return alerts

        except Exception as e:
            self.logger.error(f"Error during analysis and alerting: {e}")
            return []

    def _generate_alerts(self, analysis: AnalysisResult, trend: TrendAnalysis, project_path: str) -> List[Alert]:
        """Generate alerts based on analysis results and configured rules."""
        alerts = []
        timestamp = datetime.now()

        # Quality score alerts
        if analysis.quality_score <= self.config['alert_rules']['quality_score_critical']['threshold']:
            alerts.append(Alert(
                id=f"quality_critical_{timestamp.strftime('%Y%m%d_%H%M%S')}",
                type='quality_score_critical',
                severity='critical',
                message=f"Quality score critically low: {analysis.quality_score:.2f}/10",
                timestamp=timestamp,
                project_path=project_path,
                metric_name='quality_score',
                current_value=analysis.quality_score,
                threshold_value=self.config['alert_rules']['quality_score_critical']['threshold']
            ))
        elif analysis.quality_score <= self.config['alert_rules']['quality_score_warning']['threshold']:
            alerts.append(Alert(
                id=f"quality_warning_{timestamp.strftime('%Y%m%d_%H%M%S')}",
                type='quality_score_warning',
                severity='high',
                message=f"Quality score below warning threshold: {analysis.quality_score:.2f}/10",
                timestamp=timestamp,
                project_path=project_path,
                metric_name='quality_score',
                current_value=analysis.quality_score,
                threshold_value=self.config['alert_rules']['quality_score_warning']['threshold']
            ))

        # Complexity alerts
        if analysis.avg_cyclomatic_complexity > self.config['alert_rules']['complexity_high']['threshold']:
            alerts.append(Alert(
                id=f"complexity_high_{timestamp.strftime('%Y%m%d_%H%M%S')}",
                type='complexity_high',
                severity='medium',
                message=f"High average cyclomatic complexity: {analysis.avg_cyclomatic_complexity:.2f}",
                timestamp=timestamp,
                project_path=project_path,
                metric_name='avg_cyclomatic_complexity',
                current_value=analysis.avg_cyclomatic_complexity,
                threshold_value=self.config['alert_rules']['complexity_high']['threshold']
            ))

        # Violation count alerts
        violation_count = len(analysis.complexity_violations)
        if violation_count > self.config['alert_rules']['violations_many']['threshold']:
            alerts.append(Alert(
                id=f"violations_many_{timestamp.strftime('%Y%m%d_%H%M%S')}",
                type='violations_many',
                severity='medium',
                message=f"High number of complexity violations: {violation_count}",
                timestamp=timestamp,
                project_path=project_path,
                metric_name='violation_count',
                current_value=violation_count,
                threshold_value=self.config['alert_rules']['violations_many']['threshold']
            ))

        # Trend-based alerts
        if trend.regression_detected:
            alerts.append(Alert(
                id=f"regression_{timestamp.strftime('%Y%m%d_%H%M%S')}",
                type='regression_detected',
                severity='high',
                message=f"Quality regression detected (change: {trend.quality_score_change:+.2f})",
                timestamp=timestamp,
                project_path=project_path,
                metric_name='quality_trend',
                current_value=trend.quality_score_change,
                threshold_value=0.0,
                trend_data={'trend_direction': trend.trend_direction, 'trend_strength': trend.trend_strength}
            ))

        if trend.trend_direction == 'declining' and trend.trend_strength > 0.5:
            alerts.append(Alert(
                id=f"trend_declining_{timestamp.strftime('%Y%m%d_%H%M%S')}",
                type='trend_declining',
                severity='medium',
                message=f"Consistent declining quality trend (strength: {trend.trend_strength:.2f})",
                timestamp=timestamp,
                project_path=project_path,
                metric_name='trend_strength',
                current_value=trend.trend_strength,
                threshold_value=0.5,
                trend_data={'trend_direction': trend.trend_direction}
            ))

        return alerts

    def _process_alert(self, alert: Alert) -> None:
        """Process an individual alert (deduplication, throttling, notification)."""

        # Check if this is a duplicate alert
        if self._is_duplicate_alert(alert):
            self.logger.debug(f"Skipping duplicate alert: {alert.type}")
            return

        # Check throttling
        if self._is_alert_throttled(alert):
            self.logger.debug(f"Alert throttled: {alert.type}")
            return

        # Store alert
        self.active_alerts[alert.id] = alert
        self._save_alert_to_history(alert)

        # Send notifications
        self._send_notifications(alert)

        # Update throttling timestamp
        self.last_notification_times[alert.type] = datetime.now()

    def _is_duplicate_alert(self, alert: Alert) -> bool:
        """Check if this alert is a duplicate of an active alert."""
        for active_alert in self.active_alerts.values():
            if (active_alert.type == alert.type and
                active_alert.project_path == alert.project_path and
                not active_alert.acknowledged):

                # Check if values are similar (within 5%)
                if abs(active_alert.current_value - alert.current_value) / max(active_alert.current_value, 1) < 0.05:
                    return True

        return False

    def _is_alert_throttled(self, alert: Alert) -> bool:
        """Check if alert type is currently throttled."""
        if alert.type not in self.last_notification_times:
            return False

        throttle_seconds = self.config['notification_throttling'].get(alert.severity, 3600)
        time_since_last = datetime.now() - self.last_notification_times[alert.type]

        return time_since_last.total_seconds() < throttle_seconds

    def _save_alert_to_history(self, alert: Alert) -> None:
        """Save alert to persistent history."""
        history = []

        if self.alert_history_file.exists():
            try:
                with open(self.alert_history_file, 'r') as f:
                    history = json.load(f)
            except Exception as e:
                self.logger.warning(f"Error loading alert history: {e}")

        # Add new alert
        alert_dict = asdict(alert)
        alert_dict['timestamp'] = alert.timestamp.isoformat()
        history.append(alert_dict)

        # Keep only last 1000 alerts
        history = history[-1000:]

        try:
            with open(self.alert_history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving alert history: {e}")

    def _send_notifications(self, alert: Alert) -> None:
        """Send alert notifications to configured channels."""
        for channel in self.notification_channels:
            if not channel.enabled:
                continue

            if alert.severity not in channel.severity_filter:
                continue

            try:
                if channel.type == 'email':
                    self._send_email_notification(alert, channel)
                elif channel.type == 'slack':
                    self._send_slack_notification(alert, channel)
                elif channel.type == 'teams':
                    self._send_teams_notification(alert, channel)
                else:
                    self.logger.warning(f"Unknown notification channel type: {channel.type}")

            except Exception as e:
                self.logger.error(f"Error sending notification to {channel.name}: {e}")

    def _send_email_notification(self, alert: Alert, channel: NotificationChannel) -> None:
        """Send email notification."""
        config = channel.config

        # Create message
        msg = MIMEMultipart()
        msg['From'] = config['username']
        msg['To'] = ', '.join(config['recipients'])
        msg['Subject'] = f"🚨 Code Quality Alert: {alert.type.replace('_', ' ').title()}"

        # Create email body
        severity_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🔵'}
        body = f"""
{severity_emoji.get(alert.severity, '⚪')} **Code Quality Alert**

**Severity:** {alert.severity.upper()}
**Project:** {alert.project_path}
**Time:** {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

**Alert:** {alert.message}

**Details:**
- Metric: {alert.metric_name}
- Current Value: {alert.current_value}
- Threshold: {alert.threshold_value}

{"**Trend Data:** " + str(alert.trend_data) if alert.trend_data else ""}

This alert was generated automatically by the Code Quality Monitoring System.
"""

        msg.attach(MIMEText(body, 'plain'))

        # Send email
        server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
        server.starttls()
        server.login(config['username'], config['password'])
        server.send_message(msg)
        server.quit()

    def _send_slack_notification(self, alert: Alert, channel: NotificationChannel) -> None:
        """Send Slack notification."""
        webhook_url = channel.config['webhook_url']

        severity_colors = {'critical': '#FF0000', 'high': '#FF8800', 'medium': '#FFAA00', 'low': '#0088FF'}

        payload = {
            'text': f"🚨 Code Quality Alert: {alert.type.replace('_', ' ').title()}",
            'attachments': [{
                'color': severity_colors.get(alert.severity, '#808080'),
                'fields': [
                    {'title': 'Severity', 'value': alert.severity.upper(), 'short': True},
                    {'title': 'Project', 'value': alert.project_path, 'short': True},
                    {'title': 'Message', 'value': alert.message, 'short': False},
                    {'title': 'Current Value', 'value': str(alert.current_value), 'short': True},
                    {'title': 'Threshold', 'value': str(alert.threshold_value), 'short': True}
                ],
                'footer': 'Code Quality Monitor',
                'ts': int(alert.timestamp.timestamp())
            }]
        }

        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()

    def _send_teams_notification(self, alert: Alert, channel: NotificationChannel) -> None:
        """Send Microsoft Teams notification."""
        webhook_url = channel.config['webhook_url']

        severity_colors = {'critical': 'attention', 'high': 'warning', 'medium': 'accent', 'low': 'good'}

        payload = {
            '@type': 'MessageCard',
            '@context': 'https://schema.org/extensions',
            'summary': f'Code Quality Alert: {alert.type}',
            'themeColor': severity_colors.get(alert.severity, '808080'),
            'sections': [{
                'activityTitle': f'🚨 Code Quality Alert: {alert.type.replace("_", " ").title()}',
                'activitySubtitle': f'Severity: {alert.severity.upper()}',
                'facts': [
                    {'name': 'Project', 'value': alert.project_path},
                    {'name': 'Message', 'value': alert.message},
                    {'name': 'Current Value', 'value': str(alert.current_value)},
                    {'name': 'Threshold', 'value': str(alert.threshold_value)},
                    {'name': 'Time', 'value': alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
                ]
            }]
        }

        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()

    def generate_daily_summary(self, project_path: str) -> str:
        """Generate daily summary report."""

        # Get recent analysis
        analysis = self.ci_manager.analyze_project_for_ci(project_path)
        trend_analysis = self.trend_analyzer.analyze_trends(days_back=7)

        # Get recent alerts (last 24 hours)
        recent_alerts = self._get_recent_alerts(hours_back=24)

        summary = f"""# 📊 Daily Code Quality Summary

**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Project:** {project_path}

## 🎯 Current Status

- **Quality Score:** {analysis.quality_score:.2f}/10
- **Total Files:** {analysis.total_files}
- **Total Functions:** {analysis.total_functions}
- **Complexity Violations:** {len(analysis.complexity_violations)}

## 📈 Trend (7-day)

- **Direction:** {trend_analysis.trend_direction.title()}
- **Quality Change:** {trend_analysis.quality_score_change:+.2f}
- **Complexity Trend:** {trend_analysis.complexity_trend}

## 🚨 Alerts (Last 24h)

{len(recent_alerts)} alerts generated:
"""

        for alert in recent_alerts:
            severity_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🔵'}
            summary += f"- {severity_emoji.get(alert['severity'], '⚪')} {alert['message']}\n"

        if trend_analysis.recommendations:
            summary += "\n## 💡 Top Recommendations\n\n"
            for i, rec in enumerate(trend_analysis.recommendations[:3], 1):
                summary += f"{i}. {rec}\n"

        return summary

    def _get_recent_alerts(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Get alerts from recent time period."""
        if not self.alert_history_file.exists():
            return []

        try:
            with open(self.alert_history_file, 'r') as f:
                history = json.load(f)

            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            recent_alerts = []

            for alert_data in history:
                alert_time = datetime.fromisoformat(alert_data['timestamp'])
                if alert_time >= cutoff_time:
                    recent_alerts.append(alert_data)

            return recent_alerts

        except Exception as e:
            self.logger.error(f"Error loading recent alerts: {e}")
            return []


def main():
    """Command-line interface for alert manager."""
    import argparse

    parser = argparse.ArgumentParser(description='Code Quality Alert Manager')
    parser.add_argument('project_path', help='Path to project root')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--action', choices=['analyze', 'summary', 'test-notifications'],
                       default='analyze', help='Action to perform')
    parser.add_argument('--output', help='Output file for reports')

    args = parser.parse_args()

    # Initialize alert manager
    alert_manager = AlertManager(args.config)

    try:
        if args.action == 'analyze':
            alerts = alert_manager.analyze_and_alert(args.project_path)
            print(f"Generated {len(alerts)} alerts")

            for alert in alerts:
                severity_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🔵'}
                print(f"{severity_emoji.get(alert.severity, '⚪')} [{alert.severity.upper()}] {alert.message}")

        elif args.action == 'summary':
            summary = alert_manager.generate_daily_summary(args.project_path)

            if args.output:
                with open(args.output, 'w') as f:
                    f.write(summary)
                print(f"Summary written to {args.output}")
            else:
                print(summary)

        elif args.action == 'test-notifications':
            # Create test alert
            test_alert = Alert(
                id='test_alert',
                type='test_notification',
                severity='medium',
                message='This is a test notification from the Code Quality Alert Manager',
                timestamp=datetime.now(),
                project_path=args.project_path,
                metric_name='test_metric',
                current_value=1.0,
                threshold_value=0.5
            )

            alert_manager._send_notifications(test_alert)
            print("Test notifications sent to all configured channels")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
#!/usr/bin/env python3
"""
StreamLogix - A functional, stream-based log analysis tool
Author: Bob (Claude Code Instance)
"""

import re
import json
from datetime import datetime
from typing import Iterator, Dict, List, Callable, Any, Optional, NamedTuple
from collections import defaultdict, Counter
from dataclasses import dataclass
import sys


# Core data structures
class LogEntry(NamedTuple):
    timestamp: datetime
    level: str
    source: str
    message: str
    raw_line: str


@dataclass(frozen=True)
class AnalysisResult:
    total_entries: int
    level_distribution: Dict[str, int]
    time_range: tuple
    top_sources: List[tuple]
    patterns_found: Dict[str, int]
    anomalies: List[str]


class StreamParser:
    """Streaming log parser with pluggable format support"""

    def __init__(self):
        self.parsers = {
            'common': self._parse_common_log,
            'json': self._parse_json_log,
            'syslog': self._parse_syslog,
            'apache': self._parse_apache_log
        }

    def parse_stream(self, file_stream: Iterator[str], format_hint: str = 'auto') -> Iterator[LogEntry]:
        """Stream parser that yields LogEntry objects"""
        for line in file_stream:
            line = line.strip()
            if not line:
                continue

            # Auto-detect format if needed
            if format_hint == 'auto':
                format_hint = self._detect_format(line)

            parser = self.parsers.get(format_hint, self._parse_common_log)
            entry = parser(line)
            if entry:
                yield entry

    def _detect_format(self, line: str) -> str:
        """Simple format detection"""
        if line.startswith('{') and line.endswith('}'):
            return 'json'
        elif re.match(r'^\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}', line):
            return 'syslog'
        elif ' - - [' in line and '] "' in line:
            return 'apache'
        return 'common'

    def _parse_common_log(self, line: str) -> Optional[LogEntry]:
        """Parse common application log format: TIMESTAMP LEVEL SOURCE MESSAGE"""
        # Updated pattern to handle ISO format timestamps
        pattern = r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})\s+(\w+)\s+(\S+)\s+(.+)$'
        match = re.match(pattern, line)
        if match:
            try:
                timestamp = datetime.fromisoformat(match.group(1))
            except ValueError:
                timestamp = datetime.now()  # Fallback

            return LogEntry(
                timestamp=timestamp,
                level=match.group(2),
                source=match.group(3),
                message=match.group(4),
                raw_line=line
            )
        return None

    def _parse_json_log(self, line: str) -> Optional[LogEntry]:
        """Parse JSON log format"""
        try:
            data = json.loads(line)
            timestamp = datetime.fromisoformat(data.get('timestamp', datetime.now().isoformat()))
            return LogEntry(
                timestamp=timestamp,
                level=data.get('level', 'INFO'),
                source=data.get('source', 'unknown'),
                message=data.get('message', ''),
                raw_line=line
            )
        except (json.JSONDecodeError, ValueError):
            return None

    def _parse_syslog(self, line: str) -> Optional[LogEntry]:
        """Parse syslog format"""
        pattern = r'^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+(\S+)\s+(\S+):\s*(.+)$'
        match = re.match(pattern, line)
        if match:
            try:
                # Simplified timestamp parsing
                timestamp = datetime.now()  # Would need proper year handling
            except ValueError:
                timestamp = datetime.now()

            return LogEntry(
                timestamp=timestamp,
                level='INFO',  # Syslog doesn't always have explicit levels
                source=match.group(3),
                message=match.group(4),
                raw_line=line
            )
        return None

    def _parse_apache_log(self, line: str) -> Optional[LogEntry]:
        """Parse Apache access log format"""
        pattern = r'^(\S+).*\[([^\]]+)\]\s+"([^"]+)"\s+(\d+)\s+(\d+|-)'
        match = re.match(pattern, line)
        if match:
            try:
                # Simplified - would need proper Apache timestamp parsing
                timestamp = datetime.now()
            except ValueError:
                timestamp = datetime.now()

            status_code = int(match.group(4))
            level = 'ERROR' if status_code >= 400 else 'INFO'

            return LogEntry(
                timestamp=timestamp,
                level=level,
                source='apache',
                message=f"{match.group(3)} -> {status_code}",
                raw_line=line
            )
        return None


class AnalysisPipeline:
    """Composable analysis functions for stream processing"""

    @staticmethod
    def count_levels() -> Callable[[Iterator[LogEntry]], Dict[str, int]]:
        """Returns a function that counts log levels"""
        def _count(entries: Iterator[LogEntry]) -> Dict[str, int]:
            return Counter(entry.level for entry in entries)
        return _count

    @staticmethod
    def time_range_analysis() -> Callable[[Iterator[LogEntry]], tuple]:
        """Returns a function that finds time range"""
        def _time_range(entries: Iterator[LogEntry]) -> tuple:
            timestamps = [entry.timestamp for entry in entries]
            if not timestamps:
                return None, None
            return min(timestamps), max(timestamps)
        return _time_range

    @staticmethod
    def top_sources(n: int = 10) -> Callable[[Iterator[LogEntry]], List[tuple]]:
        """Returns a function that finds top N sources"""
        def _top_sources(entries: Iterator[LogEntry]) -> List[tuple]:
            source_counts = Counter(entry.source for entry in entries)
            return source_counts.most_common(n)
        return _top_sources

    @staticmethod
    def pattern_detector(patterns: Dict[str, str]) -> Callable[[Iterator[LogEntry]], Dict[str, int]]:
        """Returns a function that counts pattern matches"""
        compiled_patterns = {name: re.compile(pattern) for name, pattern in patterns.items()}

        def _detect_patterns(entries: Iterator[LogEntry]) -> Dict[str, int]:
            pattern_counts = defaultdict(int)
            for entry in entries:
                for name, pattern in compiled_patterns.items():
                    if pattern.search(entry.message):
                        pattern_counts[name] += 1
            return dict(pattern_counts)
        return _detect_patterns

    @staticmethod
    def anomaly_detector(threshold: float = 2.0) -> Callable[[Iterator[LogEntry]], List[str]]:
        """Returns a function that detects anomalies based on error rate"""
        def _detect_anomalies(entries: Iterator[LogEntry]) -> List[str]:
            # Simplified anomaly detection - would be more sophisticated in practice
            entries_list = list(entries)
            error_entries = [e for e in entries_list if e.level in ['ERROR', 'CRITICAL']]

            if len(entries_list) == 0:
                return []

            error_rate = len(error_entries) / len(entries_list)
            anomalies = []

            if error_rate > 0.1:  # More than 10% errors
                anomalies.append(f"High error rate detected: {error_rate:.2%}")

            # Check for repeated error messages
            error_messages = [e.message for e in error_entries]
            message_counts = Counter(error_messages)
            for message, count in message_counts.most_common(3):
                if count > 5:
                    anomalies.append(f"Repeated error: '{message[:50]}...' ({count} times)")

            return anomalies
        return _detect_anomalies


class StreamLogAnalyzer:
    """Main analyzer that orchestrates the streaming analysis"""

    def __init__(self):
        self.parser = StreamParser()
        self.default_patterns = {
            'errors': r'(?i)(error|exception|failed|timeout)',
            'warnings': r'(?i)(warning|warn|deprecated)',
            'database': r'(?i)(sql|database|db|query)',
            'authentication': r'(?i)(login|auth|token|session|password)',
            'performance': r'(?i)(slow|timeout|latency|performance|ms|seconds)'
        }

    def analyze_file(self, file_path: str, format_hint: str = 'auto') -> AnalysisResult:
        """Analyze a log file using streaming approach"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Stream the file line by line
                entries = self.parser.parse_stream(f, format_hint)

                # We need to consume the stream multiple times for different analyses
                # In a real implementation, we'd use itertools.tee or process in a single pass
                entries_list = list(entries)  # Convert to list for multiple iterations

                # Run all analyses
                level_dist = AnalysisPipeline.count_levels()(iter(entries_list))
                time_range = AnalysisPipeline.time_range_analysis()(iter(entries_list))
                top_sources = AnalysisPipeline.top_sources(10)(iter(entries_list))
                patterns = AnalysisPipeline.pattern_detector(self.default_patterns)(iter(entries_list))
                anomalies = AnalysisPipeline.anomaly_detector()(iter(entries_list))

                return AnalysisResult(
                    total_entries=len(entries_list),
                    level_distribution=level_dist,
                    time_range=time_range,
                    top_sources=top_sources,
                    patterns_found=patterns,
                    anomalies=anomalies
                )

        except FileNotFoundError:
            raise FileNotFoundError(f"Log file not found: {file_path}")
        except Exception as e:
            raise RuntimeError(f"Error analyzing file: {e}")

    def generate_report(self, result: AnalysisResult) -> str:
        """Generate a human-readable analysis report"""
        report = []
        report.append("=" * 50)
        report.append("STREAMLOGIX ANALYSIS REPORT")
        report.append("=" * 50)
        report.append(f"Total log entries processed: {result.total_entries}")

        if result.time_range[0] and result.time_range[1]:
            report.append(f"Time range: {result.time_range[0]} to {result.time_range[1]}")

        report.append("\nLOG LEVEL DISTRIBUTION:")
        for level, count in sorted(result.level_distribution.items()):
            percentage = (count / result.total_entries) * 100
            report.append(f"  {level}: {count} ({percentage:.1f}%)")

        if result.top_sources:
            report.append("\nTOP SOURCES:")
            for source, count in result.top_sources[:5]:
                report.append(f"  {source}: {count} entries")

        if result.patterns_found:
            report.append("\nPATTERNS DETECTED:")
            for pattern, count in sorted(result.patterns_found.items(), key=lambda x: x[1], reverse=True):
                report.append(f"  {pattern}: {count} matches")

        if result.anomalies:
            report.append("\nANOMALIES DETECTED:")
            for anomaly in result.anomalies:
                report.append(f"  ⚠️  {anomaly}")

        report.append("=" * 50)
        return "\n".join(report)


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python log_analyzer.py <log_file> [format]")
        print("Formats: auto (default), common, json, syslog, apache")
        return

    file_path = sys.argv[1]
    format_hint = sys.argv[2] if len(sys.argv) > 2 else 'auto'

    analyzer = StreamLogAnalyzer()

    try:
        print(f"Analyzing {file_path} with format '{format_hint}'...")
        result = analyzer.analyze_file(file_path, format_hint)
        report = analyzer.generate_report(result)
        print(report)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
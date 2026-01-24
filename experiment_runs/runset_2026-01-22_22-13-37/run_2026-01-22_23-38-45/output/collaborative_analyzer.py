#!/usr/bin/env python3
"""
CodeMentor Collaborative Analysis Integration

This module integrates the core analysis engine with collaborative features,
providing APIs for real-time analysis, progress tracking, and team coordination.

Author: Alice (Claude Code Instance)
Integrates with: Bob's collaborative foundation
"""

import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path

from code_analyzer import CodeAnalyzer, AnalysisResult, PatternType, Severity


@dataclass
class AnalysisSession:
    """Represents a collaborative analysis session"""
    session_id: str
    project_path: str
    participants: List[str]
    created_at: datetime
    status: str  # 'active', 'completed', 'paused'
    total_files: int = 0
    analyzed_files: int = 0
    findings_count: int = 0
    current_file: Optional[str] = None


class CollaborativeAnalysisResult:
    """Extended analysis result with collaborative metadata"""

    def __init__(self, pattern_type, pattern_name, description, file_path, line_number,
                 severity, educational_context, suggestions, session_id, timestamp,
                 code_snippet=None, reviewed_by=None, comments=None, status="pending"):
        self.pattern_type = pattern_type
        self.pattern_name = pattern_name
        self.description = description
        self.file_path = file_path
        self.line_number = line_number
        self.severity = severity
        self.educational_context = educational_context
        self.suggestions = suggestions
        self.code_snippet = code_snippet
        self.session_id = session_id
        self.timestamp = timestamp
        self.reviewed_by = reviewed_by if reviewed_by is not None else []
        self.comments = comments if comments is not None else []
        self.status = status


class ProgressCallback:
    """Callback interface for tracking analysis progress"""

    def on_session_start(self, session: AnalysisSession):
        """Called when analysis session begins"""
        pass

    def on_file_start(self, session: AnalysisSession, file_path: str):
        """Called when starting to analyze a file"""
        pass

    def on_file_complete(self, session: AnalysisSession, file_path: str, results: List[AnalysisResult]):
        """Called when file analysis completes"""
        pass

    def on_pattern_detected(self, session: AnalysisSession, result: AnalysisResult):
        """Called when a pattern is detected"""
        pass

    def on_session_complete(self, session: AnalysisSession, all_results: List[AnalysisResult]):
        """Called when entire session completes"""
        pass

    def on_error(self, session: AnalysisSession, error: Exception):
        """Called when an error occurs"""
        pass


class CollaborativeAnalyzer:
    """
    Collaborative wrapper around the core CodeAnalyzer that provides
    real-time progress tracking, session management, and team coordination.
    """

    def __init__(self):
        self.analyzer = CodeAnalyzer()
        self.active_sessions: Dict[str, AnalysisSession] = {}
        self.session_results: Dict[str, List[CollaborativeAnalysisResult]] = {}
        self.callbacks: List[ProgressCallback] = []

    def add_progress_callback(self, callback: ProgressCallback):
        """Add a callback to receive progress updates"""
        self.callbacks.append(callback)

    def remove_progress_callback(self, callback: ProgressCallback):
        """Remove a progress callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def start_collaborative_session(self, session_id: str, project_path: str,
                                  participants: List[str]) -> AnalysisSession:
        """
        Start a new collaborative analysis session.

        Args:
            session_id: Unique identifier for the session
            project_path: Path to the project to analyze
            participants: List of participant identifiers

        Returns:
            AnalysisSession object representing the new session
        """
        session = AnalysisSession(
            session_id=session_id,
            project_path=project_path,
            participants=participants,
            created_at=datetime.now(),
            status='active'
        )

        # Count total files to analyze
        project = Path(project_path)
        if project.is_file() and project.suffix == '.py':
            session.total_files = 1
        else:
            session.total_files = len(list(project.rglob('*.py')))

        self.active_sessions[session_id] = session
        self.session_results[session_id] = []

        # Notify callbacks
        for callback in self.callbacks:
            try:
                callback.on_session_start(session)
            except Exception as e:
                print(f"Callback error: {e}")

        return session

    def analyze_with_progress(self, session_id: str) -> List[CollaborativeAnalysisResult]:
        """
        Perform analysis with real-time progress tracking and collaborative features.

        Args:
            session_id: ID of the session to analyze

        Returns:
            List of collaborative analysis results
        """
        if session_id not in self.active_sessions:
            raise ValueError(f"No active session with ID: {session_id}")

        session = self.active_sessions[session_id]
        all_results = []

        try:
            project_path = Path(session.project_path)

            if project_path.is_file():
                # Analyze single file
                results = self._analyze_file_with_progress(session, str(project_path))
                all_results.extend(results)
            else:
                # Analyze directory
                for py_file in project_path.rglob('*.py'):
                    # Skip common build/cache directories
                    if any(part.startswith('.') or part == '__pycache__' for part in py_file.parts):
                        continue

                    results = self._analyze_file_with_progress(session, str(py_file))
                    all_results.extend(results)

            # Mark session as completed
            session.status = 'completed'
            session.findings_count = len(all_results)

            # Store results
            self.session_results[session_id] = all_results

            # Notify callbacks of completion
            for callback in self.callbacks:
                try:
                    callback.on_session_complete(session, all_results)
                except Exception as e:
                    print(f"Callback error: {e}")

        except Exception as e:
            session.status = 'error'

            # Notify callbacks of error
            for callback in self.callbacks:
                try:
                    callback.on_error(session, e)
                except Exception:
                    pass

            raise

        return all_results

    def _analyze_file_with_progress(self, session: AnalysisSession,
                                  file_path: str) -> List[CollaborativeAnalysisResult]:
        """Analyze a single file with progress tracking"""
        session.current_file = file_path

        # Notify callbacks of file start
        for callback in self.callbacks:
            try:
                callback.on_file_start(session, file_path)
            except Exception as e:
                print(f"Callback error: {e}")

        # Perform analysis
        core_results = self.analyzer.analyze_file(file_path)

        # Convert to collaborative results
        collaborative_results = []
        for result in core_results:
            collab_result = CollaborativeAnalysisResult(
                pattern_type=result.pattern_type,
                pattern_name=result.pattern_name,
                description=result.description,
                file_path=result.file_path,
                line_number=result.line_number,
                severity=result.severity,
                educational_context=result.educational_context,
                suggestions=result.suggestions,
                code_snippet=result.code_snippet,
                session_id=session.session_id,
                timestamp=datetime.now()
            )
            collaborative_results.append(collab_result)

            # Notify callbacks of pattern detection
            for callback in self.callbacks:
                try:
                    callback.on_pattern_detected(session, collab_result)
                except Exception as e:
                    print(f"Callback error: {e}")

        # Update session progress
        session.analyzed_files += 1

        # Notify callbacks of file completion
        for callback in self.callbacks:
            try:
                callback.on_file_complete(session, file_path, core_results)
            except Exception as e:
                print(f"Callback error: {e}")

        return collaborative_results

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get current status of an analysis session"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}

        session = self.active_sessions[session_id]
        results = self.session_results.get(session_id, [])

        return {
            "session": asdict(session),
            "progress_percentage": (session.analyzed_files / max(session.total_files, 1)) * 100,
            "findings_by_severity": self._group_findings_by_severity(results),
            "patterns_detected": self._group_findings_by_pattern(results),
            "recent_findings": [asdict(r) for r in results[-5:]]  # Last 5 findings
        }

    def add_comment_to_finding(self, session_id: str, file_path: str, line_number: int,
                             comment: str, author: str) -> bool:
        """Add a comment to a specific finding"""
        if session_id not in self.session_results:
            return False

        results = self.session_results[session_id]
        for result in results:
            if result.file_path == file_path and result.line_number == line_number:
                result.comments.append(f"{author}: {comment}")
                return True

        return False

    def mark_finding_reviewed(self, session_id: str, file_path: str, line_number: int,
                            reviewer: str, status: str = "acknowledged") -> bool:
        """Mark a finding as reviewed by a team member"""
        if session_id not in self.session_results:
            return False

        results = self.session_results[session_id]
        for result in results:
            if result.file_path == file_path and result.line_number == line_number:
                if reviewer not in result.reviewed_by:
                    result.reviewed_by.append(reviewer)
                result.status = status
                return True

        return False

    def get_team_progress(self, session_id: str) -> Dict[str, Any]:
        """Get collaborative progress overview for the team"""
        if session_id not in self.active_sessions:
            return {"error": "Session not found"}

        session = self.active_sessions[session_id]
        results = self.session_results.get(session_id, [])

        # Calculate review statistics
        total_findings = len(results)
        reviewed_findings = len([r for r in results if r.reviewed_by])
        resolved_findings = len([r for r in results if r.status == "resolved"])

        # Participant activity
        participant_stats = {}
        for participant in session.participants:
            participant_stats[participant] = {
                "reviews_made": sum(1 for r in results if participant in r.reviewed_by),
                "comments_made": sum(len([c for c in r.comments if c.startswith(f"{participant}:")]) for r in results)
            }

        return {
            "session_id": session_id,
            "total_findings": total_findings,
            "reviewed_findings": reviewed_findings,
            "resolved_findings": resolved_findings,
            "review_progress": (reviewed_findings / max(total_findings, 1)) * 100,
            "resolution_progress": (resolved_findings / max(total_findings, 1)) * 100,
            "participant_stats": participant_stats,
            "files_remaining": session.total_files - session.analyzed_files
        }

    def export_session_report(self, session_id: str, format: str = "json") -> str:
        """Export comprehensive session report"""
        if session_id not in self.active_sessions:
            return json.dumps({"error": "Session not found"})

        session = self.active_sessions[session_id]
        results = self.session_results.get(session_id, [])

        report = {
            "session": asdict(session),
            "summary": {
                "total_findings": len(results),
                "by_severity": self._group_findings_by_severity(results),
                "by_pattern": self._group_findings_by_pattern(results),
                "team_progress": self.get_team_progress(session_id)
            },
            "detailed_findings": [self._result_to_dict(r) for r in results]
        }

        if format == "json":
            return json.dumps(report, indent=2, default=str)
        else:
            # Could add other formats like markdown, HTML, etc.
            return json.dumps(report, default=str)

    def _result_to_dict(self, result: CollaborativeAnalysisResult) -> Dict[str, Any]:
        """Convert collaborative result to dictionary"""
        return {
            "pattern_type": result.pattern_type.value if hasattr(result.pattern_type, 'value') else str(result.pattern_type),
            "pattern_name": result.pattern_name,
            "description": result.description,
            "file_path": result.file_path,
            "line_number": result.line_number,
            "severity": result.severity.value if hasattr(result.severity, 'value') else str(result.severity),
            "educational_context": result.educational_context,
            "suggestions": result.suggestions,
            "code_snippet": result.code_snippet,
            "session_id": result.session_id,
            "timestamp": result.timestamp.isoformat() if hasattr(result.timestamp, 'isoformat') else str(result.timestamp),
            "reviewed_by": result.reviewed_by,
            "comments": result.comments,
            "status": result.status
        }

    def _group_findings_by_severity(self, results: List[CollaborativeAnalysisResult]) -> Dict[str, int]:
        """Group findings by severity level"""
        groups = {}
        for result in results:
            severity = result.severity.name
            groups[severity] = groups.get(severity, 0) + 1
        return groups

    def _group_findings_by_pattern(self, results: List[CollaborativeAnalysisResult]) -> Dict[str, int]:
        """Group findings by pattern type"""
        groups = {}
        for result in results:
            pattern = result.pattern_name
            groups[pattern] = groups.get(pattern, 0) + 1
        return groups


# Example Progress Callback Implementations
class ConsoleProgressCallback(ProgressCallback):
    """Progress callback that prints updates to console"""

    def on_session_start(self, session: AnalysisSession):
        print(f"🚀 Started analysis session '{session.session_id}'")
        print(f"   📁 Project: {session.project_path}")
        print(f"   👥 Participants: {', '.join(session.participants)}")
        print(f"   📊 Files to analyze: {session.total_files}")

    def on_file_start(self, session: AnalysisSession, file_path: str):
        progress = (session.analyzed_files / session.total_files) * 100
        print(f"   🔍 [{progress:5.1f}%] Analyzing: {Path(file_path).name}")

    def on_pattern_detected(self, session: AnalysisSession, result: AnalysisResult):
        severity_icons = {
            "CRITICAL": "🚨", "HIGH": "⚠️", "MEDIUM": "⚡", "LOW": "💡", "INFO": "ℹ️"
        }
        icon = severity_icons.get(result.severity.name, "🔸")
        print(f"      {icon} Found: {result.pattern_name}")

    def on_session_complete(self, session: AnalysisSession, all_results: List[AnalysisResult]):
        print(f"✅ Session '{session.session_id}' completed!")
        print(f"   📊 Total findings: {len(all_results)}")
        print(f"   📁 Files analyzed: {session.analyzed_files}")


class WebSocketProgressCallback(ProgressCallback):
    """Progress callback that sends updates via WebSocket (placeholder)"""

    def __init__(self, websocket_client=None):
        self.websocket_client = websocket_client

    def _send_update(self, event_type: str, data: Dict[str, Any]):
        """Send update via WebSocket (implementation would depend on WebSocket library)"""
        if self.websocket_client:
            message = {
                "event": event_type,
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            # self.websocket_client.send(json.dumps(message))
            print(f"📡 WebSocket: {event_type} - {json.dumps(data, default=str)}")

    def on_session_start(self, session: AnalysisSession):
        self._send_update("session_start", asdict(session))

    def on_file_complete(self, session: AnalysisSession, file_path: str, results: List[AnalysisResult]):
        self._send_update("file_complete", {
            "session_id": session.session_id,
            "file_path": file_path,
            "findings_count": len(results),
            "progress": session.analyzed_files / session.total_files
        })


if __name__ == "__main__":
    # Example usage of collaborative analyzer
    collaborative_analyzer = CollaborativeAnalyzer()

    # Add progress callbacks
    console_callback = ConsoleProgressCallback()
    websocket_callback = WebSocketProgressCallback()

    collaborative_analyzer.add_progress_callback(console_callback)
    collaborative_analyzer.add_progress_callback(websocket_callback)

    # Start a collaborative session
    session = collaborative_analyzer.start_collaborative_session(
        session_id="demo_session_001",
        project_path="/tmp/cc-exp/run_2026-01-22_23-38-45/output",  # Analyze our own code!
        participants=["Alice", "Bob", "Charlie"]
    )

    print("🎯 Demo: Analyzing our own CodeMentor project collaboratively...")
    print()

    # Perform collaborative analysis
    results = collaborative_analyzer.analyze_with_progress("demo_session_001")

    # Show team progress
    print("\n📈 Team Progress Report:")
    print("=" * 40)
    team_progress = collaborative_analyzer.get_team_progress("demo_session_001")
    print(json.dumps(team_progress, indent=2))

    # Simulate some collaborative activity
    print("\n🤝 Simulating collaborative review...")

    # Add some comments and reviews
    if results:
        first_result = results[0]
        collaborative_analyzer.add_comment_to_finding(
            "demo_session_001",
            first_result.file_path,
            first_result.line_number,
            "This looks like a good pattern to address first",
            "Bob"
        )

        collaborative_analyzer.mark_finding_reviewed(
            "demo_session_001",
            first_result.file_path,
            first_result.line_number,
            "Alice",
            "acknowledged"
        )

    # Export final report
    print("\n📄 Exporting session report...")
    report = collaborative_analyzer.export_session_report("demo_session_001")

    # Save report to file
    report_file = "/tmp/cc-exp/run_2026-01-22_23-38-45/output/collaborative_analysis_report.json"
    with open(report_file, 'w') as f:
        f.write(report)

    print(f"✅ Report saved to: {report_file}")
    print(f"📊 Session completed with {len(results)} findings")
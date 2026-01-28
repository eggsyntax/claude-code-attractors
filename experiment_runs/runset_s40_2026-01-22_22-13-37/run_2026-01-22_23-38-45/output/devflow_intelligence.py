"""
DevFlow Intelligence Layer
Machine learning and pattern recognition for intelligent workflow optimization.
"""

import asyncio
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from collections import defaultdict, deque

from devflow_engine_core import WorkflowExecution, WorkflowStatus, EventType


class OptimizationType(Enum):
    TIMING = "timing"  # When to run workflows
    RESOURCE = "resource"  # Resource allocation optimization
    REVIEWER = "reviewer"  # Reviewer assignment optimization
    DEPLOYMENT = "deployment"  # Deployment window optimization


@dataclass
class TeamMember:
    """Represents a team member with skills and availability"""
    username: str
    skills: List[str]
    expertise_areas: List[str]
    availability_score: float  # 0.0 to 1.0
    review_load: int  # Current number of pending reviews
    avg_review_time_hours: float
    languages: List[str]


@dataclass
class WorkflowPattern:
    """Represents a discovered workflow pattern"""
    pattern_id: str
    event_sequence: List[EventType]
    success_rate: float
    avg_duration_minutes: float
    optimal_conditions: Dict[str, Any]
    frequency: int  # How often this pattern occurs


@dataclass
class OptimizationSuggestion:
    """Represents an intelligent optimization suggestion"""
    suggestion_id: str
    type: OptimizationType
    title: str
    description: str
    expected_improvement: str  # e.g., "20% faster", "30% fewer failures"
    confidence_score: float  # 0.0 to 1.0
    implementation_effort: str  # "low", "medium", "high"
    data_points: int  # Number of data points supporting this suggestion


class WorkflowAnalyzer:
    """Analyzes workflow execution patterns and performance"""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._init_database()

        # In-memory analytics
        self.execution_history = deque(maxlen=1000)  # Keep last 1000 executions
        self.pattern_cache = {}

    def _init_database(self):
        """Initialize analytics database schema"""
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_executions (
                id TEXT PRIMARY KEY,
                workflow_id TEXT,
                status TEXT,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                duration_minutes REAL,
                trigger_event_type TEXT,
                trigger_source TEXT,
                action_count INTEGER,
                failed_actions INTEGER,
                metadata TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS team_performance (
                username TEXT,
                date DATE,
                reviews_completed INTEGER,
                avg_review_time_hours REAL,
                code_areas TEXT,
                PRIMARY KEY (username, date)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS optimization_suggestions (
                suggestion_id TEXT PRIMARY KEY,
                type TEXT,
                title TEXT,
                description TEXT,
                confidence_score REAL,
                created_at TIMESTAMP,
                applied BOOLEAN DEFAULT FALSE
            )
        """)

        self.conn.commit()

    async def record_execution(self, execution: WorkflowExecution) -> None:
        """Record a workflow execution for analysis"""
        cursor = self.conn.cursor()

        duration = None
        if execution.completed_at and execution.started_at:
            duration = (execution.completed_at - execution.started_at).total_seconds() / 60

        action_count = len(execution.action_results) if execution.action_results else 0
        failed_actions = sum(1 for result in (execution.action_results or {}).values()
                           if isinstance(result, dict) and result.get('error'))

        cursor.execute("""
            INSERT OR REPLACE INTO workflow_executions
            (id, workflow_id, status, started_at, completed_at, duration_minutes,
             trigger_event_type, trigger_source, action_count, failed_actions, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            execution.id,
            execution.workflow_id,
            execution.status.value,
            execution.started_at,
            execution.completed_at,
            duration,
            execution.trigger_event.type.value,
            execution.trigger_event.source,
            action_count,
            failed_actions,
            json.dumps(execution.trigger_event.payload)
        ))

        self.conn.commit()

        # Add to in-memory cache for real-time analysis
        self.execution_history.append(execution)

    async def analyze_workflow_patterns(self, workflow_id: str) -> List[WorkflowPattern]:
        """Analyze patterns for a specific workflow"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT * FROM workflow_executions
            WHERE workflow_id = ?
            ORDER BY started_at DESC
            LIMIT 100
        """, (workflow_id,))

        executions = cursor.fetchall()
        patterns = []

        if len(executions) < 5:  # Need minimum data points
            return patterns

        # Calculate success rate
        successful = sum(1 for exec in executions if exec[2] == 'completed')
        success_rate = successful / len(executions)

        # Calculate average duration
        durations = [exec[5] for exec in executions if exec[5] is not None]
        avg_duration = np.mean(durations) if durations else 0

        # Analyze timing patterns
        execution_hours = []
        for exec in executions:
            if exec[3]:  # started_at
                hour = datetime.fromisoformat(exec[3]).hour
                execution_hours.append(hour)

        optimal_hours = self._find_optimal_hours(execution_hours, executions)

        pattern = WorkflowPattern(
            pattern_id=f"pattern_{workflow_id}_{datetime.now().strftime('%Y%m%d')}",
            event_sequence=[EventType(executions[0][6])],  # Simplified for demo
            success_rate=success_rate,
            avg_duration_minutes=avg_duration,
            optimal_conditions={
                "preferred_hours": optimal_hours,
                "min_success_rate": success_rate
            },
            frequency=len(executions)
        )

        patterns.append(pattern)
        return patterns

    def _find_optimal_hours(self, execution_hours: List[int], executions: List) -> List[int]:
        """Find hours with highest success rates"""
        if not execution_hours:
            return []

        hour_stats = defaultdict(lambda: {'total': 0, 'successful': 0})

        for i, hour in enumerate(execution_hours):
            hour_stats[hour]['total'] += 1
            if i < len(executions) and executions[i][2] == 'completed':
                hour_stats[hour]['successful'] += 1

        # Find hours with >80% success rate
        optimal_hours = []
        for hour, stats in hour_stats.items():
            if stats['total'] >= 3:  # Minimum executions for statistical relevance
                success_rate = stats['successful'] / stats['total']
                if success_rate >= 0.8:
                    optimal_hours.append(hour)

        return sorted(optimal_hours)

    async def generate_optimization_suggestions(self) -> List[OptimizationSuggestion]:
        """Generate intelligent optimization suggestions based on analysis"""
        suggestions = []

        # Analyze recent failures
        recent_failures = await self._analyze_recent_failures()
        suggestions.extend(recent_failures)

        # Analyze timing optimization opportunities
        timing_suggestions = await self._analyze_timing_optimization()
        suggestions.extend(timing_suggestions)

        # Analyze resource optimization
        resource_suggestions = await self._analyze_resource_optimization()
        suggestions.extend(resource_suggestions)

        return suggestions

    async def _analyze_recent_failures(self) -> List[OptimizationSuggestion]:
        """Analyze recent failures and suggest improvements"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT workflow_id, COUNT(*) as failure_count
            FROM workflow_executions
            WHERE status = 'failed'
            AND started_at > datetime('now', '-7 days')
            GROUP BY workflow_id
            HAVING failure_count > 2
        """)

        results = cursor.fetchall()
        suggestions = []

        for workflow_id, failure_count in results:
            # Calculate failure rate
            cursor.execute("""
                SELECT COUNT(*) FROM workflow_executions
                WHERE workflow_id = ?
                AND started_at > datetime('now', '-7 days')
            """, (workflow_id,))

            total_count = cursor.fetchone()[0]
            failure_rate = failure_count / total_count if total_count > 0 else 0

            if failure_rate > 0.2:  # More than 20% failure rate
                suggestion = OptimizationSuggestion(
                    suggestion_id=f"failure_analysis_{workflow_id}",
                    type=OptimizationType.RESOURCE,
                    title=f"High failure rate in {workflow_id}",
                    description=f"Workflow has {failure_rate:.1%} failure rate in the last 7 days. "
                               f"Consider adding retry logic, improving error handling, or "
                               f"adjusting resource allocation.",
                    expected_improvement=f"Could reduce failures by 50%",
                    confidence_score=min(0.9, failure_count / 10),  # Higher confidence with more data
                    implementation_effort="medium",
                    data_points=failure_count
                )
                suggestions.append(suggestion)

        return suggestions

    async def _analyze_timing_optimization(self) -> List[OptimizationSuggestion]:
        """Analyze timing patterns and suggest optimal execution windows"""
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT
                strftime('%H', started_at) as hour,
                AVG(duration_minutes) as avg_duration,
                COUNT(*) as count,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful
            FROM workflow_executions
            WHERE started_at > datetime('now', '-30 days')
            AND duration_minutes IS NOT NULL
            GROUP BY strftime('%H', started_at)
            HAVING count > 5
        """)

        results = cursor.fetchall()
        suggestions = []

        if len(results) < 3:  # Need enough data points
            return suggestions

        # Find optimal execution window
        best_hour = min(results, key=lambda x: x[1])  # Fastest average duration
        worst_hour = max(results, key=lambda x: x[1])  # Slowest average duration

        improvement_potential = (worst_hour[1] - best_hour[1]) / worst_hour[1]

        if improvement_potential > 0.2:  # 20% or more improvement possible
            suggestion = OptimizationSuggestion(
                suggestion_id="timing_optimization",
                type=OptimizationType.TIMING,
                title="Optimize workflow execution timing",
                description=f"Workflows run fastest at {best_hour[0]}:00 "
                           f"({best_hour[1]:.1f} min avg) and slowest at {worst_hour[0]}:00 "
                           f"({worst_hour[1]:.1f} min avg). Consider scheduling important "
                           f"workflows during optimal hours.",
                expected_improvement=f"{improvement_potential:.1%} faster execution",
                confidence_score=min(0.8, sum(r[2] for r in results) / 100),
                implementation_effort="low",
                data_points=sum(r[2] for r in results)
            )
            suggestions.append(suggestion)

        return suggestions

    async def _analyze_resource_optimization(self) -> List[OptimizationSuggestion]:
        """Analyze resource usage patterns"""
        suggestions = []

        # Analyze concurrent execution patterns
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                DATE(started_at) as date,
                COUNT(*) as daily_executions,
                AVG(duration_minutes) as avg_duration
            FROM workflow_executions
            WHERE started_at > datetime('now', '-30 days')
            GROUP BY DATE(started_at)
            ORDER BY daily_executions DESC
        """)

        results = cursor.fetchall()

        if results:
            high_volume_days = [r for r in results if r[1] > np.percentile([r[1] for r in results], 90)]

            if high_volume_days:
                avg_duration_high = np.mean([r[2] for r in high_volume_days])
                avg_duration_normal = np.mean([r[2] for r in results if r not in high_volume_days])

                if avg_duration_high > avg_duration_normal * 1.3:  # 30% slower on high-volume days
                    suggestion = OptimizationSuggestion(
                        suggestion_id="resource_scaling",
                        type=OptimizationType.RESOURCE,
                        title="Scale resources during high-volume periods",
                        description=f"Workflows are {((avg_duration_high / avg_duration_normal - 1) * 100):.0f}% "
                                   f"slower on high-volume days. Consider implementing auto-scaling "
                                   f"or load balancing for workflow execution.",
                        expected_improvement="30% faster execution during peak times",
                        confidence_score=0.7,
                        implementation_effort="high",
                        data_points=len(high_volume_days)
                    )
                    suggestions.append(suggestion)

        return suggestions


class SmartReviewerAssignment:
    """Intelligent reviewer assignment based on expertise and workload"""

    def __init__(self):
        self.team_members: Dict[str, TeamMember] = {}
        self.assignment_history = deque(maxlen=500)

    def add_team_member(self, member: TeamMember) -> None:
        """Add or update a team member"""
        self.team_members[member.username] = member

    async def suggest_reviewers(self,
                              code_files: List[str],
                              programming_languages: List[str],
                              exclude: Optional[List[str]] = None,
                              count: int = 2) -> List[Tuple[str, float]]:
        """
        Suggest optimal reviewers based on expertise, availability, and workload.
        Returns list of (username, confidence_score) tuples.
        """
        exclude = exclude or []
        candidates = []

        for username, member in self.team_members.items():
            if username in exclude:
                continue

            # Calculate expertise score
            expertise_score = self._calculate_expertise_score(member, code_files, programming_languages)

            # Calculate availability score
            availability_score = self._calculate_availability_score(member)

            # Calculate workload balance score
            workload_score = self._calculate_workload_score(member)

            # Combined score
            combined_score = (expertise_score * 0.4 +
                            availability_score * 0.3 +
                            workload_score * 0.3)

            candidates.append((username, combined_score))

        # Sort by score and return top candidates
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[:count]

    def _calculate_expertise_score(self, member: TeamMember,
                                 code_files: List[str],
                                 languages: List[str]) -> float:
        """Calculate expertise relevance score"""
        score = 0.0

        # Language expertise
        for lang in languages:
            if lang.lower() in [l.lower() for l in member.languages]:
                score += 0.3

        # Expertise area matching
        for file_path in code_files:
            for area in member.expertise_areas:
                if area.lower() in file_path.lower():
                    score += 0.2

        # General skill matching
        for file_path in code_files:
            for skill in member.skills:
                if skill.lower() in file_path.lower():
                    score += 0.1

        return min(1.0, score)

    def _calculate_availability_score(self, member: TeamMember) -> float:
        """Calculate availability score based on current status"""
        return member.availability_score

    def _calculate_workload_score(self, member: TeamMember) -> float:
        """Calculate workload balance score (lower load = higher score)"""
        # Assuming average review load is 5
        if member.review_load <= 2:
            return 1.0
        elif member.review_load <= 5:
            return 0.7
        elif member.review_load <= 8:
            return 0.4
        else:
            return 0.1


class DevFlowIntelligence:
    """Main intelligence coordinator that combines all AI capabilities"""

    def __init__(self, db_path: str = ":memory:"):
        self.analyzer = WorkflowAnalyzer(db_path)
        self.reviewer_assignment = SmartReviewerAssignment()
        self.active_optimizations: Dict[str, OptimizationSuggestion] = {}

    async def analyze_and_optimize(self, execution: WorkflowExecution) -> Dict[str, Any]:
        """Main entry point for intelligence analysis"""
        # Record execution for learning
        await self.analyzer.record_execution(execution)

        # Generate optimization suggestions
        suggestions = await self.analyzer.generate_optimization_suggestions()

        # Analyze patterns for this workflow
        patterns = await self.analyzer.analyze_workflow_patterns(execution.workflow_id)

        return {
            "optimization_suggestions": [asdict(s) for s in suggestions],
            "discovered_patterns": [asdict(p) for p in patterns],
            "performance_metrics": {
                "success_rate": patterns[0].success_rate if patterns else None,
                "avg_duration": patterns[0].avg_duration_minutes if patterns else None
            }
        }

    async def get_smart_reviewer_suggestions(self, pr_info: Dict[str, Any]) -> List[str]:
        """Get intelligent reviewer suggestions for a PR"""
        suggestions = await self.reviewer_assignment.suggest_reviewers(
            code_files=pr_info.get('modified_files', []),
            programming_languages=pr_info.get('languages', []),
            exclude=[pr_info.get('author')],
            count=2
        )

        return [username for username, score in suggestions]


# Example usage and testing
async def demo_intelligence():
    """Demonstrate DevFlow intelligence capabilities"""

    # Initialize intelligence system
    intelligence = DevFlowIntelligence()

    # Set up sample team members
    team_members = [
        TeamMember(
            username="alice",
            skills=["frontend", "react", "typescript"],
            expertise_areas=["ui", "components", "styling"],
            availability_score=0.8,
            review_load=3,
            avg_review_time_hours=2.5,
            languages=["typescript", "javascript", "css"]
        ),
        TeamMember(
            username="bob",
            skills=["backend", "api", "database"],
            expertise_areas=["services", "models", "migrations"],
            availability_score=0.9,
            review_load=2,
            avg_review_time_hours=1.8,
            languages=["python", "sql", "go"]
        ),
        TeamMember(
            username="charlie",
            skills=["devops", "infrastructure", "monitoring"],
            expertise_areas=["deployment", "ci-cd", "docker"],
            availability_score=0.6,
            review_load=5,
            avg_review_time_hours=3.2,
            languages=["yaml", "bash", "terraform"]
        )
    ]

    for member in team_members:
        intelligence.reviewer_assignment.add_team_member(member)

    print("🧠 DevFlow Intelligence System Demo")
    print("=" * 50)

    # Simulate workflow execution data
    print("\n1. Recording sample workflow executions...")

    from devflow_engine_core import WorkflowEvent

    for i in range(20):
        # Create sample execution
        execution = WorkflowExecution(
            id=f"exec_{i}",
            workflow_id="pr-review-process",
            status=WorkflowStatus.COMPLETED if i % 5 != 0 else WorkflowStatus.FAILED,
            trigger_event=WorkflowEvent(
                id=f"event_{i}",
                type=EventType.PR_CREATED,
                source="github",
                payload={
                    "repository": "team/project",
                    "pr_number": 100 + i,
                    "author": f"dev_{i % 3}"
                },
                timestamp=datetime.utcnow() - timedelta(days=i)
            ),
            started_at=datetime.utcnow() - timedelta(days=i),
            completed_at=datetime.utcnow() - timedelta(days=i, minutes=-30 - (i * 2)),
            action_results={"action_1": {"status": "success"}}
        )

        await intelligence.analyzer.record_execution(execution)

    # Analyze and get suggestions
    print("\n2. Analyzing patterns and generating optimizations...")

    sample_execution = WorkflowExecution(
        id="sample_exec",
        workflow_id="pr-review-process",
        status=WorkflowStatus.COMPLETED,
        trigger_event=WorkflowEvent(
            id="sample_event",
            type=EventType.PR_CREATED,
            source="github",
            payload={},
            timestamp=datetime.utcnow()
        ),
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow()
    )

    analysis = await intelligence.analyze_and_optimize(sample_execution)

    print(f"\n📊 Analysis Results:")
    print(f"   Optimization suggestions: {len(analysis['optimization_suggestions'])}")
    print(f"   Discovered patterns: {len(analysis['discovered_patterns'])}")

    if analysis['optimization_suggestions']:
        print(f"\n💡 Top Optimization Suggestion:")
        top_suggestion = analysis['optimization_suggestions'][0]
        print(f"   {top_suggestion['title']}")
        print(f"   Expected improvement: {top_suggestion['expected_improvement']}")
        print(f"   Confidence: {top_suggestion['confidence_score']:.1%}")

    # Test smart reviewer assignment
    print("\n3. Testing smart reviewer assignment...")

    pr_info = {
        "modified_files": [
            "src/components/UserInterface.tsx",
            "src/api/user-service.py",
            "docker/deployment.yml"
        ],
        "languages": ["typescript", "python", "yaml"],
        "author": "new_developer"
    }

    suggested_reviewers = await intelligence.get_smart_reviewer_suggestions(pr_info)

    print(f"\n👥 Suggested reviewers for PR:")
    for reviewer in suggested_reviewers:
        member = intelligence.reviewer_assignment.team_members[reviewer]
        print(f"   {reviewer} - {', '.join(member.expertise_areas)} (load: {member.review_load})")

    print(f"\n✅ Intelligence system demo completed successfully!")

if __name__ == "__main__":
    asyncio.run(demo_intelligence())
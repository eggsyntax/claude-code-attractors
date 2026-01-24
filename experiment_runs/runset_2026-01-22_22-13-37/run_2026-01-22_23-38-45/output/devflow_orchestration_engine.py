"""
DevFlow: AI-Orchestrated Development Workflow Platform
Advanced orchestration engine for intelligent agent collaboration.

This builds upon our CodeMentor collaboration to create a comprehensive
platform for AI-driven software development workflows.

Key Innovation: Dynamic agent collaboration patterns learned from
our Alice-Bob partnership, scaled to support entire development teams.
"""

from typing import Dict, List, Any, Optional, Callable, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json
import time
import logging
from datetime import datetime, timedelta
from collections import defaultdict, deque
import heapq
from pathlib import Path

# Set up logging for the orchestration engine
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentPersonality(Enum):
    """Different AI agent personalities optimized for different work styles."""
    ANALYTICAL = "analytical"      # Deep analysis, like Alice
    INTEGRATIVE = "integrative"    # System integration, like Bob
    CREATIVE = "creative"          # Innovative solutions
    SYSTEMATIC = "systematic"      # Process-oriented
    COLLABORATIVE = "collaborative"# Team coordination

class WorkflowPhase(Enum):
    """Phases in software development lifecycle."""
    REQUIREMENTS = "requirements"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    INTEGRATION = "integration"
    DEPLOYMENT = "deployment"
    MAINTENANCE = "maintenance"

class CollaborationPattern(Enum):
    """Different patterns of agent collaboration."""
    SOLO = "solo"                  # Single agent
    PAIR = "pair"                  # Two agents collaborating (like Alice & Bob)
    SWARM = "swarm"                # Multiple agents on parallel tasks
    HIERARCHICAL = "hierarchical"  # Lead agent coordinating others
    PIPELINE = "pipeline"          # Sequential handoff between agents

@dataclass
class SkillProfile:
    """Detailed skill profile for an AI agent."""
    technical_skills: Dict[str, float] = field(default_factory=dict)  # skill -> proficiency (0.0-1.0)
    soft_skills: Dict[str, float] = field(default_factory=dict)       # communication, leadership, etc.
    domain_expertise: Dict[str, float] = field(default_factory=dict)  # frontend, backend, DevOps, etc.
    learning_rate: float = 0.1                                        # How quickly agent improves
    collaboration_preference: CollaborationPattern = CollaborationPattern.PAIR

@dataclass
class Agent:
    """Enhanced AI agent with personality, skills, and collaboration history."""
    id: str
    name: str
    personality: AgentPersonality
    skill_profile: SkillProfile
    current_load: float = 0.0
    max_concurrent_tasks: int = 3
    collaboration_history: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    preferred_partners: List[str] = field(default_factory=list)
    active_tasks: Set[str] = field(default_factory=set)

    def __post_init__(self):
        """Initialize default performance metrics."""
        if not self.performance_metrics:
            self.performance_metrics = {
                'task_completion_rate': 0.95,
                'code_quality_score': 0.85,
                'collaboration_effectiveness': 0.80,
                'learning_velocity': 0.75,
                'innovation_index': 0.70
            }

    def can_collaborate_with(self, other_agent_id: str) -> float:
        """Calculate collaboration compatibility score (0.0-1.0)."""
        if other_agent_id in self.collaboration_history:
            history = self.collaboration_history[other_agent_id]
            return history.get('success_rate', 0.5)
        return 0.5  # Neutral compatibility for new partnerships

    def update_collaboration_history(self, other_agent_id: str, success: bool,
                                   task_type: str, duration: float) -> None:
        """Update collaboration history with new interaction."""
        if other_agent_id not in self.collaboration_history:
            self.collaboration_history[other_agent_id] = {
                'total_collaborations': 0,
                'successful_collaborations': 0,
                'success_rate': 0.0,
                'avg_task_duration': 0.0,
                'task_types': defaultdict(int)
            }

        history = self.collaboration_history[other_agent_id]
        history['total_collaborations'] += 1
        if success:
            history['successful_collaborations'] += 1

        history['success_rate'] = history['successful_collaborations'] / history['total_collaborations']
        history['avg_task_duration'] = (history['avg_task_duration'] + duration) / 2
        history['task_types'][task_type] += 1

@dataclass
class WorkflowTask:
    """Enhanced task with workflow context and intelligent routing."""
    id: str
    title: str
    description: str
    phase: WorkflowPhase
    priority: int = 5  # 1 (highest) to 10 (lowest)
    estimated_effort: float = 1.0  # Story points or complexity
    required_skills: List[str] = field(default_factory=list)
    preferred_collaboration: CollaborationPattern = CollaborationPattern.SOLO
    dependencies: Set[str] = field(default_factory=set)
    context: Dict[str, Any] = field(default_factory=dict)

    # Execution tracking
    assigned_agents: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, in_progress, blocked, completed, failed
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Quality metrics
    quality_score: Optional[float] = None
    review_feedback: List[str] = field(default_factory=list)
    iteration_count: int = 0

class DevFlowIntelligentOrchestrator:
    """
    Advanced orchestration engine that learns from our Alice-Bob collaboration
    patterns and scales them to entire development workflows.

    Key Features:
    - Dynamic agent pairing based on compatibility and skills
    - Workflow-aware task routing and prioritization
    - Learning from collaboration patterns for optimization
    - Real-time load balancing and bottleneck detection
    - Quality gates and continuous improvement feedback loops
    """

    def __init__(self, learning_enabled: bool = True):
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, WorkflowTask] = {}
        self.active_collaborations: Dict[str, List[str]] = {}
        self.workflow_state: Dict[WorkflowPhase, List[str]] = defaultdict(list)
        self.learning_enabled = learning_enabled

        # Intelligence systems
        self.task_queue = []  # Priority queue for task scheduling
        self.collaboration_patterns = {}  # Learned patterns from successful collaborations
        self.performance_history = deque(maxlen=1000)  # Rolling performance metrics
        self.bottleneck_detector = BottleneckDetector()
        self.quality_analyzer = QualityAnalyzer()

        # Real-time metrics
        self.metrics = {
            'tasks_completed': 0,
            'avg_task_duration': 0.0,
            'collaboration_success_rate': 0.95,
            'throughput_per_hour': 0.0,
            'quality_score': 0.85
        }

    async def initialize_with_alice_bob_patterns(self):
        """Initialize the system with learned patterns from Alice-Bob collaboration."""
        # Register Alice and Bob as foundation agents
        alice = Agent(
            id="alice",
            name="Alice (Analysis & Architecture)",
            personality=AgentPersonality.ANALYTICAL,
            skill_profile=SkillProfile(
                technical_skills={
                    "code_analysis": 0.95,
                    "architecture_design": 0.90,
                    "pattern_recognition": 0.92,
                    "quality_assessment": 0.88
                },
                domain_expertise={
                    "backend_systems": 0.85,
                    "data_structures": 0.90,
                    "performance_optimization": 0.87
                },
                collaboration_preference=CollaborationPattern.PAIR
            )
        )

        bob = Agent(
            id="bob",
            name="Bob (Integration & Experience)",
            personality=AgentPersonality.INTEGRATIVE,
            skill_profile=SkillProfile(
                technical_skills={
                    "system_integration": 0.92,
                    "user_experience": 0.89,
                    "api_design": 0.86,
                    "testing_strategies": 0.85
                },
                domain_expertise={
                    "frontend_systems": 0.88,
                    "user_interfaces": 0.91,
                    "workflow_design": 0.87
                },
                collaboration_preference=CollaborationPattern.PAIR
            )
        )

        # Record their successful collaboration history
        alice.update_collaboration_history("bob", True, "architecture_design", 25.0)
        alice.update_collaboration_history("bob", True, "code_review", 15.0)
        alice.update_collaboration_history("bob", True, "integration_testing", 30.0)

        bob.update_collaboration_history("alice", True, "architecture_design", 25.0)
        bob.update_collaboration_history("alice", True, "code_review", 15.0)
        bob.update_collaboration_history("alice", True, "integration_testing", 30.0)

        # Mark them as preferred partners
        alice.preferred_partners.append("bob")
        bob.preferred_partners.append("alice")

        await self.register_agent(alice)
        await self.register_agent(bob)

        # Store successful collaboration patterns
        self.collaboration_patterns["analytical_integrative"] = {
            "agents": ["alice", "bob"],
            "success_rate": 0.96,
            "avg_quality": 0.92,
            "best_for_tasks": ["architecture_design", "code_review", "system_integration"]
        }

        logger.info("🤝 Initialized DevFlow with Alice-Bob collaboration patterns")

    async def register_agent(self, agent: Agent):
        """Register a new agent with the orchestrator."""
        self.agents[agent.id] = agent
        logger.info(f"✅ Registered {agent.name} ({agent.personality.value})")

    async def add_workflow_task(self, task: WorkflowTask):
        """Add a new task to the workflow with intelligent routing."""
        self.tasks[task.id] = task
        self.workflow_state[task.phase].append(task.id)

        # Add to priority queue for scheduling
        priority_score = self._calculate_task_priority(task)
        heapq.heappush(self.task_queue, (priority_score, task.created_at.timestamp(), task.id))

        logger.info(f"📋 Added task '{task.title}' to {task.phase.value} phase")

        # Try immediate assignment if agents are available
        await self._attempt_task_assignment()

    async def _attempt_task_assignment(self):
        """Intelligent task assignment using learned collaboration patterns."""
        if not self.task_queue:
            return

        # Get highest priority pending task
        while self.task_queue:
            _, _, task_id = heapq.heappop(self.task_queue)

            if task_id not in self.tasks or self.tasks[task_id].status != "pending":
                continue

            task = self.tasks[task_id]

            # Check if dependencies are satisfied
            if not self._dependencies_satisfied(task):
                # Put it back in queue with lower priority
                heapq.heappush(self.task_queue, (10, time.time(), task_id))
                continue

            # Find optimal agent assignment
            assignment = await self._find_optimal_assignment(task)

            if assignment:
                await self._assign_task(task, assignment)
                break
            else:
                # No suitable agents available, put back in queue
                heapq.heappush(self.task_queue, (task.priority, time.time(), task_id))
                break

    async def _find_optimal_assignment(self, task: WorkflowTask) -> Optional[List[str]]:
        """Find the optimal agent(s) for a task using AI-driven matching."""
        available_agents = [a for a in self.agents.values()
                          if len(a.active_tasks) < a.max_concurrent_tasks]

        if not available_agents:
            return None

        # Score all possible assignments
        best_assignment = None
        best_score = -1.0

        if task.preferred_collaboration == CollaborationPattern.SOLO:
            # Single agent assignment
            for agent in available_agents:
                score = self._calculate_agent_task_fit(agent, task)
                if score > best_score:
                    best_score = score
                    best_assignment = [agent.id]

        elif task.preferred_collaboration == CollaborationPattern.PAIR:
            # Pair assignment (like Alice & Bob)
            for i, agent1 in enumerate(available_agents):
                for agent2 in available_agents[i+1:]:
                    score = self._calculate_pair_task_fit(agent1, agent2, task)
                    if score > best_score:
                        best_score = score
                        best_assignment = [agent1.id, agent2.id]

        return best_assignment if best_score > 0.6 else None  # Quality threshold

    def _calculate_agent_task_fit(self, agent: Agent, task: WorkflowTask) -> float:
        """Calculate how well an agent fits a specific task."""
        score = 0.0

        # Skill matching
        for skill in task.required_skills:
            skill_level = agent.skill_profile.technical_skills.get(skill, 0.0)
            score += skill_level * 0.4

        # Phase expertise
        phase_skill = f"{task.phase.value}_expertise"
        if phase_skill in agent.skill_profile.domain_expertise:
            score += agent.skill_profile.domain_expertise[phase_skill] * 0.3

        # Load balancing
        load_penalty = agent.current_load * 0.2
        score -= load_penalty

        # Performance history
        score += agent.performance_metrics.get('task_completion_rate', 0.8) * 0.1

        return min(1.0, score)

    def _calculate_pair_task_fit(self, agent1: Agent, agent2: Agent, task: WorkflowTask) -> float:
        """Calculate how well a pair of agents fits a task."""
        # Individual fit scores
        fit1 = self._calculate_agent_task_fit(agent1, task)
        fit2 = self._calculate_agent_task_fit(agent2, task)
        base_score = (fit1 + fit2) / 2

        # Collaboration compatibility bonus
        compatibility = agent1.can_collaborate_with(agent2.id)
        collaboration_bonus = compatibility * 0.3

        # Complementary skills bonus
        complementary_bonus = self._calculate_skill_complementarity(agent1, agent2, task) * 0.2

        return base_score + collaboration_bonus + complementary_bonus

    def _calculate_skill_complementarity(self, agent1: Agent, agent2: Agent,
                                       task: WorkflowTask) -> float:
        """Calculate how well two agents' skills complement each other."""
        complementarity = 0.0

        for skill in task.required_skills:
            skill1 = agent1.skill_profile.technical_skills.get(skill, 0.0)
            skill2 = agent2.skill_profile.technical_skills.get(skill, 0.0)

            # Reward having at least one strong skill holder
            max_skill = max(skill1, skill2)
            # Reward balance (both have some competency)
            balance = 1.0 - abs(skill1 - skill2)

            complementarity += (max_skill * 0.7 + balance * 0.3) / len(task.required_skills)

        return complementarity

    async def _assign_task(self, task: WorkflowTask, agent_ids: List[str]):
        """Assign task to agents and begin execution."""
        task.assigned_agents = agent_ids
        task.status = "in_progress"
        task.started_at = datetime.now()

        # Update agent states
        for agent_id in agent_ids:
            agent = self.agents[agent_id]
            agent.active_tasks.add(task.id)
            agent.current_load += task.estimated_effort / len(agent_ids)

        self.active_collaborations[task.id] = agent_ids

        agent_names = [self.agents[aid].name for aid in agent_ids]
        logger.info(f"🎯 Assigned '{task.title}' to: {', '.join(agent_names)}")

        # Start task execution
        await self._execute_task(task)

    async def _execute_task(self, task: WorkflowTask):
        """Execute a task with the assigned agents."""
        if len(task.assigned_agents) == 1:
            await self._execute_solo_task(task)
        else:
            await self._execute_collaborative_task(task)

    async def _execute_solo_task(self, task: WorkflowTask):
        """Execute a task with a single agent."""
        agent = self.agents[task.assigned_agents[0]]
        logger.info(f"🚀 {agent.name} starting '{task.title}'")

        # Simulate execution time based on complexity and agent skill
        skill_multiplier = self._get_agent_skill_for_task(agent, task)
        execution_time = task.estimated_effort * (2.0 - skill_multiplier) * 5  # 5-45 seconds
        execution_time = min(execution_time, 30)  # Cap at 30 seconds for demo

        await asyncio.sleep(execution_time)

        # Simulate success based on agent performance
        success_probability = agent.performance_metrics['task_completion_rate']
        success = time.time() % 1.0 < success_probability  # Simple simulation

        await self._complete_task(task, success)

    async def _execute_collaborative_task(self, task: WorkflowTask):
        """Execute a collaborative task (like Alice-Bob partnership)."""
        agents = [self.agents[aid] for aid in task.assigned_agents]
        agent_names = [a.name for a in agents]

        logger.info(f"🤝 Collaborative execution: {' + '.join(agent_names)}")

        # Simulate collaboration phases
        phases = [
            ("Planning & Design", 0.25),
            ("Parallel Development", 0.50),
            ("Integration & Review", 0.25)
        ]

        for phase_name, duration_ratio in phases:
            logger.info(f"   📊 {phase_name} phase")
            phase_time = task.estimated_effort * duration_ratio * 3
            await asyncio.sleep(min(phase_time, 10))  # Cap phase time

        # Collaboration success based on compatibility
        agent1, agent2 = agents[0], agents[1]
        compatibility = agent1.can_collaborate_with(agent2.id)
        success_probability = (agent1.performance_metrics['task_completion_rate'] +
                             agent2.performance_metrics['task_completion_rate']) / 2
        success_probability *= (0.7 + 0.3 * compatibility)  # Compatibility bonus

        success = time.time() % 1.0 < success_probability

        await self._complete_task(task, success)

    async def _complete_task(self, task: WorkflowTask, success: bool):
        """Complete a task and update system state."""
        task.completed_at = datetime.now()
        task.status = "completed" if success else "failed"

        if success:
            task.quality_score = 0.8 + (time.time() % 0.4)  # Random 0.8-1.2
            logger.info(f"✅ Task completed: '{task.title}' (Quality: {task.quality_score:.2f})")
            self.metrics['tasks_completed'] += 1
        else:
            logger.info(f"❌ Task failed: '{task.title}'")

        # Update collaboration history
        if len(task.assigned_agents) > 1:
            duration = (task.completed_at - task.started_at).total_seconds()
            for i, agent_id1 in enumerate(task.assigned_agents):
                for agent_id2 in task.assigned_agents[i+1:]:
                    self.agents[agent_id1].update_collaboration_history(
                        agent_id2, success, task.phase.value, duration)
                    self.agents[agent_id2].update_collaboration_history(
                        agent_id1, success, task.phase.value, duration)

        # Free up agent resources
        for agent_id in task.assigned_agents:
            agent = self.agents[agent_id]
            agent.active_tasks.discard(task.id)
            agent.current_load -= task.estimated_effort / len(task.assigned_agents)
            agent.current_load = max(0, agent.current_load)  # Don't go negative

        if task.id in self.active_collaborations:
            del self.active_collaborations[task.id]

        # Store performance data for learning
        if self.learning_enabled:
            self._record_performance_data(task, success)

        # Try to assign more tasks
        await self._attempt_task_assignment()

    def get_comprehensive_status(self) -> Dict[str, Any]:
        """Get detailed system status and metrics."""
        # Agent status
        agent_status = {}
        for agent_id, agent in self.agents.items():
            recent_success_rate = sum(
                h.get('success_rate', 0.5) for h in agent.collaboration_history.values()
            ) / max(1, len(agent.collaboration_history))

            agent_status[agent_id] = {
                'name': agent.name,
                'personality': agent.personality.value,
                'load': f"{agent.current_load:.1f}",
                'active_tasks': len(agent.active_tasks),
                'collaboration_partners': len(agent.collaboration_history),
                'recent_success_rate': f"{recent_success_rate:.1%}"
            }

        # Workflow phase status
        phase_status = {}
        for phase in WorkflowPhase:
            phase_tasks = [tid for tid in self.workflow_state[phase] if tid in self.tasks]
            completed = sum(1 for tid in phase_tasks if self.tasks[tid].status == "completed")

            phase_status[phase.value] = {
                'total_tasks': len(phase_tasks),
                'completed': completed,
                'in_progress': sum(1 for tid in phase_tasks if self.tasks[tid].status == "in_progress"),
                'completion_rate': f"{completed/max(1, len(phase_tasks)):.1%}"
            }

        return {
            'agents': agent_status,
            'workflow_phases': phase_status,
            'active_collaborations': len(self.active_collaborations),
            'total_tasks': len(self.tasks),
            'overall_metrics': self.metrics,
            'collaboration_patterns_learned': len(self.collaboration_patterns)
        }

    # Helper methods
    def _calculate_task_priority(self, task: WorkflowTask) -> float:
        """Calculate task priority for scheduling."""
        base_priority = 10 - task.priority  # Lower number = higher priority

        # Phase-based priority adjustments
        phase_multipliers = {
            WorkflowPhase.REQUIREMENTS: 1.2,
            WorkflowPhase.DESIGN: 1.1,
            WorkflowPhase.IMPLEMENTATION: 1.0,
            WorkflowPhase.TESTING: 0.9,
            WorkflowPhase.INTEGRATION: 0.8,
            WorkflowPhase.DEPLOYMENT: 0.7,
            WorkflowPhase.MAINTENANCE: 0.6
        }

        return base_priority * phase_multipliers.get(task.phase, 1.0)

    def _dependencies_satisfied(self, task: WorkflowTask) -> bool:
        """Check if all task dependencies are completed."""
        return all(
            self.tasks.get(dep_id, {}).get('status') == 'completed'
            for dep_id in task.dependencies
        )

    def _get_agent_skill_for_task(self, agent: Agent, task: WorkflowTask) -> float:
        """Get agent's overall skill level for a task."""
        if not task.required_skills:
            return 0.8  # Default competency

        skill_scores = [
            agent.skill_profile.technical_skills.get(skill, 0.5)
            for skill in task.required_skills
        ]
        return sum(skill_scores) / len(skill_scores)

    def _record_performance_data(self, task: WorkflowTask, success: bool):
        """Record performance data for continuous learning."""
        data = {
            'task_id': task.id,
            'agents': task.assigned_agents,
            'phase': task.phase.value,
            'success': success,
            'duration': (task.completed_at - task.started_at).total_seconds(),
            'quality_score': task.quality_score,
            'collaboration_pattern': len(task.assigned_agents)
        }
        self.performance_history.append(data)


class BottleneckDetector:
    """Detects workflow bottlenecks and suggests optimizations."""
    pass  # Placeholder for advanced analytics

class QualityAnalyzer:
    """Analyzes code quality and provides improvement suggestions."""
    pass  # Placeholder for quality metrics

# Demonstration
async def demo_devflow_orchestration():
    """Demonstrate DevFlow's intelligent orchestration with Alice-Bob patterns."""
    print("🌟 DevFlow AI Orchestration Engine Demo")
    print("Building on Alice-Bob collaboration patterns...")
    print("=" * 60)

    # Initialize orchestrator
    orchestrator = DevFlowIntelligentOrchestrator()
    await orchestrator.initialize_with_alice_bob_patterns()

    # Add realistic development workflow tasks
    tasks = [
        WorkflowTask(
            id="req_1",
            title="Analyze user requirements and define system architecture",
            description="Deep analysis of user needs and architectural design",
            phase=WorkflowPhase.DESIGN,
            priority=2,
            estimated_effort=4.0,
            required_skills=["architecture_design", "code_analysis", "system_design"],
            preferred_collaboration=CollaborationPattern.PAIR
        ),
        WorkflowTask(
            id="impl_1",
            title="Implement core analysis engine",
            description="Build the foundational code analysis capabilities",
            phase=WorkflowPhase.IMPLEMENTATION,
            priority=3,
            estimated_effort=6.0,
            required_skills=["code_analysis", "pattern_recognition"],
            dependencies={"req_1"},
            preferred_collaboration=CollaborationPattern.SOLO
        ),
        WorkflowTask(
            id="impl_2",
            title="Create user interface and integration points",
            description="Build UI and API integration capabilities",
            phase=WorkflowPhase.IMPLEMENTATION,
            priority=3,
            estimated_effort=5.0,
            required_skills=["user_experience", "api_design", "system_integration"],
            dependencies={"req_1"},
            preferred_collaboration=CollaborationPattern.SOLO
        ),
        WorkflowTask(
            id="test_1",
            title="Comprehensive testing and quality assurance",
            description="Test all components and ensure quality standards",
            phase=WorkflowPhase.TESTING,
            priority=4,
            estimated_effort=4.0,
            required_skills=["testing_strategies", "quality_assessment"],
            dependencies={"impl_1", "impl_2"},
            preferred_collaboration=CollaborationPattern.PAIR
        ),
        WorkflowTask(
            id="integ_1",
            title="System integration and performance optimization",
            description="Integrate components and optimize performance",
            phase=WorkflowPhase.INTEGRATION,
            priority=5,
            estimated_effort=3.0,
            required_skills=["system_integration", "performance_optimization"],
            dependencies={"test_1"},
            preferred_collaboration=CollaborationPattern.PAIR
        )
    ]

    # Add tasks to orchestrator
    print("\n📋 Adding workflow tasks...")
    for task in tasks:
        await orchestrator.add_workflow_task(task)

    # Monitor execution
    print("\n🎯 Monitoring intelligent task execution...")
    print("-" * 40)

    for i in range(6):  # Monitor for 6 intervals
        await asyncio.sleep(8)  # Wait for task progress

        status = orchestrator.get_comprehensive_status()
        print(f"\n📊 Status Update #{i+1}")
        print(f"   Tasks completed: {status['overall_metrics']['tasks_completed']}")
        print(f"   Active collaborations: {status['active_collaborations']}")

        # Show collaboration patterns
        for agent_id, agent_info in status['agents'].items():
            if agent_info['active_tasks'] > 0:
                print(f"   🤖 {agent_info['name']}: {agent_info['active_tasks']} active tasks")

        # Show workflow progress
        for phase, info in status['workflow_phases'].items():
            if info['total_tasks'] > 0:
                print(f"   📈 {phase}: {info['completion_rate']} complete")

    print("\n🎉 DevFlow Orchestration Demo Complete!")

    # Final comprehensive report
    final_status = orchestrator.get_comprehensive_status()
    print(f"\n📈 Final Results:")
    print(f"   Total tasks completed: {final_status['overall_metrics']['tasks_completed']}")
    print(f"   Collaboration patterns learned: {final_status['collaboration_patterns_learned']}")

    print(f"\n🤝 Agent Collaboration Effectiveness:")
    for agent_id, info in final_status['agents'].items():
        print(f"   {info['name']}: {info['recent_success_rate']} success rate")

if __name__ == "__main__":
    asyncio.run(demo_devflow_orchestration())
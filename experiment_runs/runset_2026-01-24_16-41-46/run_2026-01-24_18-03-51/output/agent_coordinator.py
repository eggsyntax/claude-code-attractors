"""
Agent Coordinator - Extended by Bob
Part of the Multi-Agent Development Framework

This module provides coordination and orchestration capabilities for multiple AI agents
working collaboratively on development tasks.
"""

from typing import Dict, List, Optional, Callable, Any
import json
import time
from dataclasses import dataclass, asdict
from agent_protocol import AgentProtocol, Agent, Task, TaskStatus, AgentSkill, Message
import uuid

@dataclass
class CollaborationSession:
    """Represents an active collaboration session between agents."""
    session_id: str
    participants: List[str]
    active_tasks: List[str]
    start_time: float
    session_data: Dict[str, Any]

class AgentCoordinator:
    """Orchestrates collaboration between multiple AI agents."""

    def __init__(self, protocol: AgentProtocol):
        self.protocol = protocol
        self.sessions: Dict[str, CollaborationSession] = {}
        self.task_callbacks: Dict[str, Callable] = {}

    def start_collaboration_session(self, participant_ids: List[str], session_name: str = None) -> str:
        """Start a new collaboration session between specified agents."""
        session_id = str(uuid.uuid4())

        # Validate that all participants are registered
        for agent_id in participant_ids:
            if agent_id not in self.protocol.agents:
                raise ValueError(f"Agent {agent_id} not registered in protocol")

        session = CollaborationSession(
            session_id=session_id,
            participants=participant_ids,
            active_tasks=[],
            start_time=time.time(),
            session_data={
                "name": session_name or f"Session-{session_id[:8]}",
                "created_by": "AgentCoordinator",
                "messages": []
            }
        )

        self.sessions[session_id] = session

        # Broadcast session start message
        self._broadcast_session_message(session_id, "session_started", {
            "participants": participant_ids,
            "session_name": session.session_data["name"]
        })

        return session_id

    def propose_collaborative_task(self, session_id: str, proposer_id: str,
                                 task_title: str, task_description: str,
                                 subtasks: List[Dict[str, Any]]) -> List[str]:
        """
        Propose a complex task that requires collaboration between agents.
        Returns list of created task IDs.
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        created_task_ids = []

        # Create subtasks
        for i, subtask_info in enumerate(subtasks):
            task_id = str(uuid.uuid4())

            task = Task(
                task_id=task_id,
                title=f"{task_title} - {subtask_info['title']}",
                description=subtask_info['description'],
                required_skills=[AgentSkill(skill) for skill in subtask_info['required_skills']],
                status=TaskStatus.PENDING,
                dependencies=subtask_info.get('dependencies', [])
            )

            # Broadcast the task
            self.protocol.broadcast_task(task, proposer_id)
            session.active_tasks.append(task_id)
            created_task_ids.append(task_id)

        # Send collaboration proposal message
        self._broadcast_session_message(session_id, "collaborative_task_proposed", {
            "proposer": proposer_id,
            "main_task": task_title,
            "subtasks": created_task_ids,
            "description": task_description
        })

        return created_task_ids

    def auto_assign_tasks(self, session_id: str) -> Dict[str, List[str]]:
        """
        Automatically assign tasks to agents based on skills and availability.
        Returns mapping of agent_id -> [task_ids]
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        session = self.sessions[session_id]
        assignments = {}

        for agent_id in session.participants:
            agent = self.protocol.agents[agent_id]
            available_tasks = self.protocol.get_available_tasks(agent_id)

            # Filter to session tasks only
            session_tasks = [task for task in available_tasks
                           if task.task_id in session.active_tasks]

            agent_assignments = []
            for task in session_tasks:
                if self.protocol.claim_task(task.task_id, agent_id):
                    agent_assignments.append(task.task_id)

            if agent_assignments:
                assignments[agent_id] = agent_assignments

        # Broadcast assignment results
        self._broadcast_session_message(session_id, "tasks_auto_assigned", {
            "assignments": assignments
        })

        return assignments

    def get_collaboration_status(self, session_id: str) -> Dict[str, Any]:
        """Get detailed status of a collaboration session."""
        if session_id not in self.sessions:
            return {"error": "Session not found"}

        session = self.sessions[session_id]

        # Gather task status
        task_statuses = {}
        for task_id in session.active_tasks:
            if task_id in self.protocol.tasks:
                task = self.protocol.tasks[task_id]
                task_statuses[task_id] = {
                    "title": task.title,
                    "status": task.status.value,
                    "assigned_agent": task.assigned_agent,
                    "required_skills": [skill.value for skill in task.required_skills]
                }

        # Gather agent status
        agent_statuses = {}
        for agent_id in session.participants:
            agent = self.protocol.agents[agent_id]
            active_session_tasks = [tid for tid in agent.current_tasks
                                  if tid in session.active_tasks]
            agent_statuses[agent_id] = {
                "name": agent.name,
                "status": agent.status,
                "skills": [skill.value for skill in agent.skills],
                "active_tasks_in_session": active_session_tasks
            }

        return {
            "session_id": session_id,
            "session_name": session.session_data["name"],
            "participants": session.participants,
            "duration": time.time() - session.start_time,
            "task_statuses": task_statuses,
            "agent_statuses": agent_statuses,
            "messages_count": len(session.session_data.get("messages", []))
        }

    def _broadcast_session_message(self, session_id: str, message_type: str, content: Dict[str, Any]):
        """Internal method to broadcast messages within a session."""
        session = self.sessions[session_id]

        message = Message(
            message_id=str(uuid.uuid4()),
            sender_id="coordinator",
            recipient_id=None,  # Broadcast to all session participants
            message_type=message_type,
            content={
                "session_id": session_id,
                **content
            }
        )

        self.protocol.messages.append(message)
        session.session_data["messages"].append(asdict(message))

# Demonstration: Alice and Bob Collaboration
def demonstrate_alice_bob_collaboration():
    """
    Live demonstration of Alice and Bob collaborating using the framework.
    This models our actual conversation!
    """
    print("🤖 Starting Alice & Bob Collaboration Demo")
    print("=" * 50)

    # Initialize protocol and coordinator
    protocol = AgentProtocol()
    coordinator = AgentCoordinator(protocol)

    # Register Alice and Bob with their actual skills
    alice = Agent(
        agent_id="alice",
        name="Alice",
        skills=[
            AgentSkill.PYTHON_DEVELOPMENT,
            AgentSkill.DOCUMENTATION,
            AgentSkill.CODE_REVIEW
        ]
    )

    bob = Agent(
        agent_id="bob",
        name="Bob",
        skills=[
            AgentSkill.PYTHON_DEVELOPMENT,
            AgentSkill.TESTING,
            AgentSkill.WEB_DEVELOPMENT
        ]
    )

    protocol.register_agent(alice)
    protocol.register_agent(bob)

    print(f"✅ Registered agents: Alice & Bob")

    # Start collaboration session
    session_id = coordinator.start_collaboration_session(
        ["alice", "bob"],
        "Multi-Agent Framework Development"
    )

    print(f"🚀 Started collaboration session: {session_id[:8]}")

    # Alice proposes the framework development task (what actually happened!)
    framework_subtasks = [
        {
            "title": "Core Protocol Implementation",
            "description": "Implement the basic agent communication protocol",
            "required_skills": ["python_dev", "documentation"]
        },
        {
            "title": "Agent Coordinator",
            "description": "Build the coordination layer for multi-agent tasks",
            "required_skills": ["python_dev", "testing"]
        },
        {
            "title": "Live Demo System",
            "description": "Create a demonstration of the working framework",
            "required_skills": ["python_dev", "web_dev"]
        },
        {
            "title": "Integration Testing",
            "description": "Test the complete framework with real scenarios",
            "required_skills": ["testing", "python_dev"]
        }
    ]

    task_ids = coordinator.propose_collaborative_task(
        session_id,
        "alice",
        "Multi-Agent Development Framework",
        "Build a framework that allows AI agents to collaborate on software development",
        framework_subtasks
    )

    print(f"📋 Alice proposed {len(task_ids)} collaborative tasks")

    # Auto-assign tasks based on skills
    assignments = coordinator.auto_assign_tasks(session_id)
    print(f"🎯 Task assignments: {assignments}")

    # Simulate some progress
    for agent_id, task_list in assignments.items():
        for task_id in task_list[:1]:  # Start first task for each agent
            protocol.update_task_status(task_id, TaskStatus.IN_PROGRESS, agent_id)

    # Show final status
    status = coordinator.get_collaboration_status(session_id)

    print("\n📊 Collaboration Status:")
    print(f"   Session: {status['session_name']}")
    print(f"   Duration: {status['duration']:.1f} seconds")
    print(f"   Active tasks: {len(status['task_statuses'])}")
    print(f"   Messages: {status['messages_count']}")

    print("\n👥 Agent Status:")
    for agent_id, agent_info in status['agent_statuses'].items():
        print(f"   {agent_info['name']}: {len(agent_info['active_tasks_in_session'])} active tasks")

    return protocol, coordinator, session_id

if __name__ == "__main__":
    demonstrate_alice_bob_collaboration()
"""
Multi-Agent Development Protocol
Created by Alice and Bob (Claude Code instances)

This module defines a simple protocol for AI agents to coordinate on development tasks.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from enum import Enum
import json
import uuid
from datetime import datetime

class TaskStatus(Enum):
    PENDING = "pending"
    CLAIMED = "claimed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"

class AgentSkill(Enum):
    PYTHON_DEVELOPMENT = "python_dev"
    WEB_DEVELOPMENT = "web_dev"
    DATA_ANALYSIS = "data_analysis"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    CODE_REVIEW = "code_review"

@dataclass
class Task:
    """Represents a development task that can be distributed among agents."""
    task_id: str
    title: str
    description: str
    required_skills: List[AgentSkill]
    status: TaskStatus
    assigned_agent: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    dependencies: List[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class Agent:
    """Represents an AI agent with specific capabilities."""
    agent_id: str
    name: str
    skills: List[AgentSkill]
    status: str = "available"
    current_tasks: List[str] = None

    def __post_init__(self):
        if self.current_tasks is None:
            self.current_tasks = []

@dataclass
class Message:
    """Communication message between agents."""
    message_id: str
    sender_id: str
    recipient_id: Optional[str]  # None for broadcast
    message_type: str
    content: Dict[str, Any]
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class AgentProtocol:
    """Handles communication and coordination between agents."""

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.tasks: Dict[str, Task] = {}
        self.messages: List[Message] = []

    def register_agent(self, agent: Agent) -> bool:
        """Register a new agent in the system."""
        self.agents[agent.agent_id] = agent
        return True

    def broadcast_task(self, task: Task, sender_id: str) -> str:
        """Broadcast a new task to all agents."""
        self.tasks[task.task_id] = task

        message = Message(
            message_id=str(uuid.uuid4()),
            sender_id=sender_id,
            recipient_id=None,  # Broadcast
            message_type="task_broadcast",
            content={"task": asdict(task)}
        )

        self.messages.append(message)
        return message.message_id

    def claim_task(self, task_id: str, agent_id: str) -> bool:
        """Attempt to claim a task for an agent."""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        if task.status != TaskStatus.PENDING:
            return False

        # Check if agent has required skills
        agent = self.agents.get(agent_id)
        if not agent:
            return False

        required_skills = set(task.required_skills)
        agent_skills = set(agent.skills)

        if not required_skills.issubset(agent_skills):
            return False

        # Claim the task
        task.status = TaskStatus.CLAIMED
        task.assigned_agent = agent_id
        task.updated_at = datetime.now()

        agent.current_tasks.append(task_id)

        return True

    def update_task_status(self, task_id: str, status: TaskStatus, agent_id: str) -> bool:
        """Update the status of a task."""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        if task.assigned_agent != agent_id:
            return False

        task.status = status
        task.updated_at = datetime.now()

        # Send status update message
        message = Message(
            message_id=str(uuid.uuid4()),
            sender_id=agent_id,
            recipient_id=None,  # Broadcast status updates
            message_type="task_status_update",
            content={
                "task_id": task_id,
                "status": status.value,
                "timestamp": datetime.now().isoformat()
            }
        )

        self.messages.append(message)
        return True

    def get_available_tasks(self, agent_id: str) -> List[Task]:
        """Get tasks that an agent can work on."""
        agent = self.agents.get(agent_id)
        if not agent:
            return []

        available_tasks = []
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                # Check skill compatibility
                required_skills = set(task.required_skills)
                agent_skills = set(agent.skills)

                if required_skills.issubset(agent_skills):
                    available_tasks.append(task)

        return available_tasks

# Example usage demonstration
def create_example_scenario():
    """Demonstrates the protocol with Alice and Bob scenario."""
    protocol = AgentProtocol()

    # Create Alice and Bob agents
    alice = Agent(
        agent_id="alice",
        name="Alice",
        skills=[AgentSkill.PYTHON_DEVELOPMENT, AgentSkill.DOCUMENTATION, AgentSkill.CODE_REVIEW]
    )

    bob = Agent(
        agent_id="bob",
        name="Bob",
        skills=[AgentSkill.PYTHON_DEVELOPMENT, AgentSkill.TESTING, AgentSkill.WEB_DEVELOPMENT]
    )

    # Register agents
    protocol.register_agent(alice)
    protocol.register_agent(bob)

    # Create a sample task
    task = Task(
        task_id=str(uuid.uuid4()),
        title="Implement Agent Coordinator",
        description="Build the core coordination component for the multi-agent framework",
        required_skills=[AgentSkill.PYTHON_DEVELOPMENT],
        status=TaskStatus.PENDING
    )

    # Alice broadcasts the task
    protocol.broadcast_task(task, "alice")

    # Bob checks available tasks and claims one
    available = protocol.get_available_tasks("bob")
    if available:
        protocol.claim_task(available[0].task_id, "bob")
        protocol.update_task_status(available[0].task_id, TaskStatus.IN_PROGRESS, "bob")

    return protocol

if __name__ == "__main__":
    # Demonstrate the protocol
    protocol = create_example_scenario()

    print("Multi-Agent Protocol Demo")
    print("=" * 40)
    print(f"Registered agents: {len(protocol.agents)}")
    print(f"Total tasks: {len(protocol.tasks)}")
    print(f"Messages exchanged: {len(protocol.messages)}")
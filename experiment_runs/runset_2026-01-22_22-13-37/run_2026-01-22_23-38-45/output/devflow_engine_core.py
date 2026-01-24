"""
DevFlow: Intelligent Developer Workflow Orchestration Engine
Core workflow engine implementation with event-driven architecture.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from uuid import uuid4

class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class EventType(Enum):
    GIT_PUSH = "git.push"
    PR_CREATED = "pr.created"
    PR_MERGED = "pr.merged"
    BUILD_STARTED = "build.started"
    BUILD_COMPLETED = "build.completed"
    DEPLOY_REQUESTED = "deploy.requested"
    ISSUE_CREATED = "issue.created"
    CUSTOM = "custom"

@dataclass
class WorkflowEvent:
    """Represents an event that can trigger workflow actions"""
    id: str
    type: EventType
    source: str  # e.g., 'github', 'jenkins', 'custom'
    payload: Dict[str, Any]
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class WorkflowAction:
    """Represents an action within a workflow"""
    id: str
    name: str
    type: str  # e.g., 'http_request', 'shell_command', 'notification'
    config: Dict[str, Any]
    dependencies: List[str]  # IDs of actions that must complete first
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class WorkflowDefinition:
    """Defines a complete workflow with triggers and actions"""
    id: str
    name: str
    description: str
    triggers: List[EventType]
    actions: List[WorkflowAction]
    conditions: Optional[Dict[str, Any]] = None  # Optional conditions for execution
    is_active: bool = True

@dataclass
class WorkflowExecution:
    """Represents a running instance of a workflow"""
    id: str
    workflow_id: str
    status: WorkflowStatus
    trigger_event: WorkflowEvent
    started_at: datetime
    completed_at: Optional[datetime] = None
    action_results: Dict[str, Any] = None
    error_message: Optional[str] = None

class DevFlowEngine:
    """
    Core workflow orchestration engine.

    Features:
    - Event-driven workflow execution
    - Dependency management between actions
    - Retry logic and error handling
    - Real-time status tracking
    - Plugin architecture for custom actions
    """

    def __init__(self):
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        self.action_plugins: Dict[str, Callable] = {}
        self.logger = logging.getLogger(__name__)

        # Register built-in action types
        self._register_builtin_actions()

    def register_workflow(self, workflow: WorkflowDefinition) -> None:
        """Register a workflow definition"""
        self.workflows[workflow.id] = workflow
        self.logger.info(f"Registered workflow: {workflow.name} ({workflow.id})")

    def register_action_plugin(self, action_type: str, handler: Callable) -> None:
        """Register a custom action handler"""
        self.action_plugins[action_type] = handler
        self.logger.info(f"Registered action plugin: {action_type}")

    async def emit_event(self, event: WorkflowEvent) -> List[str]:
        """
        Process an incoming event and trigger matching workflows.
        Returns list of execution IDs that were started.
        """
        execution_ids = []

        # Find workflows that should be triggered by this event
        for workflow in self.workflows.values():
            if not workflow.is_active:
                continue

            if event.type in workflow.triggers:
                # Check additional conditions if specified
                if workflow.conditions and not self._evaluate_conditions(workflow.conditions, event):
                    continue

                execution_id = await self._start_workflow_execution(workflow, event)
                execution_ids.append(execution_id)

        return execution_ids

    async def get_execution_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get the current status of a workflow execution"""
        return self.executions.get(execution_id)

    async def get_active_executions(self) -> List[WorkflowExecution]:
        """Get all currently active workflow executions"""
        return [
            execution for execution in self.executions.values()
            if execution.status in [WorkflowStatus.PENDING, WorkflowStatus.RUNNING]
        ]

    async def _start_workflow_execution(self, workflow: WorkflowDefinition, trigger_event: WorkflowEvent) -> str:
        """Start a new workflow execution"""
        execution_id = str(uuid4())
        execution = WorkflowExecution(
            id=execution_id,
            workflow_id=workflow.id,
            status=WorkflowStatus.PENDING,
            trigger_event=trigger_event,
            started_at=datetime.utcnow(),
            action_results={}
        )

        self.executions[execution_id] = execution
        self.logger.info(f"Started workflow execution: {workflow.name} ({execution_id})")

        # Execute workflow in background
        asyncio.create_task(self._execute_workflow(execution, workflow))

        return execution_id

    async def _execute_workflow(self, execution: WorkflowExecution, workflow: WorkflowDefinition) -> None:
        """Execute a workflow's actions with dependency management"""
        try:
            execution.status = WorkflowStatus.RUNNING
            completed_actions = set()

            while len(completed_actions) < len(workflow.actions):
                # Find actions that are ready to execute (all dependencies met)
                ready_actions = [
                    action for action in workflow.actions
                    if action.id not in completed_actions and
                    all(dep in completed_actions for dep in action.dependencies)
                ]

                if not ready_actions:
                    raise Exception("Circular dependency or no executable actions found")

                # Execute ready actions in parallel
                tasks = [
                    self._execute_action(action, execution)
                    for action in ready_actions
                ]

                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                for action, result in zip(ready_actions, results):
                    if isinstance(result, Exception):
                        raise result

                    execution.action_results[action.id] = result
                    completed_actions.add(action.id)

            # Mark execution as completed
            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            self.logger.info(f"Completed workflow execution: {execution.id}")

        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            self.logger.error(f"Workflow execution failed: {execution.id} - {e}")

    async def _execute_action(self, action: WorkflowAction, execution: WorkflowExecution) -> Any:
        """Execute a single workflow action with retry logic"""
        for attempt in range(action.max_retries + 1):
            try:
                if action.type not in self.action_plugins:
                    raise ValueError(f"Unknown action type: {action.type}")

                handler = self.action_plugins[action.type]

                # Execute with timeout
                result = await asyncio.wait_for(
                    handler(action, execution),
                    timeout=action.timeout_seconds
                )

                self.logger.info(f"Action completed: {action.name} ({action.id})")
                return result

            except Exception as e:
                if attempt < action.max_retries:
                    self.logger.warning(f"Action failed, retrying: {action.name} (attempt {attempt + 1})")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"Action failed permanently: {action.name} - {e}")
                    raise

    def _evaluate_conditions(self, conditions: Dict[str, Any], event: WorkflowEvent) -> bool:
        """Evaluate workflow conditions against an event"""
        # Simple condition evaluation - can be extended for complex logic
        for key, expected_value in conditions.items():
            if key in event.payload:
                if event.payload[key] != expected_value:
                    return False
            else:
                return False
        return True

    def _register_builtin_actions(self) -> None:
        """Register built-in action types"""

        async def http_request_action(action: WorkflowAction, execution: WorkflowExecution) -> Dict:
            """Built-in HTTP request action"""
            import aiohttp

            config = action.config
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=config.get('method', 'GET'),
                    url=config['url'],
                    json=config.get('json'),
                    headers=config.get('headers', {})
                ) as response:
                    return {
                        'status_code': response.status,
                        'response_text': await response.text(),
                        'headers': dict(response.headers)
                    }

        async def shell_command_action(action: WorkflowAction, execution: WorkflowExecution) -> Dict:
            """Built-in shell command action"""
            import subprocess

            config = action.config
            process = await asyncio.create_subprocess_shell(
                config['command'],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=config.get('working_directory')
            )

            stdout, stderr = await process.communicate()

            return {
                'exit_code': process.returncode,
                'stdout': stdout.decode(),
                'stderr': stderr.decode()
            }

        async def notification_action(action: WorkflowAction, execution: WorkflowExecution) -> Dict:
            """Built-in notification action"""
            config = action.config
            # In real implementation, this would send to Slack, email, etc.
            message = config.get('message', 'Workflow notification')
            self.logger.info(f"NOTIFICATION: {message}")
            return {'sent': True, 'message': message}

        # Register built-in actions
        self.register_action_plugin('http_request', http_request_action)
        self.register_action_plugin('shell_command', shell_command_action)
        self.register_action_plugin('notification', notification_action)


# Example usage and testing
async def demo_devflow_engine():
    """Demonstration of the DevFlow engine capabilities"""

    # Initialize engine
    engine = DevFlowEngine()

    # Define a sample workflow: PR Review Process
    pr_review_workflow = WorkflowDefinition(
        id="pr-review-process",
        name="Smart PR Review Process",
        description="Automated PR review workflow with intelligent reviewer assignment",
        triggers=[EventType.PR_CREATED],
        actions=[
            WorkflowAction(
                id="notify-team",
                name="Notify Team",
                type="notification",
                config={"message": "New PR created and ready for review"},
                dependencies=[]
            ),
            WorkflowAction(
                id="run-tests",
                name="Run Automated Tests",
                type="shell_command",
                config={"command": "echo 'Running tests...' && sleep 2 && echo 'Tests passed'"},
                dependencies=[]
            ),
            WorkflowAction(
                id="assign-reviewers",
                name="Assign Smart Reviewers",
                type="http_request",
                config={
                    "method": "POST",
                    "url": "https://api.github.com/repos/example/repo/pulls/123/requested_reviewers",
                    "json": {"reviewers": ["alice", "bob"]}
                },
                dependencies=["run-tests"]  # Only assign reviewers after tests pass
            )
        ]
    )

    # Register the workflow
    engine.register_workflow(pr_review_workflow)

    # Simulate a PR creation event
    pr_event = WorkflowEvent(
        id=str(uuid4()),
        type=EventType.PR_CREATED,
        source="github",
        payload={
            "repository": "example/repo",
            "pr_number": 123,
            "author": "developer1",
            "title": "Add new feature"
        },
        timestamp=datetime.utcnow()
    )

    # Trigger workflow
    print("🚀 Triggering PR Review Workflow...")
    execution_ids = await engine.emit_event(pr_event)

    print(f"✅ Started {len(execution_ids)} workflow execution(s)")

    # Monitor execution
    for execution_id in execution_ids:
        print(f"\n📊 Monitoring execution: {execution_id}")

        while True:
            execution = await engine.get_execution_status(execution_id)
            print(f"Status: {execution.status.value}")

            if execution.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED]:
                break

            await asyncio.sleep(1)

        if execution.status == WorkflowStatus.COMPLETED:
            print("🎉 Workflow completed successfully!")
            print("Action Results:")
            for action_id, result in execution.action_results.items():
                print(f"  {action_id}: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Workflow failed: {execution.error_message}")

if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_devflow_engine())
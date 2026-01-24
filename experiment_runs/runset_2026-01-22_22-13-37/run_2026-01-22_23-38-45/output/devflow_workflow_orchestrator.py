"""
DevFlow Advanced Workflow Orchestration Engine
Intelligent orchestration with AI-driven decision making and real-time adaptation
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from collections import defaultdict
import networkx as nx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowState(Enum):
    """Workflow execution states"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 5
    HIGH = 4
    NORMAL = 3
    LOW = 2
    DEFERRED = 1

@dataclass
class WorkflowContext:
    """Context information for workflow execution"""
    workflow_id: str
    project_id: str
    team_id: str
    environment: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    variables: Dict[str, Any] = None

    def __post_init__(self):
        if self.variables is None:
            self.variables = {}

@dataclass
class TaskDefinition:
    """Definition of a workflow task"""
    task_id: str
    name: str
    task_type: str
    config: Dict[str, Any]
    dependencies: List[str]
    priority: TaskPriority
    estimated_duration: Optional[timedelta]
    retry_policy: Optional[Dict[str, Any]]
    timeout: Optional[timedelta]
    conditions: Optional[Dict[str, Any]]

class IntelligentTaskAllocator:
    """AI-driven task allocation system"""

    def __init__(self):
        self.developer_profiles = {}
        self.workload_history = defaultdict(list)
        self.skill_matrix = defaultdict(dict)
        self.performance_metrics = defaultdict(dict)

    async def analyze_developer_capacity(self, developer_id: str) -> Dict[str, Any]:
        """Analyze current capacity and availability of developer"""
        current_workload = len(self.workload_history.get(developer_id, []))
        avg_completion_time = self._calculate_avg_completion_time(developer_id)
        skill_relevance = self._calculate_skill_relevance(developer_id)

        return {
            "developer_id": developer_id,
            "current_workload": current_workload,
            "capacity_score": max(0, 10 - current_workload),
            "avg_completion_time": avg_completion_time,
            "skill_relevance": skill_relevance,
            "availability_score": self._calculate_availability_score(developer_id)
        }

    async def allocate_task(self, task: TaskDefinition, available_developers: List[str]) -> str:
        """Intelligently allocate task to best-suited developer"""
        allocation_scores = {}

        for dev_id in available_developers:
            capacity = await self.analyze_developer_capacity(dev_id)

            # Multi-factor scoring algorithm
            score = (
                capacity["capacity_score"] * 0.3 +
                capacity["skill_relevance"] * 0.4 +
                capacity["availability_score"] * 0.2 +
                (10 - min(capacity["current_workload"], 10)) * 0.1
            )

            allocation_scores[dev_id] = score

        # Select developer with highest score
        best_developer = max(allocation_scores.items(), key=lambda x: x[1])
        logger.info(f"Allocated task {task.task_id} to developer {best_developer[0]} (score: {best_developer[1]:.2f})")

        return best_developer[0]

    def _calculate_avg_completion_time(self, developer_id: str) -> float:
        """Calculate average task completion time for developer"""
        history = self.workload_history.get(developer_id, [])
        if not history:
            return 2.0  # Default estimated hours

        total_time = sum(task.get("completion_time", 2.0) for task in history[-10:])
        return total_time / min(len(history), 10)

    def _calculate_skill_relevance(self, developer_id: str) -> float:
        """Calculate skill relevance score for developer"""
        skills = self.skill_matrix.get(developer_id, {})
        if not skills:
            return 5.0  # Neutral score

        # Simplified skill matching - in production, this would be more sophisticated
        return sum(skills.values()) / len(skills)

    def _calculate_availability_score(self, developer_id: str) -> float:
        """Calculate availability score based on timezone, calendar, etc."""
        # Simplified implementation - would integrate with calendar APIs
        current_hour = datetime.now().hour
        if 9 <= current_hour <= 17:  # Business hours
            return 8.0
        elif 17 < current_hour <= 20:  # Extended hours
            return 6.0
        else:  # Off hours
            return 3.0

class WorkflowOrchestrator:
    """Advanced workflow orchestration engine with AI capabilities"""

    def __init__(self):
        self.active_workflows: Dict[str, WorkflowContext] = {}
        self.task_registry: Dict[str, Callable] = {}
        self.workflow_graph = nx.DiGraph()
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        self.task_allocator = IntelligentTaskAllocator()
        self.execution_queue = asyncio.Queue()
        self.running = False

    async def start_engine(self):
        """Start the orchestration engine"""
        self.running = True
        logger.info("DevFlow Workflow Orchestrator started")

        # Start background task processing
        asyncio.create_task(self._process_execution_queue())
        asyncio.create_task(self._monitor_workflow_health())

    async def stop_engine(self):
        """Stop the orchestration engine"""
        self.running = False
        logger.info("DevFlow Workflow Orchestrator stopped")

    def register_task_handler(self, task_type: str, handler: Callable):
        """Register a handler for a specific task type"""
        self.task_registry[task_type] = handler
        logger.info(f"Registered handler for task type: {task_type}")

    def register_event_handler(self, event_type: str, handler: Callable):
        """Register an event handler"""
        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered event handler for: {event_type}")

    async def create_workflow(self, workflow_def: Dict[str, Any]) -> str:
        """Create a new workflow from definition"""
        workflow_id = str(uuid.uuid4())

        # Create workflow context
        context = WorkflowContext(
            workflow_id=workflow_id,
            project_id=workflow_def.get("project_id", ""),
            team_id=workflow_def.get("team_id", ""),
            environment=workflow_def.get("environment", "development"),
            metadata=workflow_def.get("metadata", {}),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            variables=workflow_def.get("variables", {})
        )

        self.active_workflows[workflow_id] = context

        # Build workflow graph from tasks
        await self._build_workflow_graph(workflow_id, workflow_def.get("tasks", []))

        logger.info(f"Created workflow: {workflow_id}")
        return workflow_id

    async def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a workflow with intelligent orchestration"""
        if workflow_id not in self.active_workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        context = self.active_workflows[workflow_id]
        logger.info(f"Starting workflow execution: {workflow_id}")

        try:
            # Analyze workflow and optimize execution plan
            execution_plan = await self._create_execution_plan(workflow_id)

            # Execute tasks according to optimized plan
            results = await self._execute_tasks_intelligently(workflow_id, execution_plan)

            # Update workflow state
            context.updated_at = datetime.now()

            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "results": results,
                "execution_time": (context.updated_at - context.created_at).total_seconds(),
                "optimization_insights": execution_plan.get("insights", {})
            }

        except Exception as e:
            logger.error(f"Workflow execution failed: {workflow_id}, error: {str(e)}")
            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "error": str(e),
                "execution_time": (datetime.now() - context.created_at).total_seconds()
            }

    async def _build_workflow_graph(self, workflow_id: str, tasks: List[Dict[str, Any]]):
        """Build execution graph from task definitions"""
        subgraph = nx.DiGraph()

        for task_def in tasks:
            task_obj = TaskDefinition(
                task_id=task_def["task_id"],
                name=task_def["name"],
                task_type=task_def["task_type"],
                config=task_def.get("config", {}),
                dependencies=task_def.get("dependencies", []),
                priority=TaskPriority(task_def.get("priority", 3)),
                estimated_duration=timedelta(hours=task_def.get("estimated_hours", 1)),
                retry_policy=task_def.get("retry_policy"),
                timeout=timedelta(hours=task_def.get("timeout_hours", 4)),
                conditions=task_def.get("conditions")
            )

            subgraph.add_node(task_obj.task_id, task=task_obj)

            # Add dependencies as edges
            for dep in task_obj.dependencies:
                subgraph.add_edge(dep, task_obj.task_id)

        # Store graph with workflow namespace
        self.workflow_graph = nx.union(self.workflow_graph, subgraph)

    async def _create_execution_plan(self, workflow_id: str) -> Dict[str, Any]:
        """Create optimized execution plan using AI insights"""
        context = self.active_workflows[workflow_id]

        # Get workflow subgraph
        workflow_nodes = [n for n in self.workflow_graph.nodes()
                         if self.workflow_graph.nodes[n].get("task")]

        # Topological sort for execution order
        execution_order = list(nx.topological_sort(self.workflow_graph.subgraph(workflow_nodes)))

        # Analyze for parallel execution opportunities
        parallel_groups = self._identify_parallel_execution_groups(workflow_nodes)

        # Resource optimization
        resource_allocation = await self._optimize_resource_allocation(workflow_nodes)

        # Risk analysis
        risk_assessment = self._analyze_execution_risks(workflow_nodes)

        plan = {
            "execution_order": execution_order,
            "parallel_groups": parallel_groups,
            "resource_allocation": resource_allocation,
            "risk_assessment": risk_assessment,
            "insights": {
                "estimated_total_time": self._estimate_total_execution_time(workflow_nodes),
                "critical_path": self._identify_critical_path(workflow_nodes),
                "optimization_opportunities": self._identify_optimizations(workflow_nodes)
            }
        }

        logger.info(f"Created execution plan for workflow {workflow_id}: {len(execution_order)} tasks")
        return plan

    async def _execute_tasks_intelligently(self, workflow_id: str, execution_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tasks with intelligent scheduling and resource management"""
        results = {}

        # Execute tasks in optimized order
        for group in execution_plan["parallel_groups"]:
            if len(group) == 1:
                # Single task execution
                task_id = group[0]
                result = await self._execute_single_task(workflow_id, task_id)
                results[task_id] = result
            else:
                # Parallel task execution
                parallel_results = await self._execute_parallel_tasks(workflow_id, group)
                results.update(parallel_results)

        return results

    async def _execute_single_task(self, workflow_id: str, task_id: str) -> Dict[str, Any]:
        """Execute a single task with comprehensive monitoring"""
        task_node = self.workflow_graph.nodes[task_id]
        task_def = task_node["task"]

        start_time = datetime.now()

        try:
            # Get task handler
            handler = self.task_registry.get(task_def.task_type)
            if not handler:
                raise ValueError(f"No handler registered for task type: {task_def.task_type}")

            # Allocate resources if needed
            if task_def.task_type in ["code_review", "development", "testing"]:
                allocated_dev = await self.task_allocator.allocate_task(
                    task_def,
                    ["dev1", "dev2", "dev3"]  # Would come from team configuration
                )
                task_def.config["assigned_developer"] = allocated_dev

            # Execute task with timeout
            result = await asyncio.wait_for(
                handler(task_def.config),
                timeout=task_def.timeout.total_seconds() if task_def.timeout else None
            )

            execution_time = (datetime.now() - start_time).total_seconds()

            # Emit success event
            await self._emit_event("task_completed", {
                "workflow_id": workflow_id,
                "task_id": task_id,
                "result": result,
                "execution_time": execution_time
            })

            return {
                "status": "success",
                "result": result,
                "execution_time": execution_time,
                "start_time": start_time.isoformat(),
                "end_time": datetime.now().isoformat()
            }

        except asyncio.TimeoutError:
            logger.error(f"Task {task_id} timed out")
            return {"status": "timeout", "execution_time": (datetime.now() - start_time).total_seconds()}
        except Exception as e:
            logger.error(f"Task {task_id} failed: {str(e)}")
            return {"status": "failed", "error": str(e), "execution_time": (datetime.now() - start_time).total_seconds()}

    async def _execute_parallel_tasks(self, workflow_id: str, task_group: List[str]) -> Dict[str, Dict[str, Any]]:
        """Execute multiple tasks in parallel"""
        logger.info(f"Executing {len(task_group)} tasks in parallel")

        # Create tasks for parallel execution
        parallel_tasks = [
            self._execute_single_task(workflow_id, task_id)
            for task_id in task_group
        ]

        # Execute all tasks concurrently
        results = await asyncio.gather(*parallel_tasks, return_exceptions=True)

        # Map results back to task IDs
        task_results = {}
        for i, task_id in enumerate(task_group):
            if isinstance(results[i], Exception):
                task_results[task_id] = {
                    "status": "failed",
                    "error": str(results[i])
                }
            else:
                task_results[task_id] = results[i]

        return task_results

    def _identify_parallel_execution_groups(self, workflow_nodes: List[str]) -> List[List[str]]:
        """Identify groups of tasks that can be executed in parallel"""
        groups = []
        processed = set()

        # Topological sort to respect dependencies
        topo_order = list(nx.topological_sort(self.workflow_graph.subgraph(workflow_nodes)))

        for node in topo_order:
            if node in processed:
                continue

            # Find all nodes that can run in parallel with this one
            parallel_group = [node]
            processed.add(node)

            # Check remaining nodes for parallel execution possibility
            for candidate in topo_order:
                if candidate in processed:
                    continue

                # Can execute in parallel if no dependency path exists
                if not (nx.has_path(self.workflow_graph, node, candidate) or
                       nx.has_path(self.workflow_graph, candidate, node)):
                    parallel_group.append(candidate)
                    processed.add(candidate)

            groups.append(parallel_group)

        return groups

    async def _optimize_resource_allocation(self, workflow_nodes: List[str]) -> Dict[str, Any]:
        """Optimize resource allocation across workflow tasks"""
        # Simplified resource optimization - would be more sophisticated in production
        resource_requirements = defaultdict(int)

        for node in workflow_nodes:
            task_def = self.workflow_graph.nodes[node]["task"]
            resource_requirements[task_def.task_type] += 1

        return {
            "resource_requirements": dict(resource_requirements),
            "recommended_parallelism": min(len(workflow_nodes), 4),
            "estimated_resource_usage": sum(resource_requirements.values()) * 0.7
        }

    def _analyze_execution_risks(self, workflow_nodes: List[str]) -> Dict[str, Any]:
        """Analyze potential risks in workflow execution"""
        risks = []

        for node in workflow_nodes:
            task_def = self.workflow_graph.nodes[node]["task"]

            # Identify high-risk tasks
            if task_def.priority == TaskPriority.CRITICAL:
                risks.append({
                    "task_id": node,
                    "risk_type": "critical_task",
                    "impact": "high",
                    "mitigation": "Add additional monitoring and retry logic"
                })

            if task_def.estimated_duration and task_def.estimated_duration > timedelta(hours=4):
                risks.append({
                    "task_id": node,
                    "risk_type": "long_running_task",
                    "impact": "medium",
                    "mitigation": "Consider task decomposition"
                })

        return {
            "identified_risks": risks,
            "overall_risk_score": min(len(risks) * 0.2, 1.0),
            "recommended_monitoring": len(risks) > 2
        }

    def _estimate_total_execution_time(self, workflow_nodes: List[str]) -> float:
        """Estimate total execution time considering parallelization"""
        # Simplified estimation - would use historical data in production
        total_sequential_time = sum(
            self.workflow_graph.nodes[node]["task"].estimated_duration.total_seconds() / 3600
            for node in workflow_nodes
            if self.workflow_graph.nodes[node]["task"].estimated_duration
        )

        # Account for parallelization (rough estimate)
        parallelization_factor = 0.6  # 40% time savings from parallelization
        return total_sequential_time * parallelization_factor

    def _identify_critical_path(self, workflow_nodes: List[str]) -> List[str]:
        """Identify the critical path in the workflow"""
        # Simplified critical path analysis
        return list(nx.dag_longest_path(self.workflow_graph.subgraph(workflow_nodes)))

    def _identify_optimizations(self, workflow_nodes: List[str]) -> List[Dict[str, Any]]:
        """Identify optimization opportunities"""
        optimizations = []

        # Check for dependency optimization opportunities
        for node in workflow_nodes:
            dependencies = list(self.workflow_graph.predecessors(node))
            if len(dependencies) > 3:
                optimizations.append({
                    "type": "dependency_reduction",
                    "task_id": node,
                    "suggestion": "Consider reducing task dependencies for better parallelization"
                })

        return optimizations

    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit workflow events to registered handlers"""
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                await handler(data)
            except Exception as e:
                logger.error(f"Event handler failed: {event_type}, error: {str(e)}")

    async def _process_execution_queue(self):
        """Background task to process execution queue"""
        while self.running:
            try:
                # Process queued executions
                await asyncio.sleep(1)  # Simplified - would use proper queue processing
            except Exception as e:
                logger.error(f"Execution queue processing error: {str(e)}")

    async def _monitor_workflow_health(self):
        """Monitor health of active workflows"""
        while self.running:
            try:
                # Health monitoring logic
                active_count = len(self.active_workflows)
                if active_count > 0:
                    logger.info(f"Monitoring {active_count} active workflows")
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"Workflow health monitoring error: {str(e)}")

# Example usage and demonstration
async def demo_devflow_orchestrator():
    """Demonstrate the advanced workflow orchestration capabilities"""

    # Initialize orchestrator
    orchestrator = WorkflowOrchestrator()
    await orchestrator.start_engine()

    # Register sample task handlers
    async def code_review_handler(config):
        developer = config.get("assigned_developer", "auto")
        await asyncio.sleep(1)  # Simulate work
        return {"status": "reviewed", "developer": developer, "findings": 2}

    async def testing_handler(config):
        test_type = config.get("test_type", "unit")
        await asyncio.sleep(0.5)  # Simulate work
        return {"status": "passed", "test_type": test_type, "coverage": 85}

    async def deployment_handler(config):
        environment = config.get("environment", "staging")
        await asyncio.sleep(2)  # Simulate work
        return {"status": "deployed", "environment": environment, "url": f"https://{environment}.example.com"}

    # Register handlers
    orchestrator.register_task_handler("code_review", code_review_handler)
    orchestrator.register_task_handler("testing", testing_handler)
    orchestrator.register_task_handler("deployment", deployment_handler)

    # Define a complex workflow
    workflow_definition = {
        "project_id": "devflow-demo",
        "team_id": "engineering",
        "environment": "development",
        "metadata": {"version": "1.0.0", "feature": "workflow-orchestration"},
        "variables": {"branch": "feature/orchestration", "reviewer_count": 2},
        "tasks": [
            {
                "task_id": "code_review_1",
                "name": "Initial Code Review",
                "task_type": "code_review",
                "config": {"review_type": "initial", "required_approvals": 2},
                "dependencies": [],
                "priority": 4,
                "estimated_hours": 1.5
            },
            {
                "task_id": "unit_tests",
                "name": "Run Unit Tests",
                "task_type": "testing",
                "config": {"test_type": "unit", "parallel": True},
                "dependencies": ["code_review_1"],
                "priority": 3,
                "estimated_hours": 0.5
            },
            {
                "task_id": "integration_tests",
                "name": "Run Integration Tests",
                "task_type": "testing",
                "config": {"test_type": "integration"},
                "dependencies": ["code_review_1"],
                "priority": 3,
                "estimated_hours": 1.0
            },
            {
                "task_id": "security_review",
                "name": "Security Review",
                "task_type": "code_review",
                "config": {"review_type": "security", "tools": ["sonarqube", "snyk"]},
                "dependencies": ["unit_tests", "integration_tests"],
                "priority": 5,
                "estimated_hours": 2.0
            },
            {
                "task_id": "staging_deploy",
                "name": "Deploy to Staging",
                "task_type": "deployment",
                "config": {"environment": "staging", "health_checks": True},
                "dependencies": ["security_review"],
                "priority": 4,
                "estimated_hours": 0.5
            }
        ]
    }

    # Create and execute workflow
    print("🚀 Creating DevFlow workflow...")
    workflow_id = await orchestrator.create_workflow(workflow_definition)

    print(f"📋 Executing workflow: {workflow_id}")
    result = await orchestrator.execute_workflow(workflow_id)

    print(f"✅ Workflow completed!")
    print(f"📊 Execution time: {result['execution_time']:.2f} seconds")
    print(f"🔍 Optimization insights: {json.dumps(result['optimization_insights'], indent=2)}")

    # Display results
    if result["status"] == "completed":
        print("\n📈 Task Results:")
        for task_id, task_result in result["results"].items():
            status = task_result["status"]
            exec_time = task_result.get("execution_time", 0)
            print(f"  - {task_id}: {status} ({exec_time:.2f}s)")

    await orchestrator.stop_engine()
    return result

if __name__ == "__main__":
    print("🌟 DevFlow Advanced Workflow Orchestrator Demo")
    print("=" * 50)
    result = asyncio.run(demo_devflow_orchestrator())
    print(f"\n🎯 Demo completed with status: {result['status']}")
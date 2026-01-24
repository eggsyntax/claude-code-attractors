"""
DevFlow: Complete System Integration Demo
Demonstrates the full DevFlow platform working together as a comprehensive solution.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Import all DevFlow components
from devflow_engine_core import DevFlowEngine, WorkflowDefinition, WorkflowAction, WorkflowEvent, EventType
from devflow_integrations import IntegrationManager, GitHubIntegration, SlackIntegration, IntegrationConfig, IntegrationType
from devflow_intelligence import DevFlowIntelligence, TeamMember


class DevFlowPlatform:
    """
    Complete DevFlow platform that orchestrates all components.

    This represents the full system that teams would deploy to revolutionize
    their development workflows through intelligent automation.
    """

    def __init__(self, db_path: str = "devflow_production.db"):
        # Core components
        self.engine = DevFlowEngine()
        self.integration_manager = IntegrationManager()
        self.intelligence = DevFlowIntelligence(db_path)

        # Platform state
        self.active_sessions = {}
        self.workflow_templates = {}

    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the complete DevFlow platform"""
        try:
            print("🚀 Initializing DevFlow Platform...")

            # Set up integrations
            await self._setup_integrations(config.get('integrations', {}))

            # Load workflow templates
            await self._load_workflow_templates()

            # Set up intelligence system
            await self._setup_intelligence(config.get('team_members', []))

            # Connect components
            self._connect_components()

            print("✅ DevFlow Platform initialized successfully!")
            return True

        except Exception as e:
            print(f"❌ Failed to initialize DevFlow Platform: {e}")
            return False

    async def _setup_integrations(self, integration_configs: Dict[str, Dict]):
        """Set up all configured integrations"""
        for name, config in integration_configs.items():
            try:
                integration_config = IntegrationConfig(**config)

                if integration_config.type == IntegrationType.GITHUB:
                    integration = GitHubIntegration(integration_config)
                elif integration_config.type == IntegrationType.SLACK:
                    integration = SlackIntegration(integration_config)
                else:
                    print(f"⚠️  Unsupported integration type: {integration_config.type}")
                    continue

                await self.integration_manager.register_integration(name, integration)

            except Exception as e:
                print(f"⚠️  Failed to setup integration {name}: {e}")

    async def _load_workflow_templates(self):
        """Load pre-configured workflow templates"""

        # Smart PR Review Workflow
        pr_review_workflow = WorkflowDefinition(
            id="smart-pr-review",
            name="Smart PR Review Process",
            description="AI-enhanced PR review with intelligent reviewer assignment",
            triggers=[EventType.PR_CREATED],
            actions=[
                WorkflowAction(
                    id="analyze-pr",
                    name="Analyze PR Changes",
                    type="pr_analysis",
                    config={"analyze_complexity": True, "detect_patterns": True},
                    dependencies=[]
                ),
                WorkflowAction(
                    id="run-tests",
                    name="Run Automated Tests",
                    type="shell_command",
                    config={"command": "npm test && npm run lint"},
                    dependencies=[]
                ),
                WorkflowAction(
                    id="assign-smart-reviewers",
                    name="Assign Smart Reviewers",
                    type="smart_reviewer_assignment",
                    config={"count": 2, "consider_workload": True},
                    dependencies=["analyze-pr", "run-tests"]
                ),
                WorkflowAction(
                    id="notify-team",
                    name="Notify Team via Slack",
                    type="slack_notification",
                    config={"template": "pr_review_ready"},
                    dependencies=["assign-smart-reviewers"]
                )
            ]
        )

        # Intelligent Deployment Workflow
        deployment_workflow = WorkflowDefinition(
            id="intelligent-deployment",
            name="Intelligent Deployment Process",
            description="Smart deployment with optimal timing and risk assessment",
            triggers=[EventType.PR_MERGED],
            actions=[
                WorkflowAction(
                    id="assess-deployment-risk",
                    name="Assess Deployment Risk",
                    type="risk_assessment",
                    config={"check_dependencies": True, "analyze_changes": True},
                    dependencies=[]
                ),
                WorkflowAction(
                    id="find-optimal-deployment-window",
                    name="Find Optimal Deployment Window",
                    type="timing_optimization",
                    config={"consider_traffic": True, "check_team_availability": True},
                    dependencies=["assess-deployment-risk"]
                ),
                WorkflowAction(
                    id="execute-deployment",
                    name="Execute Deployment",
                    type="deployment_execution",
                    config={"environment": "production", "rollback_enabled": True},
                    dependencies=["find-optimal-deployment-window"]
                ),
                WorkflowAction(
                    id="monitor-deployment",
                    name="Monitor Deployment Health",
                    type="deployment_monitoring",
                    config={"duration_minutes": 30, "auto_rollback": True},
                    dependencies=["execute-deployment"]
                )
            ]
        )

        # Register workflows
        self.engine.register_workflow(pr_review_workflow)
        self.engine.register_workflow(deployment_workflow)

        self.workflow_templates = {
            "smart-pr-review": pr_review_workflow,
            "intelligent-deployment": deployment_workflow
        }

    async def _setup_intelligence(self, team_config: List[Dict]):
        """Set up the intelligence system with team data"""
        for member_config in team_config:
            member = TeamMember(**member_config)
            self.intelligence.reviewer_assignment.add_team_member(member)

    def _connect_components(self):
        """Connect all components to work together"""

        # Custom action handlers that use intelligence
        async def smart_reviewer_assignment_action(action, execution):
            """Custom action that uses AI for reviewer assignment"""
            pr_info = execution.trigger_event.payload
            suggested_reviewers = await self.intelligence.get_smart_reviewer_suggestions(pr_info)

            # Use GitHub integration to assign reviewers
            if 'github' in self.integration_manager.integrations:
                github = self.integration_manager.integrations['github']
                repo = pr_info.get('repository', '')
                pr_number = pr_info.get('pr_number', 0)

                if repo and pr_number:
                    success = await github.assign_reviewers(repo, pr_number, suggested_reviewers)
                    return {"assigned_reviewers": suggested_reviewers, "success": success}

            return {"assigned_reviewers": suggested_reviewers, "success": False}

        async def slack_notification_action(action, execution):
            """Custom action for intelligent Slack notifications"""
            if 'slack' in self.integration_manager.integrations:
                template = action.config.get('template', 'generic')

                if template == 'pr_review_ready':
                    pr_info = execution.trigger_event.payload
                    message = (f"🔀 New PR ready for review!\n"
                              f"**{pr_info.get('title', 'Untitled PR')}** by {pr_info.get('author', 'Unknown')}\n"
                              f"Repository: {pr_info.get('repository', 'Unknown')}\n"
                              f"Smart reviewers have been assigned based on expertise and workload.")

                    slack = self.integration_manager.integrations['slack']
                    success = await slack.send_notification(message)
                    return {"message_sent": success, "template_used": template}

            return {"message_sent": False, "error": "Slack not configured"}

        async def pr_analysis_action(action, execution):
            """Analyze PR using intelligence system"""
            pr_info = execution.trigger_event.payload

            # In a real implementation, this would use ML to analyze code changes
            analysis = {
                "complexity_score": 0.7,  # Mock data
                "risk_level": "medium",
                "estimated_review_time": "2-3 hours",
                "suggested_focus_areas": ["error handling", "test coverage"],
                "detected_patterns": ["new API endpoint", "database migration"]
            }

            return analysis

        # Register custom actions
        self.engine.register_action_plugin('smart_reviewer_assignment', smart_reviewer_assignment_action)
        self.engine.register_action_plugin('slack_notification', slack_notification_action)
        self.engine.register_action_plugin('pr_analysis', pr_analysis_action)

        # Connect integration events to workflow engine
        async def handle_integration_event(event: WorkflowEvent):
            execution_ids = await self.engine.emit_event(event)

            # Analyze each execution for learning
            for execution_id in execution_ids:
                # Wait a bit for execution to complete, then analyze
                asyncio.create_task(self._analyze_execution_after_delay(execution_id, 30))

        self.integration_manager.register_event_handler(handle_integration_event)

    async def _analyze_execution_after_delay(self, execution_id: str, delay_seconds: int):
        """Analyze execution after it completes for learning purposes"""
        await asyncio.sleep(delay_seconds)

        execution = await self.engine.get_execution_status(execution_id)
        if execution:
            await self.intelligence.analyze_and_optimize(execution)

    async def create_custom_workflow(self, workflow_definition: Dict[str, Any]) -> str:
        """Create a custom workflow from definition"""
        workflow = WorkflowDefinition(**workflow_definition)
        self.engine.register_workflow(workflow)
        return workflow.id

    async def get_platform_analytics(self) -> Dict[str, Any]:
        """Get comprehensive platform analytics"""
        active_executions = await self.engine.get_active_executions()
        recent_suggestions = await self.intelligence.analyzer.generate_optimization_suggestions()

        return {
            "active_workflows": len(active_executions),
            "total_integrations": len(self.integration_manager.integrations),
            "team_size": len(self.intelligence.reviewer_assignment.team_members),
            "optimization_opportunities": len(recent_suggestions),
            "workflow_templates": len(self.workflow_templates),
            "system_health": "operational"  # Would be computed from actual metrics
        }

    async def process_webhook(self, integration_name: str, payload: Dict, headers: Dict) -> List[str]:
        """Process incoming webhook and return triggered execution IDs"""
        events = await self.integration_manager.handle_webhook(integration_name, payload, headers)
        return [event.id for event in events]

    async def shutdown(self):
        """Clean shutdown of all platform components"""
        print("🛑 Shutting down DevFlow Platform...")
        await self.integration_manager.close_all()
        print("✅ DevFlow Platform shutdown complete")


# Complete demonstration
async def full_devflow_demo():
    """
    Complete demonstration of DevFlow platform capabilities.

    This shows how all components work together to create an intelligent
    development workflow orchestration system.
    """

    print("🌟 DevFlow Platform - Complete Integration Demo")
    print("=" * 60)

    # Platform configuration
    config = {
        "integrations": {
            "github": {
                "name": "github-main",
                "type": "github",
                "api_token": "ghp_demo_token",
                "base_url": "https://api.github.com",
                "webhook_secret": "demo_secret"
            },
            "slack": {
                "name": "slack-main",
                "type": "slack",
                "api_token": "xoxb-demo-token",
                "base_url": "https://slack.com/api",
                "custom_config": {"default_channel": "#dev-team"}
            }
        },
        "team_members": [
            {
                "username": "alice",
                "skills": ["frontend", "react", "typescript", "ui-design"],
                "expertise_areas": ["components", "styling", "user-experience"],
                "availability_score": 0.8,
                "review_load": 2,
                "avg_review_time_hours": 1.5,
                "languages": ["typescript", "javascript", "css", "html"]
            },
            {
                "username": "bob",
                "skills": ["backend", "api", "database", "microservices"],
                "expertise_areas": ["services", "data-models", "architecture"],
                "availability_score": 0.9,
                "review_load": 1,
                "avg_review_time_hours": 2.0,
                "languages": ["python", "sql", "go", "docker"]
            },
            {
                "username": "charlie",
                "skills": ["devops", "infrastructure", "monitoring", "security"],
                "expertise_areas": ["deployment", "ci-cd", "observability"],
                "availability_score": 0.7,
                "review_load": 3,
                "avg_review_time_hours": 2.5,
                "languages": ["yaml", "bash", "terraform", "kubernetes"]
            }
        ]
    }

    # Initialize platform
    platform = DevFlowPlatform()
    initialized = await platform.initialize(config)

    if not initialized:
        print("❌ Failed to initialize platform")
        return

    print("\n📊 Platform Status:")
    analytics = await platform.get_platform_analytics()
    for key, value in analytics.items():
        print(f"   {key}: {value}")

    # Simulate real-world workflow: PR Creation → Review → Merge → Deploy
    print(f"\n🎬 Simulating Real-World Development Workflow")
    print("-" * 50)

    # Step 1: Simulate PR Creation
    print("\n1. 📝 Developer creates a PR...")

    pr_webhook_payload = {
        "action": "opened",
        "pull_request": {
            "id": 98765,
            "number": 42,
            "title": "Add intelligent caching system",
            "user": {"login": "dev_sarah"},
            "base": {"ref": "main"},
            "head": {"ref": "feature/intelligent-caching"}
        },
        "repository": {"full_name": "company/awesome-product"}
    }

    pr_headers = {
        "X-GitHub-Event": "pull_request",
        "X-Hub-Signature-256": "sha256=demo_signature"
    }

    triggered_events = await platform.process_webhook("github", pr_webhook_payload, pr_headers)
    print(f"   ✅ Triggered {len(triggered_events)} workflow events")

    # Wait for workflows to process
    print(f"\n2. 🤖 AI processes PR and assigns optimal reviewers...")
    await asyncio.sleep(3)

    active_executions = await platform.engine.get_active_executions()
    print(f"   📊 Active workflow executions: {len(active_executions)}")

    if active_executions:
        execution = active_executions[0]
        print(f"   🔄 Workflow '{execution.workflow_id}' status: {execution.status.value}")

    # Step 2: Wait for workflow completion and show results
    print(f"\n3. ⏳ Waiting for workflows to complete...")

    completed_count = 0
    while completed_count < len(active_executions) and completed_count < 10:  # Safety limit
        await asyncio.sleep(2)

        completed_executions = []
        for execution in active_executions:
            current_status = await platform.engine.get_execution_status(execution.id)
            if current_status and current_status.status.value in ['completed', 'failed']:
                completed_executions.append(current_status)

        completed_count = len(completed_executions)

        print(f"   📈 Completed workflows: {completed_count}/{len(active_executions)}")

        if completed_count > 0:
            break

    # Show workflow results
    print(f"\n4. 📋 Workflow Results:")
    for execution in completed_executions[:3]:  # Show first 3
        print(f"   Workflow: {execution.workflow_id}")
        print(f"   Status: {execution.status.value}")
        print(f"   Duration: {(execution.completed_at - execution.started_at).total_seconds():.1f}s")

        if execution.action_results:
            print(f"   Action Results:")
            for action_id, result in execution.action_results.items():
                if isinstance(result, dict):
                    summary = ', '.join(f"{k}: {v}" for k, v in list(result.items())[:2])
                    print(f"     {action_id}: {summary}")

    # Step 3: Simulate PR merge and deployment
    print(f"\n5. 🎯 Simulating PR merge and intelligent deployment...")

    merge_payload = {
        "action": "closed",
        "pull_request": {
            "id": 98765,
            "number": 42,
            "title": "Add intelligent caching system",
            "merged": True,
            "merged_by": {"login": "alice"}
        },
        "repository": {"full_name": "company/awesome-product"}
    }

    merge_headers = {
        "X-GitHub-Event": "pull_request",
        "X-Hub-Signature-256": "sha256=demo_signature"
    }

    deployment_events = await platform.process_webhook("github", merge_payload, merge_headers)
    print(f"   🚀 Deployment workflow triggered: {len(deployment_events)} events")

    # Step 4: Show intelligence insights
    print(f"\n6. 🧠 AI Intelligence Insights:")

    # Create sample execution for analysis
    sample_execution_id = active_executions[0].id if active_executions else "demo_exec"
    sample_execution = await platform.engine.get_execution_status(sample_execution_id)

    if sample_execution:
        analysis = await platform.intelligence.analyze_and_optimize(sample_execution)

        print(f"   📊 Performance Analysis:")
        if analysis['performance_metrics']['success_rate']:
            print(f"     Success Rate: {analysis['performance_metrics']['success_rate']:.1%}")
        if analysis['performance_metrics']['avg_duration']:
            print(f"     Avg Duration: {analysis['performance_metrics']['avg_duration']:.1f} minutes")

        if analysis['optimization_suggestions']:
            print(f"   💡 Optimization Opportunities:")
            for suggestion in analysis['optimization_suggestions'][:2]:
                print(f"     • {suggestion['title']}")
                print(f"       Expected: {suggestion['expected_improvement']}")
                print(f"       Confidence: {suggestion['confidence_score']:.1%}")

    # Final platform status
    print(f"\n7. 🎉 Final Platform Status:")
    final_analytics = await platform.get_platform_analytics()
    for key, value in final_analytics.items():
        print(f"   {key}: {value}")

    # Cleanup
    await platform.shutdown()

    print(f"\n✅ DevFlow Complete Integration Demo Finished!")
    print(f"\n🌟 Key Achievements Demonstrated:")
    print(f"   • Event-driven workflow orchestration")
    print(f"   • Intelligent reviewer assignment based on expertise")
    print(f"   • Real-time team notifications via Slack")
    print(f"   • AI-powered optimization suggestions")
    print(f"   • Seamless integration between GitHub, Slack, and CI/CD")
    print(f"   • Pattern recognition and predictive insights")
    print(f"   • Automated deployment with risk assessment")


if __name__ == "__main__":
    # Run the complete demonstration
    asyncio.run(full_devflow_demo())
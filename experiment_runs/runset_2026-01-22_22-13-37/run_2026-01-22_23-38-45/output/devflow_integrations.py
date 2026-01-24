"""
DevFlow Integration Framework
Unified integration layer for connecting with popular developer tools.
"""

import asyncio
import aiohttp
import json
import hmac
import hashlib
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

from devflow_engine_core import WorkflowEvent, EventType


class IntegrationType(Enum):
    GITHUB = "github"
    GITLAB = "gitlab"
    JENKINS = "jenkins"
    SLACK = "slack"
    JIRA = "jira"
    DISCORD = "discord"


@dataclass
class IntegrationConfig:
    """Configuration for a specific integration"""
    name: str
    type: IntegrationType
    api_token: str
    base_url: str
    webhook_secret: Optional[str] = None
    custom_config: Optional[Dict[str, Any]] = None


class BaseIntegration(ABC):
    """Abstract base class for all tool integrations"""

    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.event_callbacks: List[Callable[[WorkflowEvent], None]] = []

    @abstractmethod
    async def authenticate(self) -> bool:
        """Verify authentication with the external service"""
        pass

    @abstractmethod
    async def parse_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> List[WorkflowEvent]:
        """Parse incoming webhook data into DevFlow events"""
        pass

    @abstractmethod
    async def send_notification(self, message: str, target: Optional[str] = None) -> bool:
        """Send a notification through this integration"""
        pass

    def register_event_callback(self, callback: Callable[[WorkflowEvent], None]) -> None:
        """Register a callback for processed events"""
        self.event_callbacks.append(callback)

    async def _emit_event(self, event: WorkflowEvent) -> None:
        """Emit an event to all registered callbacks"""
        for callback in self.event_callbacks:
            try:
                await callback(event) if asyncio.iscoroutinefunction(callback) else callback(event)
            except Exception as e:
                print(f"Error in event callback: {e}")


class GitHubIntegration(BaseIntegration):
    """GitHub integration with webhook support and API calls"""

    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.session: Optional[aiohttp.ClientSession] = None

    async def authenticate(self) -> bool:
        """Verify GitHub API token"""
        try:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"token {self.config.api_token}"}
            )

            async with self.session.get(f"{self.config.base_url}/user") as response:
                return response.status == 200
        except Exception as e:
            print(f"GitHub authentication failed: {e}")
            return False

    async def parse_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> List[WorkflowEvent]:
        """Parse GitHub webhook events"""
        events = []

        # Verify webhook signature if secret is configured
        if self.config.webhook_secret:
            signature = headers.get("X-Hub-Signature-256", "")
            expected = hmac.new(
                self.config.webhook_secret.encode(),
                json.dumps(payload).encode(),
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(f"sha256={expected}", signature):
                raise ValueError("Invalid webhook signature")

        event_type = headers.get("X-GitHub-Event")

        if event_type == "push":
            events.append(WorkflowEvent(
                id=f"github-{payload['after']}",
                type=EventType.GIT_PUSH,
                source="github",
                payload={
                    "repository": payload["repository"]["full_name"],
                    "ref": payload["ref"],
                    "commits": payload["commits"],
                    "pusher": payload["pusher"]["name"]
                },
                timestamp=datetime.utcnow()
            ))

        elif event_type == "pull_request":
            action = payload["action"]
            if action == "opened":
                events.append(WorkflowEvent(
                    id=f"github-pr-{payload['pull_request']['id']}",
                    type=EventType.PR_CREATED,
                    source="github",
                    payload={
                        "repository": payload["repository"]["full_name"],
                        "pr_number": payload["pull_request"]["number"],
                        "title": payload["pull_request"]["title"],
                        "author": payload["pull_request"]["user"]["login"],
                        "base_branch": payload["pull_request"]["base"]["ref"],
                        "head_branch": payload["pull_request"]["head"]["ref"]
                    },
                    timestamp=datetime.utcnow()
                ))
            elif action == "closed" and payload["pull_request"]["merged"]:
                events.append(WorkflowEvent(
                    id=f"github-pr-merged-{payload['pull_request']['id']}",
                    type=EventType.PR_MERGED,
                    source="github",
                    payload={
                        "repository": payload["repository"]["full_name"],
                        "pr_number": payload["pull_request"]["number"],
                        "title": payload["pull_request"]["title"],
                        "merger": payload["pull_request"]["merged_by"]["login"]
                    },
                    timestamp=datetime.utcnow()
                ))

        elif event_type == "issues":
            if payload["action"] == "opened":
                events.append(WorkflowEvent(
                    id=f"github-issue-{payload['issue']['id']}",
                    type=EventType.ISSUE_CREATED,
                    source="github",
                    payload={
                        "repository": payload["repository"]["full_name"],
                        "issue_number": payload["issue"]["number"],
                        "title": payload["issue"]["title"],
                        "author": payload["issue"]["user"]["login"],
                        "labels": [label["name"] for label in payload["issue"]["labels"]]
                    },
                    timestamp=datetime.utcnow()
                ))

        return events

    async def send_notification(self, message: str, target: Optional[str] = None) -> bool:
        """Send notification via GitHub (comment, status, etc.)"""
        # This would implement GitHub-specific notifications
        # For now, just log the message
        print(f"GitHub notification: {message} (target: {target})")
        return True

    async def assign_reviewers(self, repo: str, pr_number: int, reviewers: List[str]) -> bool:
        """Assign reviewers to a pull request"""
        if not self.session:
            return False

        try:
            async with self.session.post(
                f"{self.config.base_url}/repos/{repo}/pulls/{pr_number}/requested_reviewers",
                json={"reviewers": reviewers}
            ) as response:
                return response.status == 201
        except Exception as e:
            print(f"Failed to assign reviewers: {e}")
            return False

    async def close(self) -> None:
        """Clean up resources"""
        if self.session:
            await self.session.close()


class SlackIntegration(BaseIntegration):
    """Slack integration for notifications and team communication"""

    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.session: Optional[aiohttp.ClientSession] = None

    async def authenticate(self) -> bool:
        """Verify Slack bot token"""
        try:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.config.api_token}"}
            )

            async with self.session.post(f"{self.config.base_url}/auth.test") as response:
                return response.status == 200
        except Exception as e:
            print(f"Slack authentication failed: {e}")
            return False

    async def parse_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> List[WorkflowEvent]:
        """Parse Slack webhook events (slash commands, interactive components)"""
        events = []

        # Handle slash commands
        if payload.get("command"):
            events.append(WorkflowEvent(
                id=f"slack-{payload['trigger_id']}",
                type=EventType.CUSTOM,
                source="slack",
                payload={
                    "command": payload["command"],
                    "text": payload.get("text", ""),
                    "user": payload["user_name"],
                    "channel": payload["channel_name"]
                },
                timestamp=datetime.utcnow()
            ))

        return events

    async def send_notification(self, message: str, target: Optional[str] = None) -> bool:
        """Send message to Slack channel or user"""
        if not self.session:
            return False

        try:
            channel = target or self.config.custom_config.get("default_channel", "#general")

            async with self.session.post(
                f"{self.config.base_url}/chat.postMessage",
                json={
                    "channel": channel,
                    "text": message,
                    "username": "DevFlow Bot"
                }
            ) as response:
                return response.status == 200
        except Exception as e:
            print(f"Failed to send Slack message: {e}")
            return False

    async def send_rich_notification(self, blocks: List[Dict], channel: str) -> bool:
        """Send rich message with Slack blocks"""
        if not self.session:
            return False

        try:
            async with self.session.post(
                f"{self.config.base_url}/chat.postMessage",
                json={
                    "channel": channel,
                    "blocks": blocks,
                    "username": "DevFlow Bot"
                }
            ) as response:
                return response.status == 200
        except Exception as e:
            print(f"Failed to send rich Slack message: {e}")
            return False

    async def close(self) -> None:
        """Clean up resources"""
        if self.session:
            await self.session.close()


class JenkinsIntegration(BaseIntegration):
    """Jenkins integration for build and deployment events"""

    def __init__(self, config: IntegrationConfig):
        super().__init__(config)
        self.session: Optional[aiohttp.ClientSession] = None

    async def authenticate(self) -> bool:
        """Verify Jenkins API token"""
        try:
            auth = aiohttp.BasicAuth(
                self.config.custom_config.get("username", ""),
                self.config.api_token
            )
            self.session = aiohttp.ClientSession(auth=auth)

            async with self.session.get(f"{self.config.base_url}/api/json") as response:
                return response.status == 200
        except Exception as e:
            print(f"Jenkins authentication failed: {e}")
            return False

    async def parse_webhook(self, payload: Dict[str, Any], headers: Dict[str, str]) -> List[WorkflowEvent]:
        """Parse Jenkins webhook events"""
        events = []

        if payload.get("build"):
            build = payload["build"]

            if build["phase"] == "STARTED":
                events.append(WorkflowEvent(
                    id=f"jenkins-{build['full_url']}",
                    type=EventType.BUILD_STARTED,
                    source="jenkins",
                    payload={
                        "job_name": payload["name"],
                        "build_number": build["number"],
                        "build_url": build["full_url"],
                        "parameters": build.get("parameters", {})
                    },
                    timestamp=datetime.utcnow()
                ))

            elif build["phase"] == "COMPLETED":
                events.append(WorkflowEvent(
                    id=f"jenkins-completed-{build['full_url']}",
                    type=EventType.BUILD_COMPLETED,
                    source="jenkins",
                    payload={
                        "job_name": payload["name"],
                        "build_number": build["number"],
                        "build_url": build["full_url"],
                        "status": build["status"],
                        "duration": build.get("duration")
                    },
                    timestamp=datetime.utcnow()
                ))

        return events

    async def send_notification(self, message: str, target: Optional[str] = None) -> bool:
        """Send notification via Jenkins (console log, build description)"""
        print(f"Jenkins notification: {message} (target: {target})")
        return True

    async def trigger_build(self, job_name: str, parameters: Optional[Dict] = None) -> bool:
        """Trigger a Jenkins build job"""
        if not self.session:
            return False

        try:
            url = f"{self.config.base_url}/job/{job_name}/build"
            if parameters:
                url += "WithParameters"

            async with self.session.post(url, data=parameters or {}) as response:
                return response.status in [200, 201]
        except Exception as e:
            print(f"Failed to trigger Jenkins build: {e}")
            return False

    async def close(self) -> None:
        """Clean up resources"""
        if self.session:
            await self.session.close()


class IntegrationManager:
    """Manages all integrations and routes events appropriately"""

    def __init__(self):
        self.integrations: Dict[str, BaseIntegration] = {}
        self.event_handlers: List[Callable[[WorkflowEvent], None]] = []

    async def register_integration(self, name: str, integration: BaseIntegration) -> bool:
        """Register and authenticate an integration"""
        if await integration.authenticate():
            self.integrations[name] = integration
            integration.register_event_callback(self._handle_integration_event)
            print(f"✅ Registered integration: {name}")
            return True
        else:
            print(f"❌ Failed to register integration: {name}")
            return False

    def register_event_handler(self, handler: Callable[[WorkflowEvent], None]) -> None:
        """Register a handler for all integration events"""
        self.event_handlers.append(handler)

    async def handle_webhook(self, integration_name: str, payload: Dict[str, Any], headers: Dict[str, str]) -> List[WorkflowEvent]:
        """Process incoming webhook from a specific integration"""
        if integration_name not in self.integrations:
            raise ValueError(f"Unknown integration: {integration_name}")

        integration = self.integrations[integration_name]
        events = await integration.parse_webhook(payload, headers)

        # Process each event through handlers
        for event in events:
            await self._handle_integration_event(event)

        return events

    async def send_notification(self, integration_name: str, message: str, target: Optional[str] = None) -> bool:
        """Send notification through specific integration"""
        if integration_name not in self.integrations:
            return False

        integration = self.integrations[integration_name]
        return await integration.send_notification(message, target)

    async def _handle_integration_event(self, event: WorkflowEvent) -> None:
        """Handle events from integrations"""
        for handler in self.event_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                print(f"Error in integration event handler: {e}")

    async def close_all(self) -> None:
        """Clean up all integrations"""
        for integration in self.integrations.values():
            if hasattr(integration, 'close'):
                await integration.close()


# Example usage and testing
async def demo_integrations():
    """Demonstrate integration framework capabilities"""

    # Set up integration manager
    manager = IntegrationManager()

    # Configure GitHub integration
    github_config = IntegrationConfig(
        name="github-main",
        type=IntegrationType.GITHUB,
        api_token="ghp_example_token",
        base_url="https://api.github.com",
        webhook_secret="webhook_secret_here"
    )

    github_integration = GitHubIntegration(github_config)

    # Configure Slack integration
    slack_config = IntegrationConfig(
        name="slack-main",
        type=IntegrationType.SLACK,
        api_token="xoxb-example-token",
        base_url="https://slack.com/api",
        custom_config={"default_channel": "#dev-notifications"}
    )

    slack_integration = SlackIntegration(slack_config)

    # Register integrations
    print("🔗 Setting up integrations...")
    await manager.register_integration("github", github_integration)
    await manager.register_integration("slack", slack_integration)

    # Register event handler
    async def handle_workflow_event(event: WorkflowEvent):
        print(f"📨 Received event: {event.type.value} from {event.source}")

        # Send Slack notification for important events
        if event.type == EventType.PR_CREATED:
            message = f"🔀 New PR created: {event.payload.get('title')} by {event.payload.get('author')}"
            await manager.send_notification("slack", message)

        elif event.type == EventType.BUILD_COMPLETED:
            status = event.payload.get('status', 'unknown')
            emoji = "✅" if status == "SUCCESS" else "❌"
            message = f"{emoji} Build {status}: {event.payload.get('job_name')}"
            await manager.send_notification("slack", message)

    manager.register_event_handler(handle_workflow_event)

    # Simulate webhook events
    print("\n🚀 Simulating GitHub webhook events...")

    # Simulate PR creation webhook
    pr_payload = {
        "action": "opened",
        "pull_request": {
            "id": 12345,
            "number": 42,
            "title": "Add DevFlow integration framework",
            "user": {"login": "alice"},
            "base": {"ref": "main"},
            "head": {"ref": "feature/devflow-integrations"}
        },
        "repository": {"full_name": "team/awesome-project"}
    }

    pr_headers = {
        "X-GitHub-Event": "pull_request",
        "X-Hub-Signature-256": "sha256=example_signature"
    }

    # Process webhook (in real implementation, this would come from web server)
    events = await manager.handle_webhook("github", pr_payload, pr_headers)
    print(f"✅ Processed {len(events)} events from GitHub webhook")

    # Clean up
    await manager.close_all()
    print("\n🧹 Cleaned up integrations")

if __name__ == "__main__":
    asyncio.run(demo_integrations())
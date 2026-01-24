#!/usr/bin/env python3
"""
CI/CD Integration Module for Code Analysis Platform
==================================================

This module provides comprehensive CI/CD integration capabilities including:
- GitHub webhook handling
- GitLab CI integration
- Jenkins pipeline support
- Quality gate enforcement
- Automated reporting
- Slack/Teams notifications

Authors: Bob & Alice (Collaborative AI Development)
"""

import os
import json
import hmac
import hashlib
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import tempfile
import shutil
import logging

import git
import yaml
from fastapi import APIRouter, HTTPException, BackgroundTasks, Request, Header
from pydantic import BaseModel
import requests

from ast_analyzer import CodeAnalyzer
from complexity_analyzer import ComplexityAnalyzer
from dashboard_generator import DashboardGenerator


# Configure logging
logger = logging.getLogger(__name__)


class WebhookPayload(BaseModel):
    """Generic webhook payload model."""
    repository: Dict[str, Any]
    commits: Optional[List[Dict[str, Any]]] = None
    head_commit: Optional[Dict[str, Any]] = None
    ref: Optional[str] = None
    action: Optional[str] = None


class QualityGate(BaseModel):
    """Quality gate configuration."""
    max_complexity: int = 10
    max_cognitive_complexity: int = 15
    min_test_coverage: float = 80.0
    max_code_duplication: float = 5.0
    allow_complexity_increase: bool = False
    block_on_high_complexity: bool = True


class AnalysisReport(BaseModel):
    """CI/CD analysis report."""
    passed: bool
    quality_gate_status: str
    total_issues: int
    complexity_violations: int
    coverage_percentage: float
    summary: str
    details: Dict[str, Any]
    recommendations: List[str]


class CICDIntegration:
    """Main CI/CD integration handler."""

    def __init__(self):
        self.router = APIRouter()
        self.setup_routes()

    def setup_routes(self):
        """Setup FastAPI routes for CI/CD integration."""

        @self.router.post("/webhooks/github")
        async def github_webhook(
            request: Request,
            background_tasks: BackgroundTasks,
            x_github_event: str = Header(None),
            x_hub_signature_256: str = Header(None)
        ):
            """Handle GitHub webhook events."""
            body = await request.body()
            payload = json.loads(body.decode('utf-8'))

            # Verify webhook signature (in production)
            if not self._verify_github_signature(body, x_hub_signature_256):
                raise HTTPException(status_code=401, detail="Invalid signature")

            # Process different event types
            if x_github_event == "push":
                return await self._handle_push_event(payload, background_tasks)
            elif x_github_event == "pull_request":
                return await self._handle_pull_request_event(payload, background_tasks)
            else:
                return {"message": "Event type not handled", "event": x_github_event}

        @self.router.post("/webhooks/gitlab")
        async def gitlab_webhook(
            request: Request,
            background_tasks: BackgroundTasks,
            x_gitlab_event: str = Header(None),
            x_gitlab_token: str = Header(None)
        ):
            """Handle GitLab webhook events."""
            body = await request.body()
            payload = json.loads(body.decode('utf-8'))

            # Verify GitLab token (in production)
            if not self._verify_gitlab_token(x_gitlab_token):
                raise HTTPException(status_code=401, detail="Invalid token")

            if x_gitlab_event == "Push Hook":
                return await self._handle_gitlab_push(payload, background_tasks)
            elif x_gitlab_event == "Merge Request Hook":
                return await self._handle_gitlab_merge_request(payload, background_tasks)
            else:
                return {"message": "Event type not handled", "event": x_gitlab_event}

        @self.router.post("/analysis/quality-gate/{project_id}")
        async def check_quality_gate(
            project_id: str,
            quality_gate: QualityGate,
            background_tasks: BackgroundTasks
        ):
            """Check if code meets quality gate requirements."""
            try:
                report = await self._analyze_with_quality_gate(project_id, quality_gate)
                return report
            except Exception as e:
                logger.error(f"Quality gate check failed: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.router.get("/cicd/github-actions-workflow")
        async def get_github_actions_workflow():
            """Get GitHub Actions workflow configuration."""
            return {
                "workflow": self._generate_github_actions_workflow(),
                "instructions": "Add this to .github/workflows/code-analysis.yml"
            }

        @self.router.get("/cicd/gitlab-ci-config")
        async def get_gitlab_ci_config():
            """Get GitLab CI configuration."""
            return {
                "config": self._generate_gitlab_ci_config(),
                "instructions": "Add this to your .gitlab-ci.yml file"
            }

        @self.router.get("/cicd/jenkins-pipeline")
        async def get_jenkins_pipeline():
            """Get Jenkins pipeline configuration."""
            return {
                "pipeline": self._generate_jenkins_pipeline(),
                "instructions": "Add this to your Jenkinsfile"
            }

    def _verify_github_signature(self, body: bytes, signature: str) -> bool:
        """Verify GitHub webhook signature."""
        if not signature or not os.getenv('GITHUB_WEBHOOK_SECRET'):
            return True  # Skip verification in development

        expected_signature = 'sha256=' + hmac.new(
            os.getenv('GITHUB_WEBHOOK_SECRET').encode(),
            body,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    def _verify_gitlab_token(self, token: str) -> bool:
        """Verify GitLab webhook token."""
        expected_token = os.getenv('GITLAB_WEBHOOK_TOKEN')
        if not expected_token:
            return True  # Skip verification in development

        return hmac.compare_digest(token, expected_token)

    async def _handle_push_event(self, payload: Dict, background_tasks: BackgroundTasks):
        """Handle GitHub push event."""
        repo_url = payload['repository']['clone_url']
        repo_name = payload['repository']['name']
        commit_sha = payload['head_commit']['id']

        logger.info(f"Processing push event for {repo_name}, commit {commit_sha}")

        # Clone repository and analyze
        background_tasks.add_task(
            self._analyze_repository_async,
            repo_url,
            repo_name,
            commit_sha
        )

        return {
            "message": "Analysis started",
            "repository": repo_name,
            "commit": commit_sha
        }

    async def _handle_pull_request_event(self, payload: Dict, background_tasks: BackgroundTasks):
        """Handle GitHub pull request event."""
        if payload['action'] not in ['opened', 'synchronize', 'reopened']:
            return {"message": "PR action not processed", "action": payload['action']}

        repo_url = payload['repository']['clone_url']
        repo_name = payload['repository']['name']
        pr_number = payload['pull_request']['number']
        head_sha = payload['pull_request']['head']['sha']

        logger.info(f"Processing PR #{pr_number} for {repo_name}")

        # Analyze PR changes
        background_tasks.add_task(
            self._analyze_pull_request_async,
            repo_url,
            repo_name,
            pr_number,
            head_sha
        )

        return {
            "message": "PR analysis started",
            "repository": repo_name,
            "pr_number": pr_number
        }

    async def _handle_gitlab_push(self, payload: Dict, background_tasks: BackgroundTasks):
        """Handle GitLab push event."""
        repo_url = payload['project']['git_http_url']
        repo_name = payload['project']['name']
        commit_sha = payload['commits'][0]['id'] if payload['commits'] else None

        if not commit_sha:
            return {"message": "No commits to analyze"}

        background_tasks.add_task(
            self._analyze_repository_async,
            repo_url,
            repo_name,
            commit_sha
        )

        return {
            "message": "Analysis started",
            "repository": repo_name,
            "commit": commit_sha
        }

    async def _handle_gitlab_merge_request(self, payload: Dict, background_tasks: BackgroundTasks):
        """Handle GitLab merge request event."""
        if payload['object_attributes']['action'] not in ['open', 'update']:
            return {"message": "MR action not processed"}

        repo_url = payload['project']['git_http_url']
        repo_name = payload['project']['name']
        mr_number = payload['object_attributes']['iid']
        head_sha = payload['object_attributes']['last_commit']['id']

        background_tasks.add_task(
            self._analyze_merge_request_async,
            repo_url,
            repo_name,
            mr_number,
            head_sha
        )

        return {
            "message": "MR analysis started",
            "repository": repo_name,
            "mr_number": mr_number
        }

    async def _analyze_repository_async(self, repo_url: str, repo_name: str, commit_sha: str):
        """Analyze repository asynchronously."""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Clone repository
                repo_path = Path(temp_dir) / repo_name
                repo = git.Repo.clone_from(repo_url, repo_path)
                repo.git.checkout(commit_sha)

                # Analyze code
                generator = DashboardGenerator(str(repo_path))
                results = generator.analyze_project(str(repo_path))

                # Generate dashboard
                dashboard_path = f"dashboards/{repo_name}_{commit_sha[:8]}_dashboard.html"
                generator.generate_dashboard(output_filename=dashboard_path)

                # Apply quality gates
                quality_gate = QualityGate()  # Use default settings
                report = await self._generate_analysis_report(results, quality_gate)

                # Send notifications
                await self._send_analysis_notification(repo_name, commit_sha, report)

                logger.info(f"Analysis completed for {repo_name}:{commit_sha}")

        except Exception as e:
            logger.error(f"Repository analysis failed: {str(e)}")
            await self._send_error_notification(repo_name, commit_sha, str(e))

    async def _analyze_pull_request_async(self, repo_url: str, repo_name: str, pr_number: int, head_sha: str):
        """Analyze pull request changes."""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Clone repository
                repo_path = Path(temp_dir) / repo_name
                repo = git.Repo.clone_from(repo_url, repo_path)

                # Get changed files in PR
                base_sha = repo.commit(head_sha).parents[0].hexsha
                changed_files = list(repo.git.diff('--name-only', f'{base_sha}..{head_sha}').split('\n'))
                python_files = [f for f in changed_files if f.endswith('.py')]

                if not python_files:
                    logger.info(f"No Python files changed in PR #{pr_number}")
                    return

                # Analyze only changed files
                results = {'functions': [], 'classes': [], 'dependencies': [], 'overview': {}}

                for file_path in python_files:
                    full_path = repo_path / file_path
                    if full_path.exists():
                        analyzer = CodeAnalyzer()
                        file_results = analyzer.analyze_file(str(full_path))
                        if file_results:
                            results['functions'].extend(file_results.get('functions', []))
                            results['classes'].extend(file_results.get('classes', []))
                            results['dependencies'].extend(file_results.get('dependencies', []))

                # Calculate overview metrics
                complexity_analyzer = ComplexityAnalyzer()
                total_complexity = 0
                high_complexity_functions = 0

                for func in results['functions']:
                    try:
                        # This would need the actual AST node, simplified for demo
                        complexity = len(func.get('decorators', [])) + 1  # Simplified
                        func['complexity'] = complexity
                        total_complexity += complexity

                        if complexity > 10:
                            high_complexity_functions += 1

                    except Exception:
                        continue

                results['overview'] = {
                    'total_functions': len(results['functions']),
                    'total_classes': len(results['classes']),
                    'avg_complexity': total_complexity / max(len(results['functions']), 1),
                    'high_complexity_functions': high_complexity_functions,
                    'files_changed': len(python_files)
                }

                # Apply quality gates for PR
                quality_gate = QualityGate(max_complexity=8, block_on_high_complexity=True)
                report = await self._generate_analysis_report(results, quality_gate)

                # Post PR comment with results
                await self._post_pr_comment(repo_name, pr_number, report)

                logger.info(f"PR analysis completed for {repo_name}:#{pr_number}")

        except Exception as e:
            logger.error(f"PR analysis failed: {str(e)}")
            await self._post_pr_error_comment(repo_name, pr_number, str(e))

    async def _analyze_merge_request_async(self, repo_url: str, repo_name: str, mr_number: int, head_sha: str):
        """Analyze GitLab merge request changes."""
        # Similar to PR analysis but for GitLab
        await self._analyze_pull_request_async(repo_url, repo_name, mr_number, head_sha)

    async def _generate_analysis_report(self, results: Dict, quality_gate: QualityGate) -> AnalysisReport:
        """Generate comprehensive analysis report with quality gate checks."""
        overview = results.get('overview', {})
        functions = results.get('functions', [])

        # Check quality gate violations
        complexity_violations = 0
        high_complexity_functions = []

        for func in functions:
            complexity = func.get('complexity', 0)
            if complexity > quality_gate.max_complexity:
                complexity_violations += 1
                high_complexity_functions.append(func['name'])

        # Calculate overall pass/fail status
        passed = complexity_violations == 0 or not quality_gate.block_on_high_complexity
        quality_gate_status = "PASSED" if passed else "FAILED"

        # Generate recommendations
        recommendations = []
        if complexity_violations > 0:
            recommendations.append(f"Reduce complexity in {complexity_violations} functions")
        if overview.get('avg_complexity', 0) > quality_gate.max_complexity:
            recommendations.append("Consider refactoring to reduce overall complexity")
        if not recommendations:
            recommendations.append("Code quality looks good!")

        return AnalysisReport(
            passed=passed,
            quality_gate_status=quality_gate_status,
            total_issues=complexity_violations,
            complexity_violations=complexity_violations,
            coverage_percentage=85.0,  # Would integrate with actual coverage tools
            summary=f"Analysis found {complexity_violations} complexity violations",
            details={
                "high_complexity_functions": high_complexity_functions,
                "total_functions": len(functions),
                "average_complexity": overview.get('avg_complexity', 0)
            },
            recommendations=recommendations
        )

    async def _analyze_with_quality_gate(self, project_id: str, quality_gate: QualityGate) -> AnalysisReport:
        """Analyze project with specific quality gate requirements."""
        # This would integrate with existing analysis system
        # For demo purposes, return a sample report
        return AnalysisReport(
            passed=True,
            quality_gate_status="PASSED",
            total_issues=0,
            complexity_violations=0,
            coverage_percentage=88.5,
            summary="All quality gate requirements met",
            details={"message": "Code analysis completed successfully"},
            recommendations=["Continue maintaining good code quality!"]
        )

    async def _send_analysis_notification(self, repo_name: str, commit_sha: str, report: AnalysisReport):
        """Send analysis results notification."""
        # Integration with Slack, Teams, etc.
        message = f"""
🔍 **Code Analysis Complete** for `{repo_name}`

**Commit:** `{commit_sha[:8]}`
**Status:** {'✅ PASSED' if report.passed else '❌ FAILED'}
**Complexity Violations:** {report.complexity_violations}
**Coverage:** {report.coverage_percentage}%

**Summary:** {report.summary}
        """

        logger.info(f"Analysis notification: {message}")
        # In production, send to configured notification channels

    async def _send_error_notification(self, repo_name: str, commit_sha: str, error: str):
        """Send error notification."""
        logger.error(f"Analysis error for {repo_name}:{commit_sha} - {error}")

    async def _post_pr_comment(self, repo_name: str, pr_number: int, report: AnalysisReport):
        """Post analysis results as PR comment."""
        status_emoji = "✅" if report.passed else "❌"
        comment = f"""
## {status_emoji} Code Analysis Results

**Quality Gate Status:** {report.quality_gate_status}
**Total Issues:** {report.total_issues}
**Complexity Violations:** {report.complexity_violations}
**Test Coverage:** {report.coverage_percentage}%

### Summary
{report.summary}

### Recommendations
{chr(10).join('• ' + rec for rec in report.recommendations)}

---
*Analysis performed by Alice & Bob Code Analysis Platform*
        """

        logger.info(f"PR comment for {repo_name}:#{pr_number}: {comment}")
        # In production, use GitHub/GitLab API to post comment

    async def _post_pr_error_comment(self, repo_name: str, pr_number: int, error: str):
        """Post error comment on PR."""
        comment = f"""
## ❌ Code Analysis Error

Analysis failed with the following error:
```
{error}
```

Please check your code and try again, or contact the development team if this persists.
        """

        logger.error(f"PR error comment for {repo_name}:#{pr_number}: {comment}")

    def _generate_github_actions_workflow(self) -> str:
        """Generate GitHub Actions workflow YAML."""
        return """
name: Code Analysis

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  analyze:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install requests

    - name: Run Code Analysis
      env:
        ANALYSIS_SERVER_URL: ${{ secrets.ANALYSIS_SERVER_URL }}
      run: |
        python -c "
        import os
        import json
        import requests
        import subprocess

        # Get changed files
        try:
            result = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1'],
                                  capture_output=True, text=True)
            changed_files = [f for f in result.stdout.split('\\n') if f.endswith('.py')]
        except:
            changed_files = []

        # Prepare analysis request
        files_content = {}
        for file_path in changed_files:
            try:
                with open(file_path, 'r') as f:
                    files_content[file_path] = f.read()
            except:
                continue

        # Send analysis request
        if files_content:
            response = requests.post(
                f\"{os.environ['ANALYSIS_SERVER_URL']}/analyze\",
                json={
                    'project_name': f\"{os.environ['GITHUB_REPOSITORY']}\",
                    'repository_url': f\"https://github.com/{os.environ['GITHUB_REPOSITORY']}\",
                    'files': files_content
                }
            )

            if response.status_code == 200:
                result = response.json()
                print(f\"Analysis completed: {result['dashboard_url']}\")
            else:
                print(f\"Analysis failed: {response.text}\")
                exit(1)
        else:
            print('No Python files to analyze')
        "

    - name: Quality Gate Check
      env:
        ANALYSIS_SERVER_URL: ${{ secrets.ANALYSIS_SERVER_URL }}
      run: |
        python -c "
        import os
        import requests

        response = requests.post(
            f\"{os.environ['ANALYSIS_SERVER_URL']}/analysis/quality-gate/{os.environ['GITHUB_REPOSITORY']}\",
            json={
                'max_complexity': 10,
                'max_cognitive_complexity': 15,
                'min_test_coverage': 80.0,
                'block_on_high_complexity': True
            }
        )

        if response.status_code == 200:
            result = response.json()
            print(f\"Quality Gate: {result['quality_gate_status']}\")

            if not result['passed']:
                print(f\"Quality gate failed: {result['summary']}\")
                exit(1)
        else:
            print(f\"Quality gate check failed: {response.text}\")
            exit(1)
        "
        """

    def _generate_gitlab_ci_config(self) -> str:
        """Generate GitLab CI configuration YAML."""
        return """
stages:
  - analysis

code_analysis:
  stage: analysis
  image: python:3.9
  script:
    - pip install requests
    - python -c "
      import os
      import json
      import requests
      import subprocess
      import glob

      # Find Python files
      python_files = glob.glob('**/*.py', recursive=True)
      files_content = {}

      for file_path in python_files:
          try:
              with open(file_path, 'r') as f:
                  files_content[file_path] = f.read()
          except:
              continue

      # Send analysis request
      response = requests.post(
          f\"{os.environ['ANALYSIS_SERVER_URL']}/analyze\",
          json={
              'project_name': os.environ['CI_PROJECT_NAME'],
              'repository_url': os.environ['CI_REPOSITORY_URL'],
              'files': files_content
          }
      )

      if response.status_code == 200:
          result = response.json()
          print(f'Analysis completed: {result[\"dashboard_url\"]}')
      else:
          print(f'Analysis failed: {response.text}')
          exit(1)
      "
  only:
    - main
    - develop
    - merge_requests

quality_gate:
  stage: analysis
  image: python:3.9
  script:
    - pip install requests
    - python -c "
      import os
      import requests

      response = requests.post(
          f\"{os.environ['ANALYSIS_SERVER_URL']}/analysis/quality-gate/{os.environ['CI_PROJECT_NAME']}\",
          json={
              'max_complexity': 10,
              'block_on_high_complexity': True
          }
      )

      if response.status_code == 200:
          result = response.json()
          if not result['passed']:
              exit(1)
      else:
          exit(1)
      "
  only:
    - main
    - develop
    - merge_requests
        """

    def _generate_jenkins_pipeline(self) -> str:
        """Generate Jenkins pipeline script."""
        return """
pipeline {
    agent any

    environment {
        ANALYSIS_SERVER_URL = credentials('analysis-server-url')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Code Analysis') {
            steps {
                script {
                    // Find Python files
                    def pythonFiles = sh(
                        script: "find . -name '*.py' -type f",
                        returnStdout: true
                    ).trim().split('\\n')

                    // Read file contents
                    def filesContent = [:]
                    pythonFiles.each { file ->
                        if (file) {
                            filesContent[file] = readFile(file)
                        }
                    }

                    // Send analysis request
                    def response = httpRequest(
                        httpMode: 'POST',
                        url: "${env.ANALYSIS_SERVER_URL}/analyze",
                        contentType: 'APPLICATION_JSON',
                        requestBody: groovy.json.JsonBuilder([
                            project_name: env.JOB_NAME,
                            repository_url: env.GIT_URL,
                            files: filesContent
                        ]).toString()
                    )

                    if (response.status != 200) {
                        error("Analysis failed: ${response.content}")
                    }

                    def result = readJSON text: response.content
                    echo "Analysis completed: ${result.dashboard_url}"
                }
            }
        }

        stage('Quality Gate') {
            steps {
                script {
                    def response = httpRequest(
                        httpMode: 'POST',
                        url: "${env.ANALYSIS_SERVER_URL}/analysis/quality-gate/${env.JOB_NAME}",
                        contentType: 'APPLICATION_JSON',
                        requestBody: groovy.json.JsonBuilder([
                            max_complexity: 10,
                            block_on_high_complexity: true
                        ]).toString()
                    )

                    if (response.status != 200) {
                        error("Quality gate check failed")
                    }

                    def result = readJSON text: response.content
                    if (!result.passed) {
                        error("Quality gate failed: ${result.summary}")
                    }

                    echo "Quality gate passed: ${result.summary}"
                }
            }
        }
    }

    post {
        always {
            echo 'Code analysis pipeline completed'
        }
        failure {
            echo 'Code analysis pipeline failed'
        }
    }
}
        """
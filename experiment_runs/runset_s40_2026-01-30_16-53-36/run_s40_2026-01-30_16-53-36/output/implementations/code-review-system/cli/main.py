"""
Command Line Interface for Collaborative Code Review System

Provides the main entry point and user interaction layer for the code review system.
Integrates all components and provides a clean CLI experience.

Designed by Alice as part of AI-to-AI collaboration framework testing.
"""

import click
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
import json
import time
from datetime import datetime

# Import our components (relative imports for the package structure)
try:
    from ..workflow.orchestrator import WorkflowOrchestrator, AnalysisType
    from ..workflow.config_manager import ConfigurationManager, init_config_command, validate_config_command
    from ..reporting.formatters import ReportManager, ReviewSummary, Finding
except ImportError:
    # For testing when run directly
    import os
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    from workflow.orchestrator import WorkflowOrchestrator, AnalysisType
    from workflow.config_manager import ConfigurationManager, init_config_command, validate_config_command
    from reporting.formatters import ReportManager, ReviewSummary, Finding


@click.group()
@click.version_option(version="1.0.0")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to configuration file')
@click.pass_context
def cli(ctx, verbose: bool, config: Optional[str]):
    """
    Collaborative Code Review System

    A tool for analyzing code quality, security, and best practices.
    Built through AI-to-AI collaboration between Alice and Bob.

    Examples:
        code-review analyze ./src
        code-review analyze file.py --format html
        code-review config init --format yaml
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['config_path'] = config

    if verbose:
        click.echo("🔧 Verbose mode enabled")


@cli.group()
def config():
    """Configuration management commands"""
    pass


@config.command('init')
@click.option('--format', 'format_type', type=click.Choice(['json', 'yaml', 'toml']),
              default='yaml', help='Configuration file format')
@click.option('--path', type=click.Path(), help='Path for configuration file')
@click.option('--force', is_flag=True, help='Overwrite existing configuration')
def config_init(format_type: str, path: Optional[str], force: bool):
    """Initialize a new configuration file"""
    try:
        if path:
            config_path = Path(path)
        else:
            config_path = Path.cwd() / f".code-review.{format_type}"

        if config_path.exists() and not force:
            click.echo(f"❌ Configuration file already exists: {config_path}")
            click.echo("Use --force to overwrite")
            sys.exit(1)

        init_config_command(format_type, str(config_path))
        click.echo(f"✅ Configuration file created: {config_path}")

    except Exception as e:
        click.echo(f"❌ Failed to create configuration: {e}")
        sys.exit(1)


@config.command('validate')
@click.option('--path', type=click.Path(exists=True), help='Path to configuration file')
def config_validate(path: Optional[str]):
    """Validate a configuration file"""
    try:
        is_valid = validate_config_command(path)
        if is_valid:
            click.echo("✅ Configuration is valid")
        else:
            click.echo("❌ Configuration has errors")
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Validation failed: {e}")
        sys.exit(1)


@config.command('show')
@click.option('--path', type=click.Path(exists=True), help='Path to configuration file')
@click.option('--format', 'output_format', type=click.Choice(['json', 'yaml']),
              default='yaml', help='Output format')
@click.pass_context
def config_show(ctx, path: Optional[str], output_format: str):
    """Show current configuration"""
    try:
        config_manager = ConfigurationManager()
        config_path = Path(path) if path else None
        config = config_manager.load_config(config_path)

        if output_format == 'json':
            import json
            config_dict = config_manager._config_to_dict(config)
            click.echo(json.dumps(config_dict, indent=2))
        else:
            import yaml
            config_dict = config_manager._config_to_dict(config)
            click.echo(yaml.dump(config_dict, default_flow_style=False))

    except Exception as e:
        click.echo(f"❌ Failed to show configuration: {e}")
        sys.exit(1)


@cli.command()
@click.argument('paths', nargs=-1, required=True, type=click.Path(exists=True))
@click.option('--format', 'output_format', type=click.Choice(['json', 'yaml', 'text', 'html']),
              default='text', help='Output format')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--severity', type=click.Choice(['error', 'warning', 'info', 'style']),
              help='Minimum severity level')
@click.option('--include', multiple=True,
              type=click.Choice(['static_analysis', 'complexity', 'security', 'best_practices', 'style']),
              help='Analysis types to include')
@click.option('--exclude', multiple=True,
              type=click.Choice(['static_analysis', 'complexity', 'security', 'best_practices', 'style']),
              help='Analysis types to exclude')
@click.option('--wait/--no-wait', default=True, help='Wait for analysis to complete')
@click.pass_context
def analyze(ctx, paths: tuple, output_format: str, output: Optional[str],
           severity: Optional[str], include: tuple, exclude: tuple, wait: bool):
    """
    Analyze code files or directories

    PATHS: Files or directories to analyze

    Examples:
        code-review analyze ./src
        code-review analyze file1.py file2.py --format json
        code-review analyze . --output report.html --format html
        code-review analyze . --include security complexity
    """
    try:
        verbose = ctx.obj.get('verbose', False)
        config_path = ctx.obj.get('config_path')

        if verbose:
            click.echo(f"🔍 Analyzing {len(paths)} path(s)")

        # Load configuration
        config_manager = ConfigurationManager()
        config_file_path = Path(config_path) if config_path else None
        config = config_manager.load_config(config_file_path)

        # Override configuration with CLI options
        config = _apply_cli_overrides(config, severity, include, exclude, output_format)

        # Collect all files to analyze
        files_to_analyze = _collect_files(paths, verbose)

        if not files_to_analyze:
            click.echo("❌ No files found to analyze")
            sys.exit(1)

        if verbose:
            click.echo(f"📁 Found {len(files_to_analyze)} files to analyze")

        # Create orchestrator and submit review
        orchestrator = WorkflowOrchestrator(config_manager._config_to_dict(config))

        # TODO: This is where Bob's analysis engines would be registered
        # For now, we'll create mock engines for demonstration
        _register_mock_engines(orchestrator, verbose)

        # Submit review
        request_id = orchestrator.submit_review(files_to_analyze)

        if verbose:
            click.echo(f"🚀 Submitted review request: {request_id}")

        if wait:
            # Wait for completion with progress updates
            _wait_for_completion(orchestrator, request_id, verbose)

            # Get results and generate report
            results = orchestrator.get_review_results(request_id)
            if results:
                _generate_and_output_report(results, output_format, output, verbose)
            else:
                click.echo("❌ Failed to get review results")
                sys.exit(1)
        else:
            click.echo(f"🔄 Analysis running in background. Request ID: {request_id}")
            click.echo(f"Use 'code-review status {request_id}' to check progress")

    except Exception as e:
        click.echo(f"❌ Analysis failed: {e}")
        if ctx.obj.get('verbose'):
            import traceback
            traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.argument('request_id', required=True)
@click.pass_context
def status(ctx, request_id: str):
    """Check the status of a running analysis"""
    try:
        verbose = ctx.obj.get('verbose', False)

        # Load configuration to create orchestrator
        config_manager = ConfigurationManager()
        config = config_manager.load_config()

        orchestrator = WorkflowOrchestrator(config_manager._config_to_dict(config))

        status_info = orchestrator.get_review_status(request_id)

        if not status_info:
            click.echo(f"❌ Request not found: {request_id}")
            sys.exit(1)

        click.echo(f"📊 Status for request {request_id}:")
        click.echo(f"   Stage: {status_info['stage']}")
        click.echo(f"   Files: {status_info['files_count']}")
        click.echo(f"   Analyses completed: {status_info['analyses_completed']}")
        click.echo(f"   Submitted: {status_info['submitted_at']}")

        if verbose and status_info.get('metadata'):
            click.echo(f"   Metadata: {json.dumps(status_info['metadata'], indent=2)}")

    except Exception as e:
        click.echo(f"❌ Failed to get status: {e}")
        sys.exit(1)


@cli.command()
@click.argument('request_id', required=True)
@click.option('--format', 'output_format', type=click.Choice(['json', 'yaml', 'text', 'html']),
              default='text', help='Output format')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.pass_context
def results(ctx, request_id: str, output_format: str, output: Optional[str]):
    """Get results for a completed analysis"""
    try:
        verbose = ctx.obj.get('verbose', False)

        # Load configuration to create orchestrator
        config_manager = ConfigurationManager()
        config = config_manager.load_config()

        orchestrator = WorkflowOrchestrator(config_manager._config_to_dict(config))

        results = orchestrator.get_review_results(request_id)

        if not results:
            click.echo(f"❌ No results available for request: {request_id}")
            click.echo("Check that the analysis is complete using 'code-review status'")
            sys.exit(1)

        _generate_and_output_report(results, output_format, output, verbose)

    except Exception as e:
        click.echo(f"❌ Failed to get results: {e}")
        sys.exit(1)


def _apply_cli_overrides(config, severity, include, exclude, output_format):
    """Apply CLI option overrides to configuration"""
    config_dict = config.__dict__.copy()

    # Apply severity filter
    if severity:
        for analysis in ['static_analysis', 'complexity', 'security', 'best_practices', 'style']:
            getattr(config, analysis).severity_threshold = severity

    # Apply include/exclude filters
    if include:
        # Disable all, then enable only included
        for analysis in ['static_analysis', 'complexity', 'security', 'best_practices', 'style']:
            getattr(config, analysis).enabled = analysis in include
    elif exclude:
        # Enable all except excluded
        for analysis in exclude:
            getattr(config, analysis).enabled = False

    # Apply output format
    config.output.format = output_format

    return config


def _collect_files(paths: tuple, verbose: bool) -> List[Path]:
    """Collect all files to analyze from given paths"""
    files = []
    supported_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs'}

    for path_str in paths:
        path = Path(path_str)

        if path.is_file():
            if path.suffix in supported_extensions:
                files.append(path)
            elif verbose:
                click.echo(f"⚠️  Skipping unsupported file: {path}")
        elif path.is_dir():
            for file_path in path.rglob('*'):
                if file_path.is_file() and file_path.suffix in supported_extensions:
                    files.append(file_path)
        elif verbose:
            click.echo(f"⚠️  Path not found: {path}")

    return files


def _register_mock_engines(orchestrator: WorkflowOrchestrator, verbose: bool):
    """Register mock analysis engines for demonstration"""
    # TODO: Replace with actual engine registration when Bob's engines are ready
    from ..workflow.orchestrator import AnalysisResult

    class MockEngine:
        def __init__(self, analysis_type: AnalysisType):
            self.analysis_type = analysis_type

        def analyze(self, files: List[Path], config: Dict[str, Any]) -> AnalysisResult:
            # Mock analysis with some fake findings
            findings = [
                {
                    "file_path": str(files[0]),
                    "line_number": 10,
                    "severity": "warning",
                    "category": self.analysis_type.value,
                    "rule_id": f"MOCK-{self.analysis_type.value.upper()}-001",
                    "message": f"Mock {self.analysis_type.value} finding",
                    "description": f"This is a mock finding from {self.analysis_type.value} analysis"
                }
            ] if files else []

            return AnalysisResult(
                analysis_type=self.analysis_type,
                findings=findings,
                metadata={"mock": True},
                execution_time=0.1,
                success=True
            )

        def get_supported_languages(self) -> List[str]:
            return ["python", "javascript", "typescript", "java"]

    # Register mock engines
    for analysis_type in AnalysisType:
        engine = MockEngine(analysis_type)
        orchestrator.register_analysis_engine(analysis_type, engine)
        if verbose:
            click.echo(f"🔌 Registered mock {analysis_type.value} engine")


def _wait_for_completion(orchestrator: WorkflowOrchestrator, request_id: str, verbose: bool):
    """Wait for analysis completion with progress updates"""
    click.echo("⏳ Analysis in progress...")

    with click.progressbar(length=100, label='Analyzing') as bar:
        last_stage = ""
        progress = 0

        while True:
            status = orchestrator.get_review_status(request_id)

            if not status:
                click.echo("\n❌ Lost track of analysis")
                break

            current_stage = status['stage']

            # Update progress based on stage
            stage_progress = {
                'submitted': 10,
                'preprocessing': 25,
                'analysis': 75,
                'aggregation': 90,
                'reporting': 95,
                'completed': 100,
                'failed': 0
            }

            new_progress = stage_progress.get(current_stage, progress)
            if new_progress > progress:
                bar.update(new_progress - progress)
                progress = new_progress

            if current_stage != last_stage:
                if verbose:
                    click.echo(f"\n🔄 Stage: {current_stage}")
                last_stage = current_stage

            if current_stage in ['completed', 'failed']:
                break

            time.sleep(0.5)

        if current_stage == 'completed':
            if progress < 100:
                bar.update(100 - progress)
            click.echo("\n✅ Analysis completed!")
        else:
            click.echo(f"\n❌ Analysis failed at stage: {current_stage}")


def _generate_and_output_report(results, output_format: str, output: Optional[str], verbose: bool):
    """Generate and output the final report"""
    from ..reporting.formatters import ReportManager, ReviewSummary, Finding

    # Convert results to report format
    summary = ReviewSummary(
        request_id=results.request_id,
        files_reviewed=[str(f) for f in results.files],
        total_findings=results.metadata.get('total_findings', 0),
        findings_by_severity=results.metadata.get('analysis_summary', {}).get('severity_breakdown', {}),
        findings_by_category=results.metadata.get('analysis_summary', {}).get('category_breakdown', {}),
        analysis_types_run=[r.analysis_type.value for r in results.results if r.success],
        execution_time=sum(r.execution_time or 0 for r in results.results),
        completed_at=datetime.now(),
        configuration_used=results.configuration
    )

    # Convert findings
    findings = []
    for result in results.results:
        for finding_dict in result.findings:
            finding = Finding(
                file_path=finding_dict.get('file_path', ''),
                line_number=finding_dict.get('line_number', 0),
                column=finding_dict.get('column'),
                severity=finding_dict.get('severity', 'info'),
                category=finding_dict.get('category', ''),
                rule_id=finding_dict.get('rule_id', ''),
                message=finding_dict.get('message', ''),
                description=finding_dict.get('description'),
                suggestion=finding_dict.get('suggestion'),
                analysis_type=result.analysis_type.value
            )
            findings.append(finding)

    # Generate report
    report_manager = ReportManager()

    if output:
        output_path = Path(output)
        saved_path = report_manager.save_report(summary, findings, output_path, output_format)
        if verbose:
            click.echo(f"📄 Report saved to: {saved_path}")
        else:
            click.echo(f"Report saved to: {saved_path}")
    else:
        report_content = report_manager.generate_report(summary, findings, output_format)
        click.echo(report_content)


if __name__ == '__main__':
    cli()
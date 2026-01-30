"""
Workflow Orchestrator for Collaborative Code Review System

This module manages the overall review process, coordinating different analysis
types and managing the flow from code submission to final report.

Designed by Alice as part of AI-to-AI collaboration framework testing.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Protocol
import json
import logging
from datetime import datetime


class ReviewStage(Enum):
    """Stages in the code review workflow"""
    SUBMITTED = "submitted"
    PREPROCESSING = "preprocessing"
    ANALYSIS = "analysis"
    AGGREGATION = "aggregation"
    REPORTING = "reporting"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisType(Enum):
    """Types of analysis that can be performed"""
    STATIC_ANALYSIS = "static_analysis"
    COMPLEXITY = "complexity"
    SECURITY = "security"
    BEST_PRACTICES = "best_practices"
    STYLE = "style"


@dataclass
class AnalysisResult:
    """Result from a single analysis type"""
    analysis_type: AnalysisType
    findings: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None


@dataclass
class ReviewRequest:
    """Container for a code review request"""
    request_id: str
    files: List[Path]
    configuration: Dict[str, Any]
    language: Optional[str] = None
    framework: Optional[str] = None
    submitted_at: datetime = field(default_factory=datetime.now)
    current_stage: ReviewStage = ReviewStage.SUBMITTED
    results: List[AnalysisResult] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AnalysisEngine(Protocol):
    """Protocol for analysis engines (to be implemented by Bob)"""

    def analyze(self, files: List[Path], config: Dict[str, Any]) -> AnalysisResult:
        """Run analysis on the given files with specified configuration"""
        ...

    def get_supported_languages(self) -> List[str]:
        """Return list of supported programming languages"""
        ...


class WorkflowOrchestrator:
    """
    Orchestrates the entire code review workflow.

    This is Alice's component that will coordinate with Bob's analysis engines
    through well-defined interfaces.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_default_config()
        self.analysis_engines: Dict[AnalysisType, AnalysisEngine] = {}
        self.active_reviews: Dict[str, ReviewRequest] = {}
        self.logger = logging.getLogger(__name__)

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def register_analysis_engine(self, analysis_type: AnalysisType, engine: AnalysisEngine):
        """Register an analysis engine for a specific type of analysis"""
        self.analysis_engines[analysis_type] = engine
        self.logger.info(f"Registered {analysis_type.value} analysis engine")

    def submit_review(self, files: List[Path], config: Optional[Dict[str, Any]] = None) -> str:
        """
        Submit files for review and return a request ID for tracking.

        This is the main entry point for the review system.
        """
        request_id = self._generate_request_id()
        review_config = {**self.config, **(config or {})}

        request = ReviewRequest(
            request_id=request_id,
            files=files,
            configuration=review_config
        )

        self.active_reviews[request_id] = request
        self.logger.info(f"Submitted review request {request_id} for {len(files)} files")

        # Start the review process asynchronously
        self._process_review(request_id)

        return request_id

    def get_review_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a review request"""
        if request_id not in self.active_reviews:
            return None

        request = self.active_reviews[request_id]
        return {
            "request_id": request_id,
            "stage": request.current_stage.value,
            "files_count": len(request.files),
            "analyses_completed": len(request.results),
            "submitted_at": request.submitted_at.isoformat(),
            "metadata": request.metadata
        }

    def get_review_results(self, request_id: str) -> Optional[ReviewRequest]:
        """Get complete results for a finished review"""
        if request_id not in self.active_reviews:
            return None

        request = self.active_reviews[request_id]
        if request.current_stage not in [ReviewStage.COMPLETED, ReviewStage.FAILED]:
            return None

        return request

    def _process_review(self, request_id: str):
        """
        Main workflow processing logic.

        This coordinates all the stages of review processing.
        """
        request = self.active_reviews[request_id]

        try:
            # Stage 1: Preprocessing
            self._update_stage(request, ReviewStage.PREPROCESSING)
            self._preprocess_files(request)

            # Stage 2: Analysis
            self._update_stage(request, ReviewStage.ANALYSIS)
            self._run_analyses(request)

            # Stage 3: Aggregation
            self._update_stage(request, ReviewStage.AGGREGATION)
            self._aggregate_results(request)

            # Stage 4: Reporting
            self._update_stage(request, ReviewStage.REPORTING)
            self._generate_report(request)

            # Completion
            self._update_stage(request, ReviewStage.COMPLETED)
            self.logger.info(f"Review {request_id} completed successfully")

        except Exception as e:
            self.logger.error(f"Review {request_id} failed: {str(e)}")
            self._update_stage(request, ReviewStage.FAILED)
            request.metadata["error"] = str(e)

    def _update_stage(self, request: ReviewRequest, stage: ReviewStage):
        """Update the current stage of a review request"""
        request.current_stage = stage
        request.metadata["stage_updated_at"] = datetime.now().isoformat()
        self.logger.info(f"Review {request.request_id} moved to stage: {stage.value}")

    def _preprocess_files(self, request: ReviewRequest):
        """
        Preprocess files to extract metadata and prepare for analysis.

        This includes language detection, file validation, and metadata extraction.
        """
        valid_files = []
        total_lines = 0

        for file_path in request.files:
            if not file_path.exists():
                self.logger.warning(f"File not found: {file_path}")
                continue

            # Detect language from file extension
            if not request.language:
                request.language = self._detect_language(file_path)

            # Count lines for complexity estimation
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                    total_lines += lines
                valid_files.append(file_path)
            except Exception as e:
                self.logger.warning(f"Could not read file {file_path}: {e}")

        request.files = valid_files
        request.metadata.update({
            "total_lines": total_lines,
            "file_count": len(valid_files),
            "detected_language": request.language
        })

        self.logger.info(f"Preprocessed {len(valid_files)} files, {total_lines} total lines")

    def _run_analyses(self, request: ReviewRequest):
        """
        Run all configured analysis types on the files.

        This is where we interface with Bob's analysis engines.
        """
        enabled_analyses = request.configuration.get("enabled_analyses", list(AnalysisType))

        for analysis_type in enabled_analyses:
            if analysis_type not in self.analysis_engines:
                self.logger.warning(f"No engine registered for {analysis_type.value}")
                continue

            engine = self.analysis_engines[analysis_type]

            try:
                start_time = datetime.now()
                result = engine.analyze(request.files, request.configuration)
                end_time = datetime.now()

                result.execution_time = (end_time - start_time).total_seconds()
                request.results.append(result)

                self.logger.info(f"Completed {analysis_type.value} analysis in {result.execution_time:.2f}s")

            except Exception as e:
                error_result = AnalysisResult(
                    analysis_type=analysis_type,
                    findings=[],
                    success=False,
                    error_message=str(e)
                )
                request.results.append(error_result)
                self.logger.error(f"Analysis {analysis_type.value} failed: {e}")

    def _aggregate_results(self, request: ReviewRequest):
        """
        Aggregate and prioritize findings from all analyses.

        This combines results and resolves any conflicts or duplicates.
        """
        all_findings = []
        analysis_summary = {}

        for result in request.results:
            if result.success:
                all_findings.extend(result.findings)
                analysis_summary[result.analysis_type.value] = {
                    "findings_count": len(result.findings),
                    "execution_time": result.execution_time
                }
            else:
                analysis_summary[result.analysis_type.value] = {
                    "error": result.error_message
                }

        # Sort findings by severity/priority
        prioritized_findings = self._prioritize_findings(all_findings)

        request.metadata.update({
            "analysis_summary": analysis_summary,
            "total_findings": len(all_findings),
            "prioritized_findings": prioritized_findings[:20]  # Top 20 for summary
        })

        self.logger.info(f"Aggregated {len(all_findings)} findings from {len(request.results)} analyses")

    def _generate_report(self, request: ReviewRequest):
        """
        Generate the final formatted report.

        This will be expanded to support multiple output formats.
        """
        # For now, store report in metadata - later this could be a separate file
        report = {
            "summary": {
                "request_id": request.request_id,
                "files_reviewed": len(request.files),
                "total_findings": request.metadata.get("total_findings", 0),
                "review_completed_at": datetime.now().isoformat()
            },
            "analysis_results": request.metadata.get("analysis_summary", {}),
            "top_findings": request.metadata.get("prioritized_findings", [])
        }

        request.metadata["final_report"] = report
        self.logger.info(f"Generated report for request {request.request_id}")

    def _prioritize_findings(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize findings by severity and impact"""
        # Simple prioritization - can be enhanced
        severity_order = {"error": 3, "warning": 2, "info": 1}

        return sorted(
            findings,
            key=lambda f: severity_order.get(f.get("severity", "info"), 0),
            reverse=True
        )

    def _detect_language(self, file_path: Path) -> Optional[str]:
        """Detect programming language from file extension"""
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".go": "go",
            ".rs": "rust"
        }
        return extension_map.get(file_path.suffix.lower())

    def _generate_request_id(self) -> str:
        """Generate a unique request ID"""
        from uuid import uuid4
        return str(uuid4())[:8]

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration"""
        return {
            "enabled_analyses": [
                AnalysisType.STATIC_ANALYSIS,
                AnalysisType.COMPLEXITY,
                AnalysisType.SECURITY,
                AnalysisType.STYLE
            ],
            "output_format": "json",
            "severity_threshold": "info",
            "max_findings_per_type": 50
        }


# Example usage and testing functions
def create_test_orchestrator():
    """Create an orchestrator for testing purposes"""
    return WorkflowOrchestrator()


if __name__ == "__main__":
    # Simple test
    orchestrator = create_test_orchestrator()
    print(f"Created orchestrator with config: {orchestrator.config}")
    print(f"Registered engines: {list(orchestrator.analysis_engines.keys())}")
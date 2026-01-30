"""
Configuration Management for Collaborative Code Review System

Handles loading, validating, and managing configuration for code review workflows.
Supports multiple formats and user-specific overrides.

Designed by Alice as part of AI-to-AI collaboration framework testing.
"""

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import json
import yaml
import toml
import os
from enum import Enum


class ConfigFormat(Enum):
    """Supported configuration file formats"""
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"


class SeverityLevel(Enum):
    """Severity levels for findings"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    STYLE = "style"


@dataclass
class AnalysisConfig:
    """Configuration for individual analysis types"""
    enabled: bool = True
    severity_threshold: SeverityLevel = SeverityLevel.INFO
    max_findings: int = 50
    custom_rules: Dict[str, Any] = None
    exclude_patterns: List[str] = None

    def __post_init__(self):
        if self.custom_rules is None:
            self.custom_rules = {}
        if self.exclude_patterns is None:
            self.exclude_patterns = []


@dataclass
class OutputConfig:
    """Configuration for output formatting and reporting"""
    format: str = "json"  # json, yaml, text, html
    include_source_code: bool = True
    max_context_lines: int = 3
    group_by_file: bool = True
    include_statistics: bool = True


@dataclass
class WorkflowConfig:
    """Configuration for workflow execution"""
    parallel_analysis: bool = True
    timeout_seconds: int = 300
    cache_results: bool = True
    auto_fix_enabled: bool = False


@dataclass
class ReviewConfig:
    """Complete configuration for code review system"""
    # Analysis configurations
    static_analysis: AnalysisConfig = None
    complexity: AnalysisConfig = None
    security: AnalysisConfig = None
    best_practices: AnalysisConfig = None
    style: AnalysisConfig = None

    # Output configuration
    output: OutputConfig = None

    # Workflow configuration
    workflow: WorkflowConfig = None

    # Language-specific settings
    language_configs: Dict[str, Dict[str, Any]] = None

    # Global settings
    global_exclude_patterns: List[str] = None
    custom_rule_paths: List[str] = None

    def __post_init__(self):
        # Initialize with defaults if not provided
        if self.static_analysis is None:
            self.static_analysis = AnalysisConfig()
        if self.complexity is None:
            self.complexity = AnalysisConfig()
        if self.security is None:
            self.security = AnalysisConfig()
        if self.best_practices is None:
            self.best_practices = AnalysisConfig()
        if self.style is None:
            self.style = AnalysisConfig()
        if self.output is None:
            self.output = OutputConfig()
        if self.workflow is None:
            self.workflow = WorkflowConfig()
        if self.language_configs is None:
            self.language_configs = {}
        if self.global_exclude_patterns is None:
            self.global_exclude_patterns = [
                "*.pyc", "*.pyo", "__pycache__/",
                "node_modules/", ".git/", ".venv/",
                "*.min.js", "*.bundle.js"
            ]
        if self.custom_rule_paths is None:
            self.custom_rule_paths = []


class ConfigurationManager:
    """
    Manages loading, saving, and merging of configuration for the review system.

    Supports hierarchical configuration with user overrides, project-specific
    settings, and language-specific configurations.
    """

    def __init__(self, base_config_dir: Optional[Path] = None):
        self.base_config_dir = base_config_dir or Path.home() / ".code-review"
        self.base_config_dir.mkdir(exist_ok=True)

        # Configuration search paths (in priority order)
        self.config_search_paths = [
            Path.cwd() / ".code-review.json",          # Project-specific
            Path.cwd() / ".code-review.yaml",         # Project-specific
            Path.cwd() / ".code-review.toml",         # Project-specific
            self.base_config_dir / "config.json",     # User-specific
            self.base_config_dir / "config.yaml",     # User-specific
            self.base_config_dir / "config.toml",     # User-specific
        ]

    def load_config(self, config_path: Optional[Path] = None) -> ReviewConfig:
        """
        Load configuration from file or use defaults.

        If config_path is provided, use that file. Otherwise, search for
        configuration files in the standard locations.
        """
        if config_path:
            return self._load_config_file(config_path)

        # Search for configuration files
        for path in self.config_search_paths:
            if path.exists():
                try:
                    config = self._load_config_file(path)
                    print(f"Loaded configuration from: {path}")
                    return config
                except Exception as e:
                    print(f"Warning: Could not load config from {path}: {e}")
                    continue

        # No configuration file found, use defaults
        print("No configuration file found, using defaults")
        return ReviewConfig()

    def save_config(self, config: ReviewConfig, path: Path, format: ConfigFormat = ConfigFormat.JSON):
        """Save configuration to file in specified format"""
        path.parent.mkdir(parents=True, exist_ok=True)

        config_dict = self._config_to_dict(config)

        if format == ConfigFormat.JSON:
            with open(path, 'w') as f:
                json.dump(config_dict, f, indent=2)
        elif format == ConfigFormat.YAML:
            with open(path, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
        elif format == ConfigFormat.TOML:
            with open(path, 'w') as f:
                toml.dump(config_dict, f)

        print(f"Configuration saved to: {path}")

    def merge_configs(self, base_config: ReviewConfig, override_config: Dict[str, Any]) -> ReviewConfig:
        """
        Merge override configuration into base configuration.

        This allows for partial configuration updates without replacing
        the entire configuration.
        """
        base_dict = self._config_to_dict(base_config)
        merged_dict = self._deep_merge(base_dict, override_config)
        return self._dict_to_config(merged_dict)

    def validate_config(self, config: ReviewConfig) -> List[str]:
        """
        Validate configuration and return list of issues.

        Returns empty list if configuration is valid.
        """
        issues = []

        # Validate severity thresholds
        for analysis_name in ["static_analysis", "complexity", "security", "best_practices", "style"]:
            analysis_config = getattr(config, analysis_name)
            if not isinstance(analysis_config.severity_threshold, SeverityLevel):
                issues.append(f"{analysis_name}.severity_threshold must be a valid SeverityLevel")

        # Validate output format
        valid_formats = ["json", "yaml", "text", "html"]
        if config.output.format not in valid_formats:
            issues.append(f"output.format must be one of: {valid_formats}")

        # Validate timeout
        if config.workflow.timeout_seconds <= 0:
            issues.append("workflow.timeout_seconds must be positive")

        # Validate custom rule paths
        for rule_path in config.custom_rule_paths:
            if not Path(rule_path).exists():
                issues.append(f"Custom rule path does not exist: {rule_path}")

        return issues

    def get_language_config(self, config: ReviewConfig, language: str) -> Dict[str, Any]:
        """Get language-specific configuration merged with defaults"""
        base_config = {
            "file_extensions": [],
            "framework_patterns": {},
            "custom_rules": {},
            "style_guide": "default"
        }

        language_specific = config.language_configs.get(language, {})
        return {**base_config, **language_specific}

    def create_default_config_file(self, path: Path, format: ConfigFormat = ConfigFormat.JSON):
        """Create a default configuration file with comments"""
        default_config = ReviewConfig()

        if format == ConfigFormat.JSON:
            # For JSON, we'll create a template with comments in a separate file
            self.save_config(default_config, path, format)
            self._create_json_template(path.with_suffix(path.suffix + ".template"))

        elif format == ConfigFormat.YAML:
            self._create_yaml_template(path)

        else:
            self.save_config(default_config, path, format)

        print(f"Created default configuration file: {path}")

    def _load_config_file(self, path: Path) -> ReviewConfig:
        """Load configuration from a specific file"""
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        format = self._detect_format(path)

        with open(path, 'r') as f:
            if format == ConfigFormat.JSON:
                config_dict = json.load(f)
            elif format == ConfigFormat.YAML:
                config_dict = yaml.safe_load(f)
            elif format == ConfigFormat.TOML:
                config_dict = toml.load(f)
            else:
                raise ValueError(f"Unsupported configuration format: {format}")

        return self._dict_to_config(config_dict)

    def _detect_format(self, path: Path) -> ConfigFormat:
        """Detect configuration format from file extension"""
        suffix = path.suffix.lower()
        if suffix in [".json"]:
            return ConfigFormat.JSON
        elif suffix in [".yaml", ".yml"]:
            return ConfigFormat.YAML
        elif suffix in [".toml"]:
            return ConfigFormat.TOML
        else:
            raise ValueError(f"Cannot detect format for file: {path}")

    def _config_to_dict(self, config: ReviewConfig) -> Dict[str, Any]:
        """Convert ReviewConfig to dictionary"""
        result = asdict(config)

        # Convert enums to strings
        for analysis_name in ["static_analysis", "complexity", "security", "best_practices", "style"]:
            if analysis_name in result and "severity_threshold" in result[analysis_name]:
                result[analysis_name]["severity_threshold"] = result[analysis_name]["severity_threshold"].value

        return result

    def _dict_to_config(self, config_dict: Dict[str, Any]) -> ReviewConfig:
        """Convert dictionary to ReviewConfig"""
        # Convert string severity levels back to enums
        for analysis_name in ["static_analysis", "complexity", "security", "best_practices", "style"]:
            if analysis_name in config_dict and "severity_threshold" in config_dict[analysis_name]:
                threshold_str = config_dict[analysis_name]["severity_threshold"]
                config_dict[analysis_name]["severity_threshold"] = SeverityLevel(threshold_str)

        # Create nested objects
        for analysis_name in ["static_analysis", "complexity", "security", "best_practices", "style"]:
            if analysis_name in config_dict:
                config_dict[analysis_name] = AnalysisConfig(**config_dict[analysis_name])

        if "output" in config_dict:
            config_dict["output"] = OutputConfig(**config_dict["output"])

        if "workflow" in config_dict:
            config_dict["workflow"] = WorkflowConfig(**config_dict["workflow"])

        return ReviewConfig(**config_dict)

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _create_yaml_template(self, path: Path):
        """Create a YAML configuration template with comments"""
        template = '''# Code Review System Configuration

# Analysis configurations
static_analysis:
  enabled: true
  severity_threshold: "info"  # error, warning, info, style
  max_findings: 50
  custom_rules: {}
  exclude_patterns: []

complexity:
  enabled: true
  severity_threshold: "warning"
  max_findings: 20
  custom_rules:
    max_cyclomatic_complexity: 10
    max_function_length: 50

security:
  enabled: true
  severity_threshold: "error"
  max_findings: 100
  custom_rules: {}
  exclude_patterns: []

best_practices:
  enabled: true
  severity_threshold: "warning"
  max_findings: 30

style:
  enabled: true
  severity_threshold: "info"
  max_findings: 50

# Output configuration
output:
  format: "json"  # json, yaml, text, html
  include_source_code: true
  max_context_lines: 3
  group_by_file: true
  include_statistics: true

# Workflow configuration
workflow:
  parallel_analysis: true
  timeout_seconds: 300
  cache_results: true
  auto_fix_enabled: false

# Language-specific configurations
language_configs:
  python:
    style_guide: "pep8"
    max_line_length: 88
  javascript:
    style_guide: "airbnb"
    max_line_length: 100

# Global settings
global_exclude_patterns:
  - "*.pyc"
  - "*.pyo"
  - "__pycache__/"
  - "node_modules/"
  - ".git/"
  - ".venv/"
  - "*.min.js"
  - "*.bundle.js"

custom_rule_paths: []
'''

        with open(path, 'w') as f:
            f.write(template)

    def _create_json_template(self, path: Path):
        """Create a JSON configuration template with comments"""
        template = '''{
  "_comment": "Code Review System Configuration Template",

  "static_analysis": {
    "enabled": true,
    "severity_threshold": "info",
    "max_findings": 50,
    "custom_rules": {},
    "exclude_patterns": []
  },

  "complexity": {
    "enabled": true,
    "severity_threshold": "warning",
    "max_findings": 20,
    "custom_rules": {
      "max_cyclomatic_complexity": 10,
      "max_function_length": 50
    }
  },

  "output": {
    "format": "json",
    "include_source_code": true,
    "max_context_lines": 3,
    "group_by_file": true,
    "include_statistics": true
  },

  "workflow": {
    "parallel_analysis": true,
    "timeout_seconds": 300,
    "cache_results": true,
    "auto_fix_enabled": false
  },

  "global_exclude_patterns": [
    "*.pyc", "*.pyo", "__pycache__/",
    "node_modules/", ".git/", ".venv/"
  ]
}'''

        with open(path, 'w') as f:
            f.write(template)


# CLI helper functions for configuration management
def init_config_command(format_type: str = "yaml", path: Optional[str] = None):
    """Initialize a new configuration file"""
    config_manager = ConfigurationManager()

    if path:
        config_path = Path(path)
    else:
        config_path = Path.cwd() / f".code-review.{format_type}"

    format_enum = ConfigFormat(format_type.lower())
    config_manager.create_default_config_file(config_path, format_enum)


def validate_config_command(config_path: Optional[str] = None):
    """Validate a configuration file"""
    config_manager = ConfigurationManager()

    if config_path:
        config = config_manager.load_config(Path(config_path))
    else:
        config = config_manager.load_config()

    issues = config_manager.validate_config(config)

    if issues:
        print("Configuration validation failed:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("Configuration is valid")
        return True


if __name__ == "__main__":
    # Simple test
    config_manager = ConfigurationManager()
    config = config_manager.load_config()
    print(f"Loaded configuration with {len(config.global_exclude_patterns)} global exclude patterns")

    # Test validation
    issues = config_manager.validate_config(config)
    print(f"Configuration validation: {len(issues)} issues found")
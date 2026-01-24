#!/usr/bin/env python3
"""
Configuration System for Collaborative Code Analyzer

This module provides a flexible configuration system that allows users to
customize analysis behavior, output formatting, complexity thresholds,
and visualization options through configuration files and environment variables.

Features:
- YAML and JSON configuration file support
- Environment variable overrides
- Default configuration with sensible values
- Validation and type checking
- Profile-based configurations (strict, moderate, lenient)
- Custom metric definitions and thresholds

Configuration Hierarchy (highest to lowest priority):
1. Command-line arguments
2. Environment variables (CODE_ANALYZER_*)
3. Project-specific config file (.code_analyzer.yml)
4. User config file (~/.code_analyzer.yml)
5. System config file (/etc/code_analyzer.yml)
6. Built-in defaults

Authors: Alice & Bob (AI Collaboration)
"""

import json
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, field, asdict
from enum import Enum


class ComplexityProfile(Enum):
    """Predefined complexity analysis profiles."""
    STRICT = "strict"
    MODERATE = "moderate"
    LENIENT = "lenient"
    CUSTOM = "custom"


@dataclass
class ComplexityThresholds:
    """Configuration for complexity analysis thresholds."""
    cyclomatic_low: int = 5
    cyclomatic_moderate: int = 10
    cyclomatic_high: int = 20
    cognitive_low: int = 5
    cognitive_moderate: int = 15
    cognitive_high: int = 25
    nesting_max: int = 4
    function_lines_max: int = 50


@dataclass
class VisualizationConfig:
    """Configuration for dashboard visualization options."""
    theme: str = "light"  # light, dark, auto
    color_scheme: str = "default"  # default, colorblind, high_contrast
    show_complexity_heatmap: bool = True
    show_dependency_graph: bool = True
    show_metrics_overview: bool = True
    show_function_table: bool = True
    interactive_filters: bool = True
    auto_open: bool = False


@dataclass
class AnalysisOptions:
    """Configuration for analysis behavior."""
    include_tests: bool = True
    include_migrations: bool = False
    exclude_patterns: List[str] = field(default_factory=lambda: ["__pycache__", "*.pyc", ".git"])
    max_file_size_mb: float = 10.0
    parallel_processing: bool = True
    max_workers: int = 4
    cache_results: bool = True
    cache_duration_hours: int = 24


@dataclass
class OutputConfig:
    """Configuration for output formatting and destinations."""
    default_format: str = "text"  # text, json, html, dashboard
    output_directory: str = "./analysis_results"
    filename_template: str = "{project_name}_{timestamp}"
    include_timestamp: bool = True
    compress_output: bool = False
    verbose_logging: bool = False


@dataclass
class CodeAnalyzerConfig:
    """Main configuration class for the code analyzer."""
    profile: ComplexityProfile = ComplexityProfile.MODERATE
    complexity_thresholds: ComplexityThresholds = field(default_factory=ComplexityThresholds)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    analysis: AnalysisOptions = field(default_factory=AnalysisOptions)
    output: OutputConfig = field(default_factory=OutputConfig)

    # Meta configuration
    config_version: str = "1.0.0"
    last_updated: Optional[str] = None

    def update_from_profile(self, profile: ComplexityProfile):
        """Update thresholds based on a predefined profile."""
        self.profile = profile

        if profile == ComplexityProfile.STRICT:
            self.complexity_thresholds = ComplexityThresholds(
                cyclomatic_low=3,
                cyclomatic_moderate=6,
                cyclomatic_high=10,
                cognitive_low=3,
                cognitive_moderate=8,
                cognitive_high=15,
                nesting_max=3,
                function_lines_max=30
            )
        elif profile == ComplexityProfile.MODERATE:
            self.complexity_thresholds = ComplexityThresholds()  # Use defaults
        elif profile == ComplexityProfile.LENIENT:
            self.complexity_thresholds = ComplexityThresholds(
                cyclomatic_low=8,
                cyclomatic_moderate=15,
                cyclomatic_high=30,
                cognitive_low=10,
                cognitive_moderate=20,
                cognitive_high=40,
                nesting_max=6,
                function_lines_max=100
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary format."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert configuration to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    def to_yaml(self) -> str:
        """Convert configuration to YAML string."""
        return yaml.dump(self.to_dict(), default_flow_style=False, indent=2)


class ConfigurationManager:
    """
    Manages configuration loading, merging, and validation for the code analyzer.

    This class handles the configuration hierarchy and provides methods to
    load configuration from multiple sources with proper precedence.
    """

    # Default configuration paths
    SYSTEM_CONFIG_PATH = Path("/etc/code_analyzer.yml")
    USER_CONFIG_PATH = Path.home() / ".code_analyzer.yml"
    PROJECT_CONFIG_FILENAME = ".code_analyzer.yml"

    def __init__(self):
        """Initialize the configuration manager."""
        self._config: Optional[CodeAnalyzerConfig] = None
        self._config_sources: List[str] = []

    def load_configuration(
        self,
        project_path: Optional[Path] = None,
        config_file: Optional[Path] = None,
        profile: Optional[str] = None
    ) -> CodeAnalyzerConfig:
        """
        Load configuration from all available sources with proper precedence.

        Args:
            project_path: Path to the project being analyzed
            config_file: Explicit configuration file path
            profile: Override complexity profile

        Returns:
            CodeAnalyzerConfig: Merged configuration
        """
        # Start with default configuration
        config = CodeAnalyzerConfig()
        self._config_sources = ["built-in defaults"]

        # Load system configuration
        if self.SYSTEM_CONFIG_PATH.exists():
            system_config = self._load_config_file(self.SYSTEM_CONFIG_PATH)
            if system_config:
                config = self._merge_configs(config, system_config)
                self._config_sources.append(str(self.SYSTEM_CONFIG_PATH))

        # Load user configuration
        if self.USER_CONFIG_PATH.exists():
            user_config = self._load_config_file(self.USER_CONFIG_PATH)
            if user_config:
                config = self._merge_configs(config, user_config)
                self._config_sources.append(str(self.USER_CONFIG_PATH))

        # Load project-specific configuration
        if project_path:
            project_config_path = project_path / self.PROJECT_CONFIG_FILENAME
            if project_config_path.exists():
                project_config = self._load_config_file(project_config_path)
                if project_config:
                    config = self._merge_configs(config, project_config)
                    self._config_sources.append(str(project_config_path))

        # Load explicit configuration file
        if config_file and config_file.exists():
            explicit_config = self._load_config_file(config_file)
            if explicit_config:
                config = self._merge_configs(config, explicit_config)
                self._config_sources.append(str(config_file))

        # Apply environment variable overrides
        config = self._apply_env_overrides(config)

        # Apply profile override
        if profile:
            try:
                config.update_from_profile(ComplexityProfile(profile))
                self._config_sources.append(f"profile override: {profile}")
            except ValueError:
                print(f"Warning: Unknown profile '{profile}', using current configuration")

        self._config = config
        return config

    def _load_config_file(self, config_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load configuration from a YAML or JSON file.

        Args:
            config_path: Path to configuration file

        Returns:
            Dict containing configuration data, or None if loading failed
        """
        try:
            with open(config_path, 'r') as f:
                content = f.read()

                # Try YAML first, then JSON
                try:
                    return yaml.safe_load(content)
                except yaml.YAMLError:
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError as e:
                        print(f"Warning: Could not parse configuration file {config_path}: {e}")
                        return None

        except Exception as e:
            print(f"Warning: Could not read configuration file {config_path}: {e}")
            return None

    def _merge_configs(self, base: CodeAnalyzerConfig, override: Dict[str, Any]) -> CodeAnalyzerConfig:
        """
        Merge configuration dictionaries with proper deep merging.

        Args:
            base: Base configuration object
            override: Override configuration dictionary

        Returns:
            CodeAnalyzerConfig: Merged configuration
        """
        base_dict = base.to_dict()
        merged_dict = self._deep_merge(base_dict, override)

        # Reconstruct configuration object
        try:
            return CodeAnalyzerConfig(**merged_dict)
        except TypeError as e:
            print(f"Warning: Configuration merge failed: {e}")
            return base

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge two dictionaries."""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _apply_env_overrides(self, config: CodeAnalyzerConfig) -> CodeAnalyzerConfig:
        """
        Apply environment variable overrides to configuration.

        Environment variables follow the pattern: CODE_ANALYZER_SECTION_OPTION
        For example: CODE_ANALYZER_COMPLEXITY_THRESHOLDS_CYCLOMATIC_HIGH=25
        """
        env_overrides = {}

        for key, value in os.environ.items():
            if key.startswith("CODE_ANALYZER_"):
                # Parse environment variable name
                parts = key[len("CODE_ANALYZER_"):].lower().split("_")

                # Convert to nested dictionary structure
                current = env_overrides
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]

                # Convert value to appropriate type
                final_key = parts[-1]
                current[final_key] = self._parse_env_value(value)

        if env_overrides:
            config = self._merge_configs(config, env_overrides)
            self._config_sources.append("environment variables")

        return config

    def _parse_env_value(self, value: str) -> Union[str, int, float, bool]:
        """Parse environment variable value to appropriate Python type."""
        # Boolean values
        if value.lower() in ("true", "yes", "1", "on"):
            return True
        elif value.lower() in ("false", "no", "0", "off"):
            return False

        # Numeric values
        try:
            if "." in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass

        # Return as string
        return value

    def get_config(self) -> Optional[CodeAnalyzerConfig]:
        """Get the currently loaded configuration."""
        return self._config

    def get_config_sources(self) -> List[str]:
        """Get the list of configuration sources that were loaded."""
        return self._config_sources.copy()

    def save_config(
        self,
        config: CodeAnalyzerConfig,
        config_path: Path,
        format_type: str = "yaml"
    ) -> bool:
        """
        Save configuration to a file.

        Args:
            config: Configuration to save
            config_path: Destination file path
            format_type: File format ("yaml" or "json")

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(config_path, 'w') as f:
                if format_type.lower() == "json":
                    f.write(config.to_json())
                else:
                    f.write(config.to_yaml())

            return True

        except Exception as e:
            print(f"Error saving configuration to {config_path}: {e}")
            return False

    def create_example_config(self, output_path: Path) -> bool:
        """
        Create an example configuration file with documentation.

        Args:
            output_path: Where to save the example configuration

        Returns:
            bool: True if successful
        """
        example_config = CodeAnalyzerConfig()

        # Add documentation comments (YAML format)
        yaml_content = f"""# Code Analyzer Configuration File
#
# This file controls the behavior of the Collaborative Code Analyzer.
# Configuration hierarchy (highest to lowest priority):
# 1. Command-line arguments
# 2. Environment variables (CODE_ANALYZER_*)
# 3. Project config (.code_analyzer.yml)
# 4. User config (~/.code_analyzer.yml)
# 5. System config (/etc/code_analyzer.yml)
# 6. Built-in defaults
#
# Configuration loaded from: {', '.join(self._config_sources)}

# Complexity analysis profile: strict, moderate, lenient, custom
profile: {example_config.profile.value}

# Complexity thresholds for different metrics
complexity_thresholds:
  cyclomatic_low: {example_config.complexity_thresholds.cyclomatic_low}     # Functions below this are considered simple
  cyclomatic_moderate: {example_config.complexity_thresholds.cyclomatic_moderate} # Functions above this need attention
  cyclomatic_high: {example_config.complexity_thresholds.cyclomatic_high}    # Functions above this are complex
  cognitive_low: {example_config.complexity_thresholds.cognitive_low}       # Cognitive complexity thresholds
  cognitive_moderate: {example_config.complexity_thresholds.cognitive_moderate}
  cognitive_high: {example_config.complexity_thresholds.cognitive_high}
  nesting_max: {example_config.complexity_thresholds.nesting_max}         # Maximum recommended nesting depth
  function_lines_max: {example_config.complexity_thresholds.function_lines_max}  # Maximum recommended function length

# Visualization and dashboard options
visualization:
  theme: {example_config.visualization.theme}              # light, dark, auto
  color_scheme: {example_config.visualization.color_scheme}      # default, colorblind, high_contrast
  show_complexity_heatmap: {example_config.visualization.show_complexity_heatmap}
  show_dependency_graph: {example_config.visualization.show_dependency_graph}
  show_metrics_overview: {example_config.visualization.show_metrics_overview}
  show_function_table: {example_config.visualization.show_function_table}
  interactive_filters: {example_config.visualization.interactive_filters}
  auto_open: {example_config.visualization.auto_open}            # Auto-open dashboard in browser

# Analysis behavior options
analysis:
  include_tests: {example_config.analysis.include_tests}          # Analyze test files
  include_migrations: {example_config.analysis.include_migrations}      # Analyze database migrations
  exclude_patterns:           # File patterns to exclude
{chr(10).join(f'    - "{pattern}"' for pattern in example_config.analysis.exclude_patterns)}
  max_file_size_mb: {example_config.analysis.max_file_size_mb}     # Skip files larger than this
  parallel_processing: {example_config.analysis.parallel_processing}    # Use multiprocessing
  max_workers: {example_config.analysis.max_workers}            # Number of worker processes
  cache_results: {example_config.analysis.cache_results}         # Cache analysis results
  cache_duration_hours: {example_config.analysis.cache_duration_hours}  # Cache validity period

# Output formatting and destinations
output:
  default_format: {example_config.output.default_format}      # text, json, html, dashboard
  output_directory: {example_config.output.output_directory}
  filename_template: {example_config.output.filename_template}
  include_timestamp: {example_config.output.include_timestamp}
  compress_output: {example_config.output.compress_output}      # Gzip compress output files
  verbose_logging: {example_config.output.verbose_logging}      # Enable detailed logging

# Configuration metadata
config_version: {example_config.config_version}
"""

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(yaml_content)
            return True
        except Exception as e:
            print(f"Error creating example configuration: {e}")
            return False


# Global configuration manager instance
config_manager = ConfigurationManager()

def get_config() -> CodeAnalyzerConfig:
    """Get the current global configuration."""
    config = config_manager.get_config()
    if config is None:
        config = config_manager.load_configuration()
    return config

def load_config(
    project_path: Optional[Path] = None,
    config_file: Optional[Path] = None,
    profile: Optional[str] = None
) -> CodeAnalyzerConfig:
    """Load configuration with the specified parameters."""
    return config_manager.load_configuration(project_path, config_file, profile)
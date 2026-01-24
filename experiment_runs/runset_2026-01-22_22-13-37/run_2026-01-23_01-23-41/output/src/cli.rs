use clap::{Parser, ValueEnum};
use std::path::PathBuf;

#[derive(Parser, Debug)]
#[command(name = "codemetrics")]
#[command(about = "A fast, extensible code metrics analyzer")]
#[command(version, long_about = None)]
pub struct Args {
    /// Path to analyze (defaults to current directory)
    #[arg(default_value = ".")]
    pub path: PathBuf,

    /// Output format
    #[arg(short, long, default_value = "terminal")]
    pub format: OutputFormat,

    /// Output file (defaults to stdout for terminal format)
    #[arg(short, long)]
    pub output: Option<PathBuf>,

    /// Specific metrics to analyze (comma-separated)
    /// Available: complexity, duplication, coverage, dependencies, debt
    #[arg(short, long)]
    pub metrics: Option<String>,

    /// Minimum complexity threshold to report
    #[arg(long, default_value = "10")]
    pub complexity_threshold: u32,

    /// Include test files in analysis
    #[arg(long)]
    pub include_tests: bool,

    /// Show progress bar for large codebases
    #[arg(long)]
    pub progress: bool,

    /// Verbose output (show debug information)
    #[arg(short, long)]
    pub verbose: bool,
}

#[derive(Debug, Clone, ValueEnum)]
pub enum OutputFormat {
    /// Human-readable terminal output with tables
    Terminal,
    /// JSON format for CI/CD integration
    Json,
    /// HTML report with interactive visualizations
    Html,
    /// Markdown format for documentation
    Markdown,
}

impl Args {
    /// Validate CLI arguments
    pub fn validate(&self) -> Result<(), String> {
        if !self.path.exists() {
            return Err(format!("Path does not exist: {}", self.path.display()));
        }

        if !self.path.is_dir() {
            return Err(format!("Path is not a directory: {}", self.path.display()));
        }

        if self.complexity_threshold == 0 {
            return Err("Complexity threshold must be greater than 0".to_string());
        }

        Ok(())
    }

    /// Parse metrics string into a vector of metric types
    pub fn parse_metrics(&self) -> Vec<&str> {
        match &self.metrics {
            Some(metrics_str) => {
                metrics_str
                    .split(',')
                    .map(|m| m.trim())
                    .filter(|m| !m.is_empty())
                    .collect()
            }
            None => vec!["complexity", "duplication", "dependencies"], // Default metrics
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

    #[test]
    fn test_args_validation() {
        let temp_dir = tempdir().unwrap();

        let valid_args = Args {
            path: temp_dir.path().to_path_buf(),
            format: OutputFormat::Terminal,
            output: None,
            metrics: None,
            complexity_threshold: 10,
            include_tests: false,
            progress: false,
            verbose: false,
        };

        assert!(valid_args.validate().is_ok());

        let invalid_args = Args {
            path: PathBuf::from("/nonexistent/path"),
            ..valid_args
        };

        assert!(invalid_args.validate().is_err());
    }

    #[test]
    fn test_metrics_parsing() {
        let args = Args {
            path: PathBuf::from("."),
            format: OutputFormat::Terminal,
            output: None,
            metrics: Some("complexity,duplication".to_string()),
            complexity_threshold: 10,
            include_tests: false,
            progress: false,
            verbose: false,
        };

        let parsed = args.parse_metrics();
        assert_eq!(parsed, vec!["complexity", "duplication"]);

        let default_args = Args {
            metrics: None,
            ..args
        };

        let default_parsed = default_args.parse_metrics();
        assert_eq!(default_parsed, vec!["complexity", "duplication", "dependencies"]);
    }
}
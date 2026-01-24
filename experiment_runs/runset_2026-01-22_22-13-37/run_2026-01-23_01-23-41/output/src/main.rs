use anyhow::Result;
use clap::{Args, Parser, Subcommand};
use std::path::PathBuf;

mod analyzers;
mod parsers;
mod reporters;

use analyzers::CodeAnalyzer;
use parsers::LanguageParser;
use reporters::Reporter;

/// A powerful code analysis tool for understanding codebases
#[derive(Parser)]
#[command(author, version, about, long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Analyze code complexity and metrics
    Analyze(AnalyzeArgs),
    /// Generate detailed reports
    Report(ReportArgs),
    /// Show supported languages and features
    Languages,
}

#[derive(Args)]
pub struct AnalyzeArgs {
    /// Path to analyze
    #[arg(value_name = "PATH")]
    pub path: PathBuf,

    /// Language to analyze (auto-detected if not specified)
    #[arg(short, long)]
    pub language: Option<String>,

    /// Output format (text, json, html)
    #[arg(short, long, default_value = "text")]
    pub format: String,

    /// Include test files in analysis
    #[arg(long)]
    pub include_tests: bool,

    /// Minimum complexity threshold to report
    #[arg(long, default_value = "5")]
    pub min_complexity: u32,

    /// Show detailed function-level metrics
    #[arg(long)]
    pub detailed: bool,
}

#[derive(Args)]
struct ReportArgs {
    /// Path to analyze
    #[arg(value_name = "PATH")]
    path: PathBuf,

    /// Output file (stdout if not specified)
    #[arg(short, long)]
    output: Option<PathBuf>,

    /// Report template (html, markdown, json)
    #[arg(short, long, default_value = "html")]
    template: String,
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Analyze(args) => {
            let analyzer = CodeAnalyzer::new();
            let results = analyzer.analyze_path(&args.path, &args)?;

            let reporter = Reporter::new(&args.format);
            reporter.output_results(&results)?;
        }
        Commands::Report(args) => {
            let analyzer = CodeAnalyzer::new();
            let results = analyzer.analyze_path(&args.path, &AnalyzeArgs {
                path: args.path.clone(),
                language: None,
                format: "json".to_string(),
                include_tests: true,
                min_complexity: 1,
                detailed: true,
            })?;

            let reporter = Reporter::new(&args.template);
            reporter.generate_report(&results, args.output.as_ref())?;
        }
        Commands::Languages => {
            println!("Supported languages:");
            for lang in LanguageParser::supported_languages() {
                println!("  - {}", lang);
            }
        }
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;
    use std::fs;

    #[test]
    fn test_basic_analysis() -> Result<()> {
        let temp_dir = tempdir()?;
        let test_file = temp_dir.path().join("test.rs");

        fs::write(&test_file, r#"
            fn simple_function() -> i32 {
                42
            }

            fn complex_function(x: i32) -> i32 {
                if x > 0 {
                    if x > 10 {
                        x * 2
                    } else {
                        x + 1
                    }
                } else {
                    0
                }
            }
        "#)?;

        let analyzer = CodeAnalyzer::new(temp_dir.path().to_path_buf())?;
        let metrics_config = analyzer.configure_metrics(None)?;
        let results = analyzer.analyze(metrics_config)?;

        assert!(results.files_analyzed > 0);
        assert!(results.total_lines > 0);

        Ok(())
    }
}
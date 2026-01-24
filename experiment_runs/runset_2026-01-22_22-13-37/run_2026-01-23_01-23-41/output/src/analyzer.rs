use anyhow::{Context, Result};
use std::path::{Path, PathBuf};
use std::collections::HashMap;
use walkdir::WalkDir;
use std::time::Instant;

use crate::ast_analyzer::{ASTAnalyzer, FunctionAnalysis};
use crate::core::{Language as LangType, CodeIssue as CoreCodeIssue, IssueSeverity as CoreIssueSeverity, IssueCategory};

/// Core analyzer that orchestrates the code analysis process
pub struct CodeAnalyzer {
    root_path: PathBuf,
    ast_analyzer: ASTAnalyzer,
}

/// Analysis results containing metrics and insights
#[derive(Debug)]
pub struct AnalysisResults {
    pub files_analyzed: usize,
    pub total_lines: usize,
    pub total_complexity: u32,
    pub language_breakdown: HashMap<String, usize>,
    pub complexity_distribution: Vec<(PathBuf, u32)>,
    pub analysis_duration_ms: u64,
    pub issues: Vec<AnalysisIssue>,
}

#[derive(Debug)]
pub struct AnalysisIssue {
    pub file_path: PathBuf,
    pub line: u32,
    pub severity: IssueSeverity,
    pub message: String,
    pub suggestion: Option<String>,
}

#[derive(Debug, Clone)]
pub enum IssueSeverity {
    Info,
    Warning,
    Error,
}

/// Configuration for metrics collection
#[derive(Debug, Clone)]
pub struct MetricsConfig {
    pub enabled_metrics: Vec<String>,
    pub complexity_threshold: u32,
    pub include_tests: bool,
    pub analyze_dependencies: bool,
}

impl CodeAnalyzer {
    /// Create a new analyzer for the given root path
    pub fn new(root_path: PathBuf) -> Result<Self> {
        if !root_path.exists() {
            anyhow::bail!("Path does not exist: {}", root_path.display());
        }

        let ast_analyzer = ASTAnalyzer::new()
            .context("Failed to initialize AST analyzer")?;

        Ok(Self { root_path, ast_analyzer })
    }

    /// Configure which metrics to collect based on CLI options
    pub fn configure_metrics(&self, metrics: Option<&str>) -> Result<MetricsConfig> {
        let enabled_metrics = match metrics {
            Some(m) => m.split(',').map(|s| s.trim().to_string()).collect(),
            None => vec![
                "complexity".to_string(),
                "duplication".to_string(),
                "maintainability".to_string(),
            ],
        };

        Ok(MetricsConfig {
            enabled_metrics,
            complexity_threshold: 10,
            include_tests: false,
            analyze_dependencies: false,
        })
    }

    /// Run the analysis with the given configuration
    pub fn analyze(&self, config: MetricsConfig) -> Result<AnalysisResults> {
        let start_time = Instant::now();

        println!("🔍 Discovering source files...");
        let source_files = self.discover_source_files()?;

        println!("📊 Found {} files to analyze", source_files.len());

        let mut results = AnalysisResults {
            files_analyzed: 0,
            total_lines: 0,
            total_complexity: 0,
            language_breakdown: HashMap::new(),
            complexity_distribution: Vec::new(),
            analysis_duration_ms: 0,
            issues: Vec::new(),
        };

        // Analyze each source file
        for file_path in source_files {
            match self.analyze_file(&file_path, &config) {
                Ok(file_result) => {
                    results.files_analyzed += 1;
                    results.total_lines += file_result.lines;
                    results.total_complexity += file_result.complexity;

                    // Track language breakdown
                    let lang = self.detect_language(&file_path);
                    *results.language_breakdown.entry(lang).or_insert(0) += 1;

                    // Track complexity distribution
                    if file_result.complexity > 0 {
                        results.complexity_distribution.push((file_path.clone(), file_result.complexity));
                    }

                    // Add any issues found
                    results.issues.extend(file_result.issues);
                }
                Err(e) => {
                    eprintln!("⚠️  Failed to analyze {}: {}", file_path.display(), e);
                }
            }
        }

        // Sort complexity distribution by complexity (highest first)
        results.complexity_distribution.sort_by(|a, b| b.1.cmp(&a.1));

        results.analysis_duration_ms = start_time.elapsed().as_millis() as u64;

        Ok(results)
    }

    /// Discover all source files in the root path
    fn discover_source_files(&self) -> Result<Vec<PathBuf>> {
        let mut files = Vec::new();

        for entry in WalkDir::new(&self.root_path)
            .follow_links(false)
            .into_iter()
            .filter_map(|e| e.ok())
        {
            let path = entry.path();

            if path.is_file() && self.is_source_file(path) {
                files.push(path.to_path_buf());
            }
        }

        Ok(files)
    }

    /// Check if a file should be analyzed based on its extension
    fn is_source_file(&self, path: &Path) -> bool {
        if let Some(ext) = path.extension() {
            matches!(ext.to_str(), Some("rs" | "js" | "ts" | "py" | "go" | "jsx" | "tsx"))
        } else {
            false
        }
    }

    /// Detect programming language from file extension
    fn detect_language(&self, path: &Path) -> String {
        match path.extension().and_then(|ext| ext.to_str()) {
            Some("rs") => "Rust".to_string(),
            Some("js" | "jsx") => "JavaScript".to_string(),
            Some("ts" | "tsx") => "TypeScript".to_string(),
            Some("py") => "Python".to_string(),
            Some("go") => "Go".to_string(),
            _ => "Unknown".to_string(),
        }
    }

    /// Analyze a single source file
    fn analyze_file(&self, file_path: &Path, config: &MetricsConfig) -> Result<FileAnalysisResult> {
        let content = std::fs::read_to_string(file_path)
            .with_context(|| format!("Failed to read file: {}", file_path.display()))?;

        let lines = content.lines().count();

        // Simple complexity analysis (count decision points)
        let complexity = self.calculate_basic_complexity(&content);

        let mut issues = Vec::new();

        // Check complexity threshold
        if complexity > config.complexity_threshold {
            issues.push(AnalysisIssue {
                file_path: file_path.to_path_buf(),
                line: 1, // Could be more specific with proper parsing
                severity: IssueSeverity::Warning,
                message: format!("High complexity: {} (threshold: {})", complexity, config.complexity_threshold),
                suggestion: Some("Consider breaking this into smaller functions".to_string()),
            });
        }

        Ok(FileAnalysisResult {
            lines,
            complexity,
            issues,
        })
    }

    /// Calculate basic cyclomatic complexity by counting decision points
    fn calculate_basic_complexity(&self, content: &str) -> u32 {
        let mut complexity = 1; // Base complexity

        // Count decision points (simplified)
        for line in content.lines() {
            let line = line.trim();

            // Control flow keywords that add complexity
            if line.contains("if ") || line.contains("else if") {
                complexity += 1;
            }
            if line.contains("while ") || line.contains("for ") {
                complexity += 1;
            }
            if line.contains("match ") || line.contains("switch ") {
                complexity += 1;
            }
            if line.contains("catch ") || line.contains("except ") {
                complexity += 1;
            }
            // Count case statements in match/switch
            if line.contains("case ") || line.contains("when ") {
                complexity += 1;
            }
        }

        complexity
    }
}

/// Results from analyzing a single file
struct FileAnalysisResult {
    lines: usize,
    complexity: u32,
    issues: Vec<AnalysisIssue>,
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;
    use std::fs;

    #[test]
    fn test_complexity_calculation() {
        let analyzer = CodeAnalyzer::new(PathBuf::from(".")).unwrap();

        let simple_code = r#"
            fn simple() {
                println!("Hello");
            }
        "#;
        assert_eq!(analyzer.calculate_basic_complexity(simple_code), 1);

        let complex_code = r#"
            fn complex(x: i32) -> i32 {
                if x > 0 {
                    if x > 10 {
                        for i in 0..x {
                            if i % 2 == 0 {
                                continue;
                            }
                        }
                        x * 2
                    } else {
                        x + 1
                    }
                } else {
                    0
                }
            }
        "#;
        // Should count: base(1) + if(1) + if(1) + for(1) + if(1) = 5
        assert_eq!(analyzer.calculate_basic_complexity(complex_code), 5);
    }

    #[test]
    fn test_language_detection() {
        let analyzer = CodeAnalyzer::new(PathBuf::from(".")).unwrap();

        assert_eq!(analyzer.detect_language(Path::new("test.rs")), "Rust");
        assert_eq!(analyzer.detect_language(Path::new("test.js")), "JavaScript");
        assert_eq!(analyzer.detect_language(Path::new("test.ts")), "TypeScript");
        assert_eq!(analyzer.detect_language(Path::new("test.py")), "Python");
        assert_eq!(analyzer.detect_language(Path::new("test.unknown")), "Unknown");
    }

    #[test]
    fn test_source_file_detection() {
        let analyzer = CodeAnalyzer::new(PathBuf::from(".")).unwrap();

        assert!(analyzer.is_source_file(Path::new("test.rs")));
        assert!(analyzer.is_source_file(Path::new("test.js")));
        assert!(analyzer.is_source_file(Path::new("component.tsx")));
        assert!(!analyzer.is_source_file(Path::new("README.md")));
        assert!(!analyzer.is_source_file(Path::new("config.json")));
    }
}
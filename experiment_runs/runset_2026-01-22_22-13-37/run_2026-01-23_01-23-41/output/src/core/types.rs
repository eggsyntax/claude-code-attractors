use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;

/// Represents the programming language of a source file
#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Language {
    Rust,
    JavaScript,
    TypeScript,
    Python,
    Go,
    Unknown,
}

impl Language {
    /// Detect language from file extension
    pub fn from_extension(ext: &str) -> Self {
        match ext.to_lowercase().as_str() {
            "rs" => Language::Rust,
            "js" | "jsx" | "mjs" => Language::JavaScript,
            "ts" | "tsx" => Language::TypeScript,
            "py" | "pyi" => Language::Python,
            "go" => Language::Go,
            _ => Language::Unknown,
        }
    }

    /// Get file extensions for this language
    pub fn extensions(&self) -> Vec<&'static str> {
        match self {
            Language::Rust => vec!["rs"],
            Language::JavaScript => vec!["js", "jsx", "mjs"],
            Language::TypeScript => vec!["ts", "tsx"],
            Language::Python => vec!["py", "pyi"],
            Language::Go => vec!["go"],
            Language::Unknown => vec![],
        }
    }
}

/// Core metrics for code analysis
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CodeMetrics {
    /// Cyclomatic complexity - number of linearly independent paths
    pub cyclomatic_complexity: u32,

    /// Lines of code (excluding comments and blank lines)
    pub lines_of_code: u32,

    /// Total lines including comments and whitespace
    pub total_lines: u32,

    /// Number of functions/methods
    pub function_count: u32,

    /// Number of parameters across all functions
    pub parameter_count: u32,

    /// Nesting depth (maximum)
    pub max_nesting_depth: u32,

    /// Maintainability index (0-100, higher is better)
    pub maintainability_index: f64,
}

impl Default for CodeMetrics {
    fn default() -> Self {
        Self {
            cyclomatic_complexity: 1,
            lines_of_code: 0,
            total_lines: 0,
            function_count: 0,
            parameter_count: 0,
            max_nesting_depth: 0,
            maintainability_index: 100.0,
        }
    }
}

/// Analysis result for a single source file
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FileAnalysis {
    pub file_path: PathBuf,
    pub language: Language,
    pub metrics: CodeMetrics,
    pub issues: Vec<CodeIssue>,
    pub analysis_time_ms: u64,
}

/// Represents a code quality issue or pattern
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CodeIssue {
    pub severity: IssueSeverity,
    pub category: IssueCategory,
    pub message: String,
    pub line: u32,
    pub column: u32,
    pub suggestion: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum IssueSeverity {
    Info,
    Warning,
    Error,
    Critical,
}

#[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum IssueCategory {
    Complexity,
    Performance,
    Maintainability,
    Security,
    Style,
    Duplication,
}

/// Aggregated analysis results for entire codebase
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProjectAnalysis {
    pub files: Vec<FileAnalysis>,
    pub summary: ProjectSummary,
    pub dependency_graph: Option<DependencyGraph>,
    pub analysis_timestamp: String,
    pub total_analysis_time_ms: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProjectSummary {
    pub total_files: u32,
    pub languages: HashMap<Language, u32>,
    pub total_lines_of_code: u32,
    pub total_complexity: u32,
    pub average_maintainability: f64,
    pub issue_count_by_severity: HashMap<IssueSeverity, u32>,
    pub issue_count_by_category: HashMap<IssueCategory, u32>,
}

/// Represents dependencies between modules/files
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DependencyGraph {
    pub nodes: Vec<DependencyNode>,
    pub edges: Vec<DependencyEdge>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DependencyNode {
    pub id: String,
    pub file_path: PathBuf,
    pub module_name: String,
    pub exports: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DependencyEdge {
    pub from: String,
    pub to: String,
    pub import_type: ImportType,
    pub imported_symbols: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ImportType {
    Named,
    Default,
    Namespace,
    Side,
}

/// Configuration for analysis behavior
#[derive(Debug, Clone)]
pub struct AnalysisConfig {
    pub complexity_threshold: u32,
    pub maintainability_threshold: f64,
    pub max_function_length: u32,
    pub max_parameter_count: u32,
    pub include_patterns: Vec<String>,
    pub exclude_patterns: Vec<String>,
    pub analyze_dependencies: bool,
    pub parallel_analysis: bool,
}
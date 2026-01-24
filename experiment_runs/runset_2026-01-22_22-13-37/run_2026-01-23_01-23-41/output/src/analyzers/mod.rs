//! Core analysis engine that orchestrates parsing and metric collection

use anyhow::{Context, Result};
use rayon::prelude::*;
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use walkdir::WalkDir;
use ignore::Walk;
use indicatif::{ProgressBar, ProgressStyle};

use crate::parsers::{LanguageParser, ParsedFile, FunctionInfo};

pub struct CodeAnalyzer {
    parser: LanguageParser,
    config: AnalysisConfig,
}

#[derive(Debug, Clone)]
pub struct AnalysisConfig {
    pub min_complexity_threshold: u32,
    pub include_tests: bool,
    pub max_file_size: usize,
    pub excluded_paths: Vec<String>,
    pub focus_languages: Option<Vec<String>>,
}

impl Default for AnalysisConfig {
    fn default() -> Self {
        Self {
            min_complexity_threshold: 5,
            include_tests: false,
            max_file_size: 1024 * 1024, // 1MB
            excluded_paths: vec![
                "node_modules".to_string(),
                "target".to_string(),
                ".git".to_string(),
                "dist".to_string(),
                "build".to_string(),
            ],
            focus_languages: None,
        }
    }
}

impl CodeAnalyzer {
    pub fn new() -> Self {
        Self::with_config(AnalysisConfig::default())
    }

    pub fn with_config(config: AnalysisConfig) -> Self {
        Self {
            parser: LanguageParser::new(),
            config,
        }
    }

    pub fn analyze_path(&self, path: &Path, _args: &crate::AnalyzeArgs) -> Result<AnalysisResults> {
        let files = self.discover_files(path)?;
        println!("Found {} files to analyze", files.len());

        let progress = ProgressBar::new(files.len() as u64);
        progress.set_style(
            ProgressStyle::default_bar()
                .template("{spinner:.green} [{elapsed_precise}] [{bar:40.cyan/blue}] {pos}/{len} {msg}")
                .context("Failed to set progress style")?
        );

        // Parallel processing of files for performance
        let parsed_files: Vec<Result<ParsedFile>> = files
            .par_iter()
            .map(|file_path| {
                progress.inc(1);
                progress.set_message(format!("Analyzing {}", file_path.display()));

                let content = std::fs::read_to_string(file_path)
                    .with_context(|| format!("Failed to read file: {}", file_path.display()))?;

                self.parser.parse_file(&file_path.to_string_lossy(), &content)
            })
            .collect();

        progress.finish_with_message("Analysis complete");

        self.aggregate_results(parsed_files)
    }

    fn discover_files(&self, root_path: &Path) -> Result<Vec<PathBuf>> {
        let mut files = Vec::new();

        // Use the `ignore` crate to respect .gitignore files
        for result in Walk::new(root_path) {
            let entry = result.context("Failed to read directory entry")?;
            let path = entry.path();

            // Skip if it's not a file
            if !path.is_file() {
                continue;
            }

            // Skip if file is too large
            if let Ok(metadata) = path.metadata() {
                if metadata.len() > self.config.max_file_size as u64 {
                    continue;
                }
            }

            // Skip excluded paths
            if self.is_excluded_path(path) {
                continue;
            }

            // Skip test files if not including tests
            if !self.config.include_tests && self.is_test_file(path) {
                continue;
            }

            // Check if we support this file type
            if let Some(extension) = path.extension() {
                if let Some(ext_str) = extension.to_str() {
                    if self.is_supported_extension(ext_str) {
                        files.push(path.to_path_buf());
                    }
                }
            }
        }

        Ok(files)
    }

    fn is_excluded_path(&self, path: &Path) -> bool {
        let path_str = path.to_string_lossy();
        self.config.excluded_paths.iter().any(|excluded| {
            path_str.contains(excluded)
        })
    }

    fn is_test_file(&self, path: &Path) -> bool {
        let path_str = path.to_string_lossy();
        path_str.contains("test") ||
        path_str.contains("spec") ||
        path_str.ends_with("_test.rs") ||
        path_str.ends_with(".test.js") ||
        path_str.ends_with("_spec.rb")
    }

    fn is_supported_extension(&self, extension: &str) -> bool {
        matches!(extension, "rs" | "js" | "ts" | "py" | "go" | "jsx" | "tsx")
    }

    fn aggregate_results(&self, parsed_files: Vec<Result<ParsedFile>>) -> Result<AnalysisResults> {
        let mut results = AnalysisResults::new();

        for parsed_result in parsed_files {
            match parsed_result {
                Ok(parsed_file) => {
                    results.add_file(parsed_file);
                }
                Err(e) => {
                    eprintln!("Warning: Failed to parse file - {}", e);
                    results.errors.push(e.to_string());
                }
            }
        }

        results.finalize();
        Ok(results)
    }
}

#[derive(Debug)]
pub struct AnalysisResults {
    pub files_analyzed: usize,
    pub total_lines: u32,
    pub total_functions: usize,
    pub average_complexity: f64,
    pub high_complexity_functions: Vec<HighComplexityFunction>,
    pub language_breakdown: HashMap<String, LanguageStats>,
    pub complexity_distribution: HashMap<u32, u32>,
    pub errors: Vec<String>,
}

impl AnalysisResults {
    fn new() -> Self {
        Self {
            files_analyzed: 0,
            total_lines: 0,
            total_functions: 0,
            average_complexity: 0.0,
            high_complexity_functions: Vec::new(),
            language_breakdown: HashMap::new(),
            complexity_distribution: HashMap::new(),
            errors: Vec::new(),
        }
    }

    fn add_file(&mut self, parsed_file: ParsedFile) {
        self.files_analyzed += 1;

        // Determine language from file extension
        let language = self.detect_language(&parsed_file.path);
        let stats = self.language_breakdown.entry(language).or_insert_with(Default::default);
        stats.files += 1;

        for function in &parsed_file.functions {
            self.total_functions += 1;
            stats.functions += 1;

            // Track complexity distribution
            *self.complexity_distribution.entry(function.complexity).or_insert(0) += 1;

            // Identify high complexity functions
            if function.complexity >= 10 {  // Threshold for "high complexity"
                self.high_complexity_functions.push(HighComplexityFunction {
                    name: function.name.clone(),
                    file_path: parsed_file.path.clone(),
                    complexity: function.complexity,
                    line_start: function.line_start,
                    parameters: function.parameters,
                });
            }
        }
    }

    fn detect_language(&self, file_path: &str) -> String {
        if let Some(extension) = file_path.split('.').last() {
            match extension {
                "rs" => "Rust".to_string(),
                "js" | "jsx" => "JavaScript".to_string(),
                "ts" | "tsx" => "TypeScript".to_string(),
                "py" => "Python".to_string(),
                "go" => "Go".to_string(),
                _ => "Unknown".to_string(),
            }
        } else {
            "Unknown".to_string()
        }
    }

    fn finalize(&mut self) {
        // Calculate average complexity
        if self.total_functions > 0 {
            let total_complexity: u32 = self.complexity_distribution
                .iter()
                .map(|(complexity, count)| complexity * count)
                .sum();
            self.average_complexity = total_complexity as f64 / self.total_functions as f64;
        }

        // Sort high complexity functions by complexity (descending)
        self.high_complexity_functions.sort_by(|a, b| b.complexity.cmp(&a.complexity));
    }
}

#[derive(Debug, Clone)]
pub struct HighComplexityFunction {
    pub name: String,
    pub file_path: String,
    pub complexity: u32,
    pub line_start: u32,
    pub parameters: u32,
}

#[derive(Debug, Default)]
pub struct LanguageStats {
    pub files: usize,
    pub functions: usize,
}

impl Default for CodeAnalyzer {
    fn default() -> Self {
        Self::new()
    }
}
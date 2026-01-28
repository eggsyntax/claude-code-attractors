// Sample Rust code for testing CodeMetrics analyzer
// This file contains various complexity patterns for demonstration

use std::collections::HashMap;
use std::fs::File;
use std::io::{self, BufRead, BufReader};

/// A complex function with high cyclomatic complexity
/// This demonstrates various control flow patterns that increase complexity
pub fn complex_analysis_function(
    input_file: &str,
    threshold: i32,
    options: &AnalysisOptions,
) -> Result<AnalysisResult, AnalysisError> {
    let file = File::open(input_file)
        .map_err(|e| AnalysisError::FileError(format!("Cannot open file: {}", e)))?;

    let reader = BufReader::new(file);
    let mut results = AnalysisResult::new();
    let mut line_number = 0;

    for line in reader.lines() {
        line_number += 1;
        let line = line.map_err(|e| AnalysisError::ReadError(e.to_string()))?;

        // Multiple nested conditions increase complexity
        if !line.trim().is_empty() {
            if line.starts_with("//") || line.starts_with("#") {
                // Skip comments
                continue;
            } else if line.contains("TODO") {
                if options.track_todos {
                    results.todos.push(TodoItem {
                        line: line_number,
                        content: line.clone(),
                    });
                }
            } else if line.contains("FIXME") {
                if options.track_fixmes {
                    results.fixmes.push(FixmeItem {
                        line: line_number,
                        content: line.clone(),
                        priority: if line.contains("URGENT") {
                            Priority::High
                        } else if line.contains("LOW") {
                            Priority::Low
                        } else {
                            Priority::Medium
                        },
                    });
                }
            }

            // Complex pattern matching adds more complexity
            match analyze_line_type(&line) {
                LineType::Function => {
                    results.function_count += 1;
                    if line.contains("async") {
                        results.async_function_count += 1;
                    }
                }
                LineType::Struct => {
                    results.struct_count += 1;
                }
                LineType::Enum => {
                    results.enum_count += 1;
                }
                LineType::Impl => {
                    results.impl_count += 1;
                }
                LineType::UseStatement => {
                    results.import_count += 1;
                }
                LineType::Comment => {
                    results.comment_lines += 1;
                }
                LineType::Empty => {
                    results.empty_lines += 1;
                }
                LineType::Code => {
                    results.code_lines += 1;

                    // Additional complexity from loops
                    if line.contains("for ") || line.contains("while ") {
                        results.loop_count += 1;

                        // Nested analysis for loop complexity
                        if line.contains("if ") {
                            results.nested_control_structures += 1;
                        }
                    }

                    // Error handling patterns
                    if line.contains("match ") || line.contains("if let ") {
                        results.pattern_matches += 1;

                        // Check for error handling
                        if line.contains("Err(") || line.contains("Error") {
                            results.error_handling_sites += 1;
                        }
                    }

                    // Complexity from method chaining
                    let dot_count = line.chars().filter(|&c| c == '.').count();
                    if dot_count > 3 {
                        results.complex_expressions += 1;
                    }
                }
            }

            // Calculate line complexity score
            let line_complexity = calculate_line_complexity(&line);
            if line_complexity > threshold {
                results.high_complexity_lines.push(ComplexLine {
                    line_number,
                    content: line.clone(),
                    complexity: line_complexity,
                });
            }
        }

        // Progress reporting for large files
        if line_number % 1000 == 0 && options.show_progress {
            eprintln!("Processed {} lines...", line_number);
        }
    }

    // Final processing and scoring
    results.total_lines = line_number;
    results.complexity_score = calculate_overall_complexity(&results);

    // Apply additional filters based on options
    if options.filter_low_impact {
        results.filter_low_impact_items();
    }

    if results.complexity_score > options.complexity_threshold {
        if options.strict_mode {
            return Err(AnalysisError::ComplexityTooHigh(results.complexity_score));
        } else if options.warn_high_complexity {
            eprintln!("Warning: High complexity detected ({})", results.complexity_score);
        }
    }

    Ok(results)
}

/// Another complex function with deep nesting
pub fn process_nested_data(data: &mut AnalysisResult, config: ProcessingConfig) -> ProcessingResult {
    for category in &mut data.categories {
        for item in &mut category.items {
            if item.needs_processing {
                for sub_item in &mut item.sub_items {
                    if let Some(ref mut processor) = sub_item.processor {
                        match processor.process() {
                            Ok(result) => {
                                if result.is_valid {
                                    for validation in &result.validations {
                                        if validation.severity > config.min_severity {
                                            for action in &validation.recommended_actions {
                                                if config.auto_apply_fixes {
                                                    if let Err(e) = action.apply(&mut sub_item) {
                                                        eprintln!("Failed to apply fix: {}", e);
                                                    } else {
                                                        sub_item.fixes_applied += 1;
                                                    }
                                                } else {
                                                    sub_item.pending_fixes.push(action.clone());
                                                }
                                            }
                                        }
                                    }
                                } else if config.strict_validation {
                                    return ProcessingResult::ValidationFailed(result.errors);
                                }
                            }
                            Err(e) => {
                                if config.continue_on_error {
                                    eprintln!("Processing error (continuing): {}", e);
                                    sub_item.errors.push(e);
                                } else {
                                    return ProcessingResult::ProcessingError(e);
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    ProcessingResult::Success
}

// Supporting types and functions for the complex examples above

#[derive(Debug)]
pub struct AnalysisOptions {
    pub track_todos: bool,
    pub track_fixmes: bool,
    pub show_progress: bool,
    pub filter_low_impact: bool,
    pub complexity_threshold: i32,
    pub strict_mode: bool,
    pub warn_high_complexity: bool,
}

#[derive(Debug)]
pub struct AnalysisResult {
    pub todos: Vec<TodoItem>,
    pub fixmes: Vec<FixmeItem>,
    pub function_count: u32,
    pub async_function_count: u32,
    pub struct_count: u32,
    pub enum_count: u32,
    pub impl_count: u32,
    pub import_count: u32,
    pub comment_lines: u32,
    pub empty_lines: u32,
    pub code_lines: u32,
    pub loop_count: u32,
    pub nested_control_structures: u32,
    pub pattern_matches: u32,
    pub error_handling_sites: u32,
    pub complex_expressions: u32,
    pub high_complexity_lines: Vec<ComplexLine>,
    pub total_lines: u32,
    pub complexity_score: f64,
    pub categories: Vec<Category>,
}

impl AnalysisResult {
    fn new() -> Self {
        Self {
            todos: Vec::new(),
            fixmes: Vec::new(),
            function_count: 0,
            async_function_count: 0,
            struct_count: 0,
            enum_count: 0,
            impl_count: 0,
            import_count: 0,
            comment_lines: 0,
            empty_lines: 0,
            code_lines: 0,
            loop_count: 0,
            nested_control_structures: 0,
            pattern_matches: 0,
            error_handling_sites: 0,
            complex_expressions: 0,
            high_complexity_lines: Vec::new(),
            total_lines: 0,
            complexity_score: 0.0,
            categories: Vec::new(),
        }
    }

    fn filter_low_impact_items(&mut self) {
        // Remove low-impact items to focus on important issues
        self.todos.retain(|todo| todo.content.contains("IMPORTANT") || todo.content.contains("URGENT"));
        self.fixmes.retain(|fixme| fixme.priority != Priority::Low);
    }
}

#[derive(Debug, Clone)]
pub struct TodoItem {
    pub line: u32,
    pub content: String,
}

#[derive(Debug, Clone)]
pub struct FixmeItem {
    pub line: u32,
    pub content: String,
    pub priority: Priority,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Priority {
    Low,
    Medium,
    High,
}

#[derive(Debug)]
pub struct ComplexLine {
    pub line_number: u32,
    pub content: String,
    pub complexity: i32,
}

#[derive(Debug)]
pub enum LineType {
    Function,
    Struct,
    Enum,
    Impl,
    UseStatement,
    Comment,
    Empty,
    Code,
}

#[derive(Debug)]
pub enum AnalysisError {
    FileError(String),
    ReadError(String),
    ComplexityTooHigh(f64),
}

// Additional supporting structures for the nested processing example
#[derive(Debug)]
pub struct Category {
    pub items: Vec<Item>,
}

#[derive(Debug)]
pub struct Item {
    pub needs_processing: bool,
    pub sub_items: Vec<SubItem>,
}

#[derive(Debug)]
pub struct SubItem {
    pub processor: Option<Processor>,
    pub fixes_applied: u32,
    pub pending_fixes: Vec<Action>,
    pub errors: Vec<ProcessingError>,
}

#[derive(Debug)]
pub struct Processor;

impl Processor {
    pub fn process(&self) -> Result<ProcessingResult, ProcessingError> {
        // Simulate complex processing
        Ok(ProcessingResult::default())
    }
}

#[derive(Debug, Default)]
pub struct ProcessingResult {
    pub is_valid: bool,
    pub validations: Vec<Validation>,
    pub errors: Vec<String>,
}

#[derive(Debug)]
pub struct Validation {
    pub severity: u32,
    pub recommended_actions: Vec<Action>,
}

#[derive(Debug, Clone)]
pub struct Action;

impl Action {
    pub fn apply(&self, _sub_item: &mut SubItem) -> Result<(), String> {
        // Simulate applying a fix
        Ok(())
    }
}

#[derive(Debug)]
pub struct ProcessingConfig {
    pub min_severity: u32,
    pub auto_apply_fixes: bool,
    pub strict_validation: bool,
    pub continue_on_error: bool,
}

#[derive(Debug)]
pub enum ProcessingError {
    ValidationFailed(Vec<String>),
    ProcessingError(ProcessingError),
}

// Helper functions
fn analyze_line_type(line: &str) -> LineType {
    let trimmed = line.trim();

    if trimmed.starts_with("fn ") || trimmed.contains(" fn ") {
        LineType::Function
    } else if trimmed.starts_with("struct ") {
        LineType::Struct
    } else if trimmed.starts_with("enum ") {
        LineType::Enum
    } else if trimmed.starts_with("impl ") {
        LineType::Impl
    } else if trimmed.starts_with("use ") {
        LineType::UseStatement
    } else if trimmed.starts_with("//") || trimmed.starts_with("/*") {
        LineType::Comment
    } else if trimmed.is_empty() {
        LineType::Empty
    } else {
        LineType::Code
    }
}

fn calculate_line_complexity(line: &str) -> i32 {
    let mut complexity = 0;

    // Count various complexity indicators
    complexity += line.matches("if ").count() as i32;
    complexity += line.matches("else").count() as i32;
    complexity += line.matches("match ").count() as i32;
    complexity += line.matches("for ").count() as i32;
    complexity += line.matches("while ").count() as i32;
    complexity += line.matches("loop ").count() as i32;
    complexity += line.matches("&&").count() as i32;
    complexity += line.matches("||").count() as i32;
    complexity += line.matches("?").count() as i32;

    // Penalize long lines and deep nesting
    complexity += (line.len() / 100) as i32;
    complexity += line.chars().take_while(|&c| c == ' ' || c == '\t').count() as i32 / 4;

    complexity
}

fn calculate_overall_complexity(result: &AnalysisResult) -> f64 {
    let base_complexity = result.function_count as f64 * 2.0;
    let control_complexity = (result.loop_count + result.nested_control_structures) as f64 * 3.0;
    let expression_complexity = result.complex_expressions as f64 * 1.5;

    let total_complexity = base_complexity + control_complexity + expression_complexity;
    let lines_factor = (result.code_lines as f64 / 100.0).max(1.0);

    total_complexity / lines_factor
}
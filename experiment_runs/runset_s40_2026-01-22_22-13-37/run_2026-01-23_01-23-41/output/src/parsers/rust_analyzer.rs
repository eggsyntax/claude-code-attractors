//! Advanced Rust-specific code analysis using Tree-sitter
//!
//! This module provides deep analysis capabilities for Rust code, including:
//! - Cyclomatic complexity calculation
//! - Function signature extraction
//! - Ownership pattern detection
//! - Error handling pattern analysis

use super::{FunctionInfo, LanguageAnalyzer};
use tree_sitter::{Language, Node, Query, QueryCursor};

#[derive(Clone)]
pub struct RustAnalyzer {
    // Pre-compiled queries for efficient AST traversal
    function_query: Query,
    complexity_query: Query,
    error_handling_query: Query,
}

impl RustAnalyzer {
    pub fn new() -> Self {
        let language = tree_sitter_rust::language();

        // Query to find all function definitions
        let function_query = Query::new(language, r#"
            (function_item
                name: (identifier) @name
                parameters: (parameters) @params
                return_type: (type_annotation)? @return_type
                body: (block) @body
            ) @function
        "#).expect("Failed to compile function query");

        // Query to find complexity-contributing constructs
        let complexity_query = Query::new(language, r#"
            [
                (if_expression) @branch
                (match_expression) @branch
                (while_expression) @loop
                (for_expression) @loop
                (loop_expression) @loop
                (closure_expression) @closure
            ] @complexity
        "#).expect("Failed to compile complexity query");

        // Query to analyze error handling patterns
        let error_handling_query = Query::new(language, r#"
            [
                (try_expression) @try
                (match_expression
                    (match_arm
                        pattern: (tuple_struct_pattern
                            type: (scoped_identifier
                                name: (identifier) @result_type
                            )
                        ) @result_pattern
                    )
                ) @result_match
                (call_expression
                    function: (field_expression
                        field: (field_identifier) @method_name
                    )
                ) @method_call
            ]
        "#).expect("Failed to compile error handling query");

        Self {
            function_query,
            complexity_query,
            error_handling_query,
        }
    }

    /// Analyzes error handling patterns in Rust code
    pub fn analyze_error_handling(&self, node: &Node, source: &[u8]) -> ErrorHandlingMetrics {
        let mut cursor = QueryCursor::new();
        let matches = cursor.matches(&self.error_handling_query, *node, source);

        let mut try_count = 0;
        let mut result_matches = 0;
        let mut unwrap_calls = 0;
        let mut expect_calls = 0;

        for m in matches {
            for capture in m.captures {
                let capture_name = &self.error_handling_query.capture_names()[capture.index as usize];
                match capture_name.as_str() {
                    "try" => try_count += 1,
                    "result_match" => result_matches += 1,
                    "method_name" => {
                        let text = capture.node.utf8_text(source).unwrap_or("");
                        match text {
                            "unwrap" => unwrap_calls += 1,
                            "expect" => expect_calls += 1,
                            _ => {}
                        }
                    }
                    _ => {}
                }
            }
        }

        ErrorHandlingMetrics {
            try_expressions: try_count,
            result_matches,
            unwrap_calls,
            expect_calls,
        }
    }

    /// Detects common Rust patterns and idioms
    pub fn detect_patterns(&self, node: &Node, source: &[u8]) -> Vec<RustPattern> {
        let mut patterns = Vec::new();

        // Detect iterator patterns
        if self.has_iterator_chain(node, source) {
            patterns.push(RustPattern::IteratorChain);
        }

        // Detect RAII patterns
        if self.has_raii_pattern(node, source) {
            patterns.push(RustPattern::RAII);
        }

        // Detect builder patterns
        if self.has_builder_pattern(node, source) {
            patterns.push(RustPattern::Builder);
        }

        patterns
    }

    fn has_iterator_chain(&self, node: &Node, source: &[u8]) -> bool {
        // Look for method call chains on iterators
        let query = Query::new(tree_sitter_rust::language(), r#"
            (call_expression
                function: (field_expression
                    value: (call_expression
                        function: (field_expression
                            field: (field_identifier) @method1
                        )
                    )
                    field: (field_identifier) @method2
                )
            ) @chain
        "#).unwrap_or_else(|_| return false);

        let mut cursor = QueryCursor::new();
        let matches = cursor.matches(&query, *node, source);

        for _match in matches {
            // If we find chained method calls, it's likely an iterator pattern
            return true;
        }

        false
    }

    fn has_raii_pattern(&self, _node: &Node, _source: &[u8]) -> bool {
        // RAII detection would involve looking for Drop implementations
        // and automatic resource management patterns
        false // Simplified for now
    }

    fn has_builder_pattern(&self, _node: &Node, _source: &[u8]) -> bool {
        // Builder pattern detection would look for methods returning Self
        // and final build() methods
        false // Simplified for now
    }
}

impl LanguageAnalyzer for RustAnalyzer {
    fn language(&self) -> Language {
        tree_sitter_rust::language()
    }

    fn file_extensions(&self) -> &[&str] {
        &["rs"]
    }

    fn analyze_complexity(&self, node: &Node, source: &[u8]) -> u32 {
        let mut cursor = QueryCursor::new();
        let matches = cursor.matches(&self.complexity_query, *node, source);

        let mut complexity = 1; // Base complexity

        for _match in matches {
            complexity += 1;
        }

        complexity
    }

    fn extract_functions(&self, node: &Node, source: &[u8]) -> Vec<FunctionInfo> {
        let mut cursor = QueryCursor::new();
        let matches = cursor.matches(&self.function_query, *node, source);

        let mut functions = Vec::new();

        for m in matches {
            let mut name = String::new();
            let mut params = 0;
            let mut return_type = None;
            let mut body_node = None;
            let mut line_start = 0;
            let mut line_end = 0;

            for capture in m.captures {
                let capture_name = &self.function_query.capture_names()[capture.index as usize];
                match capture_name.as_str() {
                    "name" => {
                        name = capture.node.utf8_text(source).unwrap_or("").to_string();
                    }
                    "params" => {
                        params = capture.node.child_count() as u32;
                    }
                    "return_type" => {
                        return_type = Some(capture.node.utf8_text(source).unwrap_or("").to_string());
                    }
                    "body" => {
                        body_node = Some(capture.node);
                    }
                    "function" => {
                        line_start = capture.node.start_position().row as u32 + 1;
                        line_end = capture.node.end_position().row as u32 + 1;
                    }
                    _ => {}
                }
            }

            let complexity = if let Some(body) = body_node {
                self.analyze_complexity(&body, source)
            } else {
                1
            };

            functions.push(FunctionInfo {
                name,
                line_start,
                line_end,
                complexity,
                parameters: params,
                return_type,
            });
        }

        functions
    }

    fn extract_imports(&self, node: &Node, source: &[u8]) -> Vec<String> {
        let query = Query::new(tree_sitter_rust::language(), r#"
            (use_declaration
                argument: (scoped_identifier) @import
            )
        "#).unwrap_or_else(|_| return Vec::new());

        let mut cursor = QueryCursor::new();
        let matches = cursor.matches(&query, *node, source);

        let mut imports = Vec::new();

        for m in matches {
            for capture in m.captures {
                if let Ok(import_text) = capture.node.utf8_text(source) {
                    imports.push(import_text.to_string());
                }
            }
        }

        imports
    }
}

#[derive(Debug)]
pub struct ErrorHandlingMetrics {
    pub try_expressions: u32,
    pub result_matches: u32,
    pub unwrap_calls: u32,
    pub expect_calls: u32,
}

#[derive(Debug, PartialEq)]
pub enum RustPattern {
    IteratorChain,
    RAII,
    Builder,
    OptionChaining,
    ResultPropagation,
}
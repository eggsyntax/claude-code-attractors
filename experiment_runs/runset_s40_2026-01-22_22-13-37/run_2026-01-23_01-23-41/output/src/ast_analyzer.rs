use anyhow::{Context, Result};
use std::collections::{HashMap, HashSet};
use std::path::Path;
use tree_sitter::{Language, Node, Parser, Query, QueryCursor, Tree};
use crate::core::{CodeIssue, CodeMetrics, IssueSeverity, IssueCategory, Language as LangType};

/// Advanced AST-based code analyzer using tree-sitter
pub struct ASTAnalyzer {
    parsers: HashMap<LangType, Parser>,
    queries: HashMap<LangType, QuerySet>,
}

/// Collection of tree-sitter queries for a specific language
pub struct QuerySet {
    pub functions: Query,
    pub complexity_nodes: Query,
    pub imports: Query,
    pub exports: Query,
    pub security_patterns: Query,
}

/// Detailed function analysis result
#[derive(Debug, Clone)]
pub struct FunctionAnalysis {
    pub name: String,
    pub start_line: u32,
    pub end_line: u32,
    pub parameter_count: u32,
    pub cyclomatic_complexity: u32,
    pub nesting_depth: u32,
    pub lines_of_code: u32,
    pub is_async: bool,
    pub is_recursive: bool,
    pub calls: Vec<String>,
}

/// Import/Export analysis for dependency tracking
#[derive(Debug, Clone)]
pub struct ImportExportAnalysis {
    pub imports: Vec<ImportInfo>,
    pub exports: Vec<ExportInfo>,
}

#[derive(Debug, Clone)]
pub struct ImportInfo {
    pub module_path: String,
    pub imported_names: Vec<String>,
    pub is_default: bool,
    pub line: u32,
}

#[derive(Debug, Clone)]
pub struct ExportInfo {
    pub name: String,
    pub is_default: bool,
    pub line: u32,
}

impl ASTAnalyzer {
    pub fn new() -> Result<Self> {
        let mut parsers = HashMap::new();
        let mut queries = HashMap::new();

        // Initialize parsers for supported languages
        if let Ok(parser) = Self::create_parser(LangType::JavaScript) {
            parsers.insert(LangType::JavaScript, parser);
            queries.insert(LangType::JavaScript, Self::create_js_queries()?);
        }

        if let Ok(parser) = Self::create_parser(LangType::Rust) {
            parsers.insert(LangType::Rust, parser);
            queries.insert(LangType::Rust, Self::create_rust_queries()?);
        }

        if let Ok(parser) = Self::create_parser(LangType::Python) {
            parsers.insert(LangType::Python, parser);
            queries.insert(LangType::Python, Self::create_python_queries()?);
        }

        Ok(Self { parsers, queries })
    }

    /// Parse source code and perform comprehensive analysis
    pub fn analyze_file(&mut self, content: &str, language: &LangType, file_path: &Path) -> Result<(CodeMetrics, Vec<CodeIssue>, Vec<FunctionAnalysis>, ImportExportAnalysis)> {
        let parser = self.parsers.get_mut(language)
            .ok_or_else(|| anyhow::anyhow!("Unsupported language: {:?}", language))?;

        let tree = parser.parse(content, None)
            .ok_or_else(|| anyhow::anyhow!("Failed to parse file"))?;

        let root_node = tree.root_node();

        // Perform different types of analysis
        let functions = self.analyze_functions(&tree, content, language)?;
        let metrics = self.calculate_metrics(&root_node, content, &functions)?;
        let issues = self.detect_issues(&root_node, content, language, file_path, &functions)?;
        let imports_exports = self.analyze_imports_exports(&tree, content, language)?;

        Ok((metrics, issues, functions, imports_exports))
    }

    /// Analyze all functions in the code
    fn analyze_functions(&self, tree: &Tree, content: &str, language: &LangType) -> Result<Vec<FunctionAnalysis>> {
        let queries = self.queries.get(language)
            .ok_or_else(|| anyhow::anyhow!("No queries for language: {:?}", language))?;

        let mut cursor = QueryCursor::new();
        let captures = cursor.matches(&queries.functions, tree.root_node(), content.as_bytes());

        let mut functions = Vec::new();
        let lines: Vec<&str> = content.lines().collect();

        for match_ in captures {
            if let Some(function_node) = match_.captures.get(0).map(|c| c.node) {
                let analysis = self.analyze_single_function(function_node, &lines, content)?;
                functions.push(analysis);
            }
        }

        Ok(functions)
    }

    /// Analyze a single function node in detail
    fn analyze_single_function(&self, node: Node, lines: &[&str], content: &str) -> Result<FunctionAnalysis> {
        let start_line = node.start_position().row as u32 + 1;
        let end_line = node.end_position().row as u32 + 1;

        // Extract function name
        let name = self.extract_function_name(node, content)
            .unwrap_or_else(|| "anonymous".to_string());

        // Count parameters
        let parameter_count = self.count_parameters(node);

        // Calculate cyclomatic complexity
        let cyclomatic_complexity = self.calculate_cyclomatic_complexity(node);

        // Calculate nesting depth
        let nesting_depth = self.calculate_nesting_depth(node);

        // Count lines of code (excluding blanks and comments)
        let lines_of_code = self.count_function_loc(start_line, end_line, lines);

        // Detect async functions
        let is_async = self.is_async_function(node, content);

        // Detect recursive calls
        let is_recursive = self.is_recursive_function(node, content, &name);

        // Extract function calls
        let calls = self.extract_function_calls(node, content);

        Ok(FunctionAnalysis {
            name,
            start_line,
            end_line,
            parameter_count,
            cyclomatic_complexity,
            nesting_depth,
            lines_of_code,
            is_async,
            is_recursive,
            calls,
        })
    }

    /// Calculate comprehensive code metrics
    fn calculate_metrics(&self, root: &Node, content: &str, functions: &[FunctionAnalysis]) -> Result<CodeMetrics> {
        let lines: Vec<&str> = content.lines().collect();
        let total_lines = lines.len() as u32;

        // Count lines of code (excluding comments and blank lines)
        let lines_of_code = lines.iter()
            .filter(|line| {
                let trimmed = line.trim();
                !trimmed.is_empty() &&
                !trimmed.starts_with("//") &&
                !trimmed.starts_with('#') &&
                !trimmed.starts_with("/*")
            })
            .count() as u32;

        let function_count = functions.len() as u32;
        let parameter_count: u32 = functions.iter().map(|f| f.parameter_count).sum();
        let cyclomatic_complexity: u32 = functions.iter().map(|f| f.cyclomatic_complexity).sum();
        let max_nesting_depth = functions.iter().map(|f| f.nesting_depth).max().unwrap_or(0);

        // Calculate maintainability index (simplified version)
        let avg_complexity = if function_count > 0 {
            cyclomatic_complexity as f64 / function_count as f64
        } else {
            1.0
        };
        let avg_loc = if function_count > 0 {
            lines_of_code as f64 / function_count as f64
        } else {
            lines_of_code as f64
        };

        // Simplified maintainability index calculation
        let maintainability_index = (171.0 - 5.2 * avg_complexity.ln() - 0.23 * avg_loc - 16.2 * (lines_of_code as f64).ln())
            .max(0.0)
            .min(100.0);

        Ok(CodeMetrics {
            cyclomatic_complexity,
            lines_of_code,
            total_lines,
            function_count,
            parameter_count,
            max_nesting_depth,
            maintainability_index,
        })
    }

    /// Detect various code quality issues
    fn detect_issues(&self, root: &Node, content: &str, language: &LangType, file_path: &Path, functions: &[FunctionAnalysis]) -> Result<Vec<CodeIssue>> {
        let mut issues = Vec::new();

        // Check for overly complex functions
        for func in functions {
            if func.cyclomatic_complexity > 15 {
                issues.push(CodeIssue {
                    severity: IssueSeverity::Warning,
                    category: IssueCategory::Complexity,
                    message: format!("Function '{}' has high cyclomatic complexity ({})", func.name, func.cyclomatic_complexity),
                    line: func.start_line,
                    column: 1,
                    suggestion: Some("Consider breaking this function into smaller, more focused functions".to_string()),
                });
            }

            if func.parameter_count > 7 {
                issues.push(CodeIssue {
                    severity: IssueSeverity::Warning,
                    category: IssueCategory::Maintainability,
                    message: format!("Function '{}' has too many parameters ({})", func.name, func.parameter_count),
                    line: func.start_line,
                    column: 1,
                    suggestion: Some("Consider using a parameter object or reducing the number of parameters".to_string()),
                });
            }

            if func.lines_of_code > 50 {
                issues.push(CodeIssue {
                    severity: IssueSeverity::Info,
                    category: IssueCategory::Maintainability,
                    message: format!("Function '{}' is quite long ({} lines)", func.name, func.lines_of_code),
                    line: func.start_line,
                    column: 1,
                    suggestion: Some("Consider breaking this function into smaller functions".to_string()),
                });
            }

            if func.nesting_depth > 5 {
                issues.push(CodeIssue {
                    severity: IssueSeverity::Warning,
                    category: IssueCategory::Complexity,
                    message: format!("Function '{}' has deep nesting (depth {})", func.name, func.nesting_depth),
                    line: func.start_line,
                    column: 1,
                    suggestion: Some("Consider using early returns or extracting nested logic".to_string()),
                });
            }
        }

        // Language-specific security pattern detection
        if let Some(queries) = self.queries.get(language) {
            let security_issues = self.detect_security_patterns(root, content, &queries.security_patterns)?;
            issues.extend(security_issues);
        }

        Ok(issues)
    }

    /// Analyze imports and exports for dependency tracking
    fn analyze_imports_exports(&self, tree: &Tree, content: &str, language: &LangType) -> Result<ImportExportAnalysis> {
        let queries = self.queries.get(language)
            .ok_or_else(|| anyhow::anyhow!("No queries for language: {:?}", language))?;

        let mut cursor = QueryCursor::new();
        let mut imports = Vec::new();
        let mut exports = Vec::new();

        // Analyze imports
        let import_matches = cursor.matches(&queries.imports, tree.root_node(), content.as_bytes());
        for match_ in import_matches {
            if let Some(import_info) = self.extract_import_info(match_, content) {
                imports.push(import_info);
            }
        }

        // Analyze exports
        let export_matches = cursor.matches(&queries.exports, tree.root_node(), content.as_bytes());
        for match_ in export_matches {
            if let Some(export_info) = self.extract_export_info(match_, content) {
                exports.push(export_info);
            }
        }

        Ok(ImportExportAnalysis { imports, exports })
    }

    // Helper methods for tree-sitter operations
    fn create_parser(language: LangType) -> Result<Parser> {
        let mut parser = Parser::new();
        let tree_sitter_lang = match language {
            LangType::JavaScript => tree_sitter_javascript::language(),
            LangType::Rust => tree_sitter_rust::language(),
            LangType::Python => tree_sitter_python::language(),
            _ => return Err(anyhow::anyhow!("Unsupported language for parser creation")),
        };
        parser.set_language(&tree_sitter_lang)
            .map_err(|e| anyhow::anyhow!("Failed to set parser language: {}", e))?;
        Ok(parser)
    }

    fn create_js_queries() -> Result<QuerySet> {
        let functions = Query::new(&tree_sitter_javascript::language(),
            "(function_declaration name: (identifier) @func.name) @func.def
             (method_definition name: (property_identifier) @func.name) @func.def
             (arrow_function) @func.def")?;

        let complexity_nodes = Query::new(&tree_sitter_javascript::language(),
            "(if_statement) @decision
             (while_statement) @decision
             (for_statement) @decision
             (for_in_statement) @decision
             (switch_statement) @decision
             (try_statement) @decision")?;

        let imports = Query::new(&tree_sitter_javascript::language(),
            "(import_statement source: (string) @import.source) @import")?;

        let exports = Query::new(&tree_sitter_javascript::language(),
            "(export_statement) @export")?;

        let security_patterns = Query::new(&tree_sitter_javascript::language(),
            "(call_expression function: (identifier) @func (#match? @func \"^(eval|setTimeout|setInterval)$\")) @security.risk")?;

        Ok(QuerySet {
            functions,
            complexity_nodes,
            imports,
            exports,
            security_patterns,
        })
    }

    fn create_rust_queries() -> Result<QuerySet> {
        let functions = Query::new(&tree_sitter_rust::language(),
            "(function_item name: (identifier) @func.name) @func.def")?;

        let complexity_nodes = Query::new(&tree_sitter_rust::language(),
            "(if_expression) @decision
             (while_expression) @decision
             (for_expression) @decision
             (match_expression) @decision
             (loop_expression) @decision")?;

        let imports = Query::new(&tree_sitter_rust::language(),
            "(use_declaration) @import")?;

        let exports = Query::new(&tree_sitter_rust::language(),
            "(visibility_modifier) @export")?;

        let security_patterns = Query::new(&tree_sitter_rust::language(),
            "(macro_invocation macro: (identifier) @macro (#match? @macro \"^(unsafe|panic)$\")) @security.risk")?;

        Ok(QuerySet {
            functions,
            complexity_nodes,
            imports,
            exports,
            security_patterns,
        })
    }

    fn create_python_queries() -> Result<QuerySet> {
        let functions = Query::new(&tree_sitter_python::language(),
            "(function_definition name: (identifier) @func.name) @func.def")?;

        let complexity_nodes = Query::new(&tree_sitter_python::language(),
            "(if_statement) @decision
             (while_statement) @decision
             (for_statement) @decision
             (try_statement) @decision
             (with_statement) @decision")?;

        let imports = Query::new(&tree_sitter_python::language(),
            "(import_statement) @import
             (import_from_statement) @import")?;

        let exports = Query::new(&tree_sitter_python::language(),
            "(assignment left: (identifier) @export)")?;

        let security_patterns = Query::new(&tree_sitter_python::language(),
            "(call function: (identifier) @func (#match? @func \"^(eval|exec|compile)$\")) @security.risk")?;

        Ok(QuerySet {
            functions,
            complexity_nodes,
            imports,
            exports,
            security_patterns,
        })
    }

    // Helper method implementations for AST analysis
    fn extract_function_name(&self, node: Node, content: &str) -> Option<String> {
        let mut cursor = node.walk();

        // Look for function name in children
        if cursor.goto_first_child() {
            loop {
                let child = cursor.node();
                if child.kind() == "identifier" || child.kind() == "property_identifier" {
                    let name = &content[child.start_byte()..child.end_byte()];
                    return Some(name.to_string());
                }
                if !cursor.goto_next_sibling() {
                    break;
                }
            }
        }

        None
    }

    fn count_parameters(&self, node: Node) -> u32 {
        let mut cursor = node.walk();
        let mut param_count = 0;

        if cursor.goto_first_child() {
            loop {
                let child = cursor.node();

                // Look for parameter list nodes
                if child.kind() == "parameters" || child.kind() == "formal_parameters" {
                    let mut param_cursor = child.walk();
                    if param_cursor.goto_first_child() {
                        loop {
                            let param_child = param_cursor.node();
                            // Count parameter nodes (excluding commas and parentheses)
                            if matches!(param_child.kind(), "identifier" | "parameter" | "typed_parameter") {
                                param_count += 1;
                            }
                            if !param_cursor.goto_next_sibling() {
                                break;
                            }
                        }
                    }
                    break;
                }

                if !cursor.goto_next_sibling() {
                    break;
                }
            }
        }

        param_count
    }

    fn calculate_cyclomatic_complexity(&self, node: Node) -> u32 {
        let mut complexity = 1; // Base complexity
        let mut cursor = node.walk();

        // Recursive function to traverse all child nodes
        fn traverse_node(cursor: &mut tree_sitter::TreeCursor, complexity: &mut u32) {
            let node = cursor.node();

            // Count decision points that increase complexity
            match node.kind() {
                "if_statement" | "if_expression" => *complexity += 1,
                "else_clause" | "else" => *complexity += 1,
                "while_statement" | "while_expression" => *complexity += 1,
                "for_statement" | "for_expression" | "for_in_statement" => *complexity += 1,
                "switch_statement" | "match_expression" => *complexity += 1,
                "case_clause" | "match_arm" => *complexity += 1,
                "catch_clause" | "try_statement" => *complexity += 1,
                "conditional_expression" => *complexity += 1, // Ternary operator
                "loop_expression" => *complexity += 1,
                "binary_expression" => {
                    // Count logical operators (&&, ||) as decision points
                    // Note: We'd need to check the operator type in a real implementation
                }
                _ => {}
            }

            // Recursively traverse children
            if cursor.goto_first_child() {
                loop {
                    traverse_node(cursor, complexity);
                    if !cursor.goto_next_sibling() {
                        break;
                    }
                }
                cursor.goto_parent();
            }
        }

        traverse_node(&mut cursor, &mut complexity);
        complexity
    }

    fn calculate_nesting_depth(&self, node: Node) -> u32 {
        let mut max_depth = 0;

        fn traverse_for_depth(node: Node, current_depth: u32, max_depth: &mut u32) {
            let mut nested_depth = current_depth;

            // These node types increase nesting depth
            match node.kind() {
                "if_statement" | "if_expression" |
                "while_statement" | "while_expression" |
                "for_statement" | "for_expression" | "for_in_statement" |
                "switch_statement" | "match_expression" |
                "try_statement" | "catch_clause" |
                "loop_expression" |
                "block" | "compound_statement" => {
                    nested_depth += 1;
                    *max_depth = (*max_depth).max(nested_depth);
                }
                _ => {}
            }

            // Traverse children
            let mut cursor = node.walk();
            if cursor.goto_first_child() {
                loop {
                    traverse_for_depth(cursor.node(), nested_depth, max_depth);
                    if !cursor.goto_next_sibling() {
                        break;
                    }
                }
            }
        }

        traverse_for_depth(node, 0, &mut max_depth);
        max_depth
    }

    fn count_function_loc(&self, start_line: u32, end_line: u32, lines: &[&str]) -> u32 {
        let mut loc = 0;
        let start_idx = (start_line as usize).saturating_sub(1);
        let end_idx = ((end_line as usize).min(lines.len())).saturating_sub(1);

        for i in start_idx..=end_idx.min(lines.len().saturating_sub(1)) {
            let line = lines[i].trim();
            // Count non-empty lines that aren't just comments
            if !line.is_empty() &&
               !line.starts_with("//") &&
               !line.starts_with('#') &&
               !line.starts_with("/*") &&
               !line.starts_with("*") &&
               line != "{" && line != "}" {
                loc += 1;
            }
        }

        loc
    }

    fn is_async_function(&self, node: Node, content: &str) -> bool {
        let mut cursor = node.walk();

        // Check if any child or ancestor contains 'async' keyword
        if cursor.goto_first_child() {
            loop {
                let child = cursor.node();
                if child.kind() == "async" {
                    return true;
                }

                // Check the text content for async keyword
                let text = &content[child.start_byte()..child.end_byte()];
                if text.contains("async") {
                    return true;
                }

                if !cursor.goto_next_sibling() {
                    break;
                }
            }
        }

        false
    }

    fn is_recursive_function(&self, node: Node, content: &str, name: &str) -> bool {
        if name.is_empty() || name == "anonymous" {
            return false;
        }

        let mut cursor = node.walk();

        fn check_for_recursive_call(cursor: &mut tree_sitter::TreeCursor, content: &str, function_name: &str) -> bool {
            let node = cursor.node();

            // Check if this is a call expression
            if node.kind() == "call_expression" || node.kind() == "call" {
                // Look for the function identifier in the call
                let call_text = &content[node.start_byte()..node.end_byte()];
                if call_text.starts_with(function_name) || call_text.contains(&format!("{}(", function_name)) {
                    return true;
                }
            }

            // Check if this is an identifier that matches our function name
            if node.kind() == "identifier" {
                let text = &content[node.start_byte()..node.end_byte()];
                if text == function_name {
                    // Need to check if this is in a call context, not just a declaration
                    if let Some(parent) = node.parent() {
                        if parent.kind() == "call_expression" || parent.kind() == "call" {
                            return true;
                        }
                    }
                }
            }

            // Recursively check children
            if cursor.goto_first_child() {
                loop {
                    if check_for_recursive_call(cursor, content, function_name) {
                        cursor.goto_parent();
                        return true;
                    }
                    if !cursor.goto_next_sibling() {
                        break;
                    }
                }
                cursor.goto_parent();
            }

            false
        }

        check_for_recursive_call(&mut cursor, content, name)
    }

    fn extract_function_calls(&self, node: Node, content: &str) -> Vec<String> {
        let mut calls = Vec::new();
        let mut cursor = node.walk();

        fn collect_calls(cursor: &mut tree_sitter::TreeCursor, content: &str, calls: &mut Vec<String>) {
            let node = cursor.node();

            // Look for call expressions
            if node.kind() == "call_expression" || node.kind() == "call" {
                // Try to find the function name being called
                if cursor.goto_first_child() {
                    let function_node = cursor.node();
                    match function_node.kind() {
                        "identifier" => {
                            let call_name = &content[function_node.start_byte()..function_node.end_byte()];
                            calls.push(call_name.to_string());
                        }
                        "member_expression" | "attribute" => {
                            // For method calls like obj.method()
                            let call_text = &content[function_node.start_byte()..function_node.end_byte()];
                            calls.push(call_text.to_string());
                        }
                        _ => {}
                    }
                    cursor.goto_parent();
                }
            }

            // Recursively check children
            if cursor.goto_first_child() {
                loop {
                    collect_calls(cursor, content, calls);
                    if !cursor.goto_next_sibling() {
                        break;
                    }
                }
                cursor.goto_parent();
            }
        }

        collect_calls(&mut cursor, content, &mut calls);
        calls
    }

    fn detect_security_patterns(&self, root: &Node, content: &str, query: &Query) -> Result<Vec<CodeIssue>> {
        // Implementation would detect security anti-patterns
        Ok(Vec::new())
    }

    fn extract_import_info(&self, match_: tree_sitter::QueryMatch, content: &str) -> Option<ImportInfo> {
        // Implementation would extract import information
        None
    }

    fn extract_export_info(&self, match_: tree_sitter::QueryMatch, content: &str) -> Option<ExportInfo> {
        // Implementation would extract export information
        None
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ast_analyzer_creation() -> Result<()> {
        let analyzer = ASTAnalyzer::new()?;
        assert!(!analyzer.parsers.is_empty());
        assert!(!analyzer.queries.is_empty());
        Ok(())
    }

    #[test]
    fn test_javascript_analysis() -> Result<()> {
        let mut analyzer = ASTAnalyzer::new()?;

        let js_code = r#"
            function calculateTotal(items, tax) {
                let total = 0;
                for (let item of items) {
                    if (item.price > 0) {
                        total += item.price;
                    }
                }
                return total * (1 + tax);
            }
        "#;

        let (metrics, issues, functions, _) = analyzer
            .analyze_file(js_code, &LangType::JavaScript, Path::new("test.js"))?;

        assert!(metrics.function_count > 0);
        assert!(metrics.cyclomatic_complexity >= 1);

        Ok(())
    }
}
use anyhow::{Context, Result};
use std::collections::HashMap;
use tree_sitter::{Language, Node, Parser, Tree};

/// Registry for managing language parsers
pub struct ParserRegistry {
    parsers: HashMap<String, Box<dyn LanguageParser>>,
}

/// Trait for language-specific parsing and analysis
pub trait LanguageParser: Send + Sync {
    /// Parse source code and return syntax tree
    fn parse(&self, source: &str) -> Option<Tree>;

    /// Calculate cyclomatic complexity from AST
    fn calculate_complexity(&self, tree: &Tree) -> Result<u32>;

    /// Count functions/methods in the code
    fn count_functions(&self, tree: &Tree) -> Result<usize>;

    /// Calculate comment-to-code ratio
    fn calculate_comment_ratio(&self, source: &str, tree: &Tree) -> Result<f64>;

    /// Calculate dependency depth/imports
    fn calculate_dependency_depth(&self, tree: &Tree) -> Result<u32>;

    /// Get language name
    fn language_name(&self) -> &str;
}

impl ParserRegistry {
    /// Create new parser registry with supported languages
    pub fn new() -> Result<Self> {
        let mut parsers: HashMap<String, Box<dyn LanguageParser>> = HashMap::new();

        // Register supported languages
        parsers.insert("rs".to_string(), Box::new(RustParser::new()?));
        parsers.insert("js".to_string(), Box::new(JavaScriptParser::new()?));
        parsers.insert("jsx".to_string(), Box::new(JavaScriptParser::new()?));
        parsers.insert("ts".to_string(), Box::new(TypeScriptParser::new()?));
        parsers.insert("tsx".to_string(), Box::new(TypeScriptParser::new()?));
        parsers.insert("py".to_string(), Box::new(PythonParser::new()?));

        Ok(Self { parsers })
    }

    /// Get parser for file extension
    pub fn get_parser(&self, extension: &str) -> Option<&dyn LanguageParser> {
        self.parsers.get(extension).map(|p| p.as_ref())
    }

    /// Check if extension is supported
    pub fn supports_extension(&self, extension: &str) -> bool {
        self.parsers.contains_key(extension)
    }

    /// List all supported extensions
    pub fn supported_extensions(&self) -> Vec<&String> {
        self.parsers.keys().collect()
    }
}

/// Rust language parser
pub struct RustParser {
    parser: Parser,
}

impl RustParser {
    fn new() -> Result<Self> {
        let mut parser = Parser::new();
        parser
            .set_language(tree_sitter_rust::language())
            .context("Failed to set Rust language")?;

        Ok(Self { parser })
    }

    /// Count control flow nodes that add complexity
    fn count_complexity_nodes(&self, node: Node) -> u32 {
        let mut complexity = 0;

        match node.kind() {
            // Decision points that add complexity
            "if_expression" | "match_expression" | "while_expression"
            | "for_expression" | "loop_expression" => complexity += 1,

            // Each match arm adds complexity
            "match_arm" => complexity += 1,

            // Logical operators in conditions
            "binary_expression" => {
                if let Ok(text) = node.utf8_text(&[]) {
                    if text.contains("&&") || text.contains("||") {
                        complexity += 1;
                    }
                }
            }
            _ => {}
        }

        // Recursively check children
        let mut cursor = node.walk();
        for child in node.children(&mut cursor) {
            complexity += self.count_complexity_nodes(child);
        }

        complexity
    }

    /// Count function definitions
    fn count_function_nodes(&self, node: Node) -> usize {
        let mut count = 0;

        if matches!(node.kind(), "function_item" | "impl_item") {
            count += 1;
        }

        // Recursively check children
        let mut cursor = node.walk();
        for child in node.children(&mut cursor) {
            count += self.count_function_nodes(child);
        }

        count
    }
}

impl LanguageParser for RustParser {
    fn parse(&self, source: &str) -> Option<Tree> {
        // Note: In practice, we'd need to handle mutable parser safely
        // This is a simplified version for demonstration
        let mut parser = Parser::new();
        parser.set_language(tree_sitter_rust::language()).ok()?;
        parser.parse(source, None)
    }

    fn calculate_complexity(&self, tree: &Tree) -> Result<u32> {
        let root_node = tree.root_node();
        let complexity = self.count_complexity_nodes(root_node);
        Ok(complexity.max(1)) // Minimum complexity is 1
    }

    fn count_functions(&self, tree: &Tree) -> Result<usize> {
        let root_node = tree.root_node();
        Ok(self.count_function_nodes(root_node))
    }

    fn calculate_comment_ratio(&self, source: &str, _tree: &Tree) -> Result<f64> {
        let total_lines = source.lines().count();
        if total_lines == 0 {
            return Ok(0.0);
        }

        let comment_lines = source
            .lines()
            .filter(|line| {
                let trimmed = line.trim();
                trimmed.starts_with("//") || trimmed.starts_with("/*") || trimmed.starts_with("*")
            })
            .count();

        Ok(comment_lines as f64 / total_lines as f64)
    }

    fn calculate_dependency_depth(&self, tree: &Tree) -> Result<u32> {
        let root_node = tree.root_node();
        let mut depth = 0;

        // Count use statements and extern crate declarations
        let mut cursor = tree.walk();
        for node in root_node.children(&mut cursor) {
            if matches!(node.kind(), "use_declaration" | "extern_crate_declaration") {
                depth += 1;
            }
        }

        Ok(depth)
    }

    fn language_name(&self) -> &str {
        "Rust"
    }
}

/// JavaScript/JSX parser
pub struct JavaScriptParser {
    parser: Parser,
}

impl JavaScriptParser {
    fn new() -> Result<Self> {
        let mut parser = Parser::new();
        parser
            .set_language(tree_sitter_javascript::language())
            .context("Failed to set JavaScript language")?;

        Ok(Self { parser })
    }

    fn count_complexity_nodes(&self, node: Node) -> u32 {
        let mut complexity = 0;

        match node.kind() {
            "if_statement" | "switch_statement" | "while_statement"
            | "for_statement" | "for_in_statement" | "for_of_statement"
            | "do_statement" | "conditional_expression" => complexity += 1,

            "switch_case" => complexity += 1,
            "catch_clause" => complexity += 1,

            "binary_expression" => {
                if let Ok(text) = node.utf8_text(&[]) {
                    if text.contains("&&") || text.contains("||") {
                        complexity += 1;
                    }
                }
            }
            _ => {}
        }

        let mut cursor = node.walk();
        for child in node.children(&mut cursor) {
            complexity += self.count_complexity_nodes(child);
        }

        complexity
    }

    fn count_function_nodes(&self, node: Node) -> usize {
        let mut count = 0;

        if matches!(node.kind(),
            "function_declaration" | "function_expression" | "arrow_function"
            | "method_definition" | "generator_function_declaration"
        ) {
            count += 1;
        }

        let mut cursor = node.walk();
        for child in node.children(&mut cursor) {
            count += self.count_function_nodes(child);
        }

        count
    }
}

impl LanguageParser for JavaScriptParser {
    fn parse(&self, source: &str) -> Option<Tree> {
        let mut parser = Parser::new();
        parser.set_language(tree_sitter_javascript::language()).ok()?;
        parser.parse(source, None)
    }

    fn calculate_complexity(&self, tree: &Tree) -> Result<u32> {
        let root_node = tree.root_node();
        let complexity = self.count_complexity_nodes(root_node);
        Ok(complexity.max(1))
    }

    fn count_functions(&self, tree: &Tree) -> Result<usize> {
        let root_node = tree.root_node();
        Ok(self.count_function_nodes(root_node))
    }

    fn calculate_comment_ratio(&self, source: &str, _tree: &Tree) -> Result<f64> {
        let total_lines = source.lines().count();
        if total_lines == 0 {
            return Ok(0.0);
        }

        let comment_lines = source
            .lines()
            .filter(|line| {
                let trimmed = line.trim();
                trimmed.starts_with("//") || trimmed.starts_with("/*") || trimmed.starts_with("*")
            })
            .count();

        Ok(comment_lines as f64 / total_lines as f64)
    }

    fn calculate_dependency_depth(&self, tree: &Tree) -> Result<u32> {
        let root_node = tree.root_node();
        let mut depth = 0;

        let mut cursor = tree.walk();
        for node in root_node.children(&mut cursor) {
            if matches!(node.kind(), "import_statement" | "import_clause") {
                depth += 1;
            }
        }

        Ok(depth)
    }

    fn language_name(&self) -> &str {
        "JavaScript"
    }
}

/// TypeScript parser (extends JavaScript)
pub struct TypeScriptParser {
    parser: Parser,
}

impl TypeScriptParser {
    fn new() -> Result<Self> {
        let mut parser = Parser::new();
        parser
            .set_language(tree_sitter_typescript::language_typescript())
            .context("Failed to set TypeScript language")?;

        Ok(Self { parser })
    }

    // Reuse JavaScript complexity logic with TypeScript-specific additions
    fn count_complexity_nodes(&self, node: Node) -> u32 {
        let mut complexity = 0;

        match node.kind() {
            "if_statement" | "switch_statement" | "while_statement"
            | "for_statement" | "for_in_statement" | "for_of_statement"
            | "do_statement" | "conditional_expression" => complexity += 1,

            "switch_case" => complexity += 1,
            "catch_clause" => complexity += 1,

            "binary_expression" => {
                if let Ok(text) = node.utf8_text(&[]) {
                    if text.contains("&&") || text.contains("||") {
                        complexity += 1;
                    }
                }
            }
            _ => {}
        }

        let mut cursor = node.walk();
        for child in node.children(&mut cursor) {
            complexity += self.count_complexity_nodes(child);
        }

        complexity
    }

    fn count_function_nodes(&self, node: Node) -> usize {
        let mut count = 0;

        if matches!(node.kind(),
            "function_declaration" | "function_expression" | "arrow_function"
            | "method_definition" | "generator_function_declaration"
            | "method_signature" | "construct_signature"
        ) {
            count += 1;
        }

        let mut cursor = node.walk();
        for child in node.children(&mut cursor) {
            count += self.count_function_nodes(child);
        }

        count
    }
}

impl LanguageParser for TypeScriptParser {
    fn parse(&self, source: &str) -> Option<Tree> {
        let mut parser = Parser::new();
        parser.set_language(tree_sitter_typescript::language_typescript()).ok()?;
        parser.parse(source, None)
    }

    fn calculate_complexity(&self, tree: &Tree) -> Result<u32> {
        let root_node = tree.root_node();
        let complexity = self.count_complexity_nodes(root_node);
        Ok(complexity.max(1))
    }

    fn count_functions(&self, tree: &Tree) -> Result<usize> {
        let root_node = tree.root_node();
        Ok(self.count_function_nodes(root_node))
    }

    fn calculate_comment_ratio(&self, source: &str, _tree: &Tree) -> Result<f64> {
        // Same as JavaScript
        let total_lines = source.lines().count();
        if total_lines == 0 {
            return Ok(0.0);
        }

        let comment_lines = source
            .lines()
            .filter(|line| {
                let trimmed = line.trim();
                trimmed.starts_with("//") || trimmed.starts_with("/*") || trimmed.starts_with("*")
            })
            .count();

        Ok(comment_lines as f64 / total_lines as f64)
    }

    fn calculate_dependency_depth(&self, tree: &Tree) -> Result<u32> {
        let root_node = tree.root_node();
        let mut depth = 0;

        let mut cursor = tree.walk();
        for node in root_node.children(&mut cursor) {
            if matches!(node.kind(), "import_statement" | "import_clause" | "import_require_clause") {
                depth += 1;
            }
        }

        Ok(depth)
    }

    fn language_name(&self) -> &str {
        "TypeScript"
    }
}

/// Python parser
pub struct PythonParser {
    parser: Parser,
}

impl PythonParser {
    fn new() -> Result<Self> {
        let mut parser = Parser::new();
        parser
            .set_language(tree_sitter_python::language())
            .context("Failed to set Python language")?;

        Ok(Self { parser })
    }

    fn count_complexity_nodes(&self, node: Node) -> u32 {
        let mut complexity = 0;

        match node.kind() {
            "if_statement" | "while_statement" | "for_statement"
            | "try_statement" | "with_statement" | "match_statement" => complexity += 1,

            "elif_clause" | "else_clause" | "except_clause" => complexity += 1,
            "case_clause" => complexity += 1,
            "boolean_operator" => complexity += 1,

            _ => {}
        }

        let mut cursor = node.walk();
        for child in node.children(&mut cursor) {
            complexity += self.count_complexity_nodes(child);
        }

        complexity
    }

    fn count_function_nodes(&self, node: Node) -> usize {
        let mut count = 0;

        if matches!(node.kind(), "function_definition" | "async_function_definition") {
            count += 1;
        }

        let mut cursor = node.walk();
        for child in node.children(&mut cursor) {
            count += self.count_function_nodes(child);
        }

        count
    }
}

impl LanguageParser for PythonParser {
    fn parse(&self, source: &str) -> Option<Tree> {
        let mut parser = Parser::new();
        parser.set_language(tree_sitter_python::language()).ok()?;
        parser.parse(source, None)
    }

    fn calculate_complexity(&self, tree: &Tree) -> Result<u32> {
        let root_node = tree.root_node();
        let complexity = self.count_complexity_nodes(root_node);
        Ok(complexity.max(1))
    }

    fn count_functions(&self, tree: &Tree) -> Result<usize> {
        let root_node = tree.root_node();
        Ok(self.count_function_nodes(root_node))
    }

    fn calculate_comment_ratio(&self, source: &str, _tree: &Tree) -> Result<f64> {
        let total_lines = source.lines().count();
        if total_lines == 0 {
            return Ok(0.0);
        }

        let comment_lines = source
            .lines()
            .filter(|line| {
                let trimmed = line.trim();
                trimmed.starts_with("#")
            })
            .count();

        Ok(comment_lines as f64 / total_lines as f64)
    }

    fn calculate_dependency_depth(&self, tree: &Tree) -> Result<u32> {
        let root_node = tree.root_node();
        let mut depth = 0;

        let mut cursor = tree.walk();
        for node in root_node.children(&mut cursor) {
            if matches!(node.kind(), "import_statement" | "import_from_statement") {
                depth += 1;
            }
        }

        Ok(depth)
    }

    fn language_name(&self) -> &str {
        "Python"
    }
}

// Legacy structures for compatibility with existing code
pub struct AstAnalysis {
    pub function_count: usize,
    pub complexity_points: Vec<ComplexityPoint>,
    pub imports: Vec<String>,
    pub exports: Vec<String>,
}

pub struct ComplexityPoint {
    pub line: u32,
    pub column: u32,
    pub kind: ComplexityKind,
}

pub enum ComplexityKind {
    IfStatement,
    Loop,
    Match,
    TryCatch,
}

pub fn analyze_ast(_tree: &Tree, _source: &str) -> AstAnalysis {
    // Legacy function - new code should use LanguageParser trait methods
    AstAnalysis {
        function_count: 0,
        complexity_points: vec![],
        imports: vec![],
        exports: vec![],
    }
}
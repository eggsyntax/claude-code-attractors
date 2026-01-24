use anyhow::{Context, Result};
use std::collections::HashMap;
use tree_sitter::{Language, Node, Parser, Query, QueryCursor, Tree};

/// Supported programming languages for analysis
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum SupportedLanguage {
    Rust,
    JavaScript,
    Python,
    Go,
}

impl SupportedLanguage {
    /// Get the tree-sitter language parser for this language
    pub fn get_language(&self) -> Language {
        match self {
            Self::Rust => tree_sitter_rust::language(),
            Self::JavaScript => tree_sitter_javascript::language(),
            Self::Python => tree_sitter_python::language(),
            Self::Go => tree_sitter_go::language(),
        }
    }

    /// Detect language from file extension
    pub fn from_extension(ext: &str) -> Option<Self> {
        match ext.to_lowercase().as_str() {
            "rs" => Some(Self::Rust),
            "js" | "jsx" | "ts" | "tsx" => Some(Self::JavaScript),
            "py" | "pyx" | "pyi" => Some(Self::Python),
            "go" => Some(Self::Go),
            _ => None,
        }
    }

    /// Get common patterns for different language constructs
    pub fn get_query_patterns(&self) -> &'static LanguagePatterns {
        match self {
            Self::Rust => &RUST_PATTERNS,
            Self::JavaScript => &JAVASCRIPT_PATTERNS,
            Self::Python => &PYTHON_PATTERNS,
            Self::Go => &GO_PATTERNS,
        }
    }
}

/// Query patterns for extracting language-specific constructs
pub struct LanguagePatterns {
    pub functions: &'static str,
    pub classes: &'static str,
    pub imports: &'static str,
    pub conditionals: &'static str,
    pub loops: &'static str,
    pub complexity_nodes: &'static str,
}

// Rust patterns
static RUST_PATTERNS: LanguagePatterns = LanguagePatterns {
    functions: r#"
        (function_item
            name: (identifier) @name
            parameters: (parameters) @params
            body: (block) @body) @function

        (impl_item
            type: (type_identifier) @impl_type
            body: (declaration_list
                (function_item
                    name: (identifier) @method_name) @method)) @impl_block
    "#,

    classes: r#"
        (struct_item
            name: (type_identifier) @name
            body: (field_declaration_list) @fields) @struct

        (enum_item
            name: (type_identifier) @name
            body: (enum_variant_list) @variants) @enum

        (trait_item
            name: (type_identifier) @name
            body: (declaration_list) @methods) @trait
    "#,

    imports: r#"
        (use_declaration
            argument: (use_clause) @import) @use
    "#,

    conditionals: r#"
        (if_expression) @if
        (match_expression) @match
        (match_arm) @match_arm
    "#,

    loops: r#"
        (loop_expression) @loop
        (for_expression) @for
        (while_expression) @while
    "#,

    complexity_nodes: r#"
        (if_expression) @complexity
        (match_arm) @complexity
        (loop_expression) @complexity
        (for_expression) @complexity
        (while_expression) @complexity
        (closure_expression) @complexity
    "#,
};

// JavaScript/TypeScript patterns
static JAVASCRIPT_PATTERNS: LanguagePatterns = LanguagePatterns {
    functions: r#"
        (function_declaration
            name: (identifier) @name
            parameters: (formal_parameters) @params
            body: (statement_block) @body) @function

        (arrow_function
            parameters: (formal_parameters) @params
            body: (_) @body) @arrow_function

        (method_definition
            name: (property_identifier) @name
            value: (function_expression) @function) @method
    "#,

    classes: r#"
        (class_declaration
            name: (identifier) @name
            body: (class_body) @body) @class
    "#,

    imports: r#"
        (import_statement
            source: (string) @source) @import

        (import_clause) @import_clause
    "#,

    conditionals: r#"
        (if_statement) @if
        (switch_statement) @switch
        (conditional_expression) @ternary
    "#,

    loops: r#"
        (for_statement) @for
        (for_in_statement) @for_in
        (while_statement) @while
        (do_statement) @do_while
    "#,

    complexity_nodes: r#"
        (if_statement) @complexity
        (switch_case) @complexity
        (for_statement) @complexity
        (for_in_statement) @complexity
        (while_statement) @complexity
        (do_statement) @complexity
        (arrow_function) @complexity
        (function_expression) @complexity
        (catch_clause) @complexity
    "#,
};

// Python patterns
static PYTHON_PATTERNS: LanguagePatterns = LanguagePatterns {
    functions: r#"
        (function_definition
            name: (identifier) @name
            parameters: (parameters) @params
            body: (block) @body) @function
    "#,

    classes: r#"
        (class_definition
            name: (identifier) @name
            body: (block) @body) @class
    "#,

    imports: r#"
        (import_statement) @import
        (import_from_statement) @import_from
    "#,

    conditionals: r#"
        (if_statement) @if
        (elif_clause) @elif
        (conditional_expression) @ternary
    "#,

    loops: r#"
        (for_statement) @for
        (while_statement) @while
    "#,

    complexity_nodes: r#"
        (if_statement) @complexity
        (elif_clause) @complexity
        (for_statement) @complexity
        (while_statement) @complexity
        (try_statement) @complexity
        (except_clause) @complexity
        (lambda) @complexity
    "#,
};

// Go patterns
static GO_PATTERNS: LanguagePatterns = LanguagePatterns {
    functions: r#"
        (function_declaration
            name: (identifier) @name
            parameters: (parameter_list) @params
            body: (block) @body) @function

        (method_declaration
            receiver: (parameter_list) @receiver
            name: (field_identifier) @name
            parameters: (parameter_list) @params
            body: (block) @body) @method
    "#,

    classes: r#"
        (type_declaration
            (type_spec
                name: (type_identifier) @name
                type: (struct_type) @struct)) @struct_decl

        (type_declaration
            (type_spec
                name: (type_identifier) @name
                type: (interface_type) @interface)) @interface_decl
    "#,

    imports: r#"
        (import_declaration) @import
        (import_spec
            path: (interpreted_string_literal) @import_path) @import_spec
    "#,

    conditionals: r#"
        (if_statement) @if
        (type_switch_statement) @type_switch
        (expression_switch_statement) @switch
    "#,

    loops: r#"
        (for_statement) @for
        (range_clause) @range
    "#,

    complexity_nodes: r#"
        (if_statement) @complexity
        (expression_case) @complexity
        (type_case) @complexity
        (for_statement) @complexity
        (go_statement) @complexity
        (defer_statement) @complexity
        (select_statement) @complexity
    "#,
};

/// Tree-sitter powered parsing engine
pub struct TreeSitterEngine {
    parsers: HashMap<SupportedLanguage, Parser>,
    queries: HashMap<(SupportedLanguage, &'static str), Query>,
}

impl TreeSitterEngine {
    /// Create a new tree-sitter parsing engine
    pub fn new() -> Result<Self> {
        let mut engine = Self {
            parsers: HashMap::new(),
            queries: HashMap::new(),
        };

        // Initialize parsers for all supported languages
        for &language in &[
            SupportedLanguage::Rust,
            SupportedLanguage::JavaScript,
            SupportedLanguage::Python,
            SupportedLanguage::Go,
        ] {
            let mut parser = Parser::new();
            parser.set_language(language.get_language())
                .context(format!("Failed to set language for {:?}", language))?;
            engine.parsers.insert(language, parser);

            // Pre-compile queries for this language
            engine.compile_queries_for_language(language)?;
        }

        Ok(engine)
    }

    /// Parse source code into an AST
    pub fn parse(&mut self, source: &str, language: SupportedLanguage) -> Result<Tree> {
        let parser = self.parsers.get_mut(&language)
            .context(format!("No parser available for {:?}", language))?;

        parser.parse(source, None)
            .context("Failed to parse source code")
    }

    /// Extract functions from the AST
    pub fn extract_functions(&self, tree: &Tree, source: &str, language: SupportedLanguage) -> Result<Vec<FunctionInfo>> {
        let query = self.get_query(language, "functions")?;
        let mut cursor = QueryCursor::new();
        let matches = cursor.matches(query, tree.root_node(), source.as_bytes());

        let mut functions = Vec::new();
        for m in matches {
            if let Some(function_info) = self.extract_function_info(m, source, query) {
                functions.push(function_info);
            }
        }

        Ok(functions)
    }

    /// Calculate cyclomatic complexity for a node
    pub fn calculate_complexity(&self, tree: &Tree, source: &str, language: SupportedLanguage) -> Result<u32> {
        let query = self.get_query(language, "complexity_nodes")?;
        let mut cursor = QueryCursor::new();
        let matches = cursor.matches(query, tree.root_node(), source.as_bytes());

        // Start with base complexity of 1
        let complexity = 1 + matches.count() as u32;
        Ok(complexity)
    }

    fn compile_queries_for_language(&mut self, language: SupportedLanguage) -> Result<()> {
        let patterns = language.get_query_patterns();
        let ts_language = language.get_language();

        // Compile all pattern types
        let pattern_types = [
            ("functions", patterns.functions),
            ("classes", patterns.classes),
            ("imports", patterns.imports),
            ("conditionals", patterns.conditionals),
            ("loops", patterns.loops),
            ("complexity_nodes", patterns.complexity_nodes),
        ];

        for (pattern_type, pattern_source) in pattern_types {
            let query = Query::new(ts_language, pattern_source)
                .context(format!("Failed to compile {} query for {:?}", pattern_type, language))?;
            self.queries.insert((language, pattern_type), query);
        }

        Ok(())
    }

    fn get_query(&self, language: SupportedLanguage, query_type: &'static str) -> Result<&Query> {
        self.queries.get(&(language, query_type))
            .context(format!("No {} query available for {:?}", query_type, language))
    }

    fn extract_function_info(&self, m: tree_sitter::QueryMatch, source: &str, query: &Query) -> Option<FunctionInfo> {
        let mut name = None;
        let mut start_byte = 0;
        let mut end_byte = 0;

        for capture in m.captures {
            let capture_name = &query.capture_names()[capture.index as usize];
            match capture_name.as_str() {
                "name" => {
                    name = Some(capture.node.utf8_text(source.as_bytes()).ok()?.to_string());
                }
                "function" | "method" | "arrow_function" => {
                    start_byte = capture.node.start_byte();
                    end_byte = capture.node.end_byte();
                }
                _ => {}
            }
        }

        name.map(|n| FunctionInfo {
            name: n,
            start_byte,
            end_byte,
            line_count: source[start_byte..end_byte].lines().count() as u32,
        })
    }
}

/// Information about a function extracted from the AST
#[derive(Debug, Clone)]
pub struct FunctionInfo {
    pub name: String,
    pub start_byte: usize,
    pub end_byte: usize,
    pub line_count: u32,
}

impl Default for TreeSitterEngine {
    fn default() -> Self {
        Self::new().expect("Failed to create default TreeSitterEngine")
    }
}
use std::collections::HashMap;
use std::fs;
use std::path::Path;
use tree_sitter::{Language, Node, Parser, Tree, TreeCursor};

/// Core code analyzer that uses tree-sitter for robust parsing across multiple languages
pub struct CodeAnalyzer {
    parsers: HashMap<String, Parser>,
    languages: HashMap<String, Language>,
}

impl CodeAnalyzer {
    pub fn new() -> Self {
        let mut analyzer = Self {
            parsers: HashMap::new(),
            languages: HashMap::new(),
        };

        // Initialize with common languages
        analyzer.register_language("rust", tree_sitter_rust::language());
        analyzer.register_language("javascript", tree_sitter_javascript::language());
        analyzer.register_language("typescript", tree_sitter_typescript::language_typescript());
        analyzer.register_language("python", tree_sitter_python::language());
        analyzer.register_language("go", tree_sitter_go::language());

        analyzer
    }

    /// Register a new language parser
    pub fn register_language(&mut self, name: &str, language: Language) {
        let mut parser = Parser::new();
        parser.set_language(&language).expect("Error loading language");

        self.parsers.insert(name.to_string(), parser);
        self.languages.insert(name.to_string(), language);
    }

    /// Analyze a file and return structured analysis results
    pub fn analyze_file(&mut self, file_path: &Path) -> Result<AnalysisResult, AnalysisError> {
        let content = fs::read_to_string(file_path)?;
        let language = self.detect_language(file_path)?;

        let parser = self.parsers.get_mut(&language)
            .ok_or(AnalysisError::UnsupportedLanguage(language.clone()))?;

        let tree = parser.parse(&content, None)
            .ok_or(AnalysisError::ParseError)?;

        Ok(self.extract_analysis(&tree, &content, &language))
    }

    /// Extract comprehensive analysis from the parsed tree
    fn extract_analysis(&self, tree: &Tree, content: &str, language: &str) -> AnalysisResult {
        let root = tree.root_node();
        let mut cursor = tree.walk();

        let mut result = AnalysisResult::new(language.to_string());

        // Walk the entire tree and extract various patterns
        self.walk_tree(&root, &mut cursor, content, &mut result);

        result
    }

    /// Recursively walk the syntax tree to extract analysis data
    fn walk_tree(&self, node: &Node, cursor: &mut TreeCursor, content: &str, result: &mut AnalysisResult) {
        let node_type = node.kind();
        let node_text = node.utf8_text(content.as_bytes()).unwrap_or("");

        match node_type {
            "function_definition" | "function_declaration" | "method_definition" => {
                result.functions.push(FunctionInfo {
                    name: self.extract_function_name(node, content),
                    line_start: node.start_position().row + 1,
                    line_end: node.end_position().row + 1,
                    complexity: self.calculate_complexity(node, content),
                    parameters: self.extract_parameters(node, content),
                });
            }
            "struct_item" | "class_declaration" | "interface_declaration" => {
                result.types.push(TypeInfo {
                    name: self.extract_type_name(node, content),
                    kind: node_type.to_string(),
                    line_start: node.start_position().row + 1,
                    line_end: node.end_position().row + 1,
                    fields: self.extract_fields(node, content),
                });
            }
            "import_statement" | "use_declaration" | "import_declaration" => {
                result.imports.push(ImportInfo {
                    module: self.extract_import_module(node, content),
                    line: node.start_position().row + 1,
                });
            }
            _ => {}
        }

        // Recursively analyze child nodes
        for i in 0..node.child_count() {
            if let Some(child) = node.child(i) {
                self.walk_tree(&child, cursor, content, result);
            }
        }
    }

    /// Detect programming language from file extension
    fn detect_language(&self, file_path: &Path) -> Result<String, AnalysisError> {
        let extension = file_path.extension()
            .and_then(|ext| ext.to_str())
            .ok_or(AnalysisError::UnknownFileType)?;

        let language = match extension {
            "rs" => "rust",
            "js" => "javascript",
            "ts" => "typescript",
            "py" => "python",
            "go" => "go",
            _ => return Err(AnalysisError::UnsupportedLanguage(extension.to_string())),
        };

        Ok(language.to_string())
    }

    // Helper methods for extracting specific information
    fn extract_function_name(&self, node: &Node, content: &str) -> String {
        // Implementation depends on language-specific node structure
        "function_name".to_string() // Placeholder
    }

    fn calculate_complexity(&self, node: &Node, content: &str) -> u32 {
        // Cyclomatic complexity calculation
        1 // Placeholder
    }

    fn extract_parameters(&self, node: &Node, content: &str) -> Vec<String> {
        Vec::new() // Placeholder
    }

    fn extract_type_name(&self, node: &Node, content: &str) -> String {
        "type_name".to_string() // Placeholder
    }

    fn extract_fields(&self, node: &Node, content: &str) -> Vec<String> {
        Vec::new() // Placeholder
    }

    fn extract_import_module(&self, node: &Node, content: &str) -> String {
        "module_name".to_string() // Placeholder
    }
}

/// Comprehensive analysis results for a single file
#[derive(Debug, Clone)]
pub struct AnalysisResult {
    pub language: String,
    pub functions: Vec<FunctionInfo>,
    pub types: Vec<TypeInfo>,
    pub imports: Vec<ImportInfo>,
    pub metrics: CodeMetrics,
}

impl AnalysisResult {
    fn new(language: String) -> Self {
        Self {
            language,
            functions: Vec::new(),
            types: Vec::new(),
            imports: Vec::new(),
            metrics: CodeMetrics::default(),
        }
    }
}

#[derive(Debug, Clone)]
pub struct FunctionInfo {
    pub name: String,
    pub line_start: usize,
    pub line_end: usize,
    pub complexity: u32,
    pub parameters: Vec<String>,
}

#[derive(Debug, Clone)]
pub struct TypeInfo {
    pub name: String,
    pub kind: String, // struct, class, interface, etc.
    pub line_start: usize,
    pub line_end: usize,
    pub fields: Vec<String>,
}

#[derive(Debug, Clone)]
pub struct ImportInfo {
    pub module: String,
    pub line: usize,
}

#[derive(Debug, Clone, Default)]
pub struct CodeMetrics {
    pub lines_of_code: usize,
    pub comment_lines: usize,
    pub blank_lines: usize,
    pub function_count: usize,
    pub type_count: usize,
    pub average_complexity: f64,
}

#[derive(Debug)]
pub enum AnalysisError {
    IoError(std::io::Error),
    ParseError,
    UnsupportedLanguage(String),
    UnknownFileType,
}

impl From<std::io::Error> for AnalysisError {
    fn from(error: std::io::Error) -> Self {
        AnalysisError::IoError(error)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn test_language_detection() {
        let mut analyzer = CodeAnalyzer::new();

        assert_eq!(analyzer.detect_language(&PathBuf::from("test.rs")).unwrap(), "rust");
        assert_eq!(analyzer.detect_language(&PathBuf::from("test.js")).unwrap(), "javascript");
        assert_eq!(analyzer.detect_language(&PathBuf::from("test.py")).unwrap(), "python");
    }

    #[test]
    fn test_analyzer_initialization() {
        let analyzer = CodeAnalyzer::new();
        assert!(analyzer.languages.contains_key("rust"));
        assert!(analyzer.languages.contains_key("javascript"));
        assert!(analyzer.languages.contains_key("python"));
    }
}
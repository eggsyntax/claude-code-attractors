use std::collections::HashMap;
use tree_sitter::{Node, Query, QueryCursor, QueryMatch};
use crate::code_analyzer::{FunctionInfo, TypeInfo, ImportInfo};

/// Language-specific extractors using tree-sitter queries for robust parsing
pub struct LanguageExtractors {
    queries: HashMap<String, LanguageQueries>,
}

impl LanguageExtractors {
    pub fn new() -> Self {
        let mut extractors = Self {
            queries: HashMap::new(),
        };

        extractors.register_rust_queries();
        extractors.register_javascript_queries();
        extractors.register_typescript_queries();
        extractors.register_python_queries();
        extractors.register_go_queries();

        extractors
    }

    pub fn extract_functions(&self, language: &str, root_node: &Node, content: &str) -> Vec<FunctionInfo> {
        if let Some(queries) = self.queries.get(language) {
            self.run_function_query(&queries.functions, root_node, content)
        } else {
            Vec::new()
        }
    }

    pub fn extract_types(&self, language: &str, root_node: &Node, content: &str) -> Vec<TypeInfo> {
        if let Some(queries) = self.queries.get(language) {
            self.run_type_query(&queries.types, root_node, content)
        } else {
            Vec::new()
        }
    }

    pub fn extract_imports(&self, language: &str, root_node: &Node, content: &str) -> Vec<ImportInfo> {
        if let Some(queries) = self.queries.get(language) {
            self.run_import_query(&queries.imports, root_node, content)
        } else {
            Vec::new()
        }
    }

    fn run_function_query(&self, query: &Query, root_node: &Node, content: &str) -> Vec<FunctionInfo> {
        let mut cursor = QueryCursor::new();
        let matches = cursor.matches(query, *root_node, content.as_bytes());
        let mut functions = Vec::new();

        for query_match in matches {
            if let Some(function_info) = self.extract_function_from_match(&query_match, content) {
                functions.push(function_info);
            }
        }

        functions
    }

    fn run_type_query(&self, query: &Query, root_node: &Node, content: &str) -> Vec<TypeInfo> {
        let mut cursor = QueryCursor::new();
        let matches = cursor.matches(query, *root_node, content.as_bytes());
        let mut types = Vec::new();

        for query_match in matches {
            if let Some(type_info) = self.extract_type_from_match(&query_match, content) {
                types.push(type_info);
            }
        }

        types
    }

    fn run_import_query(&self, query: &Query, root_node: &Node, content: &str) -> Vec<ImportInfo> {
        let mut cursor = QueryCursor::new();
        let matches = cursor.matches(query, *root_node, content.as_bytes());
        let mut imports = Vec::new();

        for query_match in matches {
            if let Some(import_info) = self.extract_import_from_match(&query_match, content) {
                imports.push(import_info);
            }
        }

        imports
    }

    fn extract_function_from_match(&self, query_match: &QueryMatch, content: &str) -> Option<FunctionInfo> {
        // Extract function name and details from the query match
        let mut name = String::from("unknown_function");
        let mut line_start = 1;
        let mut line_end = 1;
        let mut parameters = Vec::new();

        for capture in query_match.captures {
            let node = capture.node;
            let node_text = node.utf8_text(content.as_bytes()).ok()?;

            match capture.index {
                0 => name = node_text.to_string(), // Function name capture
                1 => {
                    // Parameters capture - parse parameter list
                    parameters = self.parse_parameters(node_text);
                }
                _ => {}
            }

            line_start = node.start_position().row + 1;
            line_end = node.end_position().row + 1;
        }

        Some(FunctionInfo {
            name,
            line_start,
            line_end,
            complexity: self.calculate_complexity(&query_match.captures[0].node, content),
            parameters,
        })
    }

    fn extract_type_from_match(&self, query_match: &QueryMatch, content: &str) -> Option<TypeInfo> {
        let mut name = String::from("unknown_type");
        let mut kind = String::from("unknown");
        let mut line_start = 1;
        let mut line_end = 1;
        let mut fields = Vec::new();

        for capture in query_match.captures {
            let node = capture.node;
            let node_text = node.utf8_text(content.as_bytes()).ok()?;

            match capture.index {
                0 => name = node_text.to_string(),
                1 => kind = node.kind().to_string(),
                2 => fields = self.parse_fields(node_text),
                _ => {}
            }

            line_start = node.start_position().row + 1;
            line_end = node.end_position().row + 1;
        }

        Some(TypeInfo {
            name,
            kind,
            line_start,
            line_end,
            fields,
        })
    }

    fn extract_import_from_match(&self, query_match: &QueryMatch, content: &str) -> Option<ImportInfo> {
        let mut module = String::from("unknown_module");
        let mut line = 1;

        for capture in query_match.captures {
            let node = capture.node;
            let node_text = node.utf8_text(content.as_bytes()).ok()?;

            match capture.index {
                0 => module = node_text.to_string(),
                _ => {}
            }

            line = node.start_position().row + 1;
        }

        Some(ImportInfo { module, line })
    }

    fn calculate_complexity(&self, node: &Node, content: &str) -> u32 {
        let mut complexity = 1; // Base complexity
        let mut cursor = node.walk();

        // Walk through the node and count complexity-increasing constructs
        self.walk_node_for_complexity(node, &mut cursor, content, &mut complexity);

        complexity
    }

    fn walk_node_for_complexity(&self, node: &Node, cursor: &mut tree_sitter::TreeCursor, content: &str, complexity: &mut u32) {
        let kind = node.kind();

        // Increment complexity for control flow statements
        match kind {
            "if_statement" | "if_expression" => *complexity += 1,
            "while_statement" | "while_expression" => *complexity += 1,
            "for_statement" | "for_expression" => *complexity += 1,
            "match_expression" | "switch_statement" => *complexity += 1,
            "case_clause" | "match_arm" => *complexity += 1,
            "catch_clause" | "except_clause" => *complexity += 1,
            "conditional_expression" | "ternary_expression" => *complexity += 1,
            "logical_and" | "logical_or" => *complexity += 1,
            _ => {}
        }

        // Recursively analyze child nodes
        for i in 0..node.child_count() {
            if let Some(child) = node.child(i) {
                self.walk_node_for_complexity(&child, cursor, content, complexity);
            }
        }
    }

    fn parse_parameters(&self, param_text: &str) -> Vec<String> {
        // Simple parameter parsing - in a real implementation, this would be more sophisticated
        param_text
            .split(',')
            .map(|p| p.trim().to_string())
            .filter(|p| !p.is_empty())
            .collect()
    }

    fn parse_fields(&self, field_text: &str) -> Vec<String> {
        // Simple field parsing - in a real implementation, this would be more sophisticated
        field_text
            .lines()
            .map(|line| line.trim().to_string())
            .filter(|line| !line.is_empty())
            .collect()
    }

    // Language-specific query registration methods
    fn register_rust_queries(&mut self) {
        let language = tree_sitter_rust::language();

        let function_query = Query::new(&language, r#"
            (function_item
                name: (identifier) @function.name
                parameters: (parameters) @function.params)
            (impl_item
                (function_item
                    name: (identifier) @function.name
                    parameters: (parameters) @function.params))
        "#).expect("Failed to create Rust function query");

        let type_query = Query::new(&language, r#"
            (struct_item
                name: (type_identifier) @type.name
                body: (field_declaration_list) @type.fields)
            (enum_item
                name: (type_identifier) @type.name
                body: (enum_variant_list) @type.variants)
            (trait_item
                name: (type_identifier) @type.name)
        "#).expect("Failed to create Rust type query");

        let import_query = Query::new(&language, r#"
            (use_declaration
                argument: (scoped_use_list
                    path: (identifier) @import.module))
            (use_declaration
                argument: (identifier) @import.module)
        "#).expect("Failed to create Rust import query");

        self.queries.insert("rust".to_string(), LanguageQueries {
            functions: function_query,
            types: type_query,
            imports: import_query,
        });
    }

    fn register_javascript_queries(&mut self) {
        let language = tree_sitter_javascript::language();

        let function_query = Query::new(&language, r#"
            (function_declaration
                name: (identifier) @function.name
                parameters: (formal_parameters) @function.params)
            (arrow_function
                parameters: (formal_parameters) @function.params)
            (method_definition
                name: (property_identifier) @function.name
                parameters: (formal_parameters) @function.params)
        "#).expect("Failed to create JavaScript function query");

        let type_query = Query::new(&language, r#"
            (class_declaration
                name: (identifier) @type.name
                body: (class_body) @type.body)
        "#).expect("Failed to create JavaScript type query");

        let import_query = Query::new(&language, r#"
            (import_statement
                source: (string) @import.module)
        "#).expect("Failed to create JavaScript import query");

        self.queries.insert("javascript".to_string(), LanguageQueries {
            functions: function_query,
            types: type_query,
            imports: import_query,
        });
    }

    fn register_typescript_queries(&mut self) {
        let language = tree_sitter_typescript::language_typescript();

        let function_query = Query::new(&language, r#"
            (function_declaration
                name: (identifier) @function.name
                parameters: (formal_parameters) @function.params)
            (method_definition
                name: (property_identifier) @function.name
                parameters: (formal_parameters) @function.params)
        "#).expect("Failed to create TypeScript function query");

        let type_query = Query::new(&language, r#"
            (interface_declaration
                name: (type_identifier) @type.name
                body: (object_type) @type.body)
            (type_alias_declaration
                name: (type_identifier) @type.name
                value: (_) @type.definition)
        "#).expect("Failed to create TypeScript type query");

        let import_query = Query::new(&language, r#"
            (import_statement
                source: (string) @import.module)
        "#).expect("Failed to create TypeScript import query");

        self.queries.insert("typescript".to_string(), LanguageQueries {
            functions: function_query,
            types: type_query,
            imports: import_query,
        });
    }

    fn register_python_queries(&mut self) {
        let language = tree_sitter_python::language();

        let function_query = Query::new(&language, r#"
            (function_definition
                name: (identifier) @function.name
                parameters: (parameters) @function.params)
        "#).expect("Failed to create Python function query");

        let type_query = Query::new(&language, r#"
            (class_definition
                name: (identifier) @type.name
                body: (block) @type.body)
        "#).expect("Failed to create Python type query");

        let import_query = Query::new(&language, r#"
            (import_statement
                name: (dotted_name) @import.module)
            (import_from_statement
                module_name: (dotted_name) @import.module)
        "#).expect("Failed to create Python import query");

        self.queries.insert("python".to_string(), LanguageQueries {
            functions: function_query,
            types: type_query,
            imports: import_query,
        });
    }

    fn register_go_queries(&mut self) {
        let language = tree_sitter_go::language();

        let function_query = Query::new(&language, r#"
            (function_declaration
                name: (identifier) @function.name
                parameters: (parameter_list) @function.params)
            (method_declaration
                name: (field_identifier) @function.name
                parameters: (parameter_list) @function.params)
        "#).expect("Failed to create Go function query");

        let type_query = Query::new(&language, r#"
            (type_declaration
                (type_spec
                    name: (type_identifier) @type.name
                    type: (struct_type) @type.body))
            (type_declaration
                (type_spec
                    name: (type_identifier) @type.name
                    type: (interface_type) @type.body))
        "#).expect("Failed to create Go type query");

        let import_query = Query::new(&language, r#"
            (import_declaration
                (import_spec
                    path: (interpreted_string_literal) @import.module))
        "#).expect("Failed to create Go import query");

        self.queries.insert("go".to_string(), LanguageQueries {
            functions: function_query,
            types: type_query,
            imports: import_query,
        });
    }
}

struct LanguageQueries {
    functions: Query,
    types: Query,
    imports: Query,
}

#[cfg(test)]
mod tests {
    use super::*;
    use tree_sitter::Parser;

    #[test]
    fn test_rust_function_extraction() {
        let mut parser = Parser::new();
        parser.set_language(&tree_sitter_rust::language()).unwrap();

        let source_code = r#"
            fn calculate_total(items: &[Item], tax_rate: f64) -> f64 {
                let subtotal = items.iter().map(|item| item.price).sum::<f64>();
                subtotal * (1.0 + tax_rate)
            }
        "#;

        let tree = parser.parse(source_code, None).unwrap();
        let extractor = LanguageExtractors::new();
        let functions = extractor.extract_functions("rust", &tree.root_node(), source_code);

        assert_eq!(functions.len(), 1);
        assert_eq!(functions[0].name, "calculate_total");
        assert_eq!(functions[0].parameters.len(), 2);
    }

    #[test]
    fn test_complexity_calculation() {
        let mut parser = Parser::new();
        parser.set_language(&tree_sitter_rust::language()).unwrap();

        let source_code = r#"
            fn complex_function(x: i32) -> i32 {
                if x > 0 {
                    if x > 10 {
                        for i in 0..x {
                            if i % 2 == 0 {
                                return i;
                            }
                        }
                    } else {
                        match x {
                            1 => 1,
                            2 => 2,
                            _ => 0,
                        }
                    }
                } else {
                    while x < 0 {
                        x += 1;
                    }
                }
                x
            }
        "#;

        let tree = parser.parse(source_code, None).unwrap();
        let extractor = LanguageExtractors::new();
        let functions = extractor.extract_functions("rust", &tree.root_node(), source_code);

        assert_eq!(functions.len(), 1);
        // This function should have high complexity due to nested conditions
        assert!(functions[0].complexity > 5);
    }
}
use std::collections::{HashMap, HashSet};
use std::path::Path;
use serde::{Serialize, Deserialize};
use tree_sitter::{Query, QueryCursor};
use crate::analysis::AnalysisResult;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DependencyNode {
    pub id: String,
    pub name: String,
    pub file_path: String,
    pub node_type: NodeType,
    pub complexity: Option<u32>,
    pub line_count: Option<u32>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum NodeType {
    File,
    Module,
    Function,
    Class,
    Import,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DependencyEdge {
    pub source: String,
    pub target: String,
    pub relationship: RelationshipType,
    pub weight: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum RelationshipType {
    Imports,
    Calls,
    Inherits,
    Uses,
    Contains,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DependencyGraph {
    pub nodes: Vec<DependencyNode>,
    pub edges: Vec<DependencyEdge>,
    pub clusters: Vec<DependencyCluster>,
    pub metrics: GraphMetrics,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DependencyCluster {
    pub id: String,
    pub name: String,
    pub nodes: Vec<String>,
    pub internal_edges: usize,
    pub external_edges: usize,
    pub cohesion_score: f32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GraphMetrics {
    pub total_nodes: usize,
    pub total_edges: usize,
    pub circular_dependencies: Vec<Vec<String>>,
    pub strongly_connected_components: Vec<Vec<String>>,
    pub modularity_score: f32,
    pub average_degree: f32,
}

pub struct DependencyAnalyzer {
    import_queries: HashMap<String, Query>,
    call_queries: HashMap<String, Query>,
}

impl DependencyAnalyzer {
    pub fn new() -> Result<Self, Box<dyn std::error::Error>> {
        let mut import_queries = HashMap::new();
        let mut call_queries = HashMap::new();

        // Rust import and call queries
        let rust_lang = tree_sitter_rust::language();

        let rust_import_query = Query::new(rust_lang, r#"
            (use_declaration
                argument: (scoped_use_list
                    path: (scoped_identifier) @import_path
                )
            )
            (use_declaration
                argument: (identifier) @import_name
            )
            (extern_crate_declaration
                name: (identifier) @extern_crate
            )
        "#)?;

        let rust_call_query = Query::new(rust_lang, r#"
            (call_expression
                function: (identifier) @function_call
            )
            (call_expression
                function: (field_expression
                    value: (identifier) @object
                    field: (field_identifier) @method
                )
            )
        "#)?;

        import_queries.insert("rust".to_string(), rust_import_query);
        call_queries.insert("rust".to_string(), rust_call_query);

        // JavaScript/TypeScript queries
        let js_lang = tree_sitter_javascript::language();

        let js_import_query = Query::new(js_lang, r#"
            (import_statement
                source: (string) @import_source
            )
            (import_statement
                (import_clause
                    (named_imports
                        (import_specifier
                            name: (identifier) @import_name
                        )
                    )
                )
            )
            (call_expression
                function: (identifier) @require
                arguments: (arguments (string) @require_path)
                (#eq? @require "require")
            )
        "#)?;

        let js_call_query = Query::new(js_lang, r#"
            (call_expression
                function: (identifier) @function_call
            )
            (call_expression
                function: (member_expression
                    object: (identifier) @object
                    property: (property_identifier) @method
                )
            )
        "#)?;

        import_queries.insert("javascript".to_string(), js_import_query);
        import_queries.insert("typescript".to_string(), js_import_query.clone());
        call_queries.insert("javascript".to_string(), js_call_query);
        call_queries.insert("typescript".to_string(), js_call_query.clone());

        Ok(DependencyAnalyzer {
            import_queries,
            call_queries,
        })
    }

    pub fn analyze_dependencies(&self, results: &[AnalysisResult]) -> Result<DependencyGraph, Box<dyn std::error::Error>> {
        let mut nodes = Vec::new();
        let mut edges = Vec::new();
        let mut node_map = HashMap::new();

        // Create file nodes
        for result in results {
            for file_analysis in &result.files {
                let file_id = self.generate_id(&file_analysis.file_path);
                let file_node = DependencyNode {
                    id: file_id.clone(),
                    name: Path::new(&file_analysis.file_path)
                        .file_name()
                        .and_then(|n| n.to_str())
                        .unwrap_or("unknown")
                        .to_string(),
                    file_path: file_analysis.file_path.clone(),
                    node_type: NodeType::File,
                    complexity: Some(file_analysis.functions.iter().map(|f| f.complexity).sum()),
                    line_count: Some(file_analysis.line_count),
                };

                node_map.insert(file_id.clone(), file_node.clone());
                nodes.push(file_node);

                // Create function nodes
                for func in &file_analysis.functions {
                    let func_id = format!("{}::{}", file_id, func.name);
                    let func_node = DependencyNode {
                        id: func_id.clone(),
                        name: func.name.clone(),
                        file_path: file_analysis.file_path.clone(),
                        node_type: NodeType::Function,
                        complexity: Some(func.complexity),
                        line_count: None,
                    };

                    nodes.push(func_node);

                    // Add contains relationship from file to function
                    edges.push(DependencyEdge {
                        source: file_id.clone(),
                        target: func_id,
                        relationship: RelationshipType::Contains,
                        weight: 1.0,
                    });
                }

                // Analyze imports and calls
                self.analyze_file_dependencies(&result.language, file_analysis, &file_id, &mut edges)?;
            }
        }

        // Calculate graph metrics
        let metrics = self.calculate_graph_metrics(&nodes, &edges);

        // Detect clusters
        let clusters = self.detect_clusters(&nodes, &edges);

        Ok(DependencyGraph {
            nodes,
            edges,
            clusters,
            metrics,
        })
    }

    fn analyze_file_dependencies(
        &self,
        language: &str,
        file_analysis: &crate::analysis::FileAnalysis,
        file_id: &str,
        edges: &mut Vec<DependencyEdge>,
    ) -> Result<(), Box<dyn std::error::Error>> {
        // This is a simplified version - in practice, you'd parse the actual file content
        // with tree-sitter to extract real import and call relationships

        // For demonstration, we'll add some mock relationships based on common patterns
        if file_analysis.file_path.contains("main") {
            // Main files typically import other modules
            for func in &file_analysis.functions {
                if func.name.contains("init") || func.name.contains("setup") {
                    edges.push(DependencyEdge {
                        source: file_id.to_string(),
                        target: format!("config::{}", "load_config"),
                        relationship: RelationshipType::Calls,
                        weight: func.complexity as f32,
                    });
                }
            }
        }

        if file_analysis.file_path.contains("config") {
            edges.push(DependencyEdge {
                source: file_id.to_string(),
                target: "std::env".to_string(),
                relationship: RelationshipType::Uses,
                weight: 1.0,
            });
        }

        Ok(())
    }

    fn calculate_graph_metrics(&self, nodes: &[DependencyNode], edges: &[DependencyEdge]) -> GraphMetrics {
        let total_nodes = nodes.len();
        let total_edges = edges.len();

        // Calculate degree distribution
        let mut degree_sum = 0;
        let mut node_degrees = HashMap::new();

        for edge in edges {
            *node_degrees.entry(&edge.source).or_insert(0) += 1;
            *node_degrees.entry(&edge.target).or_insert(0) += 1;
            degree_sum += 2; // Each edge contributes to two nodes
        }

        let average_degree = if total_nodes > 0 {
            degree_sum as f32 / total_nodes as f32
        } else {
            0.0
        };

        // Detect circular dependencies (simplified)
        let circular_dependencies = self.detect_circular_dependencies(edges);

        // Calculate modularity score (simplified)
        let modularity_score = self.calculate_modularity(nodes, edges);

        GraphMetrics {
            total_nodes,
            total_edges,
            circular_dependencies,
            strongly_connected_components: Vec::new(), // Would implement Tarjan's algorithm
            modularity_score,
            average_degree,
        }
    }

    fn detect_circular_dependencies(&self, edges: &[DependencyEdge]) -> Vec<Vec<String>> {
        // Simplified circular dependency detection
        let mut adjacency = HashMap::new();

        for edge in edges {
            adjacency.entry(edge.source.clone())
                .or_insert_with(Vec::new)
                .push(edge.target.clone());
        }

        // For now, return empty - would implement cycle detection algorithm
        Vec::new()
    }

    fn calculate_modularity(&self, _nodes: &[DependencyNode], _edges: &[DependencyEdge]) -> f32 {
        // Simplified modularity calculation
        // In practice, would implement proper modularity calculation
        0.5
    }

    fn detect_clusters(&self, nodes: &[DependencyNode], edges: &[DependencyEdge]) -> Vec<DependencyCluster> {
        let mut clusters = Vec::new();
        let mut file_clusters = HashMap::new();

        // Group nodes by directory structure
        for node in nodes {
            if let NodeType::File = node.node_type {
                let path = Path::new(&node.file_path);
                let dir = path.parent()
                    .and_then(|p| p.to_str())
                    .unwrap_or("")
                    .to_string();

                file_clusters.entry(dir.clone())
                    .or_insert_with(Vec::new)
                    .push(node.id.clone());
            }
        }

        // Create clusters from directory groupings
        for (dir, node_ids) in file_clusters {
            if node_ids.len() > 1 {
                let cluster_name = Path::new(&dir)
                    .file_name()
                    .and_then(|n| n.to_str())
                    .unwrap_or("root")
                    .to_string();

                let internal_edges = edges.iter()
                    .filter(|e| node_ids.contains(&e.source) && node_ids.contains(&e.target))
                    .count();

                let external_edges = edges.iter()
                    .filter(|e| {
                        (node_ids.contains(&e.source) && !node_ids.contains(&e.target)) ||
                        (!node_ids.contains(&e.source) && node_ids.contains(&e.target))
                    })
                    .count();

                let cohesion_score = if internal_edges + external_edges > 0 {
                    internal_edges as f32 / (internal_edges + external_edges) as f32
                } else {
                    0.0
                };

                clusters.push(DependencyCluster {
                    id: self.generate_id(&dir),
                    name: cluster_name,
                    nodes: node_ids,
                    internal_edges,
                    external_edges,
                    cohesion_score,
                });
            }
        }

        clusters
    }

    fn generate_id(&self, path: &str) -> String {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};

        let mut hasher = DefaultHasher::new();
        path.hash(&mut hasher);
        format!("node_{:x}", hasher.finish())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_dependency_analyzer_creation() {
        let analyzer = DependencyAnalyzer::new();
        assert!(analyzer.is_ok());
    }

    #[test]
    fn test_graph_metrics_calculation() {
        let analyzer = DependencyAnalyzer::new().unwrap();
        let nodes = vec![];
        let edges = vec![];

        let metrics = analyzer.calculate_graph_metrics(&nodes, &edges);
        assert_eq!(metrics.total_nodes, 0);
        assert_eq!(metrics.total_edges, 0);
    }
}
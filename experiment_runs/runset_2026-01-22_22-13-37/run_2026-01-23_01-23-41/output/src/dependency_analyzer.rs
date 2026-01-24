use anyhow::{Context, Result};
use std::collections::{HashMap, HashSet, VecDeque};
use std::path::{Path, PathBuf};
use crate::core::types::{DependencyGraph, DependencyNode, DependencyEdge, ImportType, Language};
use crate::ast_analyzer::{ImportExportAnalysis, ImportInfo, ExportInfo};

/// Analyzes dependencies between modules to build a comprehensive dependency graph
pub struct DependencyAnalyzer {
    root_path: PathBuf,
    module_registry: HashMap<String, ModuleInfo>,
    resolved_paths: HashMap<String, PathBuf>,
}

/// Internal representation of a module's metadata
#[derive(Debug, Clone)]
struct ModuleInfo {
    file_path: PathBuf,
    module_name: String,
    language: Language,
    imports: Vec<ImportInfo>,
    exports: Vec<ExportInfo>,
    external_dependencies: HashSet<String>,
}

/// Comprehensive dependency analysis result
#[derive(Debug)]
pub struct DependencyAnalysisResult {
    pub graph: DependencyGraph,
    pub circular_dependencies: Vec<CircularDependency>,
    pub unused_exports: Vec<UnusedExport>,
    pub external_dependencies: HashMap<String, u32>, // dependency name -> usage count
    pub dependency_depth: HashMap<String, u32>,
    pub module_coupling: Vec<ModuleCoupling>,
}

#[derive(Debug)]
pub struct CircularDependency {
    pub cycle: Vec<String>,
    pub severity: CycleSeverity,
}

#[derive(Debug)]
pub enum CycleSeverity {
    Low,    // Self-reference or 2-node cycle
    Medium, // 3-4 node cycle
    High,   // 5+ node cycle
}

#[derive(Debug)]
pub struct UnusedExport {
    pub module_name: String,
    pub export_name: String,
    pub file_path: PathBuf,
    pub line: u32,
}

#[derive(Debug)]
pub struct ModuleCoupling {
    pub module_name: String,
    pub afferent_coupling: u32,  // Number of modules that depend on this module
    pub efferent_coupling: u32,  // Number of modules this module depends on
    pub instability: f64,        // Efferent / (Afferent + Efferent)
    pub abstractness: f64,       // Abstract classes/interfaces / Total classes
}

impl DependencyAnalyzer {
    pub fn new(root_path: PathBuf) -> Self {
        Self {
            root_path,
            module_registry: HashMap::new(),
            resolved_paths: HashMap::new(),
        }
    }

    /// Perform comprehensive dependency analysis
    pub fn analyze(&mut self, import_export_data: HashMap<PathBuf, (Language, ImportExportAnalysis)>) -> Result<DependencyAnalysisResult> {
        // Step 1: Build module registry
        self.build_module_registry(import_export_data)?;

        // Step 2: Resolve module paths and build dependency graph
        let graph = self.build_dependency_graph()?;

        // Step 3: Detect circular dependencies
        let circular_dependencies = self.detect_circular_dependencies(&graph)?;

        // Step 4: Find unused exports
        let unused_exports = self.find_unused_exports(&graph)?;

        // Step 5: Analyze external dependencies
        let external_dependencies = self.analyze_external_dependencies()?;

        // Step 6: Calculate dependency depths
        let dependency_depth = self.calculate_dependency_depths(&graph)?;

        // Step 7: Calculate module coupling metrics
        let module_coupling = self.calculate_module_coupling(&graph)?;

        Ok(DependencyAnalysisResult {
            graph,
            circular_dependencies,
            unused_exports,
            external_dependencies,
            dependency_depth,
            module_coupling,
        })
    }

    /// Build a registry of all modules with their import/export information
    fn build_module_registry(&mut self, data: HashMap<PathBuf, (Language, ImportExportAnalysis)>) -> Result<()> {
        for (file_path, (language, import_export_analysis)) in data {
            let module_name = self.path_to_module_name(&file_path, &language);

            let mut external_dependencies = HashSet::new();

            // Identify external vs internal dependencies
            for import in &import_export_analysis.imports {
                if self.is_external_dependency(&import.module_path, &language) {
                    external_dependencies.insert(import.module_path.clone());
                }
            }

            let module_info = ModuleInfo {
                file_path: file_path.clone(),
                module_name: module_name.clone(),
                language,
                imports: import_export_analysis.imports,
                exports: import_export_analysis.exports,
                external_dependencies,
            };

            self.module_registry.insert(module_name, module_info);
        }

        Ok(())
    }

    /// Build the dependency graph from the module registry
    fn build_dependency_graph(&mut self) -> Result<DependencyGraph> {
        let mut nodes = Vec::new();
        let mut edges = Vec::new();

        // Create nodes
        for (module_name, module_info) in &self.module_registry {
            let node = DependencyNode {
                id: module_name.clone(),
                file_path: module_info.file_path.clone(),
                module_name: module_name.clone(),
                exports: module_info.exports.iter().map(|e| e.name.clone()).collect(),
            };
            nodes.push(node);
        }

        // Create edges
        for (module_name, module_info) in &self.module_registry {
            for import in &module_info.imports {
                if let Some(target_module) = self.resolve_import_to_module(&import.module_path, &module_info.language) {
                    let edge = DependencyEdge {
                        from: module_name.clone(),
                        to: target_module,
                        import_type: if import.is_default {
                            ImportType::Default
                        } else if import.imported_names.is_empty() {
                            ImportType::Namespace
                        } else {
                            ImportType::Named
                        },
                        imported_symbols: import.imported_names.clone(),
                    };
                    edges.push(edge);
                }
            }
        }

        Ok(DependencyGraph { nodes, edges })
    }

    /// Detect circular dependencies using depth-first search
    fn detect_circular_dependencies(&self, graph: &DependencyGraph) -> Result<Vec<CircularDependency>> {
        let mut circular_deps = Vec::new();
        let mut visited = HashSet::new();
        let mut rec_stack = HashSet::new();
        let mut path_stack = Vec::new();

        // Build adjacency list
        let mut adjacency = HashMap::new();
        for edge in &graph.edges {
            adjacency.entry(edge.from.clone())
                .or_insert_with(Vec::new)
                .push(edge.to.clone());
        }

        for node in &graph.nodes {
            if !visited.contains(&node.id) {
                if let Some(cycle) = self.dfs_cycle_detection(
                    &node.id,
                    &adjacency,
                    &mut visited,
                    &mut rec_stack,
                    &mut path_stack,
                ) {
                    let severity = match cycle.len() {
                        1..=2 => CycleSeverity::Low,
                        3..=4 => CycleSeverity::Medium,
                        _ => CycleSeverity::High,
                    };

                    circular_deps.push(CircularDependency {
                        cycle,
                        severity,
                    });
                }
            }
        }

        Ok(circular_deps)
    }

    /// DFS-based cycle detection algorithm
    fn dfs_cycle_detection(
        &self,
        node: &str,
        adjacency: &HashMap<String, Vec<String>>,
        visited: &mut HashSet<String>,
        rec_stack: &mut HashSet<String>,
        path_stack: &mut Vec<String>,
    ) -> Option<Vec<String>> {
        visited.insert(node.to_string());
        rec_stack.insert(node.to_string());
        path_stack.push(node.to_string());

        if let Some(neighbors) = adjacency.get(node) {
            for neighbor in neighbors {
                if !visited.contains(neighbor) {
                    if let Some(cycle) = self.dfs_cycle_detection(
                        neighbor,
                        adjacency,
                        visited,
                        rec_stack,
                        path_stack,
                    ) {
                        return Some(cycle);
                    }
                } else if rec_stack.contains(neighbor) {
                    // Found a cycle - extract the cycle path
                    if let Some(cycle_start) = path_stack.iter().position(|x| x == neighbor) {
                        let mut cycle = path_stack[cycle_start..].to_vec();
                        cycle.push(neighbor.to_string());
                        return Some(cycle);
                    }
                }
            }
        }

        rec_stack.remove(node);
        path_stack.pop();
        None
    }

    /// Find exports that are never imported by any module
    fn find_unused_exports(&self, graph: &DependencyGraph) -> Result<Vec<UnusedExport>> {
        let mut used_symbols = HashSet::new();

        // Collect all imported symbols
        for edge in &graph.edges {
            for symbol in &edge.imported_symbols {
                used_symbols.insert(format!("{}::{}", edge.to, symbol));
            }
        }

        let mut unused_exports = Vec::new();

        // Find unused exports
        for (module_name, module_info) in &self.module_registry {
            for export in &module_info.exports {
                let symbol_key = format!("{}::{}", module_name, export.name);
                if !used_symbols.contains(&symbol_key) && !export.is_default {
                    unused_exports.push(UnusedExport {
                        module_name: module_name.clone(),
                        export_name: export.name.clone(),
                        file_path: module_info.file_path.clone(),
                        line: export.line,
                    });
                }
            }
        }

        Ok(unused_exports)
    }

    /// Analyze usage of external dependencies
    fn analyze_external_dependencies(&self) -> Result<HashMap<String, u32>> {
        let mut external_deps = HashMap::new();

        for (_, module_info) in &self.module_registry {
            for dep in &module_info.external_dependencies {
                *external_deps.entry(dep.clone()).or_insert(0) += 1;
            }
        }

        Ok(external_deps)
    }

    /// Calculate dependency depth for each module (distance from leaves)
    fn calculate_dependency_depths(&self, graph: &DependencyGraph) -> Result<HashMap<String, u32>> {
        let mut depths = HashMap::new();
        let mut adjacency = HashMap::new();
        let mut reverse_adjacency = HashMap::new();

        // Build adjacency lists
        for edge in &graph.edges {
            adjacency.entry(edge.from.clone())
                .or_insert_with(Vec::new)
                .push(edge.to.clone());

            reverse_adjacency.entry(edge.to.clone())
                .or_insert_with(Vec::new)
                .push(edge.from.clone());
        }

        // Find leaf nodes (no outgoing dependencies)
        let mut queue = VecDeque::new();
        for node in &graph.nodes {
            if !adjacency.contains_key(&node.id) {
                depths.insert(node.id.clone(), 0);
                queue.push_back((node.id.clone(), 0));
            }
        }

        // BFS to calculate depths
        while let Some((node, depth)) = queue.pop_front() {
            if let Some(dependents) = reverse_adjacency.get(&node) {
                for dependent in dependents {
                    let new_depth = depth + 1;
                    let current_depth = depths.get(dependent).unwrap_or(&u32::MAX);
                    if new_depth < *current_depth {
                        depths.insert(dependent.clone(), new_depth);
                        queue.push_back((dependent.clone(), new_depth));
                    }
                }
            }
        }

        Ok(depths)
    }

    /// Calculate coupling metrics for each module
    fn calculate_module_coupling(&self, graph: &DependencyGraph) -> Result<Vec<ModuleCoupling>> {
        let mut coupling_metrics = Vec::new();
        let mut afferent = HashMap::new();
        let mut efferent = HashMap::new();

        // Count incoming and outgoing dependencies
        for edge in &graph.edges {
            *efferent.entry(edge.from.clone()).or_insert(0) += 1;
            *afferent.entry(edge.to.clone()).or_insert(0) += 1;
        }

        for node in &graph.nodes {
            let afferent_coupling = *afferent.get(&node.id).unwrap_or(&0);
            let efferent_coupling = *efferent.get(&node.id).unwrap_or(&0);

            let instability = if afferent_coupling + efferent_coupling > 0 {
                efferent_coupling as f64 / (afferent_coupling + efferent_coupling) as f64
            } else {
                0.0
            };

            // Simplified abstractness calculation - would need more sophisticated analysis
            let abstractness = 0.0; // TODO: Implement proper abstractness calculation

            coupling_metrics.push(ModuleCoupling {
                module_name: node.id.clone(),
                afferent_coupling,
                efferent_coupling,
                instability,
                abstractness,
            });
        }

        Ok(coupling_metrics)
    }

    // Helper methods
    fn path_to_module_name(&self, file_path: &Path, language: &Language) -> String {
        // Convert file path to module name based on language conventions
        let relative_path = file_path.strip_prefix(&self.root_path).unwrap_or(file_path);
        let path_str = relative_path.to_string_lossy();

        match language {
            Language::JavaScript | Language::TypeScript => {
                path_str.trim_end_matches(".js")
                    .trim_end_matches(".ts")
                    .trim_end_matches(".jsx")
                    .trim_end_matches(".tsx")
                    .replace('/', "::")
                    .to_string()
            }
            Language::Rust => {
                path_str.trim_end_matches(".rs")
                    .replace('/', "::")
                    .to_string()
            }
            Language::Python => {
                path_str.trim_end_matches(".py")
                    .replace('/', ".")
                    .to_string()
            }
            _ => path_str.to_string(),
        }
    }

    fn is_external_dependency(&self, import_path: &str, language: &Language) -> bool {
        match language {
            Language::JavaScript | Language::TypeScript => {
                // External if it doesn't start with ./ or ../
                !import_path.starts_with('./') && !import_path.starts_with("../")
            }
            Language::Rust => {
                // External if it doesn't start with crate:: or super:: or self::
                !import_path.starts_with("crate::")
                    && !import_path.starts_with("super::")
                    && !import_path.starts_with("self::")
            }
            Language::Python => {
                // External if it doesn't start with . (relative import)
                !import_path.starts_with('.')
            }
            _ => true,
        }
    }

    fn resolve_import_to_module(&self, import_path: &str, language: &Language) -> Option<String> {
        // This would implement sophisticated module resolution logic
        // For now, return a simplified version
        if self.is_external_dependency(import_path, language) {
            None
        } else {
            Some(import_path.to_string())
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_dependency_analyzer_creation() {
        let analyzer = DependencyAnalyzer::new(PathBuf::from("."));
        assert!(analyzer.module_registry.is_empty());
    }

    #[test]
    fn test_external_dependency_detection() {
        let analyzer = DependencyAnalyzer::new(PathBuf::from("."));

        // JavaScript/TypeScript tests
        assert!(analyzer.is_external_dependency("react", &Language::JavaScript));
        assert!(!analyzer.is_external_dependency("./components", &Language::JavaScript));
        assert!(!analyzer.is_external_dependency("../utils", &Language::JavaScript));

        // Rust tests
        assert!(analyzer.is_external_dependency("serde", &Language::Rust));
        assert!(!analyzer.is_external_dependency("crate::utils", &Language::Rust));
        assert!(!analyzer.is_external_dependency("super::types", &Language::Rust));

        // Python tests
        assert!(analyzer.is_external_dependency("numpy", &Language::Python));
        assert!(!analyzer.is_external_dependency(".utils", &Language::Python));
    }
}
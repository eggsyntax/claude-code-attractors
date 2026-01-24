use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::Path;

/// Interactive HTML report generator for code analysis results
///
/// This module creates rich, interactive HTML reports with:
/// - Complexity heatmaps
/// - Dependency graphs
/// - Actionable insights dashboard
/// - Drill-down capabilities for detailed analysis

#[derive(Debug, Serialize, Deserialize)]
pub struct ReportData {
    pub project_name: String,
    pub analysis_timestamp: String,
    pub summary_metrics: SummaryMetrics,
    pub file_analysis: Vec<FileAnalysis>,
    pub complexity_distribution: HashMap<String, u32>,
    pub dependency_graph: DependencyGraph,
    pub insights: Vec<ActionableInsight>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SummaryMetrics {
    pub total_files: usize,
    pub total_functions: usize,
    pub average_complexity: f64,
    pub high_complexity_functions: usize,
    pub complexity_threshold: u32,
    pub lines_of_code: usize,
    pub technical_debt_score: f64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct FileAnalysis {
    pub path: String,
    pub language: String,
    pub complexity_score: u32,
    pub function_count: usize,
    pub lines_of_code: usize,
    pub functions: Vec<FunctionMetrics>,
    pub imports: Vec<String>,
    pub complexity_hotspots: Vec<ComplexityHotspot>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct FunctionMetrics {
    pub name: String,
    pub line_start: u32,
    pub line_end: u32,
    pub complexity: u32,
    pub parameters: usize,
    pub lines_of_code: usize,
    pub cognitive_complexity: u32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ComplexityHotspot {
    pub function_name: String,
    pub complexity: u32,
    pub line_number: u32,
    pub severity: HotspotSeverity,
    pub recommendation: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub enum HotspotSeverity {
    Low,
    Medium,
    High,
    Critical,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DependencyGraph {
    pub nodes: Vec<DependencyNode>,
    pub edges: Vec<DependencyEdge>,
    pub circular_dependencies: Vec<Vec<String>>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DependencyNode {
    pub id: String,
    pub label: String,
    pub module_type: String,
    pub complexity_score: u32,
    pub size: usize,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct DependencyEdge {
    pub from: String,
    pub to: String,
    pub strength: f64,
    pub edge_type: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ActionableInsight {
    pub category: InsightCategory,
    pub title: String,
    pub description: String,
    pub priority: Priority,
    pub affected_files: Vec<String>,
    pub recommendation: String,
    pub effort_estimate: EffortEstimate,
}

#[derive(Debug, Serialize, Deserialize)]
pub enum InsightCategory {
    Complexity,
    Dependencies,
    TechnicalDebt,
    Performance,
    Maintainability,
}

#[derive(Debug, Serialize, Deserialize)]
pub enum Priority {
    Low,
    Medium,
    High,
    Critical,
}

#[derive(Debug, Serialize, Deserialize)]
pub enum EffortEstimate {
    Small,    // < 1 day
    Medium,   // 1-3 days
    Large,    // 1-2 weeks
    XLarge,   // > 2 weeks
}

pub struct ReportGenerator {
    template_path: String,
}

impl ReportGenerator {
    pub fn new() -> Self {
        Self {
            template_path: "templates/report.html".to_string(),
        }
    }

    /// Generate comprehensive HTML report with interactive visualizations
    pub fn generate_report(&self, data: &ReportData, output_path: &Path) -> Result<(), Box<dyn std::error::Error>> {
        let html_content = self.generate_html_content(data)?;
        fs::write(output_path, html_content)?;

        // Copy static assets (CSS, JS, images)
        self.copy_static_assets(output_path.parent().unwrap())?;

        println!("✅ Interactive report generated: {}", output_path.display());
        Ok(())
    }

    fn generate_html_content(&self, data: &ReportData) -> Result<String, Box<dyn std::error::Error>> {
        let template = include_str!("../templates/report_template.html");

        // Serialize data for JavaScript consumption
        let data_json = serde_json::to_string_pretty(data)?;

        // Replace template placeholders
        let html = template
            .replace("{{PROJECT_NAME}}", &data.project_name)
            .replace("{{ANALYSIS_TIMESTAMP}}", &data.analysis_timestamp)
            .replace("{{REPORT_DATA}}", &data_json)
            .replace("{{COMPLEXITY_HEATMAP_DATA}}", &self.generate_heatmap_data(data)?)
            .replace("{{DEPENDENCY_GRAPH_DATA}}", &self.generate_dependency_graph_data(data)?)
            .replace("{{INSIGHTS_DATA}}", &self.generate_insights_data(data)?);

        Ok(html)
    }

    fn generate_heatmap_data(&self, data: &ReportData) -> Result<String, Box<dyn std::error::Error>> {
        let heatmap_data: Vec<_> = data.file_analysis
            .iter()
            .map(|file| {
                serde_json::json!({
                    "file": file.path,
                    "complexity": file.complexity_score,
                    "functions": file.function_count,
                    "loc": file.lines_of_code,
                    "hotspots": file.complexity_hotspots.len()
                })
            })
            .collect();

        Ok(serde_json::to_string(&heatmap_data)?)
    }

    fn generate_dependency_graph_data(&self, data: &ReportData) -> Result<String, Box<dyn std::error::Error>> {
        Ok(serde_json::to_string(&data.dependency_graph)?)
    }

    fn generate_insights_data(&self, data: &ReportData) -> Result<String, Box<dyn std::error::Error>> {
        Ok(serde_json::to_string(&data.insights)?)
    }

    fn copy_static_assets(&self, output_dir: &Path) -> Result<(), Box<dyn std::error::Error>> {
        // This would copy CSS, JavaScript, and other static files
        // For now, we'll create the basic structure
        let assets_dir = output_dir.join("assets");
        fs::create_dir_all(&assets_dir)?;

        // Create basic CSS
        let css_content = include_str!("../templates/styles.css");
        fs::write(assets_dir.join("styles.css"), css_content)?;

        // Create interactive JavaScript
        let js_content = include_str!("../templates/report.js");
        fs::write(assets_dir.join("report.js"), js_content)?;

        Ok(())
    }
}

/// Generate actionable insights from analysis data
pub struct InsightEngine;

impl InsightEngine {
    pub fn generate_insights(data: &ReportData) -> Vec<ActionableInsight> {
        let mut insights = Vec::new();

        // Complexity-based insights
        insights.extend(Self::analyze_complexity_patterns(data));

        // Dependency-based insights
        insights.extend(Self::analyze_dependency_patterns(data));

        // Technical debt insights
        insights.extend(Self::analyze_technical_debt(data));

        // Sort by priority
        insights.sort_by_key(|insight| match insight.priority {
            Priority::Critical => 0,
            Priority::High => 1,
            Priority::Medium => 2,
            Priority::Low => 3,
        });

        insights
    }

    fn analyze_complexity_patterns(data: &ReportData) -> Vec<ActionableInsight> {
        let mut insights = Vec::new();

        // Find functions with excessive complexity
        for file in &data.file_analysis {
            for func in &file.functions {
                if func.complexity > 15 {
                    insights.push(ActionableInsight {
                        category: InsightCategory::Complexity,
                        title: format!("High complexity function: {}", func.name),
                        description: format!(
                            "Function '{}' in {} has complexity {}, exceeding recommended threshold of 10",
                            func.name, file.path, func.complexity
                        ),
                        priority: if func.complexity > 25 { Priority::Critical } else { Priority::High },
                        affected_files: vec![file.path.clone()],
                        recommendation: "Consider breaking this function into smaller, focused functions. Extract complex logic into separate methods or use the Strategy pattern for conditional complexity.".to_string(),
                        effort_estimate: if func.complexity > 25 { EffortEstimate::Large } else { EffortEstimate::Medium },
                    });
                }
            }
        }

        insights
    }

    fn analyze_dependency_patterns(data: &ReportData) -> Vec<ActionableInsight> {
        let mut insights = Vec::new();

        // Analyze circular dependencies
        for cycle in &data.dependency_graph.circular_dependencies {
            if cycle.len() > 1 {
                insights.push(ActionableInsight {
                    category: InsightCategory::Dependencies,
                    title: "Circular dependency detected".to_string(),
                    description: format!("Circular dependency found: {}", cycle.join(" -> ")),
                    priority: Priority::High,
                    affected_files: cycle.clone(),
                    recommendation: "Refactor to remove circular dependencies by extracting common interfaces, using dependency inversion, or restructuring module boundaries.".to_string(),
                    effort_estimate: EffortEstimate::Medium,
                });
            }
        }

        insights
    }

    fn analyze_technical_debt(data: &ReportData) -> Vec<ActionableInsight> {
        let mut insights = Vec::new();

        if data.summary_metrics.technical_debt_score > 7.0 {
            insights.push(ActionableInsight {
                category: InsightCategory::TechnicalDebt,
                title: "High technical debt detected".to_string(),
                description: format!(
                    "Technical debt score is {:.1}/10. Consider prioritizing refactoring efforts.",
                    data.summary_metrics.technical_debt_score
                ),
                priority: Priority::Medium,
                affected_files: data.file_analysis
                    .iter()
                    .filter(|f| f.complexity_score > 20)
                    .map(|f| f.path.clone())
                    .collect(),
                recommendation: "Focus on the highest complexity files first. Set up complexity gates in CI to prevent debt accumulation.".to_string(),
                effort_estimate: EffortEstimate::Large,
            });
        }

        insights
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_insight_generation() {
        let sample_data = create_sample_report_data();
        let insights = InsightEngine::generate_insights(&sample_data);
        assert!(!insights.is_empty());
    }

    fn create_sample_report_data() -> ReportData {
        ReportData {
            project_name: "test_project".to_string(),
            analysis_timestamp: "2026-01-23T01:23:41Z".to_string(),
            summary_metrics: SummaryMetrics {
                total_files: 10,
                total_functions: 50,
                average_complexity: 8.5,
                high_complexity_functions: 5,
                complexity_threshold: 10,
                lines_of_code: 5000,
                technical_debt_score: 6.2,
            },
            file_analysis: vec![],
            complexity_distribution: HashMap::new(),
            dependency_graph: DependencyGraph {
                nodes: vec![],
                edges: vec![],
                circular_dependencies: vec![],
            },
            insights: vec![],
        }
    }
}
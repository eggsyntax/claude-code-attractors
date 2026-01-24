use anyhow::{Context, Result};
use handlebars::Handlebars;
use serde_json::json;
use std::collections::HashMap;
use std::fs;
use std::path::Path;

use crate::core::types::{ProjectAnalysis, FileAnalysis, DependencyGraph, CodeIssue, IssueSeverity};
use crate::dependency_analyzer::{DependencyAnalysisResult, CircularDependency, ModuleCoupling};
use crate::ast_analyzer::FunctionAnalysis;

/// Advanced visualization and reporting system
pub struct VisualizationEngine {
    handlebars: Handlebars<'static>,
}

/// Configuration for visualization output
pub struct VisualizationConfig {
    pub include_dependency_graph: bool,
    pub include_complexity_heatmap: bool,
    pub include_issue_dashboard: bool,
    pub include_function_metrics: bool,
    pub interactive_features: bool,
    pub dark_theme: bool,
}

impl Default for VisualizationConfig {
    fn default() -> Self {
        Self {
            include_dependency_graph: true,
            include_complexity_heatmap: true,
            include_issue_dashboard: true,
            include_function_metrics: true,
            interactive_features: true,
            dark_theme: false,
        }
    }
}

impl VisualizationEngine {
    pub fn new() -> Result<Self> {
        let mut handlebars = Handlebars::new();

        // Register HTML report template
        handlebars.register_template_string("html_report", HTML_REPORT_TEMPLATE)
            .context("Failed to register HTML report template")?;

        // Register dashboard template
        handlebars.register_template_string("dashboard", DASHBOARD_TEMPLATE)
            .context("Failed to register dashboard template")?;

        Ok(Self { handlebars })
    }

    /// Generate a comprehensive HTML report with interactive visualizations
    pub fn generate_html_report(
        &self,
        project_analysis: &ProjectAnalysis,
        dependency_analysis: Option<&DependencyAnalysisResult>,
        functions: &HashMap<String, Vec<FunctionAnalysis>>,
        config: &VisualizationConfig,
        output_path: &Path,
    ) -> Result<()> {
        let template_data = self.prepare_template_data(
            project_analysis,
            dependency_analysis,
            functions,
            config,
        )?;

        let html_content = self.handlebars
            .render("html_report", &template_data)
            .context("Failed to render HTML report")?;

        fs::write(output_path, html_content)
            .with_context(|| format!("Failed to write HTML report to {}", output_path.display()))?;

        // Copy static assets
        self.copy_static_assets(output_path.parent().unwrap_or(Path::new(".")))?;

        println!("✨ Interactive HTML report generated: {}", output_path.display());
        Ok(())
    }

    /// Generate a real-time dashboard for continuous monitoring
    pub fn generate_dashboard(
        &self,
        project_analysis: &ProjectAnalysis,
        dependency_analysis: Option<&DependencyAnalysisResult>,
        config: &VisualizationConfig,
        output_path: &Path,
    ) -> Result<()> {
        let template_data = json!({
            "project": {
                "name": project_analysis.files.get(0)
                    .map(|f| f.file_path.parent()
                        .and_then(|p| p.file_name())
                        .and_then(|n| n.to_str())
                        .unwrap_or("Project"))
                    .unwrap_or("Project"),
                "summary": project_analysis.summary,
                "analysis_time": project_analysis.analysis_timestamp,
                "total_files": project_analysis.files.len(),
            },
            "real_time": true,
            "config": {
                "dark_theme": config.dark_theme,
                "refresh_interval": 5000, // 5 seconds
            },
            "websocket_port": 8080,
        });

        let dashboard_html = self.handlebars
            .render("dashboard", &template_data)
            .context("Failed to render dashboard")?;

        fs::write(output_path, dashboard_html)
            .with_context(|| format!("Failed to write dashboard to {}", output_path.display()))?;

        println!("📊 Real-time dashboard generated: {}", output_path.display());
        Ok(())
    }

    /// Prepare comprehensive template data for visualization
    fn prepare_template_data(
        &self,
        project_analysis: &ProjectAnalysis,
        dependency_analysis: Option<&DependencyAnalysisResult>,
        functions: &HashMap<String, Vec<FunctionAnalysis>>,
        config: &VisualizationConfig,
    ) -> Result<serde_json::Value> {
        let mut data = json!({
            "project": {
                "summary": project_analysis.summary,
                "timestamp": project_analysis.analysis_timestamp,
                "total_analysis_time": project_analysis.total_analysis_time_ms,
            },
            "config": config,
        });

        // Add file analysis data
        let file_data: Vec<serde_json::Value> = project_analysis.files.iter()
            .map(|file| self.serialize_file_analysis(file, functions))
            .collect();
        data["files"] = json!(file_data);

        // Add complexity heatmap data
        if config.include_complexity_heatmap {
            data["complexity_heatmap"] = self.generate_complexity_heatmap_data(&project_analysis.files)?;
        }

        // Add issue dashboard data
        if config.include_issue_dashboard {
            data["issue_dashboard"] = self.generate_issue_dashboard_data(&project_analysis.files)?;
        }

        // Add dependency graph data
        if config.include_dependency_graph {
            if let Some(dep_analysis) = dependency_analysis {
                data["dependency_graph"] = self.generate_dependency_graph_data(dep_analysis)?;
            }
        }

        // Add function metrics
        if config.include_function_metrics {
            data["function_metrics"] = self.generate_function_metrics_data(functions)?;
        }

        Ok(data)
    }

    /// Serialize file analysis for template rendering
    fn serialize_file_analysis(
        &self,
        file: &FileAnalysis,
        functions: &HashMap<String, Vec<FunctionAnalysis>>,
    ) -> serde_json::Value {
        let file_path_str = file.file_path.to_string_lossy();
        let file_functions = functions.get(file_path_str.as_ref()).cloned().unwrap_or_default();

        json!({
            "path": file.file_path,
            "language": file.language,
            "metrics": file.metrics,
            "issues": file.issues,
            "analysis_time": file.analysis_time_ms,
            "functions": file_functions,
            "complexity_score": self.calculate_complexity_score(&file.metrics),
            "maintainability_rating": self.get_maintainability_rating(file.metrics.maintainability_index),
        })
    }

    /// Generate data for complexity heatmap visualization
    fn generate_complexity_heatmap_data(&self, files: &[FileAnalysis]) -> Result<serde_json::Value> {
        let heatmap_data: Vec<serde_json::Value> = files.iter()
            .map(|file| {
                json!({
                    "file": file.file_path.file_name().unwrap_or_default(),
                    "complexity": file.metrics.cyclomatic_complexity,
                    "lines": file.metrics.lines_of_code,
                    "maintainability": file.metrics.maintainability_index,
                    "functions": file.metrics.function_count,
                    "score": self.calculate_complexity_score(&file.metrics),
                })
            })
            .collect();

        Ok(json!({
            "data": heatmap_data,
            "color_scale": [
                {"value": 0, "color": "#22c55e"},    // Green - low complexity
                {"value": 25, "color": "#eab308"},   // Yellow - medium complexity
                {"value": 50, "color": "#f97316"},   // Orange - high complexity
                {"value": 75, "color": "#ef4444"},   // Red - very high complexity
                {"value": 100, "color": "#991b1b"},  // Dark red - critical
            ]
        }))
    }

    /// Generate data for issue dashboard
    fn generate_issue_dashboard_data(&self, files: &[FileAnalysis]) -> Result<serde_json::Value> {
        let mut issue_counts = HashMap::new();
        let mut severity_counts = HashMap::new();
        let mut category_counts = HashMap::new();
        let mut recent_issues = Vec::new();

        for file in files {
            for issue in &file.issues {
                // Count by file
                *issue_counts.entry(file.file_path.to_string_lossy().to_string()).or_insert(0) += 1;

                // Count by severity
                let severity_key = format!("{:?}", issue.severity);
                *severity_counts.entry(severity_key).or_insert(0) += 1;

                // Count by category
                let category_key = format!("{:?}", issue.category);
                *category_counts.entry(category_key).or_insert(0) += 1;

                // Collect recent critical issues
                if matches!(issue.severity, IssueSeverity::Critical | IssueSeverity::Error) {
                    recent_issues.push(json!({
                        "file": file.file_path,
                        "line": issue.line,
                        "severity": issue.severity,
                        "category": issue.category,
                        "message": issue.message,
                        "suggestion": issue.suggestion,
                    }));
                }
            }
        }

        // Sort recent issues by severity
        recent_issues.sort_by(|a, b| {
            let severity_order = |s: &str| match s {
                "Critical" => 0,
                "Error" => 1,
                "Warning" => 2,
                "Info" => 3,
                _ => 4,
            };

            let a_severity = a.get("severity").and_then(|s| s.as_str()).unwrap_or("");
            let b_severity = b.get("severity").and_then(|s| s.as_str()).unwrap_or("");

            severity_order(a_severity).cmp(&severity_order(b_severity))
        });

        Ok(json!({
            "issue_counts": issue_counts,
            "severity_distribution": severity_counts,
            "category_distribution": category_counts,
            "recent_issues": recent_issues.into_iter().take(10).collect::<Vec<_>>(),
            "total_issues": files.iter().map(|f| f.issues.len()).sum::<usize>(),
        }))
    }

    /// Generate data for dependency graph visualization
    fn generate_dependency_graph_data(&self, dep_analysis: &DependencyAnalysisResult) -> Result<serde_json::Value> {
        let nodes: Vec<serde_json::Value> = dep_analysis.graph.nodes.iter()
            .map(|node| {
                let coupling = dep_analysis.module_coupling.iter()
                    .find(|c| c.module_name == node.id);

                json!({
                    "id": node.id,
                    "label": node.module_name,
                    "file_path": node.file_path,
                    "exports": node.exports,
                    "coupling": coupling.map(|c| json!({
                        "afferent": c.afferent_coupling,
                        "efferent": c.efferent_coupling,
                        "instability": c.instability,
                    })),
                    "depth": dep_analysis.dependency_depth.get(&node.id).unwrap_or(&0),
                })
            })
            .collect();

        let edges: Vec<serde_json::Value> = dep_analysis.graph.edges.iter()
            .map(|edge| {
                json!({
                    "from": edge.from,
                    "to": edge.to,
                    "type": edge.import_type,
                    "symbols": edge.imported_symbols,
                })
            })
            .collect();

        Ok(json!({
            "nodes": nodes,
            "edges": edges,
            "circular_dependencies": dep_analysis.circular_dependencies.iter()
                .map(|cd| json!({
                    "cycle": cd.cycle,
                    "severity": cd.severity,
                }))
                .collect::<Vec<_>>(),
            "unused_exports": dep_analysis.unused_exports,
            "external_dependencies": dep_analysis.external_dependencies,
        }))
    }

    /// Generate function metrics data for detailed analysis
    fn generate_function_metrics_data(&self, functions: &HashMap<String, Vec<FunctionAnalysis>>) -> Result<serde_json::Value> {
        let mut all_functions = Vec::new();
        let mut complexity_distribution = HashMap::new();

        for (file_path, file_functions) in functions {
            for func in file_functions {
                all_functions.push(json!({
                    "file": file_path,
                    "name": func.name,
                    "start_line": func.start_line,
                    "end_line": func.end_line,
                    "lines_of_code": func.lines_of_code,
                    "cyclomatic_complexity": func.cyclomatic_complexity,
                    "nesting_depth": func.nesting_depth,
                    "parameter_count": func.parameter_count,
                    "is_async": func.is_async,
                    "is_recursive": func.is_recursive,
                    "calls": func.calls,
                }));

                // Build complexity distribution
                let complexity_range = match func.cyclomatic_complexity {
                    1..=5 => "Low (1-5)",
                    6..=10 => "Medium (6-10)",
                    11..=20 => "High (11-20)",
                    _ => "Very High (>20)",
                };
                *complexity_distribution.entry(complexity_range).or_insert(0) += 1;
            }
        }

        // Sort functions by complexity (highest first)
        all_functions.sort_by(|a, b| {
            let a_complexity = a.get("cyclomatic_complexity").and_then(|v| v.as_u64()).unwrap_or(0);
            let b_complexity = b.get("cyclomatic_complexity").and_then(|v| v.as_u64()).unwrap_or(0);
            b_complexity.cmp(&a_complexity)
        });

        Ok(json!({
            "functions": all_functions,
            "complexity_distribution": complexity_distribution,
            "total_functions": all_functions.len(),
            "most_complex": all_functions.first(),
            "average_complexity": if all_functions.is_empty() { 0.0 } else {
                all_functions.iter()
                    .map(|f| f.get("cyclomatic_complexity").and_then(|v| v.as_f64()).unwrap_or(0.0))
                    .sum::<f64>() / all_functions.len() as f64
            },
        }))
    }

    /// Copy static assets (CSS, JS) for the HTML report
    fn copy_static_assets(&self, output_dir: &Path) -> Result<()> {
        let assets_dir = output_dir.join("assets");
        fs::create_dir_all(&assets_dir)?;

        // Copy CSS
        fs::write(assets_dir.join("styles.css"), CSS_STYLES)?;

        // Copy JavaScript
        fs::write(assets_dir.join("visualizations.js"), VISUALIZATION_JS)?;

        Ok(())
    }

    // Helper methods
    fn calculate_complexity_score(&self, metrics: &crate::core::types::CodeMetrics) -> f64 {
        let complexity_factor = (metrics.cyclomatic_complexity as f64 / 10.0).min(1.0);
        let nesting_factor = (metrics.max_nesting_depth as f64 / 5.0).min(1.0);
        let maintainability_factor = 1.0 - (metrics.maintainability_index / 100.0);

        ((complexity_factor + nesting_factor + maintainability_factor) / 3.0 * 100.0).round()
    }

    fn get_maintainability_rating(&self, index: f64) -> &'static str {
        match index {
            x if x >= 85.0 => "Excellent",
            x if x >= 70.0 => "Good",
            x if x >= 50.0 => "Fair",
            x if x >= 25.0 => "Poor",
            _ => "Critical",
        }
    }
}

// Template constants
const HTML_REPORT_TEMPLATE: &str = r#"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodeMetrics Report</title>
    <link rel="stylesheet" href="assets/styles.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
</head>
<body{{#if config.dark_theme}} class="dark-theme"{{/if}}>
    <header>
        <h1>📊 CodeMetrics Analysis Report</h1>
        <div class="metadata">
            <span>Generated: {{project.timestamp}}</span>
            <span>Analysis Time: {{project.total_analysis_time}}ms</span>
        </div>
    </header>

    <nav>
        <ul>
            <li><a href="#overview">Overview</a></li>
            {{#if config.include_complexity_heatmap}}<li><a href="#complexity">Complexity</a></li>{{/if}}
            {{#if config.include_issue_dashboard}}<li><a href="#issues">Issues</a></li>{{/if}}
            {{#if config.include_dependency_graph}}<li><a href="#dependencies">Dependencies</a></li>{{/if}}
            {{#if config.include_function_metrics}}<li><a href="#functions">Functions</a></li>{{/if}}
        </ul>
    </nav>

    <main>
        <section id="overview">
            <h2>Project Overview</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>{{project.summary.total_files}}</h3>
                    <p>Total Files</p>
                </div>
                <div class="metric-card">
                    <h3>{{project.summary.total_lines_of_code}}</h3>
                    <p>Lines of Code</p>
                </div>
                <div class="metric-card">
                    <h3>{{project.summary.total_complexity}}</h3>
                    <p>Total Complexity</p>
                </div>
                <div class="metric-card">
                    <h3>{{project.summary.average_maintainability}}%</h3>
                    <p>Avg Maintainability</p>
                </div>
            </div>

            <div class="language-breakdown">
                <h3>Language Distribution</h3>
                <canvas id="languageChart"></canvas>
            </div>
        </section>

        {{#if config.include_complexity_heatmap}}
        <section id="complexity">
            <h2>Complexity Heatmap</h2>
            <div id="complexityHeatmap"></div>
        </section>
        {{/if}}

        {{#if config.include_issue_dashboard}}
        <section id="issues">
            <h2>Issue Dashboard</h2>
            <div class="issue-summary">
                <div class="severity-chart">
                    <canvas id="severityChart"></canvas>
                </div>
                <div class="recent-issues">
                    <h3>Critical Issues</h3>
                    <ul>
                    {{#each issue_dashboard.recent_issues}}
                        <li class="issue-item severity-{{severity}}">
                            <strong>{{file}}</strong>:{{line}} - {{message}}
                        </li>
                    {{/each}}
                    </ul>
                </div>
            </div>
        </section>
        {{/if}}

        {{#if config.include_dependency_graph}}
        <section id="dependencies">
            <h2>Dependency Graph</h2>
            <div id="dependencyGraph"></div>

            {{#if dependency_graph.circular_dependencies}}
            <div class="circular-deps">
                <h3>Circular Dependencies</h3>
                {{#each dependency_graph.circular_dependencies}}
                <div class="cycle-item severity-{{severity}}">
                    {{#each cycle}}{{this}}{{#unless @last}} → {{/unless}}{{/each}}
                </div>
                {{/each}}
            </div>
            {{/if}}
        </section>
        {{/if}}

        {{#if config.include_function_metrics}}
        <section id="functions">
            <h2>Function Analysis</h2>
            <div class="function-metrics">
                <div class="metric-summary">
                    <p>Total Functions: {{function_metrics.total_functions}}</p>
                    <p>Average Complexity: {{function_metrics.average_complexity}}</p>
                </div>

                <div class="complexity-distribution">
                    <canvas id="complexityDistChart"></canvas>
                </div>

                <div class="function-table">
                    <h3>Most Complex Functions</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Function</th>
                                <th>File</th>
                                <th>Complexity</th>
                                <th>Lines</th>
                                <th>Parameters</th>
                            </tr>
                        </thead>
                        <tbody>
                        {{#each function_metrics.functions}}
                        {{#if @index}}<tr{{#if (gt cyclomatic_complexity 15)}} class="high-complexity"{{/if}}>{{/if}}
                            <td>{{name}}</td>
                            <td>{{file}}</td>
                            <td>{{cyclomatic_complexity}}</td>
                            <td>{{lines_of_code}}</td>
                            <td>{{parameter_count}}</td>
                        {{#if @index}}</tr>{{/if}}
                        {{/each}}
                        </tbody>
                    </table>
                </div>
            </div>
        </section>
        {{/if}}
    </main>

    <script src="assets/visualizations.js"></script>
    <script>
        // Initialize visualizations with data
        const projectData = {{{json project}}};
        const complexityData = {{{json complexity_heatmap}}};
        const issueData = {{{json issue_dashboard}}};
        const dependencyData = {{{json dependency_graph}}};
        const functionData = {{{json function_metrics}}};

        initializeVisualizations({
            project: projectData,
            complexity: complexityData,
            issues: issueData,
            dependencies: dependencyData,
            functions: functionData
        });
    </script>
</body>
</html>
"#;

const DASHBOARD_TEMPLATE: &str = r#"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodeMetrics Dashboard</title>
    <link rel="stylesheet" href="assets/styles.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body{{#if config.dark_theme}} class="dark-theme"{{/if}}>
    <header>
        <h1>📊 CodeMetrics Live Dashboard</h1>
        <div class="status-indicator">
            <span id="connectionStatus">●</span>
            <span>Last Update: <span id="lastUpdate">{{project.analysis_time}}</span></span>
        </div>
    </header>

    <div class="dashboard-grid">
        <div class="card">
            <h2>Project Overview</h2>
            <div id="overviewMetrics"></div>
        </div>

        <div class="card">
            <h2>Complexity Trend</h2>
            <canvas id="complexityTrend"></canvas>
        </div>

        <div class="card">
            <h2>Issue Alerts</h2>
            <div id="issueAlerts"></div>
        </div>

        <div class="card">
            <h2>Performance</h2>
            <canvas id="performanceChart"></canvas>
        </div>
    </div>

    <script>
        // WebSocket connection for real-time updates
        const ws = new WebSocket('ws://localhost:{{websocket_port}}');

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updateDashboard(data);
        };

        ws.onopen = function() {
            document.getElementById('connectionStatus').style.color = 'green';
        };

        ws.onclose = function() {
            document.getElementById('connectionStatus').style.color = 'red';
        };

        function updateDashboard(data) {
            document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
            // Update dashboard components
        }

        // Auto-refresh every {{config.refresh_interval}}ms
        setInterval(() => {
            if (ws.readyState !== WebSocket.OPEN) {
                location.reload();
            }
        }, {{config.refresh_interval}});
    </script>
</body>
</html>
"#;

const CSS_STYLES: &str = r#"
/* CSS styles for the HTML report */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8fafc;
}

.dark-theme {
    background-color: #1a1a1a;
    color: #e5e7eb;
}

header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem 0;
    text-align: center;
}

header h1 {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}

.metadata span {
    margin: 0 1rem;
    opacity: 0.9;
}

nav {
    background: white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    position: sticky;
    top: 0;
    z-index: 100;
}

nav ul {
    display: flex;
    justify-content: center;
    list-style: none;
    padding: 1rem 0;
}

nav li {
    margin: 0 1rem;
}

nav a {
    text-decoration: none;
    color: #4a5568;
    font-weight: 500;
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
    transition: all 0.2s;
}

nav a:hover {
    background-color: #edf2f7;
    color: #2d3748;
}

main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

section {
    margin-bottom: 3rem;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.metric-card {
    background: white;
    padding: 1.5rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    text-align: center;
}

.metric-card h3 {
    font-size: 2rem;
    font-weight: bold;
    color: #667eea;
    margin-bottom: 0.5rem;
}

.issue-item {
    padding: 0.75rem;
    margin: 0.5rem 0;
    border-left: 4px solid;
    background: #f7fafc;
    border-radius: 0 0.25rem 0.25rem 0;
}

.severity-Critical { border-left-color: #e53e3e; }
.severity-Error { border-left-color: #fd1d1d; }
.severity-Warning { border-left-color: #dd6b20; }
.severity-Info { border-left-color: #3182ce; }

.function-table table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 1rem;
}

.function-table th,
.function-table td {
    padding: 0.75rem;
    text-align: left;
    border-bottom: 1px solid #e2e8f0;
}

.function-table th {
    background-color: #f7fafc;
    font-weight: 600;
}

.high-complexity {
    background-color: #fed7d7;
}

#dependencyGraph,
#complexityHeatmap {
    min-height: 400px;
    border: 1px solid #e2e8f0;
    border-radius: 0.5rem;
    background: white;
}

/* Dashboard specific styles */
.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    padding: 2rem;
}

.card {
    background: white;
    padding: 1.5rem;
    border-radius: 0.5rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.status-indicator {
    display: flex;
    align-items: center;
    gap: 1rem;
}

#connectionStatus {
    font-size: 1.2rem;
}

/* Responsive design */
@media (max-width: 768px) {
    .metrics-grid {
        grid-template-columns: 1fr;
    }

    nav ul {
        flex-direction: column;
        align-items: center;
    }

    header h1 {
        font-size: 2rem;
    }
}
"#;

const VISUALIZATION_JS: &str = r#"
// JavaScript for interactive visualizations
function initializeVisualizations(data) {
    if (data.project) {
        initializeLanguageChart(data.project.summary);
    }

    if (data.issues) {
        initializeSeverityChart(data.issues);
    }

    if (data.functions) {
        initializeComplexityDistribution(data.functions);
    }

    if (data.complexity) {
        initializeComplexityHeatmap(data.complexity);
    }

    if (data.dependencies) {
        initializeDependencyGraph(data.dependencies);
    }
}

function initializeLanguageChart(summary) {
    const ctx = document.getElementById('languageChart');
    if (!ctx) return;

    const languages = Object.keys(summary.languages);
    const counts = Object.values(summary.languages);

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: languages,
            datasets: [{
                data: counts,
                backgroundColor: [
                    '#667eea', '#764ba2', '#f093fb', '#f5576c',
                    '#4facfe', '#00f2fe', '#43e97b', '#38f9d7'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function initializeSeverityChart(issues) {
    const ctx = document.getElementById('severityChart');
    if (!ctx) return;

    const severities = Object.keys(issues.severity_distribution);
    const counts = Object.values(issues.severity_distribution);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: severities,
            datasets: [{
                label: 'Issues by Severity',
                data: counts,
                backgroundColor: [
                    '#e53e3e', '#fd1d1d', '#dd6b20', '#3182ce'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function initializeComplexityDistribution(functions) {
    const ctx = document.getElementById('complexityDistChart');
    if (!ctx) return;

    const distribution = functions.complexity_distribution;
    const labels = Object.keys(distribution);
    const data = Object.values(distribution);

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#22c55e', '#eab308', '#f97316', '#ef4444'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function initializeComplexityHeatmap(complexity) {
    const container = document.getElementById('complexityHeatmap');
    if (!container || !complexity) return;

    // Create a simple heatmap using D3.js
    const margin = {top: 20, right: 20, bottom: 30, left: 40};
    const width = container.clientWidth - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const svg = d3.select(container)
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom);

    const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    // Implement heatmap visualization logic here
    // This would create an interactive complexity heatmap
}

function initializeDependencyGraph(dependencies) {
    const container = document.getElementById('dependencyGraph');
    if (!container || !dependencies) return;

    // Create an interactive dependency graph using D3.js
    const width = container.clientWidth;
    const height = 400;

    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    const simulation = d3.forceSimulation(dependencies.nodes)
        .force('link', d3.forceLink(dependencies.edges).id(d => d.id))
        .force('charge', d3.forceManyBody().strength(-100))
        .force('center', d3.forceCenter(width / 2, height / 2));

    // Add links
    const link = svg.append('g')
        .selectAll('line')
        .data(dependencies.edges)
        .enter().append('line')
        .attr('stroke', '#999')
        .attr('stroke-opacity', 0.6);

    // Add nodes
    const node = svg.append('g')
        .selectAll('circle')
        .data(dependencies.nodes)
        .enter().append('circle')
        .attr('r', 5)
        .attr('fill', '#667eea')
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));

    // Add labels
    const label = svg.append('g')
        .selectAll('text')
        .data(dependencies.nodes)
        .enter().append('text')
        .text(d => d.label)
        .attr('font-size', 10)
        .attr('dx', 8)
        .attr('dy', 4);

    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node
            .attr('cx', d => d.x)
            .attr('cy', d => d.y);

        label
            .attr('x', d => d.x)
            .attr('y', d => d.y);
    });

    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
}

// Utility functions for data processing and formatting
function formatFileSize(bytes) {
    const sizes = ['B', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 B';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}

function formatDuration(ms) {
    if (ms < 1000) return ms + 'ms';
    if (ms < 60000) return Math.round(ms / 1000) + 's';
    return Math.round(ms / 60000) + 'm';
}
"#;
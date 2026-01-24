use std::collections::HashMap;
use std::path::Path;

use crate::report_generator::*;

/// Example usage demonstrating how to use the code analysis report generator
///
/// This shows how to:
/// 1. Collect analysis data from your codebase
/// 2. Generate actionable insights
/// 3. Create interactive HTML reports
/// 4. Customize report output and styling

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Example: Generate a comprehensive report for a sample project
    let report_data = create_sample_analysis_data();
    let generator = ReportGenerator::new();

    // Generate the interactive HTML report
    let output_path = Path::new("target/analysis_report.html");
    generator.generate_report(&report_data, output_path)?;

    println!("✅ Report generated successfully!");
    println!("📊 Open {} in your browser to view the interactive analysis", output_path.display());

    // Example: Generate insights for specific scenarios
    demonstrate_insight_scenarios()?;

    Ok(())
}

/// Create sample analysis data that demonstrates the full range of report capabilities
fn create_sample_analysis_data() -> ReportData {
    ReportData {
        project_name: "E-Commerce Platform".to_string(),
        analysis_timestamp: chrono::Utc::now().to_rfc3339(),
        summary_metrics: SummaryMetrics {
            total_files: 125,
            total_functions: 1247,
            average_complexity: 8.3,
            high_complexity_functions: 23,
            complexity_threshold: 10,
            lines_of_code: 45231,
            technical_debt_score: 6.7,
        },
        file_analysis: create_sample_file_analysis(),
        complexity_distribution: create_complexity_distribution(),
        dependency_graph: create_sample_dependency_graph(),
        insights: InsightEngine::generate_insights(&create_baseline_data()),
    }
}

fn create_sample_file_analysis() -> Vec<FileAnalysis> {
    vec![
        FileAnalysis {
            path: "src/services/payment_processor.rs".to_string(),
            language: "Rust".to_string(),
            complexity_score: 47,
            function_count: 12,
            lines_of_code: 892,
            functions: vec![
                FunctionMetrics {
                    name: "process_payment".to_string(),
                    line_start: 45,
                    line_end: 156,
                    complexity: 23,
                    parameters: 6,
                    lines_of_code: 111,
                    cognitive_complexity: 18,
                },
                FunctionMetrics {
                    name: "validate_payment_method".to_string(),
                    line_start: 158,
                    line_end: 234,
                    complexity: 15,
                    parameters: 3,
                    lines_of_code: 76,
                    cognitive_complexity: 12,
                },
                FunctionMetrics {
                    name: "handle_payment_webhook".to_string(),
                    line_start: 300,
                    line_end: 445,
                    complexity: 19,
                    parameters: 4,
                    lines_of_code: 145,
                    cognitive_complexity: 16,
                },
            ],
            imports: vec![
                "serde_json".to_string(),
                "reqwest".to_string(),
                "tokio".to_string(),
                "uuid".to_string(),
            ],
            complexity_hotspots: vec![
                ComplexityHotspot {
                    function_name: "process_payment".to_string(),
                    complexity: 23,
                    line_number: 45,
                    severity: HotspotSeverity::Critical,
                    recommendation: "Break down into smaller functions: extract validation, fee calculation, and provider communication".to_string(),
                },
            ],
        },
        FileAnalysis {
            path: "src/models/user.rs".to_string(),
            language: "Rust".to_string(),
            complexity_score: 12,
            function_count: 8,
            lines_of_code: 324,
            functions: vec![
                FunctionMetrics {
                    name: "authenticate".to_string(),
                    line_start: 67,
                    line_end: 134,
                    complexity: 8,
                    parameters: 3,
                    lines_of_code: 67,
                    cognitive_complexity: 6,
                },
                FunctionMetrics {
                    name: "update_profile".to_string(),
                    line_start: 156,
                    line_end: 198,
                    complexity: 4,
                    parameters: 2,
                    lines_of_code: 42,
                    cognitive_complexity: 3,
                },
            ],
            imports: vec![
                "bcrypt".to_string(),
                "serde".to_string(),
                "uuid".to_string(),
            ],
            complexity_hotspots: vec![],
        },
        FileAnalysis {
            path: "frontend/src/components/CheckoutFlow.tsx".to_string(),
            language: "TypeScript".to_string(),
            complexity_score: 28,
            function_count: 15,
            lines_of_code: 567,
            functions: vec![
                FunctionMetrics {
                    name: "handlePaymentSubmission".to_string(),
                    line_start: 123,
                    line_end: 203,
                    complexity: 16,
                    parameters: 2,
                    lines_of_code: 80,
                    cognitive_complexity: 14,
                },
                FunctionMetrics {
                    name: "validateCheckoutForm".to_string(),
                    line_start: 45,
                    line_end: 89,
                    complexity: 12,
                    parameters: 1,
                    lines_of_code: 44,
                    cognitive_complexity: 9,
                },
            ],
            imports: vec![
                "react".to_string(),
                "axios".to_string(),
                "@stripe/stripe-js".to_string(),
            ],
            complexity_hotspots: vec![
                ComplexityHotspot {
                    function_name: "handlePaymentSubmission".to_string(),
                    complexity: 16,
                    line_number: 123,
                    severity: HotspotSeverity::High,
                    recommendation: "Separate validation, API calls, and error handling into dedicated functions".to_string(),
                },
            ],
        },
    ]
}

fn create_complexity_distribution() -> HashMap<String, u32> {
    let mut distribution = HashMap::new();
    distribution.insert("Low (1-5)".to_string(), 892);
    distribution.insert("Medium (6-10)".to_string(), 267);
    distribution.insert("High (11-20)".to_string(), 65);
    distribution.insert("Critical (21+)".to_string(), 23);
    distribution
}

fn create_sample_dependency_graph() -> DependencyGraph {
    DependencyGraph {
        nodes: vec![
            DependencyNode {
                id: "payment_processor".to_string(),
                label: "Payment Processor".to_string(),
                module_type: "Service".to_string(),
                complexity_score: 47,
                size: 892,
            },
            DependencyNode {
                id: "user_model".to_string(),
                label: "User Model".to_string(),
                module_type: "Model".to_string(),
                complexity_score: 12,
                size: 324,
            },
            DependencyNode {
                id: "checkout_flow".to_string(),
                label: "Checkout Flow".to_string(),
                module_type: "Component".to_string(),
                complexity_score: 28,
                size: 567,
            },
            DependencyNode {
                id: "order_service".to_string(),
                label: "Order Service".to_string(),
                module_type: "Service".to_string(),
                complexity_score: 34,
                size: 678,
            },
        ],
        edges: vec![
            DependencyEdge {
                from: "checkout_flow".to_string(),
                to: "payment_processor".to_string(),
                strength: 0.8,
                edge_type: "API Call".to_string(),
            },
            DependencyEdge {
                from: "payment_processor".to_string(),
                to: "user_model".to_string(),
                strength: 0.6,
                edge_type: "Data Access".to_string(),
            },
            DependencyEdge {
                from: "checkout_flow".to_string(),
                to: "order_service".to_string(),
                strength: 0.9,
                edge_type: "Service Call".to_string(),
            },
            DependencyEdge {
                from: "order_service".to_string(),
                to: "payment_processor".to_string(),
                strength: 0.7,
                edge_type: "Business Logic".to_string(),
            },
        ],
        circular_dependencies: vec![
            vec!["order_service".to_string(), "payment_processor".to_string()],
        ],
    }
}

fn create_baseline_data() -> ReportData {
    // This would be used by InsightEngine to generate insights
    create_sample_analysis_data()
}

/// Demonstrate different insight generation scenarios
fn demonstrate_insight_scenarios() -> Result<(), Box<dyn std::error::Error>> {
    println!("\n🔍 Demonstrating Insight Generation Scenarios:");

    // Scenario 1: High complexity function
    let high_complexity_data = create_high_complexity_scenario();
    let insights = InsightEngine::generate_insights(&high_complexity_data);
    println!("\n📊 High Complexity Scenario:");
    for insight in insights.iter().take(3) {
        println!("  • {} (Priority: {:?})", insight.title, insight.priority);
    }

    // Scenario 2: Circular dependencies
    let circular_deps_data = create_circular_dependency_scenario();
    let insights = InsightEngine::generate_insights(&circular_deps_data);
    println!("\n🔄 Circular Dependency Scenario:");
    for insight in insights.iter().filter(|i| matches!(i.category, InsightCategory::Dependencies)) {
        println!("  • {} - {}", insight.title, insight.description);
    }

    // Scenario 3: Technical debt accumulation
    let technical_debt_data = create_technical_debt_scenario();
    let insights = InsightEngine::generate_insights(&technical_debt_data);
    println!("\n⚠️  Technical Debt Scenario:");
    for insight in insights.iter().filter(|i| matches!(i.category, InsightCategory::TechnicalDebt)) {
        println!("  • {} (Effort: {:?})", insight.title, insight.effort_estimate);
    }

    Ok(())
}

fn create_high_complexity_scenario() -> ReportData {
    let mut data = create_sample_analysis_data();

    // Add a function with extremely high complexity
    data.file_analysis[0].functions.push(FunctionMetrics {
        name: "legacy_data_migration".to_string(),
        line_start: 500,
        line_end: 750,
        complexity: 42, // Very high complexity
        parameters: 8,
        lines_of_code: 250,
        cognitive_complexity: 35,
    });

    data.summary_metrics.average_complexity = 12.8;
    data.summary_metrics.high_complexity_functions = 35;

    data
}

fn create_circular_dependency_scenario() -> ReportData {
    let mut data = create_sample_analysis_data();

    // Add more complex circular dependencies
    data.dependency_graph.circular_dependencies = vec![
        vec![
            "user_service".to_string(),
            "order_service".to_string(),
            "payment_processor".to_string()
        ],
        vec![
            "auth_module".to_string(),
            "session_manager".to_string()
        ],
    ];

    data
}

fn create_technical_debt_scenario() -> ReportData {
    let mut data = create_sample_analysis_data();

    // Simulate high technical debt
    data.summary_metrics.technical_debt_score = 8.7;
    data.summary_metrics.average_complexity = 15.2;

    // Add more files with high complexity scores
    for i in 0..5 {
        data.file_analysis.push(FileAnalysis {
            path: format!("src/legacy/legacy_module_{}.rs", i),
            language: "Rust".to_string(),
            complexity_score: 35 + i as u32 * 5,
            function_count: 20,
            lines_of_code: 800 + i * 100,
            functions: vec![],
            imports: vec![],
            complexity_hotspots: vec![],
        });
    }

    data
}

/// Example of customizing report output for different team needs
pub fn generate_team_specific_reports() -> Result<(), Box<dyn std::error::Error>> {
    let base_data = create_sample_analysis_data();

    // Management summary report
    generate_executive_summary(&base_data)?;

    // Developer-focused report with detailed hotspots
    generate_developer_report(&base_data)?;

    // Architecture review report focusing on dependencies
    generate_architecture_report(&base_data)?;

    Ok(())
}

fn generate_executive_summary(data: &ReportData) -> Result<(), Box<dyn std::error::Error>> {
    println!("📋 Generating Executive Summary Report...");

    // Focus on high-level metrics and critical issues
    let critical_insights: Vec<_> = data.insights.iter()
        .filter(|i| matches!(i.priority, Priority::Critical | Priority::High))
        .collect();

    println!("  • {} critical/high priority issues identified", critical_insights.len());
    println!("  • Technical debt score: {}/10", data.summary_metrics.technical_debt_score);
    println!("  • {} functions exceed complexity threshold", data.summary_metrics.high_complexity_functions);

    Ok(())
}

fn generate_developer_report(data: &ReportData) -> Result<(), Box<dyn std::error::Error>> {
    println!("👨‍💻 Generating Developer Report...");

    // Focus on actionable items for developers
    for file in &data.file_analysis {
        if file.complexity_score > 30 {
            println!("  📁 {}: {} complexity, {} hotspots",
                file.path, file.complexity_score, file.complexity_hotspots.len());

            for hotspot in &file.complexity_hotspots {
                println!("    🔥 {}: {} (line {})",
                    hotspot.function_name, hotspot.complexity, hotspot.line_number);
            }
        }
    }

    Ok(())
}

fn generate_architecture_report(data: &ReportData) -> Result<(), Box<dyn std::error::Error>> {
    println!("🏗️  Generating Architecture Report...");

    // Focus on dependency analysis and structural issues
    println!("  • {} modules analyzed", data.dependency_graph.nodes.len());
    println!("  • {} dependencies mapped", data.dependency_graph.edges.len());

    if !data.dependency_graph.circular_dependencies.is_empty() {
        println!("  ⚠️  {} circular dependency cycles detected:",
            data.dependency_graph.circular_dependencies.len());

        for (i, cycle) in data.dependency_graph.circular_dependencies.iter().enumerate() {
            println!("    {}. {}", i + 1, cycle.join(" → "));
        }
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sample_data_generation() {
        let data = create_sample_analysis_data();
        assert!(!data.file_analysis.is_empty());
        assert!(data.summary_metrics.total_files > 0);
        assert!(!data.insights.is_empty());
    }

    #[test]
    fn test_insight_scenarios() {
        let high_complexity = create_high_complexity_scenario();
        let insights = InsightEngine::generate_insights(&high_complexity);

        let complexity_insights: Vec<_> = insights.iter()
            .filter(|i| matches!(i.category, InsightCategory::Complexity))
            .collect();

        assert!(!complexity_insights.is_empty());
    }

    #[test]
    fn test_circular_dependency_detection() {
        let circular_data = create_circular_dependency_scenario();
        let insights = InsightEngine::generate_insights(&circular_data);

        let dependency_insights: Vec<_> = insights.iter()
            .filter(|i| matches!(i.category, InsightCategory::Dependencies))
            .collect();

        assert!(!dependency_insights.is_empty());
    }
}
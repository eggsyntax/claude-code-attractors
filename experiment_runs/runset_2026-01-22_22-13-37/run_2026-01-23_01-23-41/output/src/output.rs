use crate::analyzer::{AnalysisResults, AnalysisIssue, IssueSeverity};
use crate::cli::OutputFormat;
use anyhow::{Context, Result};
use comfy_table::{modifiers::UTF8_ROUND_CORNERS, presets::UTF8_FULL, Table};
use serde_json;
use std::path::Path;
use std::fs::File;
use std::io::Write;

/// Handles formatting and outputting analysis results
pub struct OutputFormatter {
    format: OutputFormat,
}

impl OutputFormatter {
    pub fn new(format: OutputFormat) -> Self {
        Self { format }
    }

    /// Output analysis results in the configured format
    pub fn output(&self, results: AnalysisResults, output_path: Option<&Path>) -> Result<()> {
        let formatted_output = match self.format {
            OutputFormat::Terminal => self.format_terminal(&results)?,
            OutputFormat::Json => self.format_json(&results)?,
            OutputFormat::Html => self.format_html(&results)?,
            OutputFormat::Markdown => self.format_markdown(&results)?,
        };

        match output_path {
            Some(path) => {
                let mut file = File::create(path)
                    .with_context(|| format!("Failed to create output file: {}", path.display()))?;
                write!(file, "{}", formatted_output)?;
                println!("📄 Results written to: {}", path.display());
            }
            None => {
                print!("{}", formatted_output);
            }
        }

        Ok(())
    }

    /// Format results for terminal display with tables and colors
    fn format_terminal(&self, results: &AnalysisResults) -> Result<String> {
        let mut output = String::new();

        // Header
        output.push_str(&format!("🎯 CodeMetrics Analysis Results\n"));
        output.push_str(&format!("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"));

        // Summary statistics
        let mut summary_table = Table::new();
        summary_table
            .load_preset(UTF8_FULL)
            .apply_modifier(UTF8_ROUND_CORNERS)
            .set_header(vec!["Metric", "Value"]);

        summary_table.add_row(vec!["Files Analyzed", &results.files_analyzed.to_string()]);
        summary_table.add_row(vec!["Total Lines", &results.total_lines.to_string()]);
        summary_table.add_row(vec!["Total Complexity", &results.total_complexity.to_string()]);
        summary_table.add_row(vec![
            "Average Complexity",
            &format!("{:.1}", results.total_complexity as f32 / results.files_analyzed.max(1) as f32)
        ]);
        summary_table.add_row(vec![
            "Analysis Time",
            &format!("{}ms", results.analysis_duration_ms)
        ]);

        output.push_str("📊 Summary\n");
        output.push_str(&summary_table.to_string());
        output.push_str("\n\n");

        // Language breakdown
        if !results.language_breakdown.is_empty() {
            output.push_str("🌐 Language Breakdown\n");
            let mut lang_table = Table::new();
            lang_table
                .load_preset(UTF8_FULL)
                .apply_modifier(UTF8_ROUND_CORNERS)
                .set_header(vec!["Language", "Files", "Percentage"]);

            for (language, count) in &results.language_breakdown {
                let percentage = (*count as f32 / results.files_analyzed as f32) * 100.0;
                lang_table.add_row(vec![
                    language,
                    &count.to_string(),
                    &format!("{:.1}%", percentage)
                ]);
            }

            output.push_str(&lang_table.to_string());
            output.push_str("\n\n");
        }

        // Top complex files
        if !results.complexity_distribution.is_empty() {
            output.push_str("🔥 Most Complex Files (Top 10)\n");
            let mut complexity_table = Table::new();
            complexity_table
                .load_preset(UTF8_FULL)
                .apply_modifier(UTF8_ROUND_CORNERS)
                .set_header(vec!["File", "Complexity", "Risk Level"]);

            for (file_path, complexity) in results.complexity_distribution.iter().take(10) {
                let risk_level = match *complexity {
                    1..=5 => "🟢 Low",
                    6..=10 => "🟡 Medium",
                    11..=20 => "🟠 High",
                    _ => "🔴 Critical",
                };

                complexity_table.add_row(vec![
                    file_path.file_name()
                        .unwrap_or_else(|| file_path.as_os_str())
                        .to_string_lossy()
                        .to_string(),
                    complexity.to_string(),
                    risk_level.to_string(),
                ]);
            }

            output.push_str(&complexity_table.to_string());
            output.push_str("\n\n");
        }

        // Issues summary
        if !results.issues.is_empty() {
            output.push_str(&format!("⚠️  Issues Found ({})\n", results.issues.len()));

            let mut issues_table = Table::new();
            issues_table
                .load_preset(UTF8_FULL)
                .apply_modifier(UTF8_ROUND_CORNERS)
                .set_header(vec!["Severity", "File", "Line", "Message"]);

            for issue in &results.issues {
                let severity_icon = match issue.severity {
                    IssueSeverity::Info => "ℹ️ ",
                    IssueSeverity::Warning => "⚠️ ",
                    IssueSeverity::Error => "❌",
                };

                issues_table.add_row(vec![
                    severity_icon,
                    &issue.file_path.file_name()
                        .unwrap_or_else(|| issue.file_path.as_os_str())
                        .to_string_lossy(),
                    &issue.line.to_string(),
                    &issue.message,
                ]);
            }

            output.push_str(&issues_table.to_string());
            output.push_str("\n");
        }

        Ok(output)
    }

    /// Format results as JSON
    fn format_json(&self, results: &AnalysisResults) -> Result<String> {
        #[derive(serde::Serialize)]
        struct JsonOutput<'a> {
            files_analyzed: usize,
            total_lines: usize,
            total_complexity: u32,
            average_complexity: f32,
            language_breakdown: &'a std::collections::HashMap<String, usize>,
            complexity_distribution: Vec<JsonComplexityEntry>,
            issues: Vec<JsonIssue>,
            analysis_duration_ms: u64,
        }

        #[derive(serde::Serialize)]
        struct JsonComplexityEntry {
            file: String,
            complexity: u32,
        }

        #[derive(serde::Serialize)]
        struct JsonIssue {
            file: String,
            line: u32,
            severity: String,
            message: String,
            suggestion: Option<String>,
        }

        let json_output = JsonOutput {
            files_analyzed: results.files_analyzed,
            total_lines: results.total_lines,
            total_complexity: results.total_complexity,
            average_complexity: results.total_complexity as f32 / results.files_analyzed.max(1) as f32,
            language_breakdown: &results.language_breakdown,
            complexity_distribution: results.complexity_distribution.iter().map(|(path, complexity)| {
                JsonComplexityEntry {
                    file: path.to_string_lossy().to_string(),
                    complexity: *complexity,
                }
            }).collect(),
            issues: results.issues.iter().map(|issue| {
                JsonIssue {
                    file: issue.file_path.to_string_lossy().to_string(),
                    line: issue.line,
                    severity: match issue.severity {
                        IssueSeverity::Info => "info".to_string(),
                        IssueSeverity::Warning => "warning".to_string(),
                        IssueSeverity::Error => "error".to_string(),
                    },
                    message: issue.message.clone(),
                    suggestion: issue.suggestion.clone(),
                }
            }).collect(),
            analysis_duration_ms: results.analysis_duration_ms,
        };

        Ok(serde_json::to_string_pretty(&json_output)?)
    }

    /// Format results as HTML report
    fn format_html(&self, results: &AnalysisResults) -> Result<String> {
        let html_template = include_str!("templates/report.html");

        // For now, return a simple HTML structure
        // TODO: Implement proper templating with handlebars
        Ok(format!(
            r#"<!DOCTYPE html>
<html>
<head>
    <title>CodeMetrics Analysis Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 40px; }}
        .header {{ color: #2563eb; border-bottom: 2px solid #e5e7eb; padding-bottom: 16px; }}
        .metric-card {{ background: #f9fafb; border-radius: 8px; padding: 20px; margin: 16px 0; }}
        .complexity-high {{ color: #dc2626; }}
        .complexity-medium {{ color: #f59e0b; }}
        .complexity-low {{ color: #16a34a; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 CodeMetrics Analysis Report</h1>
        <p>Generated on {}</p>
    </div>

    <div class="metric-card">
        <h2>📊 Summary</h2>
        <ul>
            <li><strong>Files Analyzed:</strong> {}</li>
            <li><strong>Total Lines:</strong> {}</li>
            <li><strong>Total Complexity:</strong> {}</li>
            <li><strong>Average Complexity:</strong> {:.1}</li>
            <li><strong>Analysis Time:</strong> {}ms</li>
        </ul>
    </div>

    <div class="metric-card">
        <h2>🔥 Most Complex Files</h2>
        <ol>
            {}
        </ol>
    </div>
</body>
</html>"#,
            chrono::Utc::now().format("%Y-%m-%d %H:%M:%S UTC"),
            results.files_analyzed,
            results.total_lines,
            results.total_complexity,
            results.total_complexity as f32 / results.files_analyzed.max(1) as f32,
            results.analysis_duration_ms,
            results.complexity_distribution.iter().take(10).map(|(path, complexity)| {
                let class = match *complexity {
                    1..=5 => "complexity-low",
                    6..=10 => "complexity-medium",
                    _ => "complexity-high"
                };
                format!(r#"<li class="{}"><code>{}</code> - Complexity: {}</li>"#,
                    class, path.file_name().unwrap_or_else(|| path.as_os_str()).to_string_lossy(), complexity)
            }).collect::<Vec<_>>().join("\n")
        ))
    }

    /// Format results as Markdown
    fn format_markdown(&self, results: &AnalysisResults) -> Result<String> {
        let mut output = String::new();

        output.push_str("# 🎯 CodeMetrics Analysis Report\n\n");

        // Summary
        output.push_str("## 📊 Summary\n\n");
        output.push_str(&format!("- **Files Analyzed:** {}\n", results.files_analyzed));
        output.push_str(&format!("- **Total Lines:** {}\n", results.total_lines));
        output.push_str(&format!("- **Total Complexity:** {}\n", results.total_complexity));
        output.push_str(&format!("- **Average Complexity:** {:.1}\n",
            results.total_complexity as f32 / results.files_analyzed.max(1) as f32));
        output.push_str(&format!("- **Analysis Time:** {}ms\n\n", results.analysis_duration_ms));

        // Language breakdown
        if !results.language_breakdown.is_empty() {
            output.push_str("## 🌐 Language Breakdown\n\n");
            output.push_str("| Language | Files | Percentage |\n");
            output.push_str("|----------|-------|------------|\n");

            for (language, count) in &results.language_breakdown {
                let percentage = (*count as f32 / results.files_analyzed as f32) * 100.0;
                output.push_str(&format!("| {} | {} | {:.1}% |\n", language, count, percentage));
            }
            output.push_str("\n");
        }

        // Complex files
        if !results.complexity_distribution.is_empty() {
            output.push_str("## 🔥 Most Complex Files\n\n");
            output.push_str("| Rank | File | Complexity | Risk Level |\n");
            output.push_str("|------|------|------------|------------|\n");

            for (i, (file_path, complexity)) in results.complexity_distribution.iter().take(10).enumerate() {
                let risk_emoji = match *complexity {
                    1..=5 => "🟢",
                    6..=10 => "🟡",
                    11..=20 => "🟠",
                    _ => "🔴",
                };

                output.push_str(&format!("| {} | `{}` | {} | {} |\n",
                    i + 1,
                    file_path.file_name().unwrap_or_else(|| file_path.as_os_str()).to_string_lossy(),
                    complexity,
                    risk_emoji
                ));
            }
        }

        Ok(output)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::analyzer::{AnalysisResults, AnalysisIssue, IssueSeverity};
    use std::collections::HashMap;
    use std::path::PathBuf;

    fn create_test_results() -> AnalysisResults {
        AnalysisResults {
            files_analyzed: 5,
            total_lines: 1000,
            total_complexity: 25,
            language_breakdown: {
                let mut map = HashMap::new();
                map.insert("Rust".to_string(), 3);
                map.insert("JavaScript".to_string(), 2);
                map
            },
            complexity_distribution: vec![
                (PathBuf::from("complex_file.rs"), 15),
                (PathBuf::from("simple_file.rs"), 3),
            ],
            analysis_duration_ms: 150,
            issues: vec![
                AnalysisIssue {
                    file_path: PathBuf::from("complex_file.rs"),
                    line: 42,
                    severity: IssueSeverity::Warning,
                    message: "High complexity detected".to_string(),
                    suggestion: Some("Consider refactoring".to_string()),
                }
            ],
        }
    }

    #[test]
    fn test_json_formatting() {
        let formatter = OutputFormatter::new(OutputFormat::Json);
        let results = create_test_results();

        let json_output = formatter.format_json(&results).unwrap();

        // Verify JSON structure
        assert!(json_output.contains("files_analyzed"));
        assert!(json_output.contains("total_complexity"));
        assert!(json_output.contains("language_breakdown"));
    }

    #[test]
    fn test_markdown_formatting() {
        let formatter = OutputFormatter::new(OutputFormat::Markdown);
        let results = create_test_results();

        let markdown_output = formatter.format_markdown(&results).unwrap();

        // Verify Markdown structure
        assert!(markdown_output.contains("# 🎯 CodeMetrics Analysis Report"));
        assert!(markdown_output.contains("## 📊 Summary"));
        assert!(markdown_output.contains("| Language | Files | Percentage |"));
    }
}
//! Output formatters and report generators

use anyhow::{Context, Result};
use serde::Serialize;
use std::collections::HashMap;
use std::io::Write;
use std::path::Path;
use comfy_table::{Table, Cell, Color, Attribute, ContentArrangement};
use handlebars::Handlebars;

use crate::analyzers::{AnalysisResults, HighComplexityFunction, LanguageStats};

pub struct Reporter {
    format: String,
    handlebars: Handlebars<'static>,
}

impl Reporter {
    pub fn new(format: &str) -> Self {
        let mut handlebars = Handlebars::new();

        // Register HTML report template
        handlebars.register_template_string("html_report", include_str!("templates/report.html"))
            .expect("Failed to register HTML template");

        Self {
            format: format.to_string(),
            handlebars,
        }
    }

    pub fn output_results(&self, results: &AnalysisResults) -> Result<()> {
        match self.format.as_str() {
            "json" => self.output_json(results),
            "html" => self.output_html(results, None),
            _ => self.output_text(results),
        }
    }

    pub fn generate_report(&self, results: &AnalysisResults, output_path: Option<&Path>) -> Result<()> {
        match self.format.as_str() {
            "html" => self.output_html(results, output_path),
            "markdown" => self.output_markdown(results, output_path),
            "json" => self.output_json_file(results, output_path),
            _ => self.output_text(results),
        }
    }

    fn output_text(&self, results: &AnalysisResults) -> Result<()> {
        println!("\n📊 Code Analysis Results");
        println!("========================\n");

        // Overview section
        let mut overview_table = Table::new();
        overview_table
            .set_content_arrangement(ContentArrangement::Dynamic)
            .set_header(vec!["Metric", "Value"]);

        overview_table.add_row(vec![
            Cell::new("Files Analyzed").add_attribute(Attribute::Bold),
            Cell::new(&results.files_analyzed.to_string()).fg(Color::Green),
        ]);

        overview_table.add_row(vec![
            Cell::new("Total Functions").add_attribute(Attribute::Bold),
            Cell::new(&results.total_functions.to_string()).fg(Color::Blue),
        ]);

        overview_table.add_row(vec![
            Cell::new("Average Complexity").add_attribute(Attribute::Bold),
            Cell::new(&format!("{:.2}", results.average_complexity))
                .fg(if results.average_complexity > 10.0 { Color::Red } else { Color::Green }),
        ]);

        overview_table.add_row(vec![
            Cell::new("High Complexity Functions").add_attribute(Attribute::Bold),
            Cell::new(&results.high_complexity_functions.len().to_string())
                .fg(if results.high_complexity_functions.is_empty() { Color::Green } else { Color::Yellow }),
        ]);

        println!("{}", overview_table);

        // Language breakdown
        if !results.language_breakdown.is_empty() {
            println!("\n🔤 Language Breakdown");
            println!("====================\n");

            let mut lang_table = Table::new();
            lang_table
                .set_content_arrangement(ContentArrangement::Dynamic)
                .set_header(vec!["Language", "Files", "Functions", "Percentage"]);

            for (language, stats) in &results.language_breakdown {
                let percentage = (stats.files as f64 / results.files_analyzed as f64) * 100.0;
                lang_table.add_row(vec![
                    Cell::new(language).add_attribute(Attribute::Bold),
                    Cell::new(&stats.files.to_string()),
                    Cell::new(&stats.functions.to_string()),
                    Cell::new(&format!("{:.1}%", percentage)).fg(Color::Cyan),
                ]);
            }

            println!("{}", lang_table);
        }

        // High complexity functions
        if !results.high_complexity_functions.is_empty() {
            println!("\n⚠️  High Complexity Functions (≥10)");
            println!("===================================\n");

            let mut complexity_table = Table::new();
            complexity_table
                .set_content_arrangement(ContentArrangement::Dynamic)
                .set_header(vec!["Function", "Complexity", "Parameters", "Location"]);

            for func in results.high_complexity_functions.iter().take(10) { // Show top 10
                let complexity_color = match func.complexity {
                    x if x >= 20 => Color::Red,
                    x if x >= 15 => Color::Magenta,
                    _ => Color::Yellow,
                };

                complexity_table.add_row(vec![
                    Cell::new(&func.name).add_attribute(Attribute::Bold),
                    Cell::new(&func.complexity.to_string()).fg(complexity_color),
                    Cell::new(&func.parameters.to_string()),
                    Cell::new(&format!("{}:{}", func.file_path, func.line_start)).fg(Color::Cyan),
                ]);
            }

            println!("{}", complexity_table);

            if results.high_complexity_functions.len() > 10 {
                println!("... and {} more", results.high_complexity_functions.len() - 10);
            }
        }

        // Complexity distribution
        self.print_complexity_histogram(&results.complexity_distribution);

        if !results.errors.is_empty() {
            println!("\n❌ Parsing Errors");
            println!("=================\n");
            for error in &results.errors {
                println!("• {}", error);
            }
        }

        Ok(())
    }

    fn print_complexity_histogram(&self, distribution: &HashMap<u32, u32>) {
        println!("\n📈 Complexity Distribution");
        println!("==========================\n");

        let mut sorted_complexities: Vec<(&u32, &u32)> = distribution.iter().collect();
        sorted_complexities.sort_by_key(|(complexity, _)| *complexity);

        let max_count = *distribution.values().max().unwrap_or(&0);

        for (complexity, count) in sorted_complexities.iter().take(20) { // Show up to complexity 20
            let bar_length = if max_count > 0 {
                ((*count as f64 / max_count as f64) * 40.0) as usize
            } else {
                0
            };

            let bar = "█".repeat(bar_length);
            let color = match **complexity {
                x if x >= 15 => Color::Red,
                x if x >= 10 => Color::Yellow,
                x if x >= 5 => Color::Blue,
                _ => Color::Green,
            };

            println!("{:2}: {} ({})",
                complexity,
                Cell::new(&bar).fg(color),
                count
            );
        }
    }

    fn output_json(&self, results: &AnalysisResults) -> Result<()> {
        let json = serde_json::to_string_pretty(results)
            .context("Failed to serialize results to JSON")?;
        println!("{}", json);
        Ok(())
    }

    fn output_json_file(&self, results: &AnalysisResults, output_path: Option<&Path>) -> Result<()> {
        let json = serde_json::to_string_pretty(results)
            .context("Failed to serialize results to JSON")?;

        if let Some(path) = output_path {
            std::fs::write(path, json)
                .with_context(|| format!("Failed to write JSON report to {}", path.display()))?;
            println!("JSON report written to: {}", path.display());
        } else {
            println!("{}", json);
        }

        Ok(())
    }

    fn output_html(&self, results: &AnalysisResults, output_path: Option<&Path>) -> Result<()> {
        let report_data = ReportData::from(results);
        let html = self.handlebars.render("html_report", &report_data)
            .context("Failed to render HTML template")?;

        if let Some(path) = output_path {
            std::fs::write(path, html)
                .with_context(|| format!("Failed to write HTML report to {}", path.display()))?;
            println!("HTML report written to: {}", path.display());
        } else {
            println!("{}", html);
        }

        Ok(())
    }

    fn output_markdown(&self, results: &AnalysisResults, output_path: Option<&Path>) -> Result<()> {
        let mut markdown = String::new();

        markdown.push_str("# Code Analysis Report\n\n");

        markdown.push_str("## Overview\n\n");
        markdown.push_str(&format!("- **Files Analyzed:** {}\n", results.files_analyzed));
        markdown.push_str(&format!("- **Total Functions:** {}\n", results.total_functions));
        markdown.push_str(&format!("- **Average Complexity:** {:.2}\n", results.average_complexity));
        markdown.push_str(&format!("- **High Complexity Functions:** {}\n\n", results.high_complexity_functions.len()));

        if !results.language_breakdown.is_empty() {
            markdown.push_str("## Language Breakdown\n\n");
            markdown.push_str("| Language | Files | Functions | Percentage |\n");
            markdown.push_str("|----------|-------|-----------|------------|\n");

            for (language, stats) in &results.language_breakdown {
                let percentage = (stats.files as f64 / results.files_analyzed as f64) * 100.0;
                markdown.push_str(&format!(
                    "| {} | {} | {} | {:.1}% |\n",
                    language, stats.files, stats.functions, percentage
                ));
            }
            markdown.push_str("\n");
        }

        if !results.high_complexity_functions.is_empty() {
            markdown.push_str("## High Complexity Functions\n\n");
            markdown.push_str("| Function | Complexity | Parameters | Location |\n");
            markdown.push_str("|----------|------------|------------|----------|\n");

            for func in results.high_complexity_functions.iter().take(20) {
                markdown.push_str(&format!(
                    "| `{}` | {} | {} | `{}:{}` |\n",
                    func.name, func.complexity, func.parameters, func.file_path, func.line_start
                ));
            }
            markdown.push_str("\n");
        }

        if let Some(path) = output_path {
            std::fs::write(path, markdown)
                .with_context(|| format!("Failed to write markdown report to {}", path.display()))?;
            println!("Markdown report written to: {}", path.display());
        } else {
            println!("{}", markdown);
        }

        Ok(())
    }
}

// Data structure for template rendering
#[derive(Serialize)]
struct ReportData {
    files_analyzed: usize,
    total_functions: usize,
    average_complexity: f64,
    high_complexity_count: usize,
    languages: Vec<LanguageData>,
    high_complexity_functions: Vec<HighComplexityFunction>,
    complexity_distribution: Vec<ComplexityPoint>,
}

#[derive(Serialize)]
struct LanguageData {
    name: String,
    files: usize,
    functions: usize,
    percentage: f64,
}

#[derive(Serialize)]
struct ComplexityPoint {
    complexity: u32,
    count: u32,
}

impl From<&AnalysisResults> for ReportData {
    fn from(results: &AnalysisResults) -> Self {
        let languages: Vec<LanguageData> = results.language_breakdown
            .iter()
            .map(|(name, stats)| {
                let percentage = (stats.files as f64 / results.files_analyzed as f64) * 100.0;
                LanguageData {
                    name: name.clone(),
                    files: stats.files,
                    functions: stats.functions,
                    percentage,
                }
            })
            .collect();

        let complexity_distribution: Vec<ComplexityPoint> = results.complexity_distribution
            .iter()
            .map(|(&complexity, &count)| ComplexityPoint { complexity, count })
            .collect();

        ReportData {
            files_analyzed: results.files_analyzed,
            total_functions: results.total_functions,
            average_complexity: results.average_complexity,
            high_complexity_count: results.high_complexity_functions.len(),
            languages,
            high_complexity_functions: results.high_complexity_functions.clone(),
            complexity_distribution,
        }
    }
}
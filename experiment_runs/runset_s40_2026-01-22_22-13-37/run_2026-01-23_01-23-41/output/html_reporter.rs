use std::collections::HashMap;
use std::fs;
use std::path::Path;
use serde_json::json;
use crate::analysis::{AnalysisResult, FileAnalysis, FunctionInfo};

pub struct HtmlReporter {
    template: String,
}

impl HtmlReporter {
    pub fn new() -> Result<Self, Box<dyn std::error::Error>> {
        let template = include_str!("templates/report.html");
        Ok(HtmlReporter {
            template: template.to_string(),
        })
    }

    pub fn generate_report(
        &self,
        results: &[AnalysisResult],
        output_path: &Path,
    ) -> Result<(), Box<dyn std::error::Error>> {
        let report_data = self.prepare_report_data(results);
        let html_content = self.render_template(&report_data)?;

        fs::write(output_path, html_content)?;
        println!("📊 Interactive HTML report generated: {}", output_path.display());

        Ok(())
    }

    fn prepare_report_data(&self, results: &[AnalysisResult]) -> serde_json::Value {
        let mut total_files = 0;
        let mut total_functions = 0;
        let mut total_lines = 0;
        let mut complexity_distribution = HashMap::new();
        let mut language_stats = HashMap::new();
        let mut hotspots = Vec::new();

        for result in results {
            total_files += result.files.len();

            for file_analysis in &result.files {
                total_functions += file_analysis.functions.len();
                total_lines += file_analysis.line_count;

                // Track language statistics
                let lang_stats = language_stats.entry(&result.language).or_insert_with(|| {
                    json!({
                        "files": 0,
                        "functions": 0,
                        "lines": 0,
                        "avg_complexity": 0.0
                    })
                });

                lang_stats["files"] = lang_stats["files"].as_u64().unwrap() + 1;
                lang_stats["functions"] = lang_stats["functions"].as_u64().unwrap() + file_analysis.functions.len() as u64;
                lang_stats["lines"] = lang_stats["lines"].as_u64().unwrap() + file_analysis.line_count as u64;

                // Identify complexity hotspots
                for func in &file_analysis.functions {
                    if func.complexity > 10 {
                        hotspots.push(json!({
                            "file": file_analysis.file_path,
                            "function": func.name,
                            "complexity": func.complexity,
                            "line": func.line_number,
                            "language": result.language
                        }));
                    }

                    // Build complexity distribution
                    let complexity_bucket = match func.complexity {
                        1..=5 => "simple",
                        6..=10 => "moderate",
                        11..=20 => "complex",
                        _ => "very_complex"
                    };
                    *complexity_distribution.entry(complexity_bucket).or_insert(0) += 1;
                }
            }
        }

        // Calculate average complexity for each language
        for (lang, stats) in language_stats.iter_mut() {
            if let (Some(functions), Some(total_complexity)) = (
                stats["functions"].as_u64(),
                self.calculate_total_complexity_for_lang(results, lang)
            ) {
                if functions > 0 {
                    stats["avg_complexity"] = json!(total_complexity as f64 / functions as f64);
                }
            }
        }

        // Sort hotspots by complexity
        hotspots.sort_by(|a, b| {
            b["complexity"].as_u64().unwrap_or(0)
                .cmp(&a["complexity"].as_u64().unwrap_or(0))
        });

        json!({
            "summary": {
                "total_files": total_files,
                "total_functions": total_functions,
                "total_lines": total_lines,
                "languages": language_stats.len()
            },
            "language_stats": language_stats,
            "complexity_distribution": complexity_distribution,
            "hotspots": hotspots.into_iter().take(20).collect::<Vec<_>>(),
            "recommendations": self.generate_recommendations(&hotspots, &complexity_distribution),
            "timestamp": chrono::Utc::now().format("%Y-%m-%d %H:%M:%S UTC").to_string()
        })
    }

    fn calculate_total_complexity_for_lang(&self, results: &[AnalysisResult], language: &str) -> Option<u32> {
        let mut total = 0;
        for result in results {
            if result.language == language {
                for file_analysis in &result.files {
                    for func in &file_analysis.functions {
                        total += func.complexity;
                    }
                }
            }
        }
        Some(total)
    }

    fn generate_recommendations(
        &self,
        hotspots: &[serde_json::Value],
        complexity_distribution: &HashMap<&str, u32>
    ) -> Vec<serde_json::Value> {
        let mut recommendations = Vec::new();

        // High complexity functions
        let very_complex_count = complexity_distribution.get("very_complex").unwrap_or(&0);
        let complex_count = complexity_distribution.get("complex").unwrap_or(&0);

        if *very_complex_count > 0 {
            recommendations.push(json!({
                "priority": "high",
                "category": "complexity",
                "title": format!("{} functions have very high complexity (>20)", very_complex_count),
                "description": "Consider breaking down these functions into smaller, more focused units.",
                "action": "refactor_complex_functions"
            }));
        }

        if *complex_count > 5 {
            recommendations.push(json!({
                "priority": "medium",
                "category": "complexity",
                "title": format!("{} functions have high complexity (11-20)", complex_count),
                "description": "Review these functions for potential simplification opportunities.",
                "action": "review_complex_functions"
            }));
        }

        // Code coverage recommendation
        let total_functions: u32 = complexity_distribution.values().sum();
        if total_functions > 50 {
            recommendations.push(json!({
                "priority": "medium",
                "category": "testing",
                "title": "Consider implementing comprehensive testing",
                "description": format!("With {} functions in the codebase, automated testing would help maintain quality.", total_functions),
                "action": "implement_testing"
            }));
        }

        // Documentation recommendation
        if hotspots.len() > 10 {
            recommendations.push(json!({
                "priority": "low",
                "category": "documentation",
                "title": "Document complex functions",
                "description": "Functions with high complexity would benefit from detailed documentation.",
                "action": "add_documentation"
            }));
        }

        recommendations
    }

    fn render_template(&self, data: &serde_json::Value) -> Result<String, Box<dyn std::error::Error>> {
        let html = self.template.replace("{{DATA_PLACEHOLDER}}", &data.to_string());
        Ok(html)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

    #[test]
    fn test_report_generation() {
        let reporter = HtmlReporter::new().unwrap();
        let results = vec![];
        let dir = tempdir().unwrap();
        let output_path = dir.path().join("test_report.html");

        assert!(reporter.generate_report(&results, &output_path).is_ok());
        assert!(output_path.exists());
    }
}
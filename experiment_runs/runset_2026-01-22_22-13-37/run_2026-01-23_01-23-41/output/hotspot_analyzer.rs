use std::collections::HashMap;
use serde::{Serialize, Deserialize};
use crate::analysis::{AnalysisResult, FileAnalysis, FunctionInfo};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CodeHotspot {
    pub id: String,
    pub file_path: String,
    pub function_name: Option<String>,
    pub line_start: u32,
    pub line_end: u32,
    pub hotspot_type: HotspotType,
    pub severity: Severity,
    pub score: f32,
    pub metrics: HotspotMetrics,
    pub recommendations: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum HotspotType {
    HighComplexity,
    LargeFunction,
    DeepNesting,
    TooManyParameters,
    DuplicatedCode,
    LowCohesion,
    TightCoupling,
    CodeSmell,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Severity {
    Critical,
    High,
    Medium,
    Low,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HotspotMetrics {
    pub complexity: Option<u32>,
    pub lines_of_code: Option<u32>,
    pub nesting_depth: Option<u32>,
    pub parameter_count: Option<u32>,
    pub coupling_score: Option<f32>,
    pub cohesion_score: Option<f32>,
    pub duplication_percentage: Option<f32>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct HotspotAnalysisResult {
    pub hotspots: Vec<CodeHotspot>,
    pub summary: HotspotSummary,
    pub quality_score: f32,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct HotspotSummary {
    pub total_hotspots: usize,
    pub critical_count: usize,
    pub high_count: usize,
    pub medium_count: usize,
    pub low_count: usize,
    pub most_problematic_files: Vec<String>,
    pub improvement_potential: f32,
}

pub struct HotspotAnalyzer {
    complexity_threshold: u32,
    function_size_threshold: u32,
    nesting_depth_threshold: u32,
    parameter_count_threshold: u32,
}

impl HotspotAnalyzer {
    pub fn new() -> Self {
        HotspotAnalyzer {
            complexity_threshold: 10,
            function_size_threshold: 50,
            nesting_depth_threshold: 4,
            parameter_count_threshold: 5,
        }
    }

    pub fn with_thresholds(
        complexity: u32,
        function_size: u32,
        nesting_depth: u32,
        parameter_count: u32,
    ) -> Self {
        HotspotAnalyzer {
            complexity_threshold: complexity,
            function_size_threshold: function_size,
            nesting_depth_threshold: nesting_depth,
            parameter_count_threshold: parameter_count,
        }
    }

    pub fn analyze_hotspots(&self, results: &[AnalysisResult]) -> HotspotAnalysisResult {
        let mut hotspots = Vec::new();
        let mut file_scores = HashMap::new();

        for result in results {
            for file_analysis in &result.files {
                let file_hotspots = self.analyze_file_hotspots(file_analysis, &result.language);

                // Calculate file quality score
                let file_score = self.calculate_file_quality_score(file_analysis, &file_hotspots);
                file_scores.insert(file_analysis.file_path.clone(), file_score);

                hotspots.extend(file_hotspots);
            }
        }

        // Sort hotspots by severity and score
        hotspots.sort_by(|a, b| {
            match (&a.severity, &b.severity) {
                (Severity::Critical, Severity::Critical) => b.score.partial_cmp(&a.score).unwrap(),
                (Severity::Critical, _) => std::cmp::Ordering::Less,
                (_, Severity::Critical) => std::cmp::Ordering::Greater,
                (Severity::High, Severity::High) => b.score.partial_cmp(&a.score).unwrap(),
                (Severity::High, _) => std::cmp::Ordering::Less,
                (_, Severity::High) => std::cmp::Ordering::Greater,
                (Severity::Medium, Severity::Medium) => b.score.partial_cmp(&a.score).unwrap(),
                (Severity::Medium, _) => std::cmp::Ordering::Less,
                (_, Severity::Medium) => std::cmp::Ordering::Greater,
                (Severity::Low, Severity::Low) => b.score.partial_cmp(&a.score).unwrap(),
            }
        });

        let summary = self.create_summary(&hotspots, &file_scores);
        let quality_score = self.calculate_overall_quality_score(&hotspots, results);

        HotspotAnalysisResult {
            hotspots,
            summary,
            quality_score,
        }
    }

    fn analyze_file_hotspots(&self, file_analysis: &FileAnalysis, language: &str) -> Vec<CodeHotspot> {
        let mut hotspots = Vec::new();

        // Analyze each function
        for (index, function) in file_analysis.functions.iter().enumerate() {
            hotspots.extend(self.analyze_function_hotspots(
                file_analysis,
                function,
                language,
                index,
            ));
        }

        // Analyze file-level hotspots
        hotspots.extend(self.analyze_file_level_hotspots(file_analysis, language));

        hotspots
    }

    fn analyze_function_hotspots(
        &self,
        file_analysis: &FileAnalysis,
        function: &FunctionInfo,
        language: &str,
        function_index: usize,
    ) -> Vec<CodeHotspot> {
        let mut hotspots = Vec::new();

        // High complexity hotspot
        if function.complexity > self.complexity_threshold {
            let severity = match function.complexity {
                21.. => Severity::Critical,
                16..=20 => Severity::High,
                11..=15 => Severity::Medium,
                _ => Severity::Low,
            };

            let score = function.complexity as f32 * 10.0;

            hotspots.push(CodeHotspot {
                id: format!("complexity_{}_{}", file_analysis.file_path, function.name),
                file_path: file_analysis.file_path.clone(),
                function_name: Some(function.name.clone()),
                line_start: function.line_number,
                line_end: function.line_number + self.estimate_function_lines(function),
                hotspot_type: HotspotType::HighComplexity,
                severity,
                score,
                metrics: HotspotMetrics {
                    complexity: Some(function.complexity),
                    lines_of_code: Some(self.estimate_function_lines(function)),
                    nesting_depth: None,
                    parameter_count: None,
                    coupling_score: None,
                    cohesion_score: None,
                    duplication_percentage: None,
                },
                recommendations: vec![
                    "Consider breaking this function into smaller, more focused functions".to_string(),
                    "Extract complex logic into separate helper functions".to_string(),
                    "Review nested conditionals and loops for simplification opportunities".to_string(),
                ],
            });
        }

        // Large function hotspot
        let estimated_lines = self.estimate_function_lines(function);
        if estimated_lines > self.function_size_threshold {
            let severity = match estimated_lines {
                101.. => Severity::High,
                71..=100 => Severity::Medium,
                _ => Severity::Low,
            };

            hotspots.push(CodeHotspot {
                id: format!("large_function_{}_{}", file_analysis.file_path, function.name),
                file_path: file_analysis.file_path.clone(),
                function_name: Some(function.name.clone()),
                line_start: function.line_number,
                line_end: function.line_number + estimated_lines,
                hotspot_type: HotspotType::LargeFunction,
                severity,
                score: estimated_lines as f32,
                metrics: HotspotMetrics {
                    complexity: Some(function.complexity),
                    lines_of_code: Some(estimated_lines),
                    nesting_depth: None,
                    parameter_count: None,
                    coupling_score: None,
                    cohesion_score: None,
                    duplication_percentage: None,
                },
                recommendations: vec![
                    "Split this large function into smaller, single-responsibility functions".to_string(),
                    "Extract reusable logic into utility functions".to_string(),
                    "Consider using the Strategy or Template Method patterns".to_string(),
                ],
            });
        }

        // Analyze parameter count (simplified estimation)
        let estimated_params = self.estimate_parameter_count(function, language);
        if estimated_params > self.parameter_count_threshold {
            hotspots.push(CodeHotspot {
                id: format!("too_many_params_{}_{}", file_analysis.file_path, function.name),
                file_path: file_analysis.file_path.clone(),
                function_name: Some(function.name.clone()),
                line_start: function.line_number,
                line_end: function.line_number + 1,
                hotspot_type: HotspotType::TooManyParameters,
                severity: if estimated_params > 8 { Severity::High } else { Severity::Medium },
                score: estimated_params as f32 * 5.0,
                metrics: HotspotMetrics {
                    complexity: Some(function.complexity),
                    lines_of_code: Some(estimated_lines),
                    nesting_depth: None,
                    parameter_count: Some(estimated_params),
                    coupling_score: None,
                    cohesion_score: None,
                    duplication_percentage: None,
                },
                recommendations: vec![
                    "Consider using a parameter object or struct".to_string(),
                    "Group related parameters into configuration objects".to_string(),
                    "Review if all parameters are necessary".to_string(),
                ],
            });
        }

        hotspots
    }

    fn analyze_file_level_hotspots(&self, file_analysis: &FileAnalysis, _language: &str) -> Vec<CodeHotspot> {
        let mut hotspots = Vec::new();

        // Large file hotspot
        if file_analysis.line_count > 500 {
            let severity = match file_analysis.line_count {
                1001.. => Severity::High,
                751..=1000 => Severity::Medium,
                _ => Severity::Low,
            };

            hotspots.push(CodeHotspot {
                id: format!("large_file_{}", file_analysis.file_path),
                file_path: file_analysis.file_path.clone(),
                function_name: None,
                line_start: 1,
                line_end: file_analysis.line_count,
                hotspot_type: HotspotType::LowCohesion,
                severity,
                score: file_analysis.line_count as f32 / 10.0,
                metrics: HotspotMetrics {
                    complexity: None,
                    lines_of_code: Some(file_analysis.line_count),
                    nesting_depth: None,
                    parameter_count: None,
                    coupling_score: None,
                    cohesion_score: None,
                    duplication_percentage: None,
                },
                recommendations: vec![
                    "Consider splitting this large file into smaller, focused modules".to_string(),
                    "Group related functionality into separate files".to_string(),
                    "Extract utility functions to separate modules".to_string(),
                ],
            });
        }

        // Too many functions in one file
        if file_analysis.functions.len() > 20 {
            hotspots.push(CodeHotspot {
                id: format!("too_many_functions_{}", file_analysis.file_path),
                file_path: file_analysis.file_path.clone(),
                function_name: None,
                line_start: 1,
                line_end: file_analysis.line_count,
                hotspot_type: HotspotType::LowCohesion,
                severity: Severity::Medium,
                score: file_analysis.functions.len() as f32 * 2.0,
                metrics: HotspotMetrics {
                    complexity: None,
                    lines_of_code: Some(file_analysis.line_count),
                    nesting_depth: None,
                    parameter_count: None,
                    coupling_score: None,
                    cohesion_score: Some(self.calculate_file_cohesion(file_analysis)),
                    duplication_percentage: None,
                },
                recommendations: vec![
                    "Organize functions into logical groups or classes".to_string(),
                    "Consider using modules or namespaces to group related functions".to_string(),
                    "Extract utility functions to a separate utilities module".to_string(),
                ],
            });
        }

        hotspots
    }

    fn estimate_function_lines(&self, function: &FunctionInfo) -> u32 {
        // Rough estimation based on complexity
        match function.complexity {
            1..=5 => 5 + (function.complexity * 2),
            6..=10 => 15 + (function.complexity * 3),
            11..=20 => 25 + (function.complexity * 4),
            _ => 50 + (function.complexity * 5),
        }
    }

    fn estimate_parameter_count(&self, function: &FunctionInfo, language: &str) -> u32 {
        // Simplified parameter estimation based on function name patterns and complexity
        let base_params = match language {
            "rust" => {
                if function.name.contains("new") || function.name.contains("create") {
                    3
                } else if function.name.starts_with("set_") || function.name.starts_with("update_") {
                    2
                } else {
                    1
                }
            }
            "javascript" | "typescript" => {
                if function.name.contains("handle") || function.name.contains("process") {
                    4
                } else {
                    2
                }
            }
            _ => 2,
        };

        // Adjust based on complexity
        base_params + (function.complexity / 5)
    }

    fn calculate_file_cohesion(&self, file_analysis: &FileAnalysis) -> f32 {
        if file_analysis.functions.is_empty() {
            return 1.0;
        }

        // Simplified cohesion calculation based on function name similarity
        let mut similarity_scores = Vec::new();

        for i in 0..file_analysis.functions.len() {
            for j in (i + 1)..file_analysis.functions.len() {
                let similarity = self.calculate_name_similarity(
                    &file_analysis.functions[i].name,
                    &file_analysis.functions[j].name,
                );
                similarity_scores.push(similarity);
            }
        }

        if similarity_scores.is_empty() {
            1.0
        } else {
            similarity_scores.iter().sum::<f32>() / similarity_scores.len() as f32
        }
    }

    fn calculate_name_similarity(&self, name1: &str, name2: &str) -> f32 {
        // Simple similarity based on common prefixes and word patterns
        let name1_parts: Vec<&str> = name1.split('_').collect();
        let name2_parts: Vec<&str> = name2.split('_').collect();

        let common_parts = name1_parts.iter()
            .filter(|part| name2_parts.contains(part))
            .count();

        let total_parts = (name1_parts.len() + name2_parts.len()) as f32;

        if total_parts > 0.0 {
            (common_parts as f32 * 2.0) / total_parts
        } else {
            0.0
        }
    }

    fn calculate_file_quality_score(&self, file_analysis: &FileAnalysis, hotspots: &[CodeHotspot]) -> f32 {
        let base_score = 100.0;
        let penalty_per_hotspot = hotspots.iter().map(|h| match h.severity {
            Severity::Critical => 20.0,
            Severity::High => 10.0,
            Severity::Medium => 5.0,
            Severity::Low => 2.0,
        }).sum::<f32>();

        (base_score - penalty_per_hotspot).max(0.0)
    }

    fn create_summary(&self, hotspots: &[CodeHotspot], file_scores: &HashMap<String, f32>) -> HotspotSummary {
        let mut critical_count = 0;
        let mut high_count = 0;
        let mut medium_count = 0;
        let mut low_count = 0;

        for hotspot in hotspots {
            match hotspot.severity {
                Severity::Critical => critical_count += 1,
                Severity::High => high_count += 1,
                Severity::Medium => medium_count += 1,
                Severity::Low => low_count += 1,
            }
        }

        // Find most problematic files
        let mut file_scores_vec: Vec<(&String, &f32)> = file_scores.iter().collect();
        file_scores_vec.sort_by(|a, b| a.1.partial_cmp(b.1).unwrap());
        let most_problematic_files: Vec<String> = file_scores_vec
            .iter()
            .take(5)
            .map(|(path, _)| (*path).clone())
            .collect();

        // Calculate improvement potential
        let improvement_potential = if file_scores.is_empty() {
            0.0
        } else {
            let average_score: f32 = file_scores.values().sum::<f32>() / file_scores.len() as f32;
            100.0 - average_score
        };

        HotspotSummary {
            total_hotspots: hotspots.len(),
            critical_count,
            high_count,
            medium_count,
            low_count,
            most_problematic_files,
            improvement_potential,
        }
    }

    fn calculate_overall_quality_score(&self, hotspots: &[CodeHotspot], results: &[AnalysisResult]) -> f32 {
        let total_functions: usize = results.iter()
            .flat_map(|r| &r.files)
            .map(|f| f.functions.len())
            .sum();

        if total_functions == 0 {
            return 100.0;
        }

        let penalty = hotspots.iter().map(|h| match h.severity {
            Severity::Critical => 10.0,
            Severity::High => 5.0,
            Severity::Medium => 2.0,
            Severity::Low => 1.0,
        }).sum::<f32>();

        let penalty_per_function = penalty / total_functions as f32;
        (100.0 - (penalty_per_function * 10.0)).max(0.0)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::analysis::{FileAnalysis, FunctionInfo};

    #[test]
    fn test_hotspot_analyzer_creation() {
        let analyzer = HotspotAnalyzer::new();
        assert_eq!(analyzer.complexity_threshold, 10);
    }

    #[test]
    fn test_function_line_estimation() {
        let analyzer = HotspotAnalyzer::new();
        let function = FunctionInfo {
            name: "test_function".to_string(),
            line_number: 1,
            complexity: 15,
        };

        let estimated_lines = analyzer.estimate_function_lines(&function);
        assert!(estimated_lines > 20);
    }

    #[test]
    fn test_name_similarity() {
        let analyzer = HotspotAnalyzer::new();
        let similarity = analyzer.calculate_name_similarity("get_user_data", "get_user_profile");
        assert!(similarity > 0.5);
    }
}
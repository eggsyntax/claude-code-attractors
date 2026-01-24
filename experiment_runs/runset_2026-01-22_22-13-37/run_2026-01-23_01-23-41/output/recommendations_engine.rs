use std::collections::HashMap;
use serde::{Serialize, Deserialize};
use crate::analysis::AnalysisResult;
use crate::hotspot_analyzer::{HotspotAnalysisResult, CodeHotspot, Severity};
use crate::dependency_analyzer::DependencyGraph;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Recommendation {
    pub id: String,
    pub title: String,
    pub description: String,
    pub category: RecommendationCategory,
    pub priority: Priority,
    pub impact: Impact,
    pub effort: Effort,
    pub roi_score: f32,
    pub actionable_steps: Vec<ActionableStep>,
    pub affected_files: Vec<String>,
    pub metrics_improvement: MetricsImprovement,
    pub examples: Vec<CodeExample>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum RecommendationCategory {
    Architecture,
    CodeQuality,
    Performance,
    Maintainability,
    Testing,
    Security,
    Documentation,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Priority {
    Critical,
    High,
    Medium,
    Low,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Impact {
    High,      // Significant improvement to codebase quality
    Medium,    // Moderate improvement
    Low,       // Minor improvement
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Effort {
    Low,       // < 1 day
    Medium,    // 1-3 days
    High,      // 1+ week
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ActionableStep {
    pub step_number: u32,
    pub description: String,
    pub estimated_time: String,
    pub tools_required: Vec<String>,
    pub code_changes: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetricsImprovement {
    pub complexity_reduction: Option<f32>,
    pub maintainability_increase: Option<f32>,
    pub performance_gain: Option<f32>,
    pub test_coverage_increase: Option<f32>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CodeExample {
    pub language: String,
    pub before: String,
    pub after: String,
    pub explanation: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RecommendationReport {
    pub recommendations: Vec<Recommendation>,
    pub summary: RecommendationSummary,
    pub implementation_roadmap: Vec<RoadmapPhase>,
    pub roi_analysis: ROIAnalysis,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RecommendationSummary {
    pub total_recommendations: usize,
    pub by_category: HashMap<String, usize>,
    pub by_priority: HashMap<String, usize>,
    pub estimated_improvement: f32,
    pub quick_wins: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RoadmapPhase {
    pub phase_number: u32,
    pub name: String,
    pub description: String,
    pub recommendations: Vec<String>,
    pub estimated_duration: String,
    pub prerequisites: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ROIAnalysis {
    pub total_effort_estimate: String,
    pub expected_benefits: Vec<String>,
    pub risk_mitigation: Vec<String>,
    pub success_metrics: Vec<String>,
}

pub struct RecommendationsEngine {
    knowledge_base: RecommendationKnowledgeBase,
}

struct RecommendationKnowledgeBase {
    complexity_patterns: HashMap<String, RecommendationTemplate>,
    architectural_patterns: HashMap<String, RecommendationTemplate>,
    best_practices: HashMap<String, RecommendationTemplate>,
}

struct RecommendationTemplate {
    title_template: String,
    description_template: String,
    steps_template: Vec<String>,
    examples: Vec<CodeExample>,
}

impl RecommendationsEngine {
    pub fn new() -> Self {
        let knowledge_base = RecommendationKnowledgeBase::new();
        RecommendationsEngine { knowledge_base }
    }

    pub fn generate_recommendations(
        &self,
        analysis_results: &[AnalysisResult],
        hotspot_results: &HotspotAnalysisResult,
        dependency_graph: &DependencyGraph,
    ) -> RecommendationReport {
        let mut recommendations = Vec::new();

        // Generate complexity-based recommendations
        recommendations.extend(self.generate_complexity_recommendations(hotspot_results));

        // Generate architecture recommendations
        recommendations.extend(self.generate_architecture_recommendations(dependency_graph));

        // Generate maintainability recommendations
        recommendations.extend(self.generate_maintainability_recommendations(analysis_results, hotspot_results));

        // Generate testing recommendations
        recommendations.extend(self.generate_testing_recommendations(analysis_results));

        // Generate performance recommendations
        recommendations.extend(self.generate_performance_recommendations(analysis_results, hotspot_results));

        // Calculate ROI scores and sort by priority
        self.calculate_roi_scores(&mut recommendations);
        self.sort_recommendations_by_priority(&mut recommendations);

        let summary = self.create_summary(&recommendations);
        let roadmap = self.create_implementation_roadmap(&recommendations);
        let roi_analysis = self.create_roi_analysis(&recommendations);

        RecommendationReport {
            recommendations,
            summary,
            implementation_roadmap: roadmap,
            roi_analysis,
        }
    }

    fn generate_complexity_recommendations(&self, hotspot_results: &HotspotAnalysisResult) -> Vec<Recommendation> {
        let mut recommendations = Vec::new();

        // High complexity functions
        let critical_hotspots: Vec<&CodeHotspot> = hotspot_results.hotspots
            .iter()
            .filter(|h| matches!(h.severity, Severity::Critical))
            .collect();

        if !critical_hotspots.is_empty() {
            let affected_files: Vec<String> = critical_hotspots
                .iter()
                .map(|h| h.file_path.clone())
                .collect::<std::collections::HashSet<_>>()
                .into_iter()
                .collect();

            recommendations.push(Recommendation {
                id: "reduce_critical_complexity".to_string(),
                title: format!("Reduce Complexity in {} Critical Functions", critical_hotspots.len()),
                description: "Functions with very high cyclomatic complexity are difficult to understand, test, and maintain. Breaking them down will significantly improve code quality.".to_string(),
                category: RecommendationCategory::CodeQuality,
                priority: Priority::Critical,
                impact: Impact::High,
                effort: Effort::Medium,
                roi_score: 0.0, // Will be calculated later
                actionable_steps: vec![
                    ActionableStep {
                        step_number: 1,
                        description: "Identify the most complex control flow paths in each function".to_string(),
                        estimated_time: "2-4 hours".to_string(),
                        tools_required: vec!["IDE with complexity analysis".to_string()],
                        code_changes: None,
                    },
                    ActionableStep {
                        step_number: 2,
                        description: "Extract complex logic blocks into separate helper functions".to_string(),
                        estimated_time: "1-2 days per function".to_string(),
                        tools_required: vec!["Refactoring tools".to_string()],
                        code_changes: Some("Create smaller, focused functions with single responsibilities".to_string()),
                    },
                    ActionableStep {
                        step_number: 3,
                        description: "Add unit tests for the new smaller functions".to_string(),
                        estimated_time: "4-8 hours".to_string(),
                        tools_required: vec!["Testing framework".to_string()],
                        code_changes: None,
                    },
                ],
                affected_files,
                metrics_improvement: MetricsImprovement {
                    complexity_reduction: Some(40.0),
                    maintainability_increase: Some(30.0),
                    performance_gain: None,
                    test_coverage_increase: Some(20.0),
                },
                examples: vec![
                    self.create_complexity_reduction_example(),
                ],
            });
        }

        recommendations
    }

    fn generate_architecture_recommendations(&self, dependency_graph: &DependencyGraph) -> Vec<Recommendation> {
        let mut recommendations = Vec::new();

        // Circular dependencies
        if !dependency_graph.metrics.circular_dependencies.is_empty() {
            recommendations.push(Recommendation {
                id: "resolve_circular_dependencies".to_string(),
                title: "Resolve Circular Dependencies".to_string(),
                description: "Circular dependencies create tight coupling and make the codebase harder to maintain and test.".to_string(),
                category: RecommendationCategory::Architecture,
                priority: Priority::High,
                impact: Impact::High,
                effort: Effort::High,
                roi_score: 0.0,
                actionable_steps: vec![
                    ActionableStep {
                        step_number: 1,
                        description: "Map out all circular dependency chains".to_string(),
                        estimated_time: "4-6 hours".to_string(),
                        tools_required: vec!["Dependency visualization tools".to_string()],
                        code_changes: None,
                    },
                    ActionableStep {
                        step_number: 2,
                        description: "Identify shared abstractions that can break the cycles".to_string(),
                        estimated_time: "1-2 days".to_string(),
                        tools_required: vec!["Architecture design tools".to_string()],
                        code_changes: Some("Create interfaces or abstract base classes".to_string()),
                    },
                    ActionableStep {
                        step_number: 3,
                        description: "Refactor code to use dependency injection".to_string(),
                        estimated_time: "3-5 days".to_string(),
                        tools_required: vec!["DI container or framework".to_string()],
                        code_changes: Some("Invert dependencies using interfaces".to_string()),
                    },
                ],
                affected_files: dependency_graph.metrics.circular_dependencies
                    .iter()
                    .flatten()
                    .cloned()
                    .collect(),
                metrics_improvement: MetricsImprovement {
                    complexity_reduction: Some(20.0),
                    maintainability_increase: Some(50.0),
                    performance_gain: None,
                    test_coverage_increase: Some(25.0),
                },
                examples: vec![
                    self.create_dependency_inversion_example(),
                ],
            });
        }

        // Low modularity
        if dependency_graph.metrics.modularity_score < 0.5 {
            recommendations.push(Recommendation {
                id: "improve_modularity".to_string(),
                title: "Improve Code Modularity".to_string(),
                description: "Low modularity indicates that related functionality is scattered across the codebase, making it harder to maintain.".to_string(),
                category: RecommendationCategory::Architecture,
                priority: Priority::Medium,
                impact: Impact::Medium,
                effort: Effort::High,
                roi_score: 0.0,
                actionable_steps: vec![
                    ActionableStep {
                        step_number: 1,
                        description: "Analyze current module boundaries and responsibilities".to_string(),
                        estimated_time: "1 day".to_string(),
                        tools_required: vec!["Code analysis tools".to_string()],
                        code_changes: None,
                    },
                    ActionableStep {
                        step_number: 2,
                        description: "Group related functionality into cohesive modules".to_string(),
                        estimated_time: "1-2 weeks".to_string(),
                        tools_required: vec!["Refactoring tools".to_string()],
                        code_changes: Some("Reorganize code into logical modules".to_string()),
                    },
                ],
                affected_files: vec![], // Would be populated based on analysis
                metrics_improvement: MetricsImprovement {
                    complexity_reduction: None,
                    maintainability_increase: Some(35.0),
                    performance_gain: None,
                    test_coverage_increase: None,
                },
                examples: vec![],
            });
        }

        recommendations
    }

    fn generate_maintainability_recommendations(
        &self,
        analysis_results: &[AnalysisResult],
        hotspot_results: &HotspotAnalysisResult,
    ) -> Vec<Recommendation> {
        let mut recommendations = Vec::new();

        // Large files
        let large_files: Vec<&CodeHotspot> = hotspot_results.hotspots
            .iter()
            .filter(|h| h.metrics.lines_of_code.unwrap_or(0) > 500)
            .collect();

        if !large_files.is_empty() {
            recommendations.push(Recommendation {
                id: "split_large_files".to_string(),
                title: format!("Split {} Large Files", large_files.len()),
                description: "Large files are harder to navigate and maintain. Splitting them improves code organization.".to_string(),
                category: RecommendationCategory::Maintainability,
                priority: Priority::Medium,
                impact: Impact::Medium,
                effort: Effort::Medium,
                roi_score: 0.0,
                actionable_steps: vec![
                    ActionableStep {
                        step_number: 1,
                        description: "Identify logical groupings within each large file".to_string(),
                        estimated_time: "2-4 hours per file".to_string(),
                        tools_required: vec!["Code editor with outline view".to_string()],
                        code_changes: None,
                    },
                    ActionableStep {
                        step_number: 2,
                        description: "Extract related functions/classes into separate files".to_string(),
                        estimated_time: "4-8 hours per file".to_string(),
                        tools_required: vec!["Refactoring tools".to_string()],
                        code_changes: Some("Create new files and move related code".to_string()),
                    },
                ],
                affected_files: large_files.iter().map(|h| h.file_path.clone()).collect(),
                metrics_improvement: MetricsImprovement {
                    complexity_reduction: Some(10.0),
                    maintainability_increase: Some(25.0),
                    performance_gain: None,
                    test_coverage_increase: None,
                },
                examples: vec![],
            });
        }

        recommendations
    }

    fn generate_testing_recommendations(&self, analysis_results: &[AnalysisResult]) -> Vec<Recommendation> {
        let mut recommendations = Vec::new();

        let total_functions: usize = analysis_results
            .iter()
            .flat_map(|r| &r.files)
            .map(|f| f.functions.len())
            .sum();

        // Assume low test coverage if we have many functions (simplified heuristic)
        if total_functions > 50 {
            recommendations.push(Recommendation {
                id: "improve_test_coverage".to_string(),
                title: "Implement Comprehensive Testing Strategy".to_string(),
                description: "With a large codebase, comprehensive testing is essential for maintaining quality and enabling safe refactoring.".to_string(),
                category: RecommendationCategory::Testing,
                priority: Priority::High,
                impact: Impact::High,
                effort: Effort::High,
                roi_score: 0.0,
                actionable_steps: vec![
                    ActionableStep {
                        step_number: 1,
                        description: "Set up testing framework and CI pipeline".to_string(),
                        estimated_time: "1-2 days".to_string(),
                        tools_required: vec!["Testing framework", "CI/CD tools"].iter().map(|s| s.to_string()).collect(),
                        code_changes: Some("Add test configuration and CI scripts".to_string()),
                    },
                    ActionableStep {
                        step_number: 2,
                        description: "Write unit tests for critical business logic".to_string(),
                        estimated_time: "2-3 weeks".to_string(),
                        tools_required: vec!["Testing framework".to_string()],
                        code_changes: Some("Create test files for core functionality".to_string()),
                    },
                    ActionableStep {
                        step_number: 3,
                        description: "Add integration tests for key user flows".to_string(),
                        estimated_time: "1-2 weeks".to_string(),
                        tools_required: vec!["Testing framework", "Test environment"].iter().map(|s| s.to_string()).collect(),
                        code_changes: Some("Create integration test suites".to_string()),
                    },
                ],
                affected_files: vec!["entire codebase".to_string()],
                metrics_improvement: MetricsImprovement {
                    complexity_reduction: None,
                    maintainability_increase: Some(40.0),
                    performance_gain: None,
                    test_coverage_increase: Some(70.0),
                },
                examples: vec![],
            });
        }

        recommendations
    }

    fn generate_performance_recommendations(
        &self,
        _analysis_results: &[AnalysisResult],
        hotspot_results: &HotspotAnalysisResult,
    ) -> Vec<Recommendation> {
        let mut recommendations = Vec::new();

        // High complexity functions might have performance implications
        let high_complexity_functions: Vec<&CodeHotspot> = hotspot_results.hotspots
            .iter()
            .filter(|h| h.metrics.complexity.unwrap_or(0) > 15)
            .collect();

        if !high_complexity_functions.is_empty() {
            recommendations.push(Recommendation {
                id: "optimize_performance_hotspots".to_string(),
                title: "Optimize Performance in Complex Functions".to_string(),
                description: "Complex functions often contain performance bottlenecks due to nested loops and inefficient algorithms.".to_string(),
                category: RecommendationCategory::Performance,
                priority: Priority::Medium,
                impact: Impact::Medium,
                effort: Effort::Medium,
                roi_score: 0.0,
                actionable_steps: vec![
                    ActionableStep {
                        step_number: 1,
                        description: "Profile the application to identify actual performance bottlenecks".to_string(),
                        estimated_time: "1-2 days".to_string(),
                        tools_required: vec!["Profiling tools".to_string()],
                        code_changes: None,
                    },
                    ActionableStep {
                        step_number: 2,
                        description: "Optimize algorithms in identified bottleneck functions".to_string(),
                        estimated_time: "3-5 days".to_string(),
                        tools_required: vec!["Performance analysis tools".to_string()],
                        code_changes: Some("Improve algorithm efficiency and data structures".to_string()),
                    },
                ],
                affected_files: high_complexity_functions.iter().map(|h| h.file_path.clone()).collect(),
                metrics_improvement: MetricsImprovement {
                    complexity_reduction: Some(15.0),
                    maintainability_increase: Some(10.0),
                    performance_gain: Some(30.0),
                    test_coverage_increase: None,
                },
                examples: vec![],
            });
        }

        recommendations
    }

    fn calculate_roi_scores(&self, recommendations: &mut [Recommendation]) {
        for recommendation in recommendations.iter_mut() {
            let impact_score = match recommendation.impact {
                Impact::High => 3.0,
                Impact::Medium => 2.0,
                Impact::Low => 1.0,
            };

            let effort_score = match recommendation.effort {
                Effort::Low => 1.0,
                Effort::Medium => 2.0,
                Effort::High => 3.0,
            };

            // ROI = Impact / Effort, with some category weighting
            let category_weight = match recommendation.category {
                RecommendationCategory::Architecture => 1.2,
                RecommendationCategory::CodeQuality => 1.1,
                RecommendationCategory::Testing => 1.15,
                _ => 1.0,
            };

            recommendation.roi_score = (impact_score / effort_score) * category_weight;
        }
    }

    fn sort_recommendations_by_priority(&self, recommendations: &mut Vec<Recommendation>) {
        recommendations.sort_by(|a, b| {
            match (&a.priority, &b.priority) {
                (Priority::Critical, Priority::Critical) => b.roi_score.partial_cmp(&a.roi_score).unwrap(),
                (Priority::Critical, _) => std::cmp::Ordering::Less,
                (_, Priority::Critical) => std::cmp::Ordering::Greater,
                (Priority::High, Priority::High) => b.roi_score.partial_cmp(&a.roi_score).unwrap(),
                (Priority::High, _) => std::cmp::Ordering::Less,
                (_, Priority::High) => std::cmp::Ordering::Greater,
                (Priority::Medium, Priority::Medium) => b.roi_score.partial_cmp(&a.roi_score).unwrap(),
                (Priority::Medium, _) => std::cmp::Ordering::Less,
                (_, Priority::Medium) => std::cmp::Ordering::Greater,
                (Priority::Low, Priority::Low) => b.roi_score.partial_cmp(&a.roi_score).unwrap(),
            }
        });
    }

    fn create_summary(&self, recommendations: &[Recommendation]) -> RecommendationSummary {
        let mut by_category = HashMap::new();
        let mut by_priority = HashMap::new();

        for rec in recommendations {
            let category_key = format!("{:?}", rec.category);
            *by_category.entry(category_key).or_insert(0) += 1;

            let priority_key = format!("{:?}", rec.priority);
            *by_priority.entry(priority_key).or_insert(0) += 1;
        }

        // Identify quick wins (high impact, low effort)
        let quick_wins: Vec<String> = recommendations
            .iter()
            .filter(|r| matches!(r.impact, Impact::High | Impact::Medium) && matches!(r.effort, Effort::Low))
            .map(|r| r.title.clone())
            .collect();

        RecommendationSummary {
            total_recommendations: recommendations.len(),
            by_category,
            by_priority,
            estimated_improvement: recommendations.iter()
                .map(|r| r.roi_score)
                .sum::<f32>() / recommendations.len() as f32 * 10.0,
            quick_wins,
        }
    }

    fn create_implementation_roadmap(&self, recommendations: &[Recommendation]) -> Vec<RoadmapPhase> {
        vec![
            RoadmapPhase {
                phase_number: 1,
                name: "Critical Issues & Quick Wins".to_string(),
                description: "Address critical issues and implement low-effort, high-impact improvements".to_string(),
                recommendations: recommendations
                    .iter()
                    .filter(|r| matches!(r.priority, Priority::Critical) ||
                              (matches!(r.impact, Impact::High) && matches!(r.effort, Effort::Low)))
                    .map(|r| r.id.clone())
                    .collect(),
                estimated_duration: "2-3 weeks".to_string(),
                prerequisites: vec![],
            },
            RoadmapPhase {
                phase_number: 2,
                name: "Architectural Improvements".to_string(),
                description: "Implement architectural changes and major refactoring efforts".to_string(),
                recommendations: recommendations
                    .iter()
                    .filter(|r| matches!(r.category, RecommendationCategory::Architecture) &&
                              matches!(r.priority, Priority::High | Priority::Medium))
                    .map(|r| r.id.clone())
                    .collect(),
                estimated_duration: "4-8 weeks".to_string(),
                prerequisites: vec!["Phase 1 completion".to_string()],
            },
            RoadmapPhase {
                phase_number: 3,
                name: "Quality & Maintainability".to_string(),
                description: "Focus on code quality, testing, and long-term maintainability".to_string(),
                recommendations: recommendations
                    .iter()
                    .filter(|r| matches!(r.category, RecommendationCategory::CodeQuality | RecommendationCategory::Testing | RecommendationCategory::Maintainability))
                    .map(|r| r.id.clone())
                    .collect(),
                estimated_duration: "3-6 weeks".to_string(),
                prerequisites: vec!["Phase 1 completion".to_string()],
            },
        ]
    }

    fn create_roi_analysis(&self, recommendations: &[Recommendation]) -> ROIAnalysis {
        let total_effort = recommendations.iter()
            .map(|r| match r.effort {
                Effort::Low => 1,
                Effort::Medium => 3,
                Effort::High => 8,
            })
            .sum::<u32>();

        ROIAnalysis {
            total_effort_estimate: format!("{}-{} weeks", total_effort / 2, total_effort),
            expected_benefits: vec![
                "Improved code maintainability and readability".to_string(),
                "Reduced technical debt and development friction".to_string(),
                "Enhanced testing coverage and confidence".to_string(),
                "Better architecture and separation of concerns".to_string(),
            ],
            risk_mitigation: vec![
                "Gradual implementation reduces deployment risk".to_string(),
                "Increased test coverage catches regressions early".to_string(),
                "Improved code quality reduces bug introduction rate".to_string(),
            ],
            success_metrics: vec![
                "Cyclomatic complexity reduction by 25-40%".to_string(),
                "Test coverage increase to 70%+".to_string(),
                "Code review time reduction by 30%".to_string(),
                "Bug report reduction by 40%".to_string(),
            ],
        }
    }

    fn create_complexity_reduction_example(&self) -> CodeExample {
        CodeExample {
            language: "rust".to_string(),
            before: r#"fn process_user_data(user: &User) -> Result<ProcessedData, Error> {
    if user.is_active {
        if user.has_premium {
            if user.age >= 18 {
                // Complex processing logic here
                for item in &user.items {
                    if item.is_valid() {
                        // More nested logic
                        match item.category {
                            Category::A => { /* complex logic */ },
                            Category::B => { /* complex logic */ },
                            _ => { /* more complex logic */ }
                        }
                    }
                }
            } else {
                return Err(Error::UnderageUser);
            }
        } else {
            // Different processing for non-premium
        }
    } else {
        return Err(Error::InactiveUser);
    }
    Ok(result)
}"#.to_string(),
            after: r#"fn process_user_data(user: &User) -> Result<ProcessedData, Error> {
    validate_user_eligibility(user)?;

    if user.has_premium {
        process_premium_user(user)
    } else {
        process_regular_user(user)
    }
}

fn validate_user_eligibility(user: &User) -> Result<(), Error> {
    if !user.is_active {
        return Err(Error::InactiveUser);
    }
    if user.age < 18 {
        return Err(Error::UnderageUser);
    }
    Ok(())
}

fn process_premium_user(user: &User) -> Result<ProcessedData, Error> {
    user.items.iter()
        .filter(|item| item.is_valid())
        .map(|item| process_item(item))
        .collect()
}

fn process_item(item: &Item) -> ProcessedData {
    match item.category {
        Category::A => process_category_a(item),
        Category::B => process_category_b(item),
        _ => process_default_category(item),
    }
}"#.to_string(),
            explanation: "The complex function was broken down into smaller, focused functions that each handle a specific responsibility. This reduces complexity, improves readability, and makes testing easier.".to_string(),
        }
    }

    fn create_dependency_inversion_example(&self) -> CodeExample {
        CodeExample {
            language: "rust".to_string(),
            before: r#"// Circular dependency: A depends on B, B depends on A
mod user_service {
    use crate::notification_service::NotificationService;

    pub struct UserService {
        notifier: NotificationService,
    }

    impl UserService {
        pub fn create_user(&self, user: User) {
            // ... create user logic
            self.notifier.send_welcome_email(&user);
        }
    }
}

mod notification_service {
    use crate::user_service::UserService;

    pub struct NotificationService {
        user_service: UserService, // Circular dependency!
    }
}"#.to_string(),
            after: r#"// Dependency inversion: both depend on abstractions
trait UserRepository {
    fn create_user(&self, user: User) -> Result<(), Error>;
}

trait NotificationSender {
    fn send_welcome_email(&self, user: &User) -> Result<(), Error>;
}

mod user_service {
    use crate::{UserRepository, NotificationSender};

    pub struct UserService<R: UserRepository, N: NotificationSender> {
        repository: R,
        notifier: N,
    }

    impl<R: UserRepository, N: NotificationSender> UserService<R, N> {
        pub fn create_user(&self, user: User) -> Result<(), Error> {
            self.repository.create_user(user)?;
            self.notifier.send_welcome_email(&user)?;
            Ok(())
        }
    }
}

mod notification_service {
    use crate::NotificationSender;

    pub struct EmailNotificationService;

    impl NotificationSender for EmailNotificationService {
        fn send_welcome_email(&self, user: &User) -> Result<(), Error> {
            // Send email logic
            Ok(())
        }
    }
}"#.to_string(),
            explanation: "By introducing trait abstractions and using dependency injection, we eliminated the circular dependency and made the code more testable and flexible.".to_string(),
        }
    }
}

impl RecommendationKnowledgeBase {
    fn new() -> Self {
        RecommendationKnowledgeBase {
            complexity_patterns: HashMap::new(),
            architectural_patterns: HashMap::new(),
            best_practices: HashMap::new(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_recommendations_engine_creation() {
        let engine = RecommendationsEngine::new();
        // Should not panic
    }

    #[test]
    fn test_roi_score_calculation() {
        let mut recommendations = vec![
            Recommendation {
                id: "test".to_string(),
                title: "Test".to_string(),
                description: "Test".to_string(),
                category: RecommendationCategory::CodeQuality,
                priority: Priority::High,
                impact: Impact::High,
                effort: Effort::Low,
                roi_score: 0.0,
                actionable_steps: vec![],
                affected_files: vec![],
                metrics_improvement: MetricsImprovement {
                    complexity_reduction: None,
                    maintainability_increase: None,
                    performance_gain: None,
                    test_coverage_increase: None,
                },
                examples: vec![],
            }
        ];

        let engine = RecommendationsEngine::new();
        engine.calculate_roi_scores(&mut recommendations);

        assert!(recommendations[0].roi_score > 0.0);
    }
}
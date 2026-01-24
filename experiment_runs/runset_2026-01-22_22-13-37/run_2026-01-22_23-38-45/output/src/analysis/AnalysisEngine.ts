import Parser from 'tree-sitter';
import { CodeFile, AnalysisResult, DetectedPattern, QualityMetrics, DependencyInfo, Suggestion, PatternType, SuggestionType } from '../types/core.js';
import { PatternDetector } from './PatternDetector.js';
import { MetricsCalculator } from './MetricsCalculator.js';
import { DependencyAnalyzer } from './DependencyAnalyzer.js';
import { SuggestionGenerator } from './SuggestionGenerator.js';
import { EducationalEngine, EducationalSummary } from './EducationalEngine.js';

/**
 * Core analysis engine that orchestrates all code analysis activities
 *
 * The AnalysisEngine serves as the central coordinator for:
 * - AST parsing and code structure analysis
 * - Pattern detection (architectural, design, anti-patterns)
 * - Quality metrics calculation
 * - Dependency mapping and analysis
 * - Educational suggestion generation
 *
 * It provides both real-time analysis for active development and
 * batch analysis for comprehensive codebase reviews.
 */
export class AnalysisEngine {
  private parsers: Map<string, Parser> = new Map();
  private patternDetector: PatternDetector;
  private metricsCalculator: MetricsCalculator;
  private dependencyAnalyzer: DependencyAnalyzer;
  private suggestionGenerator: SuggestionGenerator;
  private educationalEngine: EducationalEngine;

  // Cache for expensive analysis operations
  private analysisCache: Map<string, AnalysisResult> = new Map();
  private cacheMaxAge = 5 * 60 * 1000; // 5 minutes

  constructor() {
    this.patternDetector = new PatternDetector();
    this.metricsCalculator = new MetricsCalculator();
    this.dependencyAnalyzer = new DependencyAnalyzer();
    this.suggestionGenerator = new SuggestionGenerator();
    this.educationalEngine = new EducationalEngine();
  }

  /**
   * Initializes parsers for supported languages
   */
  async initialize(): Promise<void> {
    try {
      // Initialize tree-sitter parsers for supported languages
      await this.initializeParser('typescript', require('tree-sitter-typescript'));
      await this.initializeParser('javascript', require('tree-sitter-javascript'));
      await this.initializeParser('python', require('tree-sitter-python'));

      console.log('AnalysisEngine initialized with parsers for: TypeScript, JavaScript, Python');
    } catch (error) {
      console.error('Failed to initialize AnalysisEngine:', error);
      throw error;
    }
  }

  /**
   * Performs comprehensive analysis of a single file
   */
  async analyzeFile(file: CodeFile): Promise<AnalysisResult> {
    // Check cache first
    const cacheKey = this.getCacheKey(file);
    const cached = this.analysisCache.get(cacheKey);
    if (cached && this.isCacheValid(cached)) {
      return cached;
    }

    try {
      console.log(`Analyzing file: ${file.path} (${file.language})`);

      // Parse the file into an AST
      const tree = await this.parseFile(file);
      if (!tree) {
        throw new Error(`Unable to parse file ${file.path} - unsupported language: ${file.language}`);
      }

      // Parallel analysis execution for better performance
      const [patterns, metrics, dependencies] = await Promise.all([
        this.patternDetector.detectPatterns(file, tree),
        this.metricsCalculator.calculateMetrics(file, tree),
        this.dependencyAnalyzer.analyzeDependencies(file, tree)
      ]);

      // Generate educational suggestions based on findings
      const suggestions = await this.suggestionGenerator.generateSuggestions(
        file,
        patterns,
        metrics,
        dependencies
      );

      const result: AnalysisResult = {
        fileId: file.id,
        patterns,
        metrics,
        dependencies,
        suggestions,
        timestamp: new Date()
      };

      // Cache the result
      this.analysisCache.set(cacheKey, result);

      console.log(`Analysis complete: ${patterns.length} patterns, ${suggestions.length} suggestions`);
      return result;

    } catch (error) {
      console.error(`Error analyzing file ${file.path}:`, error);
      throw error;
    }
  }

  /**
   * Performs batch analysis of multiple files with cross-file insights
   */
  async analyzeProject(files: CodeFile[]): Promise<Map<string, AnalysisResult>> {
    console.log(`Starting project analysis for ${files.length} files`);

    const results = new Map<string, AnalysisResult>();
    const analysisPromises = files.map(file =>
      this.analyzeFile(file).then(result => ({ file, result }))
    );

    // Process files in parallel but respect system limits
    const batchSize = 5; // Prevent overwhelming the system
    for (let i = 0; i < analysisPromises.length; i += batchSize) {
      const batch = analysisPromises.slice(i, i + batchSize);
      const batchResults = await Promise.allSettled(batch);

      for (const outcome of batchResults) {
        if (outcome.status === 'fulfilled') {
          const { file, result } = outcome.value;
          results.set(file.id, result);
        } else {
          console.error('Failed to analyze file in batch:', outcome.reason);
        }
      }

      // Brief pause between batches to prevent resource exhaustion
      if (i + batchSize < analysisPromises.length) {
        await new Promise(resolve => setTimeout(resolve, 100));
      }
    }

    // Perform cross-file analysis to detect architectural patterns
    await this.performCrossFileAnalysis(Array.from(results.values()), files);

    console.log(`Project analysis complete: ${results.size} files analyzed`);
    return results;
  }

  /**
   * Gets analysis summary with key insights and recommendations
   */
  getProjectSummary(analysisResults: Map<string, AnalysisResult>): ProjectAnalysisSummary {
    const allResults = Array.from(analysisResults.values());

    // Aggregate metrics
    const avgComplexity = this.calculateAverageMetric(allResults, 'complexity');
    const avgMaintainability = this.calculateAverageMetric(allResults, 'maintainability');
    const avgTestability = this.calculateAverageMetric(allResults, 'testability');

    // Pattern frequency analysis
    const patternFrequency = this.analyzePatternFrequency(allResults);

    // Critical issues identification
    const criticalIssues = this.identifyCriticalIssues(allResults);

    // Architectural insights
    const architecturalInsights = this.generateArchitecturalInsights(allResults);

    return {
      totalFiles: analysisResults.size,
      averageMetrics: {
        complexity: avgComplexity,
        maintainability: avgMaintainability,
        testability: avgTestability,
        readability: this.calculateAverageMetric(allResults, 'readability'),
        performance: this.calculateAverageMetric(allResults, 'performance')
      },
      patternDistribution: patternFrequency,
      criticalIssues,
      architecturalInsights,
      recommendedActions: this.generateRecommendedActions(allResults),
      timestamp: new Date()
    };
  }

  /**
   * Provides real-time analysis feedback for active editing
   */
  async getRealtimeAnalysis(file: CodeFile, changesSinceLastAnalysis?: string[]): Promise<Partial<AnalysisResult>> {
    // For real-time analysis, we focus on quick checks rather than comprehensive analysis
    try {
      const tree = await this.parseFile(file);
      if (!tree) return {};

      // Quick pattern detection for immediate feedback
      const quickPatterns = await this.patternDetector.detectQuickPatterns(file, tree);

      // Basic metrics for immediate feedback
      const basicMetrics = await this.metricsCalculator.calculateBasicMetrics(file, tree);

      return {
        patterns: quickPatterns,
        metrics: basicMetrics,
        timestamp: new Date()
      };
    } catch (error) {
      console.error('Error in real-time analysis:', error);
      return {};
    }
  }

  private async initializeParser(language: string, parserModule: any): Promise<void> {
    const parser = new Parser();
    parser.setLanguage(parserModule);
    this.parsers.set(language, parser);
  }

  private async parseFile(file: CodeFile): Promise<Parser.Tree | null> {
    const parser = this.parsers.get(file.language);
    if (!parser) {
      console.warn(`No parser available for language: ${file.language}`);
      return null;
    }

    try {
      return parser.parse(file.content);
    } catch (error) {
      console.error(`Parse error for ${file.path}:`, error);
      return null;
    }
  }

  private getCacheKey(file: CodeFile): string {
    // Create cache key based on file path and content hash
    const contentHash = this.simpleHash(file.content);
    return `${file.path}:${file.lastModified.getTime()}:${contentHash}`;
  }

  private isCacheValid(result: AnalysisResult): boolean {
    const age = Date.now() - result.timestamp.getTime();
    return age < this.cacheMaxAge;
  }

  private simpleHash(str: string): string {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash.toString(36);
  }

  private async performCrossFileAnalysis(results: AnalysisResult[], files: CodeFile[]): Promise<void> {
    // This method would analyze patterns across multiple files
    // For now, we'll implement a basic version that looks for architectural patterns
    console.log('Performing cross-file architectural analysis...');

    // TODO: Implement cross-file pattern detection
    // - Module organization patterns
    // - Dependency injection patterns
    // - Layered architecture validation
    // - API design consistency checks
  }

  private calculateAverageMetric(results: AnalysisResult[], metric: keyof QualityMetrics): number {
    if (results.length === 0) return 0;
    const sum = results.reduce((acc, result) => acc + result.metrics[metric], 0);
    return Math.round((sum / results.length) * 100) / 100;
  }

  private analyzePatternFrequency(results: AnalysisResult[]): Map<PatternType, number> {
    const frequency = new Map<PatternType, number>();

    for (const result of results) {
      for (const pattern of result.patterns) {
        frequency.set(pattern.type, (frequency.get(pattern.type) || 0) + 1);
      }
    }

    return frequency;
  }

  private identifyCriticalIssues(results: AnalysisResult[]): CriticalIssue[] {
    const issues: CriticalIssue[] = [];

    for (const result of results) {
      // Identify critical suggestions
      for (const suggestion of result.suggestions) {
        if (suggestion.priority === 'critical') {
          issues.push({
            type: suggestion.type,
            description: suggestion.title,
            fileId: result.fileId,
            location: suggestion.location,
            severity: 'critical'
          });
        }
      }

      // Identify files with poor metrics
      if (result.metrics.maintainability < 3 || result.metrics.complexity > 8) {
        issues.push({
          type: 'maintainability',
          description: 'Low maintainability score detected',
          fileId: result.fileId,
          severity: 'high'
        });
      }
    }

    return issues;
  }

  private generateArchitecturalInsights(results: AnalysisResult[]): string[] {
    const insights: string[] = [];

    // Analyze overall patterns
    const patternCounts = this.analyzePatternFrequency(results);

    if (patternCounts.get('anti-pattern')! > patternCounts.get('design')!) {
      insights.push('Consider refactoring to replace anti-patterns with established design patterns');
    }

    if (patternCounts.get('security')! > 0) {
      insights.push('Security patterns detected - ensure these align with your security requirements');
    }

    return insights;
  }

  private generateRecommendedActions(results: AnalysisResult[]): string[] {
    const actions: string[] = [];

    // Analyze metrics to suggest actions
    const avgComplexity = this.calculateAverageMetric(results, 'complexity');
    const avgMaintainability = this.calculateAverageMetric(results, 'maintainability');

    if (avgComplexity > 6) {
      actions.push('Focus on reducing cyclomatic complexity through method extraction and simplification');
    }

    if (avgMaintainability < 5) {
      actions.push('Improve maintainability by adding documentation and reducing coupling');
    }

    return actions;
  }

  /**
   * Generates educational context for analysis results
   */
  generateEducationalSummary(analysisResults: Map<string, AnalysisResult>): EducationalSummary {
    const allPatterns = Array.from(analysisResults.values())
      .flatMap(result => result.patterns);

    return this.educationalEngine.generateEducationalContext(allPatterns);
  }

  /**
   * Provides detailed pattern explanation for learning
   */
  explainPattern(patternName: string, analysisResults: Map<string, AnalysisResult>): any {
    const allPatterns = Array.from(analysisResults.values())
      .flatMap(result => result.patterns);

    const pattern = allPatterns.find(p => p.name === patternName);
    if (!pattern) {
      return null;
    }

    const relatedPatterns = allPatterns.filter(p => p.name !== patternName);
    return this.educationalEngine.explainPatternInContext(pattern, relatedPatterns);
  }

  /**
   * Generates personalized learning path based on analysis
   */
  generateLearningPath(analysisResults: Map<string, AnalysisResult>): any {
    const allPatterns = Array.from(analysisResults.values())
      .flatMap(result => result.patterns);

    return this.educationalEngine.generateLearningPath(allPatterns);
  }

  /**
   * Clears the analysis cache to free memory
   */
  clearCache(): void {
    this.analysisCache.clear();
    console.log('Analysis cache cleared');
  }
}

// Supporting types for analysis summaries
export interface ProjectAnalysisSummary {
  totalFiles: number;
  averageMetrics: QualityMetrics;
  patternDistribution: Map<PatternType, number>;
  criticalIssues: CriticalIssue[];
  architecturalInsights: string[];
  recommendedActions: string[];
  timestamp: Date;
}

export interface CriticalIssue {
  type: SuggestionType;
  description: string;
  fileId: string;
  location?: any; // CodeLocation
  severity: 'critical' | 'high' | 'medium' | 'low';
}
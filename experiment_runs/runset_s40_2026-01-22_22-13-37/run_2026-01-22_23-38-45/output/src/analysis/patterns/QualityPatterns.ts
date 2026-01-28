/**
 * Code Quality Patterns Detection Engine
 *
 * This module identifies code quality patterns and anti-patterns that affect
 * maintainability, readability, and performance. It focuses on detecting
 * issues that impact long-term code health and team productivity.
 *
 * Quality patterns include:
 * - SOLID principles adherence/violations
 * - Code complexity issues
 * - Performance anti-patterns
 * - Security vulnerabilities
 * - Maintainability concerns
 */

import { SyntaxNode } from 'tree-sitter';
import { DetectedPattern, CodeFile, PatternType, PatternConfidence } from '../../types/core';

export interface QualityAnalysis {
  patterns: DetectedPattern[];
  metrics: QualityMetrics;
  suggestions: QualitySuggestion[];
}

export interface QualityMetrics {
  complexity: number;
  maintainability: number;
  readability: number;
  testability: number;
  performance: number;
}

export interface QualitySuggestion {
  type: 'refactor' | 'performance' | 'security' | 'maintainability';
  priority: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  location: {
    file: string;
    startLine: number;
    endLine: number;
  };
  before?: string;
  after?: string;
}

/**
 * Code Quality Pattern Detection Engine
 */
export class QualityPatterns {

  /**
   * Analyze code quality patterns across all files
   */
  async analyzeQuality(files: CodeFile[], astNodes: Map<string, SyntaxNode>): Promise<QualityAnalysis> {
    const patterns: DetectedPattern[] = [];
    const suggestions: QualitySuggestion[] = [];
    const metrics: QualityMetrics = {
      complexity: 0,
      maintainability: 0,
      readability: 0,
      testability: 0,
      performance: 0
    };

    // Run quality analysis in parallel
    const analysisPromises = files.map(async file => {
      const ast = astNodes.get(file.path);
      if (!ast) return null;

      return await this.analyzeFileQuality(file, ast);
    });

    const results = await Promise.all(analysisPromises);
    const validResults = results.filter(r => r !== null) as QualityAnalysis[];

    // Aggregate results
    validResults.forEach(result => {
      patterns.push(...result.patterns);
      suggestions.push(...result.suggestions);

      // Average metrics across files
      metrics.complexity += result.metrics.complexity;
      metrics.maintainability += result.metrics.maintainability;
      metrics.readability += result.metrics.readability;
      metrics.testability += result.metrics.testability;
      metrics.performance += result.metrics.performance;
    });

    if (validResults.length > 0) {
      metrics.complexity /= validResults.length;
      metrics.maintainability /= validResults.length;
      metrics.readability /= validResults.length;
      metrics.testability /= validResults.length;
      metrics.performance /= validResults.length;
    }

    return { patterns, metrics, suggestions };
  }

  /**
   * Analyze quality patterns for a single file
   */
  private async analyzeFileQuality(file: CodeFile, ast: SyntaxNode): Promise<QualityAnalysis> {
    const patterns: DetectedPattern[] = [];
    const suggestions: QualitySuggestion[] = [];

    // Detect various quality patterns/anti-patterns
    const solidViolations = await this.detectSOLIDViolations(file, ast);
    const complexityIssues = await this.detectComplexityIssues(file, ast);
    const performanceIssues = await this.detectPerformanceIssues(file, ast);
    const maintainabilityIssues = await this.detectMaintainabilityIssues(file, ast);
    const securityIssues = await this.detectSecurityIssues(file, ast);

    patterns.push(...solidViolations.patterns);
    patterns.push(...complexityIssues.patterns);
    patterns.push(...performanceIssues.patterns);
    patterns.push(...maintainabilityIssues.patterns);
    patterns.push(...securityIssues.patterns);

    suggestions.push(...solidViolations.suggestions);
    suggestions.push(...complexityIssues.suggestions);
    suggestions.push(...performanceIssues.suggestions);
    suggestions.push(...maintainabilityIssues.suggestions);
    suggestions.push(...securityIssues.suggestions);

    // Calculate quality metrics
    const metrics = this.calculateQualityMetrics(file, ast, patterns);

    return { patterns, metrics, suggestions };
  }

  /**
   * Detect SOLID principles violations
   */
  private async detectSOLIDViolations(file: CodeFile, ast: SyntaxNode): Promise<{patterns: DetectedPattern[], suggestions: QualitySuggestion[]}> {
    const patterns: DetectedPattern[] = [];
    const suggestions: QualitySuggestion[] = [];

    // Single Responsibility Principle violations
    const srpViolations = this.detectSRPViolations(file, ast);
    if (srpViolations.length > 0) {
      patterns.push({
        id: this.generateId(),
        name: 'Single Responsibility Principle Violation',
        type: PatternType.ANTI_PATTERN,
        description: 'Class or function has multiple responsibilities, making it harder to maintain and test',
        location: {
          files: [file.path],
          startLine: srpViolations[0].startLine,
          endLine: srpViolations[0].endLine
        },
        confidence: 0.8,
        benefits: [],
        drawbacks: [
          'Increased complexity and coupling',
          'Harder to unit test individual responsibilities',
          'Changes in one responsibility affect others',
          'Violates Open/Closed Principle'
        ],
        examples: [
          'A User class that handles both user data and user persistence',
          'A function that validates input, processes data, and sends notifications',
          'A component that manages state, handles API calls, and renders UI'
        ]
      });

      suggestions.push({
        type: 'refactor',
        priority: 'high',
        title: 'Split class/function responsibilities',
        description: 'Break down the class or function into smaller, focused units with single responsibilities',
        location: {
          file: file.path,
          startLine: srpViolations[0].startLine,
          endLine: srpViolations[0].endLine
        }
      });
    }

    // Open/Closed Principle violations
    const ocpViolations = this.detectOCPViolations(file, ast);
    if (ocpViolations.length > 0) {
      patterns.push({
        id: this.generateId(),
        name: 'Open/Closed Principle Violation',
        type: PatternType.ANTI_PATTERN,
        description: 'Code is not open for extension but closed for modification, requiring changes to existing code for new features',
        location: {
          files: [file.path],
          startLine: ocpViolations[0].startLine,
          endLine: ocpViolations[0].endLine
        },
        confidence: 0.7,
        benefits: [],
        drawbacks: [
          'New features require modifying existing code',
          'Higher risk of introducing bugs',
          'Difficult to extend without understanding all existing logic',
          'Testing burden increases with each modification'
        ],
        examples: [
          'Large switch/if-else statements for different types',
          'Classes that need modification to add new behaviors',
          'Functions with hardcoded logic for different scenarios'
        ]
      });

      suggestions.push({
        type: 'refactor',
        priority: 'medium',
        title: 'Use polymorphism or strategy pattern',
        description: 'Replace conditional logic with polymorphic classes or strategy pattern to allow extension without modification',
        location: {
          file: file.path,
          startLine: ocpViolations[0].startLine,
          endLine: ocpViolations[0].endLine
        }
      });
    }

    // Dependency Inversion Principle violations
    const dipViolations = this.detectDIPViolations(file, ast);
    if (dipViolations.length > 0) {
      patterns.push({
        id: this.generateId(),
        name: 'Dependency Inversion Principle Violation',
        type: PatternType.ANTI_PATTERN,
        description: 'High-level modules depend on low-level modules, creating tight coupling',
        location: {
          files: [file.path],
          startLine: dipViolations[0].startLine,
          endLine: dipViolations[0].endLine
        },
        confidence: 0.7,
        benefits: [],
        drawbacks: [
          'Tight coupling between modules',
          'Difficult to test in isolation',
          'Hard to swap implementations',
          'Reduced flexibility and reusability'
        ],
        examples: [
          'Business logic directly instantiating database connections',
          'Controllers directly importing specific service implementations',
          'Classes with hard-coded dependencies on concrete types'
        ]
      });

      suggestions.push({
        type: 'refactor',
        priority: 'high',
        title: 'Use dependency injection',
        description: 'Inject dependencies through interfaces or abstract classes to reduce coupling',
        location: {
          file: file.path,
          startLine: dipViolations[0].startLine,
          endLine: dipViolations[0].endLine
        }
      });
    }

    return { patterns, suggestions };
  }

  /**
   * Detect complexity issues (cyclomatic complexity, nesting depth, etc.)
   */
  private async detectComplexityIssues(file: CodeFile, ast: SyntaxNode): Promise<{patterns: DetectedPattern[], suggestions: QualitySuggestion[]}> {
    const patterns: DetectedPattern[] = [];
    const suggestions: QualitySuggestion[] = [];

    const complexity = this.calculateCyclomaticComplexity(ast);
    const maxNesting = this.calculateMaxNestingDepth(ast);
    const functionLength = this.calculateLongestFunction(ast);

    // High cyclomatic complexity
    if (complexity > 10) {
      patterns.push({
        id: this.generateId(),
        name: 'High Cyclomatic Complexity',
        type: PatternType.ANTI_PATTERN,
        description: `Code has high cyclomatic complexity (${complexity}), making it difficult to understand and test`,
        location: {
          files: [file.path],
          startLine: 1,
          endLine: file.content.split('\n').length
        },
        confidence: 0.9,
        benefits: [],
        drawbacks: [
          'Difficult to understand and maintain',
          'Higher chance of bugs',
          'Hard to achieve comprehensive test coverage',
          'Code review becomes challenging'
        ],
        examples: [
          'Functions with many if-else or switch statements',
          'Deeply nested conditional logic',
          'Functions with multiple exit points',
          'Complex loops with internal conditions'
        ]
      });

      suggestions.push({
        type: 'refactor',
        priority: 'high',
        title: 'Reduce cyclomatic complexity',
        description: 'Break down complex functions into smaller, focused functions. Consider using early returns, guard clauses, or strategy pattern.',
        location: {
          file: file.path,
          startLine: 1,
          endLine: file.content.split('\n').length
        }
      });
    }

    // Deep nesting
    if (maxNesting > 4) {
      patterns.push({
        id: this.generateId(),
        name: 'Deep Nesting',
        type: PatternType.ANTI_PATTERN,
        description: `Code has deep nesting levels (${maxNesting}), reducing readability`,
        location: {
          files: [file.path],
          startLine: 1,
          endLine: file.content.split('\n').length
        },
        confidence: 0.8,
        benefits: [],
        drawbacks: [
          'Reduced code readability',
          'Increased cognitive load',
          'Higher chance of logical errors',
          'Difficult to follow execution flow'
        ],
        examples: [
          'Nested if statements going 5+ levels deep',
          'Multiple nested loops',
          'Try-catch blocks inside loops inside conditions',
          'Callback hell in asynchronous code'
        ]
      });

      suggestions.push({
        type: 'refactor',
        priority: 'medium',
        title: 'Reduce nesting depth',
        description: 'Use early returns, guard clauses, or extract nested logic into separate functions to reduce nesting depth.',
        location: {
          file: file.path,
          startLine: 1,
          endLine: file.content.split('\n').length
        }
      });
    }

    return { patterns, suggestions };
  }

  /**
   * Detect performance anti-patterns
   */
  private async detectPerformanceIssues(file: CodeFile, ast: SyntaxNode): Promise<{patterns: DetectedPattern[], suggestions: QualitySuggestion[]}> {
    const patterns: DetectedPattern[] = [];
    const suggestions: QualitySuggestion[] = [];

    // N+1 Query problem
    const nPlusOneIssues = this.detectNPlusOneQueries(file, ast);
    if (nPlusOneIssues.length > 0) {
      patterns.push({
        id: this.generateId(),
        name: 'N+1 Query Problem',
        type: PatternType.PERFORMANCE,
        description: 'Code potentially executes N+1 database queries instead of a single optimized query',
        location: {
          files: [file.path],
          startLine: nPlusOneIssues[0].line,
          endLine: nPlusOneIssues[0].line + 10
        },
        confidence: 0.7,
        benefits: [],
        drawbacks: [
          'Poor database performance',
          'Increased latency',
          'Higher resource consumption',
          'Poor scalability'
        ],
        examples: [
          'Fetching user data in a loop instead of using JOIN',
          'Loading related entities one by one',
          'Multiple API calls in iteration instead of batch operations'
        ]
      });

      suggestions.push({
        type: 'performance',
        priority: 'high',
        title: 'Use bulk operations or JOIN queries',
        description: 'Replace individual queries in loops with bulk operations, JOINs, or batch API calls.',
        location: {
          file: file.path,
          startLine: nPlusOneIssues[0].line,
          endLine: nPlusOneIssues[0].line + 10
        }
      });
    }

    // Inefficient loops
    const inefficientLoops = this.detectInefficientLoops(file, ast);
    if (inefficientLoops.length > 0) {
      patterns.push({
        id: this.generateId(),
        name: 'Inefficient Loop Operations',
        type: PatternType.PERFORMANCE,
        description: 'Loops contain operations that could be optimized for better performance',
        location: {
          files: [file.path],
          startLine: inefficientLoops[0].line,
          endLine: inefficientLoops[0].line + 5
        },
        confidence: 0.6,
        benefits: [],
        drawbacks: [
          'Poor performance with large datasets',
          'Unnecessary CPU consumption',
          'Blocking event loop in Node.js',
          'Poor user experience'
        ],
        examples: [
          'Nested loops with O(n²) complexity that could be O(n)',
          'String concatenation in loops instead of array.join()',
          'DOM queries inside loops',
          'Expensive operations not cached or memoized'
        ]
      });

      suggestions.push({
        type: 'performance',
        priority: 'medium',
        title: 'Optimize loop operations',
        description: 'Move expensive operations outside loops, use efficient data structures, or consider memoization.',
        location: {
          file: file.path,
          startLine: inefficientLoops[0].line,
          endLine: inefficientLoops[0].line + 5
        }
      });
    }

    return { patterns, suggestions };
  }

  /**
   * Detect maintainability issues
   */
  private async detectMaintainabilityIssues(file: CodeFile, ast: SyntaxNode): Promise<{patterns: DetectedPattern[], suggestions: QualitySuggestion[]}> {
    const patterns: DetectedPattern[] = [];
    const suggestions: QualitySuggestion[] = [];

    // Code duplication
    const duplicatedCode = this.detectCodeDuplication(file, ast);
    if (duplicatedCode.length > 0) {
      patterns.push({
        id: this.generateId(),
        name: 'Code Duplication',
        type: PatternType.ANTI_PATTERN,
        description: 'Similar code blocks found that could be extracted into reusable functions',
        location: {
          files: [file.path],
          startLine: duplicatedCode[0].line,
          endLine: duplicatedCode[0].line + duplicatedCode[0].length
        },
        confidence: 0.8,
        benefits: [],
        drawbacks: [
          'Increased maintenance burden',
          'Inconsistent behavior when only one copy is updated',
          'Larger codebase',
          'Higher chance of bugs'
        ],
        examples: [
          'Similar validation logic repeated across functions',
          'Identical error handling patterns',
          'Repeated data transformation logic',
          'Copy-pasted utility functions'
        ]
      });

      suggestions.push({
        type: 'refactor',
        priority: 'medium',
        title: 'Extract common code into reusable functions',
        description: 'Create utility functions or shared modules for duplicated code patterns.',
        location: {
          file: file.path,
          startLine: duplicatedCode[0].line,
          endLine: duplicatedCode[0].line + duplicatedCode[0].length
        }
      });
    }

    // Magic numbers/strings
    const magicValues = this.detectMagicValues(file, ast);
    if (magicValues.length > 0) {
      patterns.push({
        id: this.generateId(),
        name: 'Magic Numbers/Strings',
        type: PatternType.MAINTAINABILITY,
        description: 'Hard-coded values that should be named constants for better maintainability',
        location: {
          files: [file.path],
          startLine: 1,
          endLine: file.content.split('\n').length
        },
        confidence: 0.6,
        benefits: [],
        drawbacks: [
          'Unclear code intent',
          'Difficult to modify values',
          'Potential for errors when values need to change',
          'Poor self-documentation'
        ],
        examples: [
          'setTimeout with hardcoded millisecond values',
          'Array/string indices without explanation',
          'HTTP status codes as numbers instead of named constants',
          'Configuration values embedded in business logic'
        ]
      });

      suggestions.push({
        type: 'maintainability',
        priority: 'low',
        title: 'Replace magic values with named constants',
        description: 'Extract hard-coded values into well-named constants or configuration objects.',
        location: {
          file: file.path,
          startLine: 1,
          endLine: file.content.split('\n').length
        }
      });
    }

    return { patterns, suggestions };
  }

  /**
   * Detect security issues
   */
  private async detectSecurityIssues(file: CodeFile, ast: SyntaxNode): Promise<{patterns: DetectedPattern[], suggestions: QualitySuggestion[]}> {
    const patterns: DetectedPattern[] = [];
    const suggestions: QualitySuggestion[] = [];

    // SQL injection vulnerabilities
    const sqlInjection = this.detectSQLInjection(file, ast);
    if (sqlInjection.length > 0) {
      patterns.push({
        id: this.generateId(),
        name: 'Potential SQL Injection',
        type: PatternType.SECURITY,
        description: 'Code may be vulnerable to SQL injection attacks due to string concatenation in queries',
        location: {
          files: [file.path],
          startLine: sqlInjection[0].line,
          endLine: sqlInjection[0].line + 2
        },
        confidence: 0.8,
        benefits: [],
        drawbacks: [
          'Critical security vulnerability',
          'Data breach risk',
          'Unauthorized data access',
          'Potential system compromise'
        ],
        examples: [
          'String concatenation in SQL queries',
          'Dynamic query building without parameterization',
          'User input directly embedded in queries',
          'Template literals with unsanitized variables'
        ]
      });

      suggestions.push({
        type: 'security',
        priority: 'critical',
        title: 'Use parameterized queries',
        description: 'Replace string concatenation with parameterized queries or prepared statements to prevent SQL injection.',
        location: {
          file: file.path,
          startLine: sqlInjection[0].line,
          endLine: sqlInjection[0].line + 2
        }
      });
    }

    // XSS vulnerabilities
    const xssIssues = this.detectXSS(file, ast);
    if (xssIssues.length > 0) {
      patterns.push({
        id: this.generateId(),
        name: 'Potential XSS Vulnerability',
        type: PatternType.SECURITY,
        description: 'Code may be vulnerable to Cross-Site Scripting (XSS) attacks due to unsanitized output',
        location: {
          files: [file.path],
          startLine: xssIssues[0].line,
          endLine: xssIssues[0].line + 2
        },
        confidence: 0.7,
        benefits: [],
        drawbacks: [
          'Cross-site scripting attacks possible',
          'User session hijacking risk',
          'Malicious script execution',
          'Data theft potential'
        ],
        examples: [
          'innerHTML with unsanitized user input',
          'Template rendering without escaping',
          'Dynamic script generation from user data',
          'Unsafe HTML construction'
        ]
      });

      suggestions.push({
        type: 'security',
        priority: 'critical',
        title: 'Sanitize user input and escape output',
        description: 'Use proper input validation, output escaping, and Content Security Policy to prevent XSS attacks.',
        location: {
          file: file.path,
          startLine: xssIssues[0].line,
          endLine: xssIssues[0].line + 2
        }
      });
    }

    return { patterns, suggestions };
  }

  /**
   * Calculate quality metrics for a file
   */
  private calculateQualityMetrics(file: CodeFile, ast: SyntaxNode, patterns: DetectedPattern[]): QualityMetrics {
    const complexity = this.calculateCyclomaticComplexity(ast);
    const linesOfCode = file.content.split('\n').length;
    const antiPatterns = patterns.filter(p => p.type === PatternType.ANTI_PATTERN).length;
    const securityIssues = patterns.filter(p => p.type === PatternType.SECURITY).length;

    // Normalize metrics to 0-10 scale (higher is better, except for complexity)
    const complexityScore = Math.max(0, 10 - (complexity / 2)); // Invert: lower complexity = higher score
    const maintainabilityScore = Math.max(0, 10 - antiPatterns * 2);
    const readabilityScore = Math.max(0, 10 - (linesOfCode / 50)); // Penalize very long files
    const testabilityScore = complexityScore; // Simpler code is more testable
    const performanceScore = Math.max(0, 10 - patterns.filter(p => p.type === PatternType.PERFORMANCE).length * 3);

    return {
      complexity: Math.round(complexityScore * 10) / 10,
      maintainability: Math.round(maintainabilityScore * 10) / 10,
      readability: Math.round(readabilityScore * 10) / 10,
      testability: Math.round(testabilityScore * 10) / 10,
      performance: Math.round(performanceScore * 10) / 10
    };
  }

  // Helper methods for pattern detection (simplified implementations)

  private detectSRPViolations(file: CodeFile, ast: SyntaxNode): Array<{startLine: number, endLine: number}> {
    const violations: Array<{startLine: number, endLine: number}> = [];

    // Look for classes with many methods or functions with many responsibilities
    const content = file.content;
    const classMatches = content.match(/class\s+\w+[^{]*\{([^}]+)\}/gs);

    if (classMatches) {
      classMatches.forEach((classContent, index) => {
        const methodCount = (classContent.match(/\w+\s*\([^)]*\)\s*\{/g) || []).length;
        if (methodCount > 10) { // Classes with many methods might violate SRP
          violations.push({ startLine: 1, endLine: 50 }); // Simplified line calculation
        }
      });
    }

    return violations;
  }

  private detectOCPViolations(file: CodeFile, ast: SyntaxNode): Array<{startLine: number, endLine: number}> {
    const violations: Array<{startLine: number, endLine: number}> = [];

    // Look for large switch statements or if-else chains
    const content = file.content;
    const switchMatches = content.match(/switch\s*\([^)]+\)\s*\{([^}]+)\}/gs);

    if (switchMatches) {
      switchMatches.forEach(switchContent => {
        const caseCount = (switchContent.match(/case\s+/g) || []).length;
        if (caseCount > 5) { // Large switch statements might violate OCP
          violations.push({ startLine: 1, endLine: 20 });
        }
      });
    }

    return violations;
  }

  private detectDIPViolations(file: CodeFile, ast: SyntaxNode): Array<{startLine: number, endLine: number}> {
    const violations: Array<{startLine: number, endLine: number}> = [];

    // Look for direct instantiation of concrete classes
    const content = file.content;
    if (content.includes('new ') && !content.includes('interface ') && !content.includes('abstract ')) {
      // Simplified check for direct instantiation without interfaces
      violations.push({ startLine: 1, endLine: 10 });
    }

    return violations;
  }

  private calculateCyclomaticComplexity(ast: SyntaxNode): number {
    const content = ast.text || '';

    // Count decision points (simplified)
    const ifCount = (content.match(/\bif\s*\(/g) || []).length;
    const whileCount = (content.match(/\bwhile\s*\(/g) || []).length;
    const forCount = (content.match(/\bfor\s*\(/g) || []).length;
    const switchCount = (content.match(/\bswitch\s*\(/g) || []).length;
    const catchCount = (content.match(/\bcatch\s*\(/g) || []).length;
    const ternaryCount = (content.match(/\?[^:]+:/g) || []).length;

    return 1 + ifCount + whileCount + forCount + switchCount + catchCount + ternaryCount;
  }

  private calculateMaxNestingDepth(ast: SyntaxNode): number {
    const content = ast.text || '';
    let maxDepth = 0;
    let currentDepth = 0;

    for (let i = 0; i < content.length; i++) {
      if (content[i] === '{') {
        currentDepth++;
        maxDepth = Math.max(maxDepth, currentDepth);
      } else if (content[i] === '}') {
        currentDepth--;
      }
    }

    return maxDepth;
  }

  private calculateLongestFunction(ast: SyntaxNode): number {
    const content = ast.text || '';
    const functionMatches = content.match(/function[^{]*\{[^}]*\}/gs);

    if (!functionMatches) return 0;

    return Math.max(...functionMatches.map(fn => fn.split('\n').length));
  }

  private detectNPlusOneQueries(file: CodeFile, ast: SyntaxNode): Array<{line: number}> {
    const issues: Array<{line: number}> = [];
    const lines = file.content.split('\n');

    lines.forEach((line, index) => {
      if (line.includes('for') && (line.includes('await') || line.includes('query') || line.includes('find'))) {
        issues.push({ line: index + 1 });
      }
    });

    return issues;
  }

  private detectInefficientLoops(file: CodeFile, ast: SyntaxNode): Array<{line: number}> {
    const issues: Array<{line: number}> = [];
    const lines = file.content.split('\n');

    lines.forEach((line, index) => {
      if (line.includes('for') && (line.includes('indexOf') || line.includes('includes') || line.includes('+'))) {
        issues.push({ line: index + 1 });
      }
    });

    return issues;
  }

  private detectCodeDuplication(file: CodeFile, ast: SyntaxNode): Array<{line: number, length: number}> {
    const duplicates: Array<{line: number, length: number}> = [];
    const lines = file.content.split('\n');

    // Simple duplicate detection - look for similar consecutive lines
    for (let i = 0; i < lines.length - 3; i++) {
      for (let j = i + 3; j < lines.length - 3; j++) {
        if (lines[i].trim() === lines[j].trim() &&
            lines[i + 1].trim() === lines[j + 1].trim() &&
            lines[i + 2].trim() === lines[j + 2].trim()) {
          duplicates.push({ line: i + 1, length: 3 });
          break;
        }
      }
    }

    return duplicates;
  }

  private detectMagicValues(file: CodeFile, ast: SyntaxNode): Array<{line: number, value: string}> {
    const magicValues: Array<{line: number, value: string}> = [];
    const lines = file.content.split('\n');

    lines.forEach((line, index) => {
      // Look for hardcoded numbers (excluding 0, 1, -1 which are commonly acceptable)
      const numberMatches = line.match(/\b(?!0\b|1\b|-1\b)\d+\b/g);
      if (numberMatches) {
        numberMatches.forEach(match => {
          magicValues.push({ line: index + 1, value: match });
        });
      }
    });

    return magicValues;
  }

  private detectSQLInjection(file: CodeFile, ast: SyntaxNode): Array<{line: number}> {
    const issues: Array<{line: number}> = [];
    const lines = file.content.split('\n');

    lines.forEach((line, index) => {
      if ((line.includes('SELECT') || line.includes('INSERT') || line.includes('UPDATE') || line.includes('DELETE')) &&
          (line.includes('+') || line.includes('${') || line.includes('`'))) {
        issues.push({ line: index + 1 });
      }
    });

    return issues;
  }

  private detectXSS(file: CodeFile, ast: SyntaxNode): Array<{line: number}> {
    const issues: Array<{line: number}> = [];
    const lines = file.content.split('\n');

    lines.forEach((line, index) => {
      if ((line.includes('innerHTML') || line.includes('outerHTML') || line.includes('document.write')) &&
          (line.includes('+') || line.includes('${') || line.includes('`'))) {
        issues.push({ line: index + 1 });
      }
    });

    return issues;
  }

  private generateId(): string {
    return Math.random().toString(36).substr(2, 9);
  }
}
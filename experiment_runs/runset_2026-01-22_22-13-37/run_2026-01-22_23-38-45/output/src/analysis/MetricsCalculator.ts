import Parser from 'tree-sitter';
import { CodeFile, QualityMetrics } from '../types/core.js';

/**
 * Calculates various quality metrics for code files
 *
 * The MetricsCalculator provides quantitative analysis including:
 * - Cyclomatic complexity
 * - Maintainability index
 * - Testability score
 * - Readability assessment
 * - Performance indicators
 *
 * Metrics are normalized to a 0-10 scale for consistency and comparison.
 */
export class MetricsCalculator {

  /**
   * Calculates comprehensive quality metrics for a file
   */
  async calculateMetrics(file: CodeFile, tree: Parser.Tree): Promise<QualityMetrics> {
    const rootNode = tree.rootNode;

    // Calculate individual metrics
    const complexity = this.calculateComplexity(file, rootNode);
    const maintainability = this.calculateMaintainability(file, rootNode);
    const testability = this.calculateTestability(file, rootNode);
    const readability = this.calculateReadability(file, rootNode);
    const performance = this.calculatePerformanceIndicators(file, rootNode);

    return {
      complexity: this.normalizeScore(complexity, 1, 20, true), // Higher complexity = lower score
      maintainability: this.normalizeScore(maintainability, 0, 100, false),
      testability: this.normalizeScore(testability, 0, 100, false),
      readability: this.normalizeScore(readability, 0, 100, false),
      performance: this.normalizeScore(performance, 0, 100, false)
    };
  }

  /**
   * Quick basic metrics calculation for real-time analysis
   */
  async calculateBasicMetrics(file: CodeFile, tree: Parser.Tree): Promise<Partial<QualityMetrics>> {
    const rootNode = tree.rootNode;

    // Only calculate lightweight metrics for real-time feedback
    const complexity = this.calculateBasicComplexity(file, rootNode);
    const readability = this.calculateBasicReadability(file, rootNode);

    return {
      complexity: this.normalizeScore(complexity, 1, 20, true),
      readability: this.normalizeScore(readability, 0, 100, false)
    };
  }

  /**
   * Calculates cyclomatic complexity using control flow analysis
   */
  private calculateComplexity(file: CodeFile, node: Parser.SyntaxNode): number {
    let complexity = 1; // Base complexity

    const complexityNodes = [
      'if_statement',
      'switch_statement',
      'for_statement',
      'for_in_statement',
      'while_statement',
      'do_statement',
      'catch_clause',
      'conditional_expression',
      'logical_expression'
    ];

    this.traverseNodes(node, (current) => {
      if (complexityNodes.includes(current.type)) {
        complexity++;
      }

      // Additional complexity for logical operators
      if (current.type === 'logical_expression') {
        const text = this.getNodeText(current, file.content);
        const andOrCount = (text.match(/&&|\|\|/g) || []).length;
        complexity += andOrCount;
      }

      // Nested conditions add more complexity
      if (current.type === 'if_statement') {
        let depth = this.getNestedDepth(current, 'if_statement');
        if (depth > 1) {
          complexity += Math.floor(depth / 2);
        }
      }
    });

    return complexity;
  }

  /**
   * Simplified complexity calculation for real-time analysis
   */
  private calculateBasicComplexity(file: CodeFile, node: Parser.SyntaxNode): number {
    let complexity = 1;

    const quickComplexityNodes = ['if_statement', 'for_statement', 'while_statement', 'switch_statement'];

    this.traverseNodes(node, (current) => {
      if (quickComplexityNodes.includes(current.type)) {
        complexity++;
      }
    });

    return complexity;
  }

  /**
   * Calculates maintainability index based on various factors
   */
  private calculateMaintainability(file: CodeFile, node: Parser.SyntaxNode): number {
    let score = 100; // Start with perfect score

    // Factor 1: Lines of code (penalize very long files)
    const lineCount = file.content.split('\n').length;
    if (lineCount > 500) score -= 20;
    else if (lineCount > 300) score -= 10;
    else if (lineCount > 200) score -= 5;

    // Factor 2: Function/method length
    const longMethods = this.findLongMethods(file, node);
    score -= longMethods * 5;

    // Factor 3: Class size
    const largeClasses = this.findLargeClasses(file, node);
    score -= largeClasses * 10;

    // Factor 4: Coupling (imports/dependencies)
    const coupling = this.calculateCoupling(file, node);
    score -= Math.max(0, (coupling - 10) * 2);

    // Factor 5: Comment ratio (reward good documentation)
    const commentRatio = this.calculateCommentRatio(file);
    if (commentRatio > 0.15) score += 10;
    else if (commentRatio < 0.05) score -= 10;

    // Factor 6: Nesting depth
    const maxNestingDepth = this.calculateMaxNestingDepth(node);
    if (maxNestingDepth > 5) score -= (maxNestingDepth - 5) * 5;

    return Math.max(0, Math.min(100, score));
  }

  /**
   * Calculates testability score based on code structure
   */
  private calculateTestability(file: CodeFile, node: Parser.SyntaxNode): number {
    let score = 50; // Start with neutral score

    // Factor 1: Public methods (easier to test)
    const publicMethods = this.countPublicMethods(file, node);
    score += Math.min(publicMethods * 2, 20);

    // Factor 2: Constructor complexity (dependency injection friendliness)
    const constructorComplexity = this.calculateConstructorComplexity(file, node);
    score -= constructorComplexity * 3;

    // Factor 3: Static dependencies (harder to mock)
    const staticDependencies = this.countStaticDependencies(file, node);
    score -= staticDependencies * 5;

    // Factor 4: Global state usage
    const globalStateUsage = this.countGlobalStateUsage(file, node);
    score -= globalStateUsage * 4;

    // Factor 5: Pure functions (highly testable)
    const pureFunctions = this.countPureFunctions(file, node);
    score += pureFunctions * 3;

    // Factor 6: Error handling (testable error paths)
    const errorHandling = this.countErrorHandling(file, node);
    score += Math.min(errorHandling * 2, 15);

    return Math.max(0, Math.min(100, score));
  }

  /**
   * Calculates readability score based on code style and structure
   */
  private calculateReadability(file: CodeFile, node: Parser.SyntaxNode): number {
    let score = 70; // Start with reasonable baseline

    // Factor 1: Average line length
    const avgLineLength = this.calculateAverageLineLength(file);
    if (avgLineLength > 120) score -= 15;
    else if (avgLineLength > 100) score -= 10;
    else if (avgLineLength > 80) score -= 5;
    else if (avgLineLength < 40) score += 5;

    // Factor 2: Consistent naming conventions
    const namingConsistency = this.calculateNamingConsistency(file, node);
    score += namingConsistency * 10;

    // Factor 3: Method/function naming descriptiveness
    const descriptiveNaming = this.calculateDescriptiveNaming(file, node);
    score += descriptiveNaming * 15;

    // Factor 4: Comment quality and quantity
    const commentQuality = this.calculateCommentQuality(file);
    score += commentQuality * 10;

    // Factor 5: Code formatting consistency
    const formattingScore = this.calculateFormattingConsistency(file);
    score += formattingScore * 10;

    // Factor 6: Avoid deeply nested code
    const nestingPenalty = Math.min(this.calculateMaxNestingDepth(node) - 3, 0) * -5;
    score += nestingPenalty;

    return Math.max(0, Math.min(100, score));
  }

  /**
   * Simplified readability calculation for real-time analysis
   */
  private calculateBasicReadability(file: CodeFile, node: Parser.SyntaxNode): number {
    let score = 70;

    const avgLineLength = this.calculateAverageLineLength(file);
    if (avgLineLength > 120) score -= 15;
    else if (avgLineLength < 40) score += 5;

    const maxNesting = this.calculateMaxNestingDepth(node);
    if (maxNesting > 5) score -= (maxNesting - 5) * 5;

    return Math.max(0, Math.min(100, score));
  }

  /**
   * Calculates performance indicators based on potential bottlenecks
   */
  private calculatePerformanceIndicators(file: CodeFile, node: Parser.SyntaxNode): number {
    let score = 80; // Start with good baseline

    // Factor 1: Nested loops (O(n²) or worse complexity)
    const nestedLoops = this.countNestedLoops(file, node);
    score -= nestedLoops * 15;

    // Factor 2: String concatenation in loops
    const stringConcatInLoops = this.countStringConcatInLoops(file, node);
    score -= stringConcatInLoops * 10;

    // Factor 3: Inefficient array operations
    const inefficientArrayOps = this.countInefficientArrayOperations(file, node);
    score -= inefficientArrayOps * 8;

    // Factor 4: Synchronous I/O operations
    const syncIOOps = this.countSynchronousIOOperations(file, node);
    score -= syncIOOps * 12;

    // Factor 5: Memory allocation patterns
    const memoryIssues = this.identifyMemoryAllocationIssues(file, node);
    score -= memoryIssues * 7;

    // Factor 6: Database query patterns
    const queryIssues = this.identifyQueryPerformanceIssues(file, node);
    score -= queryIssues * 10;

    return Math.max(0, Math.min(100, score));
  }

  // Helper methods for metric calculations
  private findLongMethods(file: CodeFile, node: Parser.SyntaxNode): number {
    let count = 0;
    this.traverseNodes(node, (current) => {
      if (current.type === 'method_definition' || current.type === 'function_declaration') {
        const lineCount = current.endPosition.row - current.startPosition.row;
        if (lineCount > 30) count++;
      }
    });
    return count;
  }

  private findLargeClasses(file: CodeFile, node: Parser.SyntaxNode): number {
    let count = 0;
    this.traverseNodes(node, (current) => {
      if (current.type === 'class_declaration') {
        const lineCount = current.endPosition.row - current.startPosition.row;
        if (lineCount > 200) count++;
      }
    });
    return count;
  }

  private calculateCoupling(file: CodeFile, node: Parser.SyntaxNode): number {
    let imports = 0;
    this.traverseNodes(node, (current) => {
      if (current.type === 'import_statement' || current.type === 'import_declaration') {
        imports++;
      }
    });
    return imports;
  }

  private calculateCommentRatio(file: CodeFile): number {
    const lines = file.content.split('\n');
    let commentLines = 0;
    let codeLines = 0;

    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed === '') continue;

      if (trimmed.startsWith('//') || trimmed.startsWith('/*') || trimmed.startsWith('*')) {
        commentLines++;
      } else {
        codeLines++;
      }
    }

    return codeLines === 0 ? 0 : commentLines / (commentLines + codeLines);
  }

  private calculateMaxNestingDepth(node: Parser.SyntaxNode): number {
    let maxDepth = 0;

    const calculateDepth = (current: Parser.SyntaxNode, depth: number): void => {
      maxDepth = Math.max(maxDepth, depth);

      for (const child of current.children) {
        const newDepth = this.isNestingNode(child) ? depth + 1 : depth;
        calculateDepth(child, newDepth);
      }
    };

    calculateDepth(node, 0);
    return maxDepth;
  }

  private isNestingNode(node: Parser.SyntaxNode): boolean {
    const nestingTypes = [
      'if_statement', 'for_statement', 'while_statement', 'do_statement',
      'switch_statement', 'try_statement', 'function_declaration', 'method_definition'
    ];
    return nestingTypes.includes(node.type);
  }

  private countPublicMethods(file: CodeFile, node: Parser.SyntaxNode): number {
    let count = 0;
    this.traverseNodes(node, (current) => {
      if (current.type === 'method_definition') {
        const text = this.getNodeText(current, file.content);
        if (!text.includes('private') && !text.includes('protected')) {
          count++;
        }
      }
    });
    return count;
  }

  private calculateConstructorComplexity(file: CodeFile, node: Parser.SyntaxNode): number {
    let complexity = 0;
    this.traverseNodes(node, (current) => {
      if (current.type === 'constructor_definition' ||
          (current.type === 'method_definition' && this.getNodeText(current, file.content).includes('constructor'))) {
        complexity += this.calculateBasicComplexity(file, current);
      }
    });
    return complexity;
  }

  private countStaticDependencies(file: CodeFile, node: Parser.SyntaxNode): number {
    let count = 0;
    const content = file.content;

    // Look for static method calls and global dependencies
    const staticCallPattern = /\w+\.\w+\(/g;
    const matches = content.match(staticCallPattern) || [];
    count += matches.length;

    return Math.min(count, 20); // Cap to prevent skewing
  }

  private countGlobalStateUsage(file: CodeFile, node: Parser.SyntaxNode): number {
    let count = 0;
    const content = file.content.toLowerCase();

    // Look for global variables and state patterns
    if (content.includes('global.') || content.includes('window.') || content.includes('process.env')) {
      count += 2;
    }

    return count;
  }

  private countPureFunctions(file: CodeFile, node: Parser.SyntaxNode): number {
    let count = 0;

    this.traverseNodes(node, (current) => {
      if (current.type === 'function_declaration' || current.type === 'arrow_function') {
        const text = this.getNodeText(current, file.content);

        // Simple heuristic: functions that return values and don't modify external state
        if (text.includes('return') && !text.includes('this.') && !text.includes('=')) {
          count++;
        }
      }
    });

    return count;
  }

  private countErrorHandling(file: CodeFile, node: Parser.SyntaxNode): number {
    let count = 0;
    this.traverseNodes(node, (current) => {
      if (current.type === 'try_statement' || current.type === 'catch_clause') {
        count++;
      }
    });
    return count;
  }

  private calculateAverageLineLength(file: CodeFile): number {
    const lines = file.content.split('\n').filter(line => line.trim() !== '');
    if (lines.length === 0) return 0;

    const totalLength = lines.reduce((sum, line) => sum + line.length, 0);
    return totalLength / lines.length;
  }

  private calculateNamingConsistency(file: CodeFile, node: Parser.SyntaxNode): number {
    // Simplified implementation - check for consistent naming conventions
    const content = file.content;

    let camelCaseCount = 0;
    let snake_caseCount = 0;
    let PascalCaseCount = 0;

    const identifiers = content.match(/[a-zA-Z_$][a-zA-Z0-9_$]*/g) || [];

    for (const id of identifiers) {
      if (/^[a-z][a-zA-Z0-9]*$/.test(id)) camelCaseCount++;
      else if (/^[a-z][a-z0-9_]*$/.test(id)) snake_caseCount++;
      else if (/^[A-Z][a-zA-Z0-9]*$/.test(id)) PascalCaseCount++;
    }

    const total = camelCaseCount + snake_caseCount + PascalCaseCount;
    if (total === 0) return 0;

    const dominant = Math.max(camelCaseCount, snake_caseCount, PascalCaseCount);
    return dominant / total;
  }

  private calculateDescriptiveNaming(file: CodeFile, node: Parser.SyntaxNode): number {
    let descriptiveCount = 0;
    let totalCount = 0;

    this.traverseNodes(node, (current) => {
      if (current.type === 'function_declaration' || current.type === 'method_definition') {
        const text = this.getNodeText(current, file.content);
        const nameMatch = text.match(/(?:function\s+|def\s+)(\w+)/);

        if (nameMatch) {
          totalCount++;
          const name = nameMatch[1];

          // Consider names descriptive if they're longer than 3 chars and not generic
          if (name.length > 3 && !['func', 'method', 'test', 'temp'].includes(name.toLowerCase())) {
            descriptiveCount++;
          }
        }
      }
    });

    return totalCount === 0 ? 0 : descriptiveCount / totalCount;
  }

  private calculateCommentQuality(file: CodeFile): number {
    const lines = file.content.split('\n');
    let qualityComments = 0;
    let totalComments = 0;

    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith('//') || trimmed.startsWith('/*') || trimmed.startsWith('*')) {
        totalComments++;

        // Quality heuristics: longer comments, contains explanation words
        if (trimmed.length > 20 && /why|because|note|todo|fixme|explain|purpose/.test(trimmed.toLowerCase())) {
          qualityComments++;
        }
      }
    }

    return totalComments === 0 ? 0 : qualityComments / totalComments;
  }

  private calculateFormattingConsistency(file: CodeFile): number {
    // Simplified formatting consistency check
    const lines = file.content.split('\n');
    let consistentIndentation = true;
    let indentationType = '';

    for (const line of lines) {
      if (line.length === 0) continue;

      const leadingWhitespace = line.match(/^(\s*)/)?.[1] || '';
      if (leadingWhitespace.length > 0) {
        const hasSpaces = leadingWhitespace.includes(' ');
        const hasTabs = leadingWhitespace.includes('\t');

        if (indentationType === '') {
          indentationType = hasSpaces ? 'spaces' : 'tabs';
        } else if ((indentationType === 'spaces' && hasTabs) || (indentationType === 'tabs' && hasSpaces)) {
          consistentIndentation = false;
          break;
        }
      }
    }

    return consistentIndentation ? 1 : 0;
  }

  private countNestedLoops(file: CodeFile, node: Parser.SyntaxNode): number {
    let count = 0;

    this.traverseNodes(node, (current) => {
      if (this.isLoopNode(current)) {
        // Check if this loop contains another loop
        this.traverseNodes(current, (inner) => {
          if (inner !== current && this.isLoopNode(inner)) {
            count++;
          }
        });
      }
    });

    return count;
  }

  private isLoopNode(node: Parser.SyntaxNode): boolean {
    return ['for_statement', 'while_statement', 'do_statement', 'for_in_statement'].includes(node.type);
  }

  // Placeholder implementations for performance analysis methods
  private countStringConcatInLoops(file: CodeFile, node: Parser.SyntaxNode): number { return 0; }
  private countInefficientArrayOperations(file: CodeFile, node: Parser.SyntaxNode): number { return 0; }
  private countSynchronousIOOperations(file: CodeFile, node: Parser.SyntaxNode): number { return 0; }
  private identifyMemoryAllocationIssues(file: CodeFile, node: Parser.SyntaxNode): number { return 0; }
  private identifyQueryPerformanceIssues(file: CodeFile, node: Parser.SyntaxNode): number { return 0; }

  // Utility methods
  private getNestedDepth(node: Parser.SyntaxNode, nodeType: string, depth: number = 0): number {
    let maxDepth = depth;

    for (const child of node.children) {
      if (child.type === nodeType) {
        maxDepth = Math.max(maxDepth, this.getNestedDepth(child, nodeType, depth + 1));
      } else {
        maxDepth = Math.max(maxDepth, this.getNestedDepth(child, nodeType, depth));
      }
    }

    return maxDepth;
  }

  private traverseNodes(node: Parser.SyntaxNode, callback: (node: Parser.SyntaxNode) => void): void {
    callback(node);
    for (const child of node.children) {
      this.traverseNodes(child, callback);
    }
  }

  private getNodeText(node: Parser.SyntaxNode, content: string): string {
    return content.slice(node.startIndex, node.endIndex);
  }

  /**
   * Normalizes a score to a 0-10 scale
   * @param value The raw value to normalize
   * @param min The minimum expected value
   * @param max The maximum expected value
   * @param invert Whether higher values should result in lower scores (for complexity, etc.)
   */
  private normalizeScore(value: number, min: number, max: number, invert: boolean = false): number {
    // Clamp value to range
    const clamped = Math.max(min, Math.min(max, value));

    // Normalize to 0-1 scale
    let normalized = (clamped - min) / (max - min);

    // Invert if needed (for metrics where lower is better)
    if (invert) {
      normalized = 1 - normalized;
    }

    // Scale to 0-10 and round to 1 decimal place
    return Math.round(normalized * 100) / 10;
  }
}
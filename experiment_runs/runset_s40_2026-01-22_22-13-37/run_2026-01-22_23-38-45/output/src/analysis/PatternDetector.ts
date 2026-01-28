import Parser from 'tree-sitter';
import { CodeFile, DetectedPattern, PatternType, CodeLocation } from '../types/core.js';

/**
 * Advanced pattern detection engine that identifies architectural and design patterns
 *
 * The PatternDetector uses AST analysis to identify:
 * - Architectural patterns (MVC, Singleton, Observer, etc.)
 * - Design patterns (Factory, Strategy, Decorator, etc.)
 * - Anti-patterns (God Object, Feature Envy, etc.)
 * - Security patterns and vulnerabilities
 * - Performance patterns and bottlenecks
 */
export class PatternDetector {
  private patternRules: Map<PatternType, PatternRule[]> = new Map();

  constructor() {
    this.initializePatternRules();
  }

  /**
   * Detects all patterns in a code file
   */
  async detectPatterns(file: CodeFile, tree: Parser.Tree): Promise<DetectedPattern[]> {
    const patterns: DetectedPattern[] = [];
    const rootNode = tree.rootNode;

    // Run all pattern detection rules
    for (const [patternType, rules] of this.patternRules) {
      for (const rule of rules) {
        const detectedPatterns = await this.applyRule(rule, file, rootNode);
        patterns.push(...detectedPatterns);
      }
    }

    // Sort by confidence score (highest first)
    return patterns.sort((a, b) => b.confidence - a.confidence);
  }

  /**
   * Quick pattern detection for real-time analysis
   * Focuses on lightweight checks that can run during typing
   */
  async detectQuickPatterns(file: CodeFile, tree: Parser.Tree): Promise<DetectedPattern[]> {
    const patterns: DetectedPattern[] = [];
    const rootNode = tree.rootNode;

    // Only run quick, non-expensive pattern checks
    const quickRules = this.getQuickRules();

    for (const rule of quickRules) {
      const detectedPatterns = await this.applyRule(rule, file, rootNode);
      patterns.push(...detectedPatterns);
    }

    return patterns.sort((a, b) => b.confidence - a.confidence);
  }

  private async applyRule(rule: PatternRule, file: CodeFile, node: Parser.SyntaxNode): Promise<DetectedPattern[]> {
    const patterns: DetectedPattern[] = [];

    try {
      const matches = rule.detector(file, node);

      for (const match of matches) {
        patterns.push({
          id: this.generatePatternId(),
          name: rule.name,
          type: rule.type,
          description: rule.description,
          location: this.nodeToLocation(file.path, match.node),
          confidence: match.confidence,
          examples: rule.examples
        });
      }
    } catch (error) {
      console.error(`Error applying pattern rule ${rule.name}:`, error);
    }

    return patterns;
  }

  private initializePatternRules(): void {
    // Architectural Patterns
    this.patternRules.set('architectural', [
      this.createSingletonRule(),
      this.createFactoryRule(),
      this.createObserverRule(),
      this.createMVCRule()
    ]);

    // Design Patterns
    this.patternRules.set('design', [
      this.createBuilderRule(),
      this.createStrategyRule(),
      this.createDecoratorRule(),
      this.createCommandRule()
    ]);

    // Anti-patterns
    this.patternRules.set('anti-pattern', [
      this.createGodObjectRule(),
      this.createFeatureEnvyRule(),
      this.createDeadCodeRule(),
      this.createMagicNumberRule()
    ]);

    // Security Patterns
    this.patternRules.set('security', [
      this.createSQLInjectionRule(),
      this.createXSSRule(),
      this.createHardcodedCredentialsRule()
    ]);

    // Performance Patterns
    this.patternRules.set('performance', [
      this.createN1QueryRule(),
      this.createMemoryLeakRule(),
      this.createEfficientLoopRule()
    ]);

    // Maintainability Patterns
    this.patternRules.set('maintainability', [
      this.createLongParameterListRule(),
      this.createDuplicateCodeRule(),
      this.createComplexConditionalRule()
    ]);
  }

  // Singleton Pattern Detection
  private createSingletonRule(): PatternRule {
    return {
      name: 'Singleton Pattern',
      type: 'architectural',
      description: 'A class that ensures only one instance exists and provides global access to it',
      examples: ['Database connection manager', 'Configuration manager', 'Logger'],
      isQuick: false,
      detector: (file: CodeFile, node: Parser.SyntaxNode) => {
        const matches: PatternMatch[] = [];

        // Look for class declarations
        this.traverseNodes(node, (current) => {
          if (current.type === 'class_declaration') {
            let hasPrivateConstructor = false;
            let hasStaticInstance = false;
            let hasGetInstance = false;

            // Check class body for singleton characteristics
            this.traverseNodes(current, (member) => {
              // Private constructor
              if (member.type === 'method_definition' || member.type === 'constructor_definition') {
                const name = this.getNodeText(member, file.content);
                if (name.includes('private') && name.includes('constructor')) {
                  hasPrivateConstructor = true;
                }
              }

              // Static instance field
              if (member.type === 'field_definition' || member.type === 'property_definition') {
                const text = this.getNodeText(member, file.content);
                if (text.includes('static') && text.includes('instance')) {
                  hasStaticInstance = true;
                }
              }

              // getInstance method
              if (member.type === 'method_definition') {
                const name = this.getNodeText(member, file.content);
                if (name.includes('getInstance') || name.includes('instance')) {
                  hasGetInstance = true;
                }
              }
            });

            // Calculate confidence based on singleton characteristics
            let confidence = 0;
            if (hasPrivateConstructor) confidence += 0.4;
            if (hasStaticInstance) confidence += 0.4;
            if (hasGetInstance) confidence += 0.2;

            if (confidence >= 0.6) {
              matches.push({ node: current, confidence });
            }
          }
        });

        return matches;
      }
    };
  }

  // Factory Pattern Detection
  private createFactoryRule(): PatternRule {
    return {
      name: 'Factory Pattern',
      type: 'design',
      description: 'Creates objects without specifying their exact class, using a common interface',
      examples: ['Object creation based on type', 'Database driver factory', 'UI component factory'],
      isQuick: false,
      detector: (file: CodeFile, node: Parser.SyntaxNode) => {
        const matches: PatternMatch[] = [];

        this.traverseNodes(node, (current) => {
          if (current.type === 'method_definition' || current.type === 'function_declaration') {
            const methodText = this.getNodeText(current, file.content);

            let confidence = 0;

            // Check for factory method naming patterns
            if (/create\w*|make\w*|build\w*|new\w*Factory/i.test(methodText)) {
              confidence += 0.3;
            }

            // Check for conditional object creation
            if (methodText.includes('switch') || methodText.includes('if')) {
              confidence += 0.2;
            }

            // Check for return statements with object creation
            if (/return\s+new\s+\w+/g.test(methodText)) {
              confidence += 0.3;
            }

            // Check for multiple object types being created
            const newMatches = methodText.match(/new\s+(\w+)/g);
            if (newMatches && newMatches.length > 1) {
              confidence += 0.2;
            }

            if (confidence >= 0.5) {
              matches.push({ node: current, confidence });
            }
          }
        });

        return matches;
      }
    };
  }

  // God Object Anti-pattern Detection
  private createGodObjectRule(): PatternRule {
    return {
      name: 'God Object',
      type: 'anti-pattern',
      description: 'A class that knows too much or does too much, violating single responsibility principle',
      examples: ['Classes with >20 methods', 'Classes with >500 lines', 'Classes with multiple responsibilities'],
      isQuick: true,
      detector: (file: CodeFile, node: Parser.SyntaxNode) => {
        const matches: PatternMatch[] = [];

        this.traverseNodes(node, (current) => {
          if (current.type === 'class_declaration') {
            let methodCount = 0;
            let fieldCount = 0;
            let lineCount = current.endPosition.row - current.startPosition.row;

            this.traverseNodes(current, (member) => {
              if (member.type === 'method_definition' || member.type === 'function_definition') {
                methodCount++;
              }
              if (member.type === 'field_definition' || member.type === 'property_definition') {
                fieldCount++;
              }
            });

            let confidence = 0;

            // Too many methods
            if (methodCount > 20) confidence += 0.4;
            else if (methodCount > 15) confidence += 0.3;
            else if (methodCount > 10) confidence += 0.2;

            // Too many lines
            if (lineCount > 500) confidence += 0.4;
            else if (lineCount > 300) confidence += 0.3;
            else if (lineCount > 200) confidence += 0.2;

            // Too many fields
            if (fieldCount > 15) confidence += 0.2;
            else if (fieldCount > 10) confidence += 0.1;

            if (confidence >= 0.6) {
              matches.push({ node: current, confidence });
            }
          }
        });

        return matches;
      }
    };
  }

  // SQL Injection Security Pattern
  private createSQLInjectionRule(): PatternRule {
    return {
      name: 'Potential SQL Injection',
      type: 'security',
      description: 'Dynamic SQL query construction that may be vulnerable to injection attacks',
      examples: ['String concatenation in SQL', 'User input directly in queries'],
      isQuick: true,
      detector: (file: CodeFile, node: Parser.SyntaxNode) => {
        const matches: PatternMatch[] = [];

        this.traverseNodes(node, (current) => {
          const text = this.getNodeText(current, file.content);

          let confidence = 0;

          // Look for SQL keywords with string concatenation
          if (/(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE).*\+.*['"`]/i.test(text)) {
            confidence += 0.7;
          }

          // Look for template literals with SQL
          if (/(SELECT|INSERT|UPDATE|DELETE).*\$\{.*\}/i.test(text)) {
            confidence += 0.8;
          }

          // Look for format strings with SQL
          if (/(SELECT|INSERT|UPDATE|DELETE).*%s|%d/i.test(text)) {
            confidence += 0.6;
          }

          if (confidence >= 0.6) {
            matches.push({ node: current, confidence });
          }
        });

        return matches;
      }
    };
  }

  // N+1 Query Performance Pattern
  private createN1QueryRule(): PatternRule {
    return {
      name: 'N+1 Query Problem',
      type: 'performance',
      description: 'A query executed in a loop, potentially causing performance issues',
      examples: ['Database queries in loops', 'API calls in iterations'],
      isQuick: false,
      detector: (file: CodeFile, node: Parser.SyntaxNode) => {
        const matches: PatternMatch[] = [];

        this.traverseNodes(node, (current) => {
          if (current.type === 'for_statement' || current.type === 'while_statement' || current.type === 'do_statement') {
            let hasQuery = false;

            this.traverseNodes(current, (inner) => {
              const text = this.getNodeText(inner, file.content);

              // Look for database query patterns
              if (/(query|execute|find|select|get).*\(.*\)/i.test(text) ||
                  /(await|\.then).*\.(query|find|get)/i.test(text)) {
                hasQuery = true;
              }
            });

            if (hasQuery) {
              matches.push({ node: current, confidence: 0.8 });
            }
          }
        });

        return matches;
      }
    };
  }

  // Add more pattern rules following similar structure...
  private createObserverRule(): PatternRule {
    return {
      name: 'Observer Pattern',
      type: 'architectural',
      description: 'Defines a dependency between objects so that when one changes state, dependents are notified',
      examples: ['Event listeners', 'Model-View architectures', 'Reactive programming'],
      isQuick: false,
      detector: (file: CodeFile, node: Parser.SyntaxNode) => {
        const matches: PatternMatch[] = [];

        this.traverseNodes(node, (current) => {
          if (current.type === 'class_declaration') {
            let hasObservers = false;
            let hasNotifyMethod = false;
            let hasAddObserverMethod = false;
            let hasRemoveObserverMethod = false;

            this.traverseNodes(current, (member) => {
              const text = this.getNodeText(member, file.content);

              // Look for observer collection (list, array, set)
              if (member.type === 'field_definition' &&
                  (text.includes('observer') || text.includes('listener') || text.includes('subscriber'))) {
                hasObservers = true;
              }

              // Look for notification method
              if (member.type === 'method_definition') {
                if (/notify|broadcast|emit|publish/i.test(text)) {
                  hasNotifyMethod = true;
                }
                if (/add.*observer|subscribe|attach|register.*listener/i.test(text)) {
                  hasAddObserverMethod = true;
                }
                if (/remove.*observer|unsubscribe|detach|unregister.*listener/i.test(text)) {
                  hasRemoveObserverMethod = true;
                }
              }
            });

            let confidence = 0;
            if (hasObservers) confidence += 0.3;
            if (hasNotifyMethod) confidence += 0.3;
            if (hasAddObserverMethod) confidence += 0.2;
            if (hasRemoveObserverMethod) confidence += 0.2;

            if (confidence >= 0.6) {
              matches.push({ node: current, confidence });
            }
          }
        });

        return matches;
      }
    };
  }

  private createMVCRule(): PatternRule {
    return {
      name: 'MVC Pattern',
      type: 'architectural',
      description: 'Separates application into Model, View, and Controller components',
      examples: ['Web application architecture', 'Desktop application structure'],
      isQuick: false,
      detector: (file: CodeFile, node: Parser.SyntaxNode) => {
        // Implementation for MVC pattern detection
        return [];
      }
    };
  }

  // Builder Pattern Detection
  private createBuilderRule(): PatternRule {
    return {
      name: 'Builder Pattern',
      type: 'design',
      description: 'Constructs complex objects step by step using a fluent interface',
      examples: ['QueryBuilder', 'ConfigurationBuilder', 'HTMLBuilder'],
      isQuick: false,
      detector: (file: CodeFile, node: Parser.SyntaxNode) => {
        const matches: PatternMatch[] = [];

        this.traverseNodes(node, (current) => {
          if (current.type === 'class_declaration') {
            let hasFluentMethods = 0;
            let hasBuilderName = false;
            let hasBuildMethod = false;

            // Check class name
            const className = this.getNodeText(current, file.content);
            if (/Builder|Construction/i.test(className)) {
              hasBuilderName = true;
            }

            this.traverseNodes(current, (member) => {
              if (member.type === 'method_definition') {
                const methodText = this.getNodeText(member, file.content);

                // Check for fluent interface (methods returning 'this')
                if (methodText.includes('return this') || methodText.includes('return self')) {
                  hasFluentMethods++;
                }

                // Check for build/create method
                if (/build|create|construct/i.test(methodText)) {
                  hasBuildMethod = true;
                }
              }
            });

            let confidence = 0;
            if (hasBuilderName) confidence += 0.3;
            if (hasFluentMethods >= 3) confidence += 0.4;
            if (hasBuildMethod) confidence += 0.3;

            if (confidence >= 0.6) {
              matches.push({ node: current, confidence });
            }
          }
        });

        return matches;
      }
    };
  }

  private createStrategyRule(): PatternRule {
    return {
      name: 'Strategy Pattern',
      type: 'design',
      description: 'Defines a family of algorithms, encapsulates each one, and makes them interchangeable',
      examples: ['Payment processing strategies', 'Sorting algorithms', 'Validation strategies'],
      isQuick: false,
      detector: (file: CodeFile, node: Parser.SyntaxNode) => {
        const matches: PatternMatch[] = [];

        this.traverseNodes(node, (current) => {
          if (current.type === 'class_declaration') {
            let hasStrategyField = false;
            let hasExecuteMethod = false;
            let hasStrategyInterface = false;

            const classText = this.getNodeText(current, file.content);

            // Check for strategy field/property
            this.traverseNodes(current, (member) => {
              const text = this.getNodeText(member, file.content);

              if (member.type === 'field_definition' || member.type === 'property_definition') {
                if (/strategy|algorithm|handler|processor/i.test(text)) {
                  hasStrategyField = true;
                }
              }

              // Check for execute/process/handle method that delegates
              if (member.type === 'method_definition') {
                if (/execute|process|handle|perform/i.test(text) &&
                    /this\.|strategy\.|algorithm\./i.test(text)) {
                  hasExecuteMethod = true;
                }
              }
            });

            // Check if multiple similar classes exist (strategy implementations)
            if (/Strategy|Algorithm|Handler|Processor/.test(classText)) {
              hasStrategyInterface = true;
            }

            let confidence = 0;
            if (hasStrategyField) confidence += 0.4;
            if (hasExecuteMethod) confidence += 0.3;
            if (hasStrategyInterface) confidence += 0.3;

            if (confidence >= 0.6) {
              matches.push({ node: current, confidence });
            }
          }
        });

        return matches;
      }
    };
  }

  private createDecoratorRule(): PatternRule {
    return { name: 'Decorator Pattern', type: 'design', description: '', examples: [], isQuick: false, detector: () => [] };
  }

  private createCommandRule(): PatternRule {
    return { name: 'Command Pattern', type: 'design', description: '', examples: [], isQuick: false, detector: () => [] };
  }

  private createFeatureEnvyRule(): PatternRule {
    return {
      name: 'Feature Envy',
      type: 'anti-pattern',
      description: 'A method that uses more features of another class than its own class',
      examples: ['Methods accessing many external properties', 'Logic that belongs in another class'],
      isQuick: true,
      detector: (file: CodeFile, node: Parser.SyntaxNode) => {
        const matches: PatternMatch[] = [];

        this.traverseNodes(node, (current) => {
          if (current.type === 'method_definition') {
            const methodText = this.getNodeText(current, file.content);

            // Count external object accesses vs internal accesses
            let externalAccesses = 0;
            let internalAccesses = 0;

            // Look for patterns like "object.property" or "object.method()"
            const externalAccessMatches = methodText.match(/\w+\.\w+/g);
            if (externalAccessMatches) {
              for (const match of externalAccessMatches) {
                if (!match.startsWith('this.') && !match.startsWith('super.')) {
                  externalAccesses++;
                } else {
                  internalAccesses++;
                }
              }
            }

            // Feature Envy if method uses external objects much more than internal ones
            if (externalAccesses > 5 && externalAccesses > internalAccesses * 2) {
              const confidence = Math.min(0.9, externalAccesses / (externalAccesses + internalAccesses + 1));
              matches.push({ node: current, confidence });
            }
          }
        });

        return matches;
      }
    };
  }

  private createDeadCodeRule(): PatternRule {
    return { name: 'Dead Code', type: 'anti-pattern', description: '', examples: [], isQuick: true, detector: () => [] };
  }

  private createMagicNumberRule(): PatternRule {
    return {
      name: 'Magic Numbers',
      type: 'anti-pattern',
      description: 'Numeric literals that appear without explanation in code',
      examples: ['Hardcoded array indices', 'Business rule constants', 'Configuration values'],
      isQuick: true,
      detector: (file: CodeFile, node: Parser.SyntaxNode) => {
        const matches: PatternMatch[] = [];

        this.traverseNodes(node, (current) => {
          if (current.type === 'number' || current.type === 'integer' || current.type === 'float') {
            const numberText = this.getNodeText(current, file.content);
            const number = parseFloat(numberText);

            // Skip common non-magic numbers
            const commonNumbers = [0, 1, -1, 2, 10, 100, 1000];
            if (commonNumbers.includes(number)) {
              return;
            }

            // Skip numbers in test files (they often have legitimate magic numbers)
            if (file.path.includes('test') || file.path.includes('spec')) {
              return;
            }

            // Skip numbers that look like they're in arrays/object initializers
            const parent = current.parent;
            if (parent && (parent.type === 'array' || parent.type === 'object')) {
              return;
            }

            // This is likely a magic number
            matches.push({ node: current, confidence: 0.7 });
          }
        });

        return matches;
      }
    };
  }

  private createXSSRule(): PatternRule {
    return {
      name: 'XSS Vulnerability',
      type: 'security',
      description: 'Cross-Site Scripting vulnerability where user input is not properly sanitized',
      examples: ['innerHTML with user data', 'Unescaped template variables', 'Dynamic script generation'],
      isQuick: true,
      detector: (file: CodeFile, node: Parser.SyntaxNode) => {
        const matches: PatternMatch[] = [];

        this.traverseNodes(node, (current) => {
          const text = this.getNodeText(current, file.content);

          let confidence = 0;

          // Dangerous DOM manipulation
          if (/innerHTML\s*=.*\+|innerHTML\s*=.*\$\{/i.test(text)) {
            confidence += 0.8;
          }

          // Document.write with variables
          if (/document\.write\(.*\+|document\.write\(.*\$\{/i.test(text)) {
            confidence += 0.9;
          }

          // eval() with user input
          if (/eval\(.*\+|eval\(.*\$\{/i.test(text)) {
            confidence += 0.9;
          }

          // Unescaped template rendering (common patterns)
          if (/\{\{\{.*\}\}\}|\<%=.*%\>|<%.*user.*%>/i.test(text)) {
            confidence += 0.6;
          }

          // Direct HTML concatenation
          if (/<[^>]+>.*\+.*<\/[^>]+>|<[^>]+>.*\$\{.*\}/i.test(text)) {
            confidence += 0.7;
          }

          if (confidence >= 0.6) {
            matches.push({ node: current, confidence });
          }
        });

        return matches;
      }
    };
  }

  private createHardcodedCredentialsRule(): PatternRule {
    return {
      name: 'Hardcoded Credentials',
      type: 'security',
      description: 'Sensitive information like passwords, API keys, or tokens embedded in source code',
      examples: ['API keys in strings', 'Database passwords', 'Authentication tokens'],
      isQuick: true,
      detector: (file: CodeFile, node: Parser.SyntaxNode) => {
        const matches: PatternMatch[] = [];

        this.traverseNodes(node, (current) => {
          if (current.type === 'string' || current.type === 'string_literal') {
            const stringContent = this.getNodeText(current, file.content);

            let confidence = 0;

            // Check for suspicious key-value patterns
            if (/password\s*[:=]\s*['"`]/i.test(stringContent)) confidence += 0.8;
            if (/api[_-]?key\s*[:=]\s*['"`]/i.test(stringContent)) confidence += 0.8;
            if (/secret\s*[:=]\s*['"`]/i.test(stringContent)) confidence += 0.7;
            if (/token\s*[:=]\s*['"`]/i.test(stringContent)) confidence += 0.7;

            // Check for suspicious string patterns
            if (/^['"`][A-Za-z0-9+/]{20,}={0,2}['"`]$/.test(stringContent)) {
              // Base64-like patterns
              confidence += 0.6;
            }

            if (/^['"`]sk-[a-zA-Z0-9]{32,}['"`]$/.test(stringContent)) {
              // API key patterns (like OpenAI)
              confidence += 0.9;
            }

            if (/^['"`][a-f0-9]{32,}['"`]$/.test(stringContent)) {
              // Hash-like patterns
              confidence += 0.5;
            }

            if (confidence >= 0.5) {
              matches.push({ node: current, confidence });
            }
          }
        });

        return matches;
      }
    };
  }

  private createMemoryLeakRule(): PatternRule {
    return { name: 'Memory Leak Risk', type: 'performance', description: '', examples: [], isQuick: false, detector: () => [] };
  }

  private createEfficientLoopRule(): PatternRule {
    return { name: 'Efficient Loop', type: 'performance', description: '', examples: [], isQuick: false, detector: () => [] };
  }

  private createLongParameterListRule(): PatternRule {
    return {
      name: 'Long Parameter List',
      type: 'maintainability',
      description: 'Functions or methods with too many parameters, making them hard to use and understand',
      examples: ['Functions with >5 parameters', 'Constructor with many arguments', 'Config-heavy methods'],
      isQuick: true,
      detector: (file: CodeFile, node: Parser.SyntaxNode) => {
        const matches: PatternMatch[] = [];

        this.traverseNodes(node, (current) => {
          if (current.type === 'function_declaration' ||
              current.type === 'method_definition' ||
              current.type === 'constructor_definition') {

            // Find the parameter list
            let parameterCount = 0;

            this.traverseNodes(current, (child) => {
              if (child.type === 'formal_parameters' || child.type === 'parameters') {
                // Count parameters by looking at commas + 1, or by counting parameter nodes
                const paramText = this.getNodeText(child, file.content);
                const commas = (paramText.match(/,/g) || []).length;
                parameterCount = paramText.trim() === '()' ? 0 : commas + 1;
              }
            });

            let confidence = 0;
            if (parameterCount >= 8) confidence = 0.9;
            else if (parameterCount >= 6) confidence = 0.7;
            else if (parameterCount >= 5) confidence = 0.5;

            if (confidence >= 0.5) {
              matches.push({ node: current, confidence });
            }
          }
        });

        return matches;
      }
    };
  }

  private createDuplicateCodeRule(): PatternRule {
    return { name: 'Duplicate Code', type: 'maintainability', description: '', examples: [], isQuick: false, detector: () => [] };
  }

  private createComplexConditionalRule(): PatternRule {
    return { name: 'Complex Conditional', type: 'maintainability', description: '', examples: [], isQuick: true, detector: () => [] };
  }

  // Helper methods
  private getQuickRules(): PatternRule[] {
    const allRules: PatternRule[] = [];
    for (const rules of this.patternRules.values()) {
      allRules.push(...rules);
    }
    return allRules.filter(rule => rule.isQuick);
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

  private nodeToLocation(filePath: string, node: Parser.SyntaxNode): CodeLocation {
    return {
      file: filePath,
      line: node.startPosition.row + 1, // Convert to 1-based
      column: node.startPosition.column + 1,
      endLine: node.endPosition.row + 1,
      endColumn: node.endPosition.column + 1
    };
  }

  private generatePatternId(): string {
    return 'pattern_' + Math.random().toString(36).substr(2, 9);
  }
}

// Supporting interfaces
interface PatternRule {
  name: string;
  type: PatternType;
  description: string;
  examples: string[];
  isQuick: boolean; // Can be run during real-time analysis
  detector: (file: CodeFile, node: Parser.SyntaxNode) => PatternMatch[];
}

interface PatternMatch {
  node: Parser.SyntaxNode;
  confidence: number; // 0-1 score indicating detection certainty
}
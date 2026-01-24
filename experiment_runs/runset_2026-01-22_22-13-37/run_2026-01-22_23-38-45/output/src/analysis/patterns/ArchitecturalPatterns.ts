/**
 * Architectural Patterns Detection Engine
 *
 * This module implements detection algorithms for common architectural patterns
 * in software systems. It analyzes code structure, dependencies, and relationships
 * to identify patterns like MVC, Observer, Singleton, Factory, and more.
 *
 * The detection uses a combination of:
 * - AST structural analysis
 * - Naming convention recognition
 * - Dependency relationship mapping
 * - Behavioral pattern inference
 */

import { SyntaxNode } from 'tree-sitter';
import { DetectedPattern, CodeFile, PatternType, PatternConfidence } from '../../types/core';

export interface PatternDetectionResult {
  patterns: DetectedPattern[];
  confidence: PatternConfidence;
  reasoning: string[];
}

export interface ArchitecturalContext {
  files: CodeFile[];
  astNodes: Map<string, SyntaxNode>;
  dependencies: Map<string, string[]>;
}

/**
 * Core architectural pattern detection engine
 */
export class ArchitecturalPatterns {

  /**
   * Detect all architectural patterns in the given context
   */
  async detectPatterns(context: ArchitecturalContext): Promise<PatternDetectionResult[]> {
    const results: PatternDetectionResult[] = [];

    // Run pattern detection algorithms in parallel for performance
    const detectionPromises = [
      this.detectMVCPattern(context),
      this.detectObserverPattern(context),
      this.detectSingletonPattern(context),
      this.detectFactoryPattern(context),
      this.detectRepositoryPattern(context),
      this.detectDecoratorPattern(context),
      this.detectAdapterPattern(context),
      this.detectCommandPattern(context),
      this.detectBuilderPattern(context),
      this.detectFacadePattern(context)
    ];

    const detectedResults = await Promise.all(detectionPromises);
    results.push(...detectedResults.filter(result => result.patterns.length > 0));

    return results;
  }

  /**
   * Detect Model-View-Controller (MVC) pattern
   *
   * Looks for:
   * - Separation of Model, View, and Controller concerns
   * - Controllers handling user input and coordinating with models/views
   * - Models managing data and business logic
   * - Views handling presentation logic
   */
  private async detectMVCPattern(context: ArchitecturalContext): Promise<PatternDetectionResult> {
    const patterns: DetectedPattern[] = [];
    const reasoning: string[] = [];
    let confidence = 0;

    // Look for MVC directory structure
    const mvcDirectories = this.findMVCDirectoryStructure(context.files);
    if (mvcDirectories.length > 0) {
      confidence += 0.4;
      reasoning.push(`Found MVC directory structure: ${mvcDirectories.join(', ')}`);
    }

    // Analyze file naming conventions
    const mvcFiles = this.analyzeMVCFileNaming(context.files);
    if (mvcFiles.models.length > 0 || mvcFiles.views.length > 0 || mvcFiles.controllers.length > 0) {
      confidence += 0.3;
      reasoning.push(`Found MVC naming conventions: ${mvcFiles.models.length} models, ${mvcFiles.views.length} views, ${mvcFiles.controllers.length} controllers`);
    }

    // Analyze class relationships and dependencies
    const mvcRelationships = await this.analyzeMVCRelationships(context);
    if (mvcRelationships.hasControllerModelInteraction || mvcRelationships.hasControllerViewInteraction) {
      confidence += 0.3;
      reasoning.push('Found MVC interaction patterns between controllers, models, and views');
    }

    if (confidence >= 0.6) {
      patterns.push({
        id: this.generateId(),
        name: 'Model-View-Controller (MVC)',
        type: PatternType.ARCHITECTURAL,
        description: 'Separates application logic into three interconnected components: Model (data), View (presentation), and Controller (user input handling)',
        location: {
          files: context.files.map(f => f.path),
          startLine: 1,
          endLine: 1
        },
        confidence: confidence as PatternConfidence,
        benefits: [
          'Clear separation of concerns',
          'Improved maintainability and testability',
          'Parallel development capability',
          'Reusable components'
        ],
        drawbacks: [
          'Can be overkill for simple applications',
          'May introduce unnecessary complexity',
          'Potential for tight coupling if not implemented carefully'
        ],
        examples: [
          'Web frameworks like Express.js with separate route handlers (controllers), data models, and template engines (views)',
          'Desktop applications with separate business logic, UI components, and event handlers'
        ]
      });
    }

    return { patterns, confidence: confidence as PatternConfidence, reasoning };
  }

  /**
   * Detect Observer pattern
   *
   * Looks for:
   * - Subject/Observable classes with observer lists
   * - Observer interface or classes with update methods
   * - Subscribe/unsubscribe mechanisms
   * - Notification/event dispatching logic
   */
  private async detectObserverPattern(context: ArchitecturalContext): Promise<PatternDetectionResult> {
    const patterns: DetectedPattern[] = [];
    const reasoning: string[] = [];
    let confidence = 0;

    // Look for EventEmitter usage (Node.js)
    const eventEmitterUsage = this.findEventEmitterUsage(context);
    if (eventEmitterUsage.length > 0) {
      confidence += 0.4;
      reasoning.push(`Found EventEmitter usage in ${eventEmitterUsage.length} files`);
    }

    // Look for custom observer implementations
    const customObservers = await this.findCustomObserverPatterns(context);
    if (customObservers.length > 0) {
      confidence += 0.5;
      reasoning.push(`Found custom observer implementations: ${customObservers.map(o => o.className).join(', ')}`);
    }

    // Look for reactive programming patterns (RxJS, etc.)
    const reactivePatterns = this.findReactivePatterns(context);
    if (reactivePatterns.length > 0) {
      confidence += 0.3;
      reasoning.push(`Found reactive programming patterns: ${reactivePatterns.join(', ')}`);
    }

    if (confidence >= 0.6) {
      patterns.push({
        id: this.generateId(),
        name: 'Observer Pattern',
        type: PatternType.BEHAVIORAL,
        description: 'Defines a one-to-many dependency between objects so that when one object changes state, all its dependents are notified automatically',
        location: {
          files: context.files.filter(f =>
            eventEmitterUsage.includes(f.path) ||
            customObservers.some(o => o.filePath === f.path)
          ).map(f => f.path),
          startLine: 1,
          endLine: 1
        },
        confidence: confidence as PatternConfidence,
        benefits: [
          'Loose coupling between subject and observers',
          'Dynamic relationships - observers can be added/removed at runtime',
          'Support for broadcast communication',
          'Open/Closed Principle compliance'
        ],
        drawbacks: [
          'Observers are notified in random order',
          'Memory leaks if observers are not properly unsubscribed',
          'Can create complex chains of updates',
          'Difficult to debug notification chains'
        ],
        examples: [
          'Event handling systems in GUI applications',
          'Model-View architectures where views observe model changes',
          'Publish-subscribe messaging systems',
          'Reactive programming with RxJS Observables'
        ]
      });
    }

    return { patterns, confidence: confidence as PatternConfidence, reasoning };
  }

  /**
   * Detect Singleton pattern
   *
   * Looks for:
   * - Classes with private constructors
   * - Static getInstance() methods
   * - Static instance variables
   * - Module patterns that ensure single instance
   */
  private async detectSingletonPattern(context: ArchitecturalContext): Promise<PatternDetectionResult> {
    const patterns: DetectedPattern[] = [];
    const reasoning: string[] = [];
    let confidence = 0;

    const singletonClasses: Array<{className: string, filePath: string, line: number}> = [];

    for (const [filePath, astNode] of context.astNodes.entries()) {
      const singletons = this.findSingletonClasses(astNode, filePath);
      singletonClasses.push(...singletons);
    }

    if (singletonClasses.length > 0) {
      confidence = Math.min(0.9, 0.3 * singletonClasses.length);
      reasoning.push(`Found ${singletonClasses.length} singleton implementations: ${singletonClasses.map(s => s.className).join(', ')}`);

      patterns.push({
        id: this.generateId(),
        name: 'Singleton Pattern',
        type: PatternType.CREATIONAL,
        description: 'Ensures a class has only one instance and provides global access to that instance',
        location: {
          files: [...new Set(singletonClasses.map(s => s.filePath))],
          startLine: Math.min(...singletonClasses.map(s => s.line)),
          endLine: Math.max(...singletonClasses.map(s => s.line))
        },
        confidence: confidence as PatternConfidence,
        benefits: [
          'Controlled access to sole instance',
          'Reduced namespace pollution',
          'Permits refinement of operations and representation',
          'Can be extended to allow controlled number of instances'
        ],
        drawbacks: [
          'Violates Single Responsibility Principle',
          'Difficult to unit test due to global state',
          'Can mask bad design (overuse of global state)',
          'Creates implicit dependencies',
          'Thread safety concerns in concurrent environments'
        ],
        examples: [
          'Database connection pools',
          'Logger instances',
          'Configuration managers',
          'Cache managers',
          'Application state stores'
        ]
      });
    }

    return { patterns, confidence: confidence as PatternConfidence, reasoning };
  }

  /**
   * Detect Factory pattern (Factory Method and Abstract Factory)
   *
   * Looks for:
   * - Classes with factory methods that return instances of related classes
   * - Abstract factory classes with concrete implementations
   * - Factory functions that create and return objects
   * - Builder-like patterns for object creation
   */
  private async detectFactoryPattern(context: ArchitecturalContext): Promise<PatternDetectionResult> {
    const patterns: DetectedPattern[] = [];
    const reasoning: string[] = [];
    let confidence = 0;

    const factoryMethods: Array<{methodName: string, className: string, filePath: string}> = [];
    const factoryClasses: Array<{className: string, filePath: string}> = [];

    for (const [filePath, astNode] of context.astNodes.entries()) {
      const methods = this.findFactoryMethods(astNode, filePath);
      const classes = this.findFactoryClasses(astNode, filePath);

      factoryMethods.push(...methods);
      factoryClasses.push(...classes);
    }

    if (factoryMethods.length > 0) {
      confidence += Math.min(0.5, 0.1 * factoryMethods.length);
      reasoning.push(`Found ${factoryMethods.length} factory methods: ${factoryMethods.map(f => f.methodName).join(', ')}`);
    }

    if (factoryClasses.length > 0) {
      confidence += Math.min(0.4, 0.15 * factoryClasses.length);
      reasoning.push(`Found ${factoryClasses.length} factory classes: ${factoryClasses.map(f => f.className).join(', ')}`);
    }

    if (confidence >= 0.6) {
      patterns.push({
        id: this.generateId(),
        name: 'Factory Pattern',
        type: PatternType.CREATIONAL,
        description: 'Provides an interface for creating objects without specifying their concrete classes',
        location: {
          files: [...new Set([
            ...factoryMethods.map(f => f.filePath),
            ...factoryClasses.map(f => f.filePath)
          ])],
          startLine: 1,
          endLine: 1
        },
        confidence: confidence as PatternConfidence,
        benefits: [
          'Eliminates need to bind application-specific classes into code',
          'Enables creation of objects without knowing their exact classes',
          'Provides hooks for subclasses to extend object creation',
          'Connects parallel class hierarchies'
        ],
        drawbacks: [
          'Can become complex with many product types',
          'May require creating many subclasses',
          'Code can become more difficult to understand',
          'Can violate Dependency Inversion Principle if not carefully designed'
        ],
        examples: [
          'GUI frameworks creating different types of buttons/widgets',
          'Database drivers creating connections for different databases',
          'File parsers creating appropriate parser instances based on file type',
          'HTTP client factories creating clients with different configurations'
        ]
      });
    }

    return { patterns, confidence: confidence as PatternConfidence, reasoning };
  }

  /**
   * Detect Repository pattern
   *
   * Looks for:
   * - Classes that encapsulate data access logic
   * - Interfaces defining data access contracts
   * - Methods like find, save, delete, update
   * - Separation of domain logic from data access
   */
  private async detectRepositoryPattern(context: ArchitecturalContext): Promise<PatternDetectionResult> {
    const patterns: DetectedPattern[] = [];
    const reasoning: string[] = [];
    let confidence = 0;

    const repositoryClasses: Array<{className: string, filePath: string, methods: string[]}> = [];

    for (const [filePath, astNode] of context.astNodes.entries()) {
      const repos = this.findRepositoryClasses(astNode, filePath);
      repositoryClasses.push(...repos);
    }

    if (repositoryClasses.length > 0) {
      confidence = Math.min(0.9, 0.3 * repositoryClasses.length);
      reasoning.push(`Found ${repositoryClasses.length} repository classes: ${repositoryClasses.map(r => r.className).join(', ')}`);

      const totalMethods = repositoryClasses.reduce((sum, repo) => sum + repo.methods.length, 0);
      reasoning.push(`Repository classes contain ${totalMethods} data access methods`);
    }

    if (confidence >= 0.6) {
      patterns.push({
        id: this.generateId(),
        name: 'Repository Pattern',
        type: PatternType.ARCHITECTURAL,
        description: 'Encapsulates the logic needed to access data sources, centralizing common data access functionality',
        location: {
          files: repositoryClasses.map(r => r.filePath),
          startLine: 1,
          endLine: 1
        },
        confidence: confidence as PatternConfidence,
        benefits: [
          'Centralized data access logic',
          'Testability through interface abstraction',
          'Flexibility to change data sources',
          'Consistent query patterns across application'
        ],
        drawbacks: [
          'Can become a "god class" with too many responsibilities',
          'May add unnecessary abstraction for simple CRUD operations',
          'Can hide performance issues with data access',
          'Potential for tight coupling with specific ORM patterns'
        ],
        examples: [
          'UserRepository class handling all user data operations',
          'ProductRepository with methods like findById, findByCategory, save',
          'Generic Repository<T> interface implemented for different entities',
          'Repository classes wrapping database-specific ORM operations'
        ]
      });
    }

    return { patterns, confidence: confidence as PatternConfidence, reasoning };
  }

  // Additional pattern detection methods...
  private async detectDecoratorPattern(context: ArchitecturalContext): Promise<PatternDetectionResult> {
    // Implementation for Decorator pattern detection
    return { patterns: [], confidence: 0, reasoning: [] };
  }

  private async detectAdapterPattern(context: ArchitecturalContext): Promise<PatternDetectionResult> {
    // Implementation for Adapter pattern detection
    return { patterns: [], confidence: 0, reasoning: [] };
  }

  private async detectCommandPattern(context: ArchitecturalContext): Promise<PatternDetectionResult> {
    // Implementation for Command pattern detection
    return { patterns: [], confidence: 0, reasoning: [] };
  }

  private async detectBuilderPattern(context: ArchitecturalContext): Promise<PatternDetectionResult> {
    // Implementation for Builder pattern detection
    return { patterns: [], confidence: 0, reasoning: [] };
  }

  private async detectFacadePattern(context: ArchitecturalContext): Promise<PatternDetectionResult> {
    // Implementation for Facade pattern detection
    return { patterns: [], confidence: 0, reasoning: [] };
  }

  // Helper methods for pattern detection

  private findMVCDirectoryStructure(files: CodeFile[]): string[] {
    const directories = new Set<string>();
    const mvcKeywords = ['model', 'view', 'controller', 'models', 'views', 'controllers'];

    files.forEach(file => {
      const pathParts = file.path.toLowerCase().split('/');
      pathParts.forEach(part => {
        if (mvcKeywords.includes(part)) {
          directories.add(part);
        }
      });
    });

    return Array.from(directories);
  }

  private analyzeMVCFileNaming(files: CodeFile[]): {models: string[], views: string[], controllers: string[]} {
    const result = { models: [], views: [], controllers: [] };

    files.forEach(file => {
      const fileName = file.path.toLowerCase();
      if (fileName.includes('model') || fileName.endsWith('.model.ts') || fileName.endsWith('.model.js')) {
        result.models.push(file.path);
      }
      if (fileName.includes('view') || fileName.endsWith('.view.ts') || fileName.endsWith('.view.js')) {
        result.views.push(file.path);
      }
      if (fileName.includes('controller') || fileName.endsWith('.controller.ts') || fileName.endsWith('.controller.js')) {
        result.controllers.push(file.path);
      }
    });

    return result;
  }

  private async analyzeMVCRelationships(context: ArchitecturalContext): Promise<{hasControllerModelInteraction: boolean, hasControllerViewInteraction: boolean}> {
    // Simplified relationship analysis - in a real implementation, this would
    // analyze import statements and method calls between MVC components
    const dependencies = context.dependencies;
    let hasControllerModelInteraction = false;
    let hasControllerViewInteraction = false;

    for (const [file, deps] of dependencies.entries()) {
      if (file.toLowerCase().includes('controller')) {
        hasControllerModelInteraction = deps.some(dep => dep.toLowerCase().includes('model'));
        hasControllerViewInteraction = deps.some(dep => dep.toLowerCase().includes('view'));
      }
    }

    return { hasControllerModelInteraction, hasControllerViewInteraction };
  }

  private findEventEmitterUsage(context: ArchitecturalContext): string[] {
    const files: string[] = [];

    context.files.forEach(file => {
      if (file.content.includes('EventEmitter') ||
          file.content.includes('.on(') ||
          file.content.includes('.emit(') ||
          file.content.includes('addEventListener')) {
        files.push(file.path);
      }
    });

    return files;
  }

  private async findCustomObserverPatterns(context: ArchitecturalContext): Promise<Array<{className: string, filePath: string}>> {
    const observers: Array<{className: string, filePath: string}> = [];

    // This would use AST analysis to find classes with observer-like methods
    // Simplified implementation for now
    context.files.forEach(file => {
      const content = file.content;
      if ((content.includes('subscribe') && content.includes('unsubscribe') && content.includes('notify')) ||
          (content.includes('addObserver') && content.includes('removeObserver')) ||
          (content.includes('attach') && content.includes('detach') && content.includes('update'))) {
        // Extract class names from content - this is a simplified approach
        const classMatches = content.match(/class\s+(\w+)/g);
        if (classMatches) {
          classMatches.forEach(match => {
            const className = match.replace('class ', '');
            observers.push({ className, filePath: file.path });
          });
        }
      }
    });

    return observers;
  }

  private findReactivePatterns(context: ArchitecturalContext): string[] {
    const patterns: string[] = [];

    context.files.forEach(file => {
      if (file.content.includes('Observable') || file.content.includes('Subject') ||
          file.content.includes('BehaviorSubject') || file.content.includes('pipe(')) {
        patterns.push('RxJS Observable patterns');
      }
      if (file.content.includes('useState') || file.content.includes('useEffect')) {
        patterns.push('React Hooks reactive patterns');
      }
    });

    return [...new Set(patterns)];
  }

  private findSingletonClasses(astNode: SyntaxNode, filePath: string): Array<{className: string, filePath: string, line: number}> {
    const singletons: Array<{className: string, filePath: string, line: number}> = [];

    // This is a simplified implementation - would need proper AST traversal
    // For now, using regex patterns on the source text
    const sourceText = astNode.text || '';

    // Look for getInstance patterns
    const getInstancePattern = /static\s+getInstance\s*\(\s*\)/g;
    const privateConstructorPattern = /private\s+constructor/g;
    const staticInstancePattern = /private\s+static\s+instance/g;

    if (getInstancePattern.test(sourceText) &&
        (privateConstructorPattern.test(sourceText) || staticInstancePattern.test(sourceText))) {

      // Extract class name
      const classPattern = /class\s+(\w+)/;
      const match = sourceText.match(classPattern);
      if (match) {
        singletons.push({
          className: match[1],
          filePath,
          line: 1 // Would calculate actual line number from AST
        });
      }
    }

    return singletons;
  }

  private findFactoryMethods(astNode: SyntaxNode, filePath: string): Array<{methodName: string, className: string, filePath: string}> {
    const methods: Array<{methodName: string, className: string, filePath: string}> = [];

    // Look for methods with names suggesting factory pattern
    const sourceText = astNode.text || '';
    const factoryMethodPattern = /(create\w*|make\w*|build\w*|new\w*)\s*\([^)]*\)\s*:\s*\w+/g;

    let match;
    while ((match = factoryMethodPattern.exec(sourceText)) !== null) {
      methods.push({
        methodName: match[1],
        className: 'Unknown', // Would extract from AST context
        filePath
      });
    }

    return methods;
  }

  private findFactoryClasses(astNode: SyntaxNode, filePath: string): Array<{className: string, filePath: string}> {
    const classes: Array<{className: string, filePath: string}> = [];

    const sourceText = astNode.text || '';
    const factoryClassPattern = /class\s+(\w*Factory|\w*Builder|\w*Creator)/g;

    let match;
    while ((match = factoryClassPattern.exec(sourceText)) !== null) {
      classes.push({
        className: match[1],
        filePath
      });
    }

    return classes;
  }

  private findRepositoryClasses(astNode: SyntaxNode, filePath: string): Array<{className: string, filePath: string, methods: string[]}> {
    const repositories: Array<{className: string, filePath: string, methods: string[]}> = [];

    const sourceText = astNode.text || '';

    // Look for repository class patterns
    const repositoryClassPattern = /class\s+(\w*Repository|\w*DAO)/g;
    const crudMethodPattern = /(find\w*|get\w*|save|update|delete|create|insert)\s*\(/g;

    let classMatch;
    while ((classMatch = repositoryClassPattern.exec(sourceText)) !== null) {
      const className = classMatch[1];
      const methods: string[] = [];

      let methodMatch;
      while ((methodMatch = crudMethodPattern.exec(sourceText)) !== null) {
        methods.push(methodMatch[1]);
      }

      if (methods.length > 2) { // Must have at least a few CRUD methods
        repositories.push({
          className,
          filePath,
          methods: [...new Set(methods)] // Remove duplicates
        });
      }
    }

    return repositories;
  }

  private generateId(): string {
    return Math.random().toString(36).substr(2, 9);
  }
}
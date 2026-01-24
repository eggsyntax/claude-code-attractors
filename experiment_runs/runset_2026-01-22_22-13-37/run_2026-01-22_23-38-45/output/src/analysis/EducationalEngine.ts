import { DetectedPattern, PatternType, Suggestion } from '../types/core.js';

/**
 * Educational engine that provides learning context for detected patterns
 *
 * The EducationalEngine transforms pattern detection into learning opportunities by:
 * - Explaining WHY patterns matter in software architecture
 * - Providing historical context and evolution of design practices
 * - Connecting patterns to broader software engineering principles
 * - Offering curated resources for deeper learning
 * - Tracking learning progress and suggesting growth paths
 */
export class EducationalEngine {
  private readonly patternEducation: Map<string, PatternEducationContent> = new Map();
  private readonly principleConnections: Map<string, SoftwarePrinciple[]> = new Map();

  constructor() {
    this.initializePatternEducation();
    this.initializePrincipleConnections();
  }

  /**
   * Generates educational context for detected patterns
   */
  generateEducationalContext(patterns: DetectedPattern[]): EducationalSummary {
    const learningOpportunities: LearningOpportunity[] = [];
    const principles: Set<SoftwarePrinciple> = new Set();
    const recommendedResources: Resource[] = [];

    for (const pattern of patterns) {
      const education = this.patternEducation.get(pattern.name);
      if (education) {
        learningOpportunities.push(this.createLearningOpportunity(pattern, education));

        // Add related principles
        const relatedPrinciples = this.principleConnections.get(pattern.name) || [];
        relatedPrinciples.forEach(principle => principles.add(principle));

        // Add educational resources
        recommendedResources.push(...education.resources);
      }
    }

    return {
      learningOpportunities,
      principlesInvolved: Array.from(principles),
      recommendedResources: this.deduplicateResources(recommendedResources),
      architecturalInsights: this.generateArchitecturalInsights(patterns),
      nextSteps: this.suggestNextSteps(patterns)
    };
  }

  /**
   * Provides contextual explanations for patterns within their architectural context
   */
  explainPatternInContext(pattern: DetectedPattern, relatedPatterns: DetectedPattern[]): PatternExplanation {
    const education = this.patternEducation.get(pattern.name);
    if (!education) {
      return this.createBasicExplanation(pattern);
    }

    return {
      pattern: pattern.name,
      whatItIs: education.definition,
      whyItMatters: education.importance,
      whenToUse: education.appropriateContexts,
      whenNotToUse: education.inappropriateContexts,
      commonMistakes: education.commonMistakes,
      relatedPatterns: this.findRelatedPatterns(pattern, relatedPatterns),
      realWorldExamples: education.realWorldExamples,
      evolutionPath: education.evolutionPath,
      testingConsiderations: education.testingConsiderations
    };
  }

  /**
   * Generates learning path suggestions based on detected patterns
   */
  generateLearningPath(patterns: DetectedPattern[]): LearningPath {
    const patternsByComplexity = this.groupPatternsByComplexity(patterns);
    const missingFundamentals = this.identifyMissingFundamentals(patterns);

    return {
      currentLevel: this.assessCurrentLevel(patterns),
      fundamentalGaps: missingFundamentals,
      beginnerTopics: patternsByComplexity.beginner,
      intermediateTopics: patternsByComplexity.intermediate,
      advancedTopics: patternsByComplexity.advanced,
      practicalExercises: this.generatePracticalExercises(patterns),
      milestones: this.createLearningMilestones(patterns)
    };
  }

  private initializePatternEducation(): void {
    // Singleton Pattern Education
    this.patternEducation.set('Singleton Pattern', {
      definition: 'Ensures a class has only one instance and provides global access to it',
      importance: 'Controls object creation and provides a single point of access for shared resources',
      appropriateContexts: ['Configuration managers', 'Logging systems', 'Database connection pools', 'Thread pools'],
      inappropriateContexts: ['When you need multiple instances', 'In unit tests (hard to mock)', 'When state changes frequently'],
      benefits: ['Controlled access to sole instance', 'Reduced memory footprint', 'Lazy initialization'],
      drawbacks: ['Violates Single Responsibility Principle', 'Difficult to unit test', 'Can become a bottleneck'],
      commonMistakes: ['Making everything singleton', 'Not thread-safe implementation', 'Using for temporary convenience'],
      realWorldExamples: ['Java Runtime.getRuntime()', 'Python logging module', 'Spring ApplicationContext'],
      evolutionPath: 'Originally from Gang of Four → Modern alternatives: Dependency Injection, Service Locator pattern',
      testingConsiderations: 'Hard to test due to global state. Use dependency injection for better testability.',
      resources: [
        { type: 'article', title: 'Singleton Pattern Explained', url: 'https://refactoring.guru/design-patterns/singleton' },
        { type: 'book', title: 'Design Patterns: Elements of Reusable Object-Oriented Software', url: '' }
      ]
    });

    // Factory Pattern Education
    this.patternEducation.set('Factory Pattern', {
      definition: 'Creates objects without specifying the exact class to create',
      importance: 'Encapsulates object creation logic and provides flexibility in object instantiation',
      appropriateContexts: ['Creating objects based on configuration', 'Database drivers', 'UI components', 'Plugin systems'],
      inappropriateContexts: ['Simple object creation', 'When object type never changes', 'Over-engineering simple cases'],
      benefits: ['Decouples client from concrete classes', 'Supports Open/Closed Principle', 'Centralizes creation logic'],
      drawbacks: ['Can introduce unnecessary complexity', 'May violate Tell-Dont-Ask principle'],
      commonMistakes: ['Creating factories for everything', 'Not following naming conventions', 'Mixing factory types'],
      realWorldExamples: ['JDBC DriverManager', 'React createElement', 'DOM document.createElement'],
      evolutionPath: 'Simple Factory → Factory Method → Abstract Factory → Modern: IoC containers',
      testingConsiderations: 'Easy to test by injecting mock factories or using factory interfaces.',
      resources: [
        { type: 'article', title: 'Factory Pattern Guide', url: 'https://refactoring.guru/design-patterns/factory-method' }
      ]
    });

    // God Object Anti-pattern Education
    this.patternEducation.set('God Object', {
      definition: 'A class that knows too much or does too much, centralizing too many functions',
      importance: 'Violates Single Responsibility Principle and creates maintenance nightmares',
      appropriateContexts: ['Never appropriate - always an anti-pattern'],
      inappropriateContexts: ['Any production code', 'Long-term maintainable systems'],
      benefits: ['None - this is an anti-pattern'],
      drawbacks: ['Hard to understand', 'Difficult to test', 'Breaks encapsulation', 'High coupling'],
      commonMistakes: ['Gradual feature additions without refactoring', 'Not recognizing the problem early'],
      realWorldExamples: ['Legacy enterprise applications', 'Monolithic controllers in web apps'],
      evolutionPath: 'Small class → Feature additions → God Object → Refactoring needed',
      testingConsiderations: 'Extremely difficult to test due to many dependencies and responsibilities.',
      resources: [
        { type: 'article', title: 'Refactoring God Objects', url: 'https://sourcemaking.com/refactoring/smells/large-class' }
      ]
    });

    // SQL Injection Security Pattern Education
    this.patternEducation.set('Potential SQL Injection', {
      definition: 'A security vulnerability where user input is directly concatenated into SQL queries',
      importance: 'One of the most dangerous security vulnerabilities, can lead to data breaches',
      appropriateContexts: ['Never appropriate - always a vulnerability'],
      inappropriateContexts: ['Any production system', 'Systems handling user data'],
      benefits: ['None - this is a vulnerability'],
      drawbacks: ['Data theft risk', 'Data corruption risk', 'System compromise', 'Regulatory violations'],
      commonMistakes: ['Trusting user input', 'Dynamic query building', 'Not using parameterized queries'],
      realWorldExamples: ['OWASP Top 10 #3', 'Equifax breach (2017)', 'TalkTalk breach (2015)'],
      evolutionPath: 'Manual SQL → String concatenation → SQL Injection → Parameterized queries',
      testingConsiderations: 'Use SQL injection testing tools and security-focused unit tests.',
      resources: [
        { type: 'guide', title: 'OWASP SQL Injection Prevention', url: 'https://owasp.org/www-project-top-ten/' }
      ]
    });

    // N+1 Query Performance Pattern Education
    this.patternEducation.set('N+1 Query Problem', {
      definition: 'A query executed N times in a loop, instead of one optimized query',
      importance: 'Causes exponential performance degradation as data grows',
      appropriateContexts: ['Never appropriate - always a performance issue'],
      inappropriateContexts: ['Production systems', 'Systems with large datasets'],
      benefits: ['None - this is a performance anti-pattern'],
      drawbacks: ['Poor performance', 'Database overload', 'Poor user experience', 'Resource waste'],
      commonMistakes: ['Loading related data in loops', 'Not understanding ORM behavior', 'Lazy loading without consideration'],
      realWorldExamples: ['ORM lazy loading', 'REST API calls in loops', 'Database queries in templates'],
      evolutionPath: 'Single queries → Loop-based loading → N+1 problem → Batch loading/eager loading',
      testingConsiderations: 'Monitor query count in tests, use database query analysis tools.',
      resources: [
        { type: 'article', title: 'Solving N+1 Query Problem', url: 'https://stackoverflow.com/questions/97197/what-is-the-n1-selects-query-issue' }
      ]
    });
  }

  private initializePrincipleConnections(): void {
    this.principleConnections.set('Singleton Pattern', [
      { name: 'Single Responsibility Principle', violated: true },
      { name: 'Dependency Inversion Principle', violated: true }
    ]);

    this.principleConnections.set('Factory Pattern', [
      { name: 'Open/Closed Principle', violated: false },
      { name: 'Dependency Inversion Principle', violated: false }
    ]);

    this.principleConnections.set('God Object', [
      { name: 'Single Responsibility Principle', violated: true },
      { name: 'Interface Segregation Principle', violated: true }
    ]);
  }

  private createLearningOpportunity(pattern: DetectedPattern, education: PatternEducationContent): LearningOpportunity {
    return {
      pattern: pattern.name,
      patternType: pattern.type,
      confidence: pattern.confidence,
      location: pattern.location,
      keyLearnings: [
        education.importance,
        ...education.benefits.slice(0, 2),
        education.evolutionPath
      ],
      practicalAdvice: education.appropriateContexts.slice(0, 2),
      pitfallsToAvoid: education.commonMistakes.slice(0, 2),
      nextSteps: this.generatePatternNextSteps(pattern, education)
    };
  }

  private generatePatternNextSteps(pattern: DetectedPattern, education: PatternEducationContent): string[] {
    const steps: string[] = [];

    if (pattern.type === 'anti-pattern') {
      steps.push(`Refactor the ${pattern.name.toLowerCase()} to improve code quality`);
      steps.push(`Study alternative approaches: ${education.appropriateContexts.join(', ')}`);
    } else if (pattern.type === 'security') {
      steps.push('Immediately fix this security vulnerability');
      steps.push('Review other code for similar issues');
      steps.push('Implement security testing practices');
    } else if (pattern.type === 'architectural' || pattern.type === 'design') {
      steps.push(`Understand when to use ${pattern.name}`);
      steps.push('Practice implementing variations of this pattern');
      steps.push('Learn related patterns and their trade-offs');
    }

    return steps;
  }

  private generateArchitecturalInsights(patterns: DetectedPattern[]): string[] {
    const insights: string[] = [];
    const patternTypes = new Set(patterns.map(p => p.type));

    if (patternTypes.has('anti-pattern') && patterns.filter(p => p.type === 'anti-pattern').length > 2) {
      insights.push('Multiple anti-patterns detected suggest the codebase may benefit from systematic refactoring');
    }

    if (patternTypes.has('security')) {
      insights.push('Security patterns detected - prioritize fixing these vulnerabilities immediately');
    }

    if (patternTypes.has('performance')) {
      insights.push('Performance patterns found - consider profiling to measure actual impact');
    }

    if (patternTypes.has('design') && !patternTypes.has('architectural')) {
      insights.push('Good use of design patterns, consider exploring architectural patterns for system-level improvements');
    }

    return insights;
  }

  private suggestNextSteps(patterns: DetectedPattern[]): string[] {
    const steps: Set<string> = new Set();

    for (const pattern of patterns) {
      switch (pattern.type) {
        case 'security':
          steps.add('Audit code for additional security vulnerabilities');
          steps.add('Implement security testing in CI/CD pipeline');
          break;
        case 'anti-pattern':
          steps.add('Plan refactoring sessions to address anti-patterns');
          steps.add('Review code review process to catch anti-patterns early');
          break;
        case 'performance':
          steps.add('Set up performance monitoring and profiling');
          steps.add('Create performance benchmarks and tests');
          break;
        case 'design':
          steps.add('Document successful pattern usage for team knowledge sharing');
          break;
        case 'architectural':
          steps.add('Review overall system architecture for consistency');
          break;
      }
    }

    return Array.from(steps);
  }

  private groupPatternsByComplexity(patterns: DetectedPattern[]): { beginner: string[], intermediate: string[], advanced: string[] } {
    const complexity = {
      beginner: ['Magic Numbers', 'Long Parameter List', 'Dead Code'],
      intermediate: ['God Object', 'Feature Envy', 'N+1 Query Problem', 'Factory Pattern'],
      advanced: ['Singleton Pattern', 'Builder Pattern', 'Observer Pattern', 'Strategy Pattern']
    };

    return {
      beginner: patterns.filter(p => complexity.beginner.includes(p.name)).map(p => p.name),
      intermediate: patterns.filter(p => complexity.intermediate.includes(p.name)).map(p => p.name),
      advanced: patterns.filter(p => complexity.advanced.includes(p.name)).map(p => p.name)
    };
  }

  private identifyMissingFundamentals(patterns: DetectedPattern[]): string[] {
    const fundamentals = ['SOLID Principles', 'Clean Code Practices', 'Security Best Practices'];
    const missing: string[] = [];

    // Check if anti-patterns suggest missing fundamentals
    const antiPatterns = patterns.filter(p => p.type === 'anti-pattern');
    if (antiPatterns.some(p => p.name === 'God Object' || p.name === 'Feature Envy')) {
      missing.push('Single Responsibility Principle');
    }

    if (patterns.some(p => p.type === 'security')) {
      missing.push('Security Best Practices');
    }

    return missing;
  }

  private assessCurrentLevel(patterns: DetectedPattern[]): LearningLevel {
    const designPatterns = patterns.filter(p => p.type === 'design').length;
    const antiPatterns = patterns.filter(p => p.type === 'anti-pattern').length;
    const securityIssues = patterns.filter(p => p.type === 'security').length;

    if (securityIssues > 0 || antiPatterns > designPatterns * 2) {
      return 'beginner';
    } else if (designPatterns > 0 && antiPatterns <= designPatterns) {
      return 'intermediate';
    } else {
      return 'advanced';
    }
  }

  private generatePracticalExercises(patterns: DetectedPattern[]): string[] {
    const exercises: string[] = [];
    const uniquePatterns = new Set(patterns.map(p => p.name));

    for (const patternName of uniquePatterns) {
      exercises.push(`Practice refactoring code that exhibits ${patternName.toLowerCase()}`);
    }

    return exercises.slice(0, 5); // Limit to 5 exercises
  }

  private createLearningMilestones(patterns: DetectedPattern[]): string[] {
    return [
      'Understand all detected anti-patterns and their solutions',
      'Successfully refactor one major anti-pattern in your codebase',
      'Implement proper security practices to prevent vulnerabilities',
      'Master the design patterns found in your code',
      'Apply architectural patterns at the system level'
    ];
  }

  private findRelatedPatterns(pattern: DetectedPattern, allPatterns: DetectedPattern[]): string[] {
    // Simple relationship mapping - in a real system, this would be more sophisticated
    const relationships = {
      'Singleton Pattern': ['Factory Pattern', 'Dependency Injection'],
      'Factory Pattern': ['Builder Pattern', 'Abstract Factory'],
      'God Object': ['Single Responsibility Principle', 'Extract Class refactoring']
    };

    return relationships[pattern.name] || [];
  }

  private createBasicExplanation(pattern: DetectedPattern): PatternExplanation {
    return {
      pattern: pattern.name,
      whatItIs: pattern.description,
      whyItMatters: 'This pattern affects code quality and maintainability',
      whenToUse: 'Context-dependent',
      whenNotToUse: 'When simpler solutions exist',
      commonMistakes: ['Overuse', 'Incorrect implementation'],
      relatedPatterns: [],
      realWorldExamples: [],
      evolutionPath: 'Pattern usage has evolved with best practices',
      testingConsiderations: 'Consider testability when using this pattern'
    };
  }

  private deduplicateResources(resources: Resource[]): Resource[] {
    const seen = new Set<string>();
    return resources.filter(resource => {
      const key = resource.title + resource.url;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }
}

// Supporting interfaces
export interface EducationalSummary {
  learningOpportunities: LearningOpportunity[];
  principlesInvolved: SoftwarePrinciple[];
  recommendedResources: Resource[];
  architecturalInsights: string[];
  nextSteps: string[];
}

export interface LearningOpportunity {
  pattern: string;
  patternType: PatternType;
  confidence: number;
  location: any; // CodeLocation
  keyLearnings: string[];
  practicalAdvice: string[];
  pitfallsToAvoid: string[];
  nextSteps: string[];
}

export interface PatternExplanation {
  pattern: string;
  whatItIs: string;
  whyItMatters: string;
  whenToUse: string;
  whenNotToUse: string;
  commonMistakes: string[];
  relatedPatterns: string[];
  realWorldExamples: string[];
  evolutionPath: string;
  testingConsiderations: string;
}

export interface LearningPath {
  currentLevel: LearningLevel;
  fundamentalGaps: string[];
  beginnerTopics: string[];
  intermediateTopics: string[];
  advancedTopics: string[];
  practicalExercises: string[];
  milestones: string[];
}

interface PatternEducationContent {
  definition: string;
  importance: string;
  appropriateContexts: string[];
  inappropriateContexts: string[];
  benefits: string[];
  drawbacks: string[];
  commonMistakes: string[];
  realWorldExamples: string[];
  evolutionPath: string;
  testingConsiderations: string;
  resources: Resource[];
}

interface SoftwarePrinciple {
  name: string;
  violated: boolean;
}

interface Resource {
  type: 'article' | 'book' | 'video' | 'guide' | 'tutorial';
  title: string;
  url: string;
}

type LearningLevel = 'beginner' | 'intermediate' | 'advanced';
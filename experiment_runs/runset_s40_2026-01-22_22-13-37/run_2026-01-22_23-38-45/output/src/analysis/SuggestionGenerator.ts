import { CodeFile, DetectedPattern, QualityMetrics, DependencyInfo, Suggestion, SuggestionType, CodeExample, CodeLocation } from '../types/core.js';

/**
 * Intelligent suggestion generator that creates educational, actionable recommendations
 *
 * The SuggestionGenerator analyzes detected patterns, metrics, and dependencies to:
 * - Provide specific, actionable improvement recommendations
 * - Explain WHY changes are beneficial (educational context)
 * - Offer concrete code examples showing before/after
 * - Prioritize suggestions based on impact and difficulty
 * - Connect improvements to broader architectural principles
 */
export class SuggestionGenerator {
  private readonly suggestionRules: SuggestionRule[] = [];
  private readonly educationalContext: Map<string, EducationalContent> = new Map();

  constructor() {
    this.initializeSuggestionRules();
    this.initializeEducationalContent();
  }

  /**
   * Generates comprehensive suggestions based on analysis results
   */
  async generateSuggestions(
    file: CodeFile,
    patterns: DetectedPattern[],
    metrics: QualityMetrics,
    dependencies: DependencyInfo[]
  ): Promise<Suggestion[]> {
    const suggestions: Suggestion[] = [];

    // Generate pattern-based suggestions
    for (const pattern of patterns) {
      const patternSuggestions = await this.generatePatternSuggestions(file, pattern);
      suggestions.push(...patternSuggestions);
    }

    // Generate metrics-based suggestions
    const metricSuggestions = await this.generateMetricSuggestions(file, metrics);
    suggestions.push(...metricSuggestions);

    // Generate dependency-based suggestions
    const dependencySuggestions = await this.generateDependencySuggestions(file, dependencies);
    suggestions.push(...dependencySuggestions);

    // Generate cross-cutting suggestions (combining multiple analysis types)
    const crossCuttingSuggestions = await this.generateCrossCuttingSuggestions(
      file, patterns, metrics, dependencies
    );
    suggestions.push(...crossCuttingSuggestions);

    // Sort by priority and confidence, remove duplicates
    return this.prioritizeAndDeduplicate(suggestions);
  }

  private async generatePatternSuggestions(file: CodeFile, pattern: DetectedPattern): Promise<Suggestion[]> {
    const suggestions: Suggestion[] = [];

    switch (pattern.type) {
      case 'anti-pattern':
        suggestions.push(...this.handleAntiPatternSuggestions(file, pattern));
        break;
      case 'security':
        suggestions.push(...this.handleSecurityPatternSuggestions(file, pattern));
        break;
      case 'performance':
        suggestions.push(...this.handlePerformancePatternSuggestions(file, pattern));
        break;
      case 'maintainability':
        suggestions.push(...this.handleMaintainabilityPatternSuggestions(file, pattern));
        break;
      case 'architectural':
        suggestions.push(...this.handleArchitecturalPatternSuggestions(file, pattern));
        break;
      case 'design':
        suggestions.push(...this.handleDesignPatternSuggestions(file, pattern));
        break;
    }

    return suggestions;
  }

  private handleAntiPatternSuggestions(file: CodeFile, pattern: DetectedPattern): Suggestion[] {
    const suggestions: Suggestion[] = [];

    switch (pattern.name) {
      case 'God Object':
        suggestions.push(this.createSuggestion({
          type: 'refactor',
          priority: 'high',
          title: 'Extract Responsibilities from God Object',
          description: `The class at ${pattern.location.file}:${pattern.location.line} has too many responsibilities. Consider breaking it into smaller, focused classes.`,
          location: pattern.location,
          reasoning: 'God objects violate the Single Responsibility Principle, making code harder to understand, test, and maintain. Smaller classes are easier to reason about and modify.',
          examples: [
            {
              title: 'Split by Functional Areas',
              before: `class UserManager {
  validateUser() { /* validation logic */ }
  saveToDatabase() { /* persistence logic */ }
  sendEmail() { /* notification logic */ }
  generateReport() { /* reporting logic */ }
}`,
              after: `class UserValidator {
  validateUser() { /* validation logic */ }
}

class UserRepository {
  saveToDatabase() { /* persistence logic */ }
}

class NotificationService {
  sendEmail() { /* notification logic */ }
}

class ReportGenerator {
  generateReport() { /* reporting logic */ }
}`,
              explanation: 'Each class now has a single, clear responsibility, making the code more modular and testable.'
            }
          ]
        }));
        break;

      case 'Magic Numbers':
        suggestions.push(this.createSuggestion({
          type: 'best-practice',
          priority: 'medium',
          title: 'Replace Magic Numbers with Named Constants',
          description: `Magic numbers found at ${pattern.location.file}:${pattern.location.line}. Consider using named constants to improve code readability.`,
          location: pattern.location,
          reasoning: 'Magic numbers make code harder to understand and maintain. Named constants provide context and make the code self-documenting.',
          examples: [
            {
              title: 'Use Named Constants',
              before: `if (user.age >= 18 && user.accountBalance > 1000) {
  // approve loan
}`,
              after: `const MINIMUM_AGE = 18;
const MINIMUM_BALANCE = 1000;

if (user.age >= MINIMUM_AGE && user.accountBalance > MINIMUM_BALANCE) {
  // approve loan
}`,
              explanation: 'The code is now self-documenting and the business rules are clearly expressed.'
            }
          ]
        }));
        break;

      case 'Dead Code':
        suggestions.push(this.createSuggestion({
          type: 'refactor',
          priority: 'low',
          title: 'Remove Unused Code',
          description: `Unused code detected at ${pattern.location.file}:${pattern.location.line}. Consider removing it to reduce codebase complexity.`,
          location: pattern.location,
          reasoning: 'Dead code increases maintenance burden, confuses developers, and can hide bugs. Removing unused code keeps the codebase clean and focused.',
          examples: [
            {
              title: 'Clean Up Unused Code',
              before: `function processUser(user) {
  // validateUser(user); // Commented out code
  return saveUser(user);
}

function oldFunction() {
  // This function is never called
  return 'legacy';
}`,
              after: `function processUser(user) {
  return saveUser(user);
}`,
              explanation: 'Removed commented code and unused functions to keep the codebase clean and maintainable.'
            }
          ]
        }));
        break;
    }

    return suggestions;
  }

  private handleSecurityPatternSuggestions(file: CodeFile, pattern: DetectedPattern): Suggestion[] {
    const suggestions: Suggestion[] = [];

    switch (pattern.name) {
      case 'Potential SQL Injection':
        suggestions.push(this.createSuggestion({
          type: 'security',
          priority: 'critical',
          title: 'Fix SQL Injection Vulnerability',
          description: `Potential SQL injection detected at ${pattern.location.file}:${pattern.location.line}. Use parameterized queries to prevent injection attacks.`,
          location: pattern.location,
          reasoning: 'SQL injection is one of the most dangerous security vulnerabilities. Parameterized queries ensure user input cannot be interpreted as SQL commands.',
          examples: [
            {
              title: 'Use Parameterized Queries',
              before: `const query = \`SELECT * FROM users WHERE name = '\${userName}'\`;
db.execute(query);`,
              after: `const query = 'SELECT * FROM users WHERE name = ?';
db.execute(query, [userName]);`,
              explanation: 'Parameterized queries separate SQL code from data, preventing injection attacks even with malicious input.'
            }
          ]
        }));
        break;

      case 'Hardcoded Credentials':
        suggestions.push(this.createSuggestion({
          type: 'security',
          priority: 'critical',
          title: 'Remove Hardcoded Credentials',
          description: `Hardcoded credentials detected at ${pattern.location.file}:${pattern.location.line}. Move sensitive data to environment variables or secure configuration.`,
          location: pattern.location,
          reasoning: 'Hardcoded credentials in source code are a major security risk. They can be exposed through version control, logs, or code sharing.',
          examples: [
            {
              title: 'Use Environment Variables',
              before: `const config = {
  apiKey: 'sk-1234567890abcdef',
  password: 'supersecret123'
};`,
              after: `const config = {
  apiKey: process.env.API_KEY,
  password: process.env.DB_PASSWORD
};`,
              explanation: 'Environment variables keep secrets out of source code and allow different values for different environments.'
            }
          ]
        }));
        break;
    }

    return suggestions;
  }

  private handlePerformancePatternSuggestions(file: CodeFile, pattern: DetectedPattern): Suggestion[] {
    const suggestions: Suggestion[] = [];

    switch (pattern.name) {
      case 'N+1 Query Problem':
        suggestions.push(this.createSuggestion({
          type: 'performance',
          priority: 'high',
          title: 'Fix N+1 Query Problem',
          description: `N+1 query pattern detected at ${pattern.location.file}:${pattern.location.line}. Consider using batch loading or eager loading to reduce database queries.`,
          location: pattern.location,
          reasoning: 'N+1 queries can severely impact performance by executing many individual queries instead of one efficient query. This becomes worse as data grows.',
          examples: [
            {
              title: 'Use Batch Loading',
              before: `const users = await getUsers();
for (const user of users) {
  user.profile = await getUserProfile(user.id); // N+1 problem
}`,
              after: `const users = await getUsers();
const userIds = users.map(u => u.id);
const profiles = await getUserProfiles(userIds);
const profileMap = new Map(profiles.map(p => [p.userId, p]));

users.forEach(user => {
  user.profile = profileMap.get(user.id);
});`,
              explanation: 'Batch loading reduces N+1 queries to just 2 queries total, dramatically improving performance.'
            }
          ]
        }));
        break;
    }

    return suggestions;
  }

  private handleMaintainabilityPatternSuggestions(file: CodeFile, pattern: DetectedPattern): Suggestion[] {
    const suggestions: Suggestion[] = [];

    switch (pattern.name) {
      case 'Long Parameter List':
        suggestions.push(this.createSuggestion({
          type: 'refactor',
          priority: 'medium',
          title: 'Reduce Parameter Count',
          description: `Function with too many parameters at ${pattern.location.file}:${pattern.location.line}. Consider using parameter objects or dependency injection.`,
          location: pattern.location,
          reasoning: 'Long parameter lists are hard to understand, remember, and maintain. They often indicate that a function is doing too much.',
          examples: [
            {
              title: 'Use Parameter Object',
              before: `function createUser(name, email, age, address, phone, preferences, settings) {
  // function implementation
}`,
              after: `function createUser(userData) {
  const { name, email, age, address, phone, preferences, settings } = userData;
  // function implementation
}`,
              explanation: 'Parameter objects group related data, reduce parameter count, and make functions easier to call and extend.'
            }
          ]
        }));
        break;
    }

    return suggestions;
  }

  private handleArchitecturalPatternSuggestions(file: CodeFile, pattern: DetectedPattern): Suggestion[] {
    const suggestions: Suggestion[] = [];

    switch (pattern.name) {
      case 'Singleton Pattern':
        suggestions.push(this.createSuggestion({
          type: 'architecture',
          priority: 'low',
          title: 'Consider Singleton Alternatives',
          description: `Singleton pattern detected at ${pattern.location.file}:${pattern.location.line}. Consider if dependency injection might be a better approach for testability.`,
          location: pattern.location,
          reasoning: 'While Singletons ensure single instances, they can make testing difficult and create hidden dependencies. Modern alternatives often provide better flexibility.',
          examples: [
            {
              title: 'Dependency Injection Alternative',
              before: `class DatabaseConnection {
  private static instance: DatabaseConnection;

  static getInstance() {
    if (!this.instance) {
      this.instance = new DatabaseConnection();
    }
    return this.instance;
  }
}

class UserService {
  private db = DatabaseConnection.getInstance(); // Hard dependency
}`,
              after: `class UserService {
  constructor(private db: DatabaseConnection) {} // Injected dependency
}

// In your application setup:
const dbConnection = new DatabaseConnection();
const userService = new UserService(dbConnection);`,
              explanation: 'Dependency injection makes testing easier by allowing mock objects and reduces coupling between classes.'
            }
          ]
        }));
        break;
    }

    return suggestions;
  }

  private handleDesignPatternSuggestions(file: CodeFile, pattern: DetectedPattern): Suggestion[] {
    const suggestions: Suggestion[] = [];

    switch (pattern.name) {
      case 'Factory Pattern':
        suggestions.push(this.createSuggestion({
          type: 'best-practice',
          priority: 'low',
          title: 'Well-Implemented Factory Pattern',
          description: `Good use of Factory pattern at ${pattern.location.file}:${pattern.location.line}. This encapsulates object creation logic effectively.`,
          location: pattern.location,
          reasoning: 'Factory patterns provide a clean way to create objects without exposing instantiation logic, making code more maintainable and extensible.',
          examples: []
        }));
        break;
    }

    return suggestions;
  }

  private async generateMetricSuggestions(file: CodeFile, metrics: QualityMetrics): Promise<Suggestion[]> {
    const suggestions: Suggestion[] = [];

    if (metrics.complexity > 7) {
      suggestions.push(this.createSuggestion({
        type: 'refactor',
        priority: 'high',
        title: 'Reduce Cyclomatic Complexity',
        description: `High complexity detected (${metrics.complexity}). Consider breaking down complex functions into smaller, simpler ones.`,
        location: { file: file.path, line: 1, column: 1 },
        reasoning: 'High cyclomatic complexity indicates code that is hard to understand, test, and maintain. Simpler functions are easier to reason about and debug.',
        examples: [
          {
            title: 'Extract Complex Logic',
            before: `function processOrder(order) {
  if (order.items.length > 0) {
    if (order.customer.isPremium) {
      if (order.total > 100) {
        // Apply premium discount logic
        if (order.customer.loyaltyPoints > 500) {
          // Apply loyalty bonus
          if (order.shippingAddress.country === 'US') {
            // Apply domestic shipping
          } else {
            // Apply international shipping
          }
        }
      }
    } else {
      // Regular customer logic
    }
  }
}`,
            after: `function processOrder(order) {
  if (!hasValidItems(order)) return;

  const discount = calculateDiscount(order);
  const shipping = calculateShipping(order);

  return applyOrderCalculations(order, discount, shipping);
}

function hasValidItems(order) {
  return order.items.length > 0;
}

function calculateDiscount(order) {
  if (!order.customer.isPremium) return 0;
  if (order.total <= 100) return 0;

  return order.customer.loyaltyPoints > 500
    ? getPremiumLoyaltyDiscount(order)
    : getStandardPremiumDiscount(order);
}`,
            explanation: 'Breaking complex functions into smaller, focused functions reduces complexity and improves readability.'
          }
        ]
      }));
    }

    if (metrics.maintainability < 4) {
      suggestions.push(this.createSuggestion({
        type: 'refactor',
        priority: 'medium',
        title: 'Improve Code Maintainability',
        description: `Low maintainability score (${metrics.maintainability}). Consider adding documentation, reducing coupling, and improving naming.`,
        location: { file: file.path, line: 1, column: 1 },
        reasoning: 'Low maintainability makes code harder to understand and modify, increasing development time and bug risk.',
        examples: []
      }));
    }

    return suggestions;
  }

  private async generateDependencySuggestions(file: CodeFile, dependencies: DependencyInfo[]): Promise<Suggestion[]> {
    const suggestions: Suggestion[] = [];

    // Check for circular dependencies or high coupling
    const importCount = dependencies.filter(dep => dep.type === 'import').length;

    if (importCount > 15) {
      suggestions.push(this.createSuggestion({
        type: 'architecture',
        priority: 'medium',
        title: 'Reduce Import Dependencies',
        description: `High number of imports (${importCount}). Consider if this module has too many responsibilities.`,
        location: { file: file.path, line: 1, column: 1 },
        reasoning: 'Too many imports can indicate a module that knows too much about other parts of the system, violating the Single Responsibility Principle.',
        examples: []
      }));
    }

    return suggestions;
  }

  private async generateCrossCuttingSuggestions(
    file: CodeFile,
    patterns: DetectedPattern[],
    metrics: QualityMetrics,
    dependencies: DependencyInfo[]
  ): Promise<Suggestion[]> {
    const suggestions: Suggestion[] = [];

    // Correlate high complexity with anti-patterns
    if (metrics.complexity > 6 && patterns.some(p => p.type === 'anti-pattern')) {
      suggestions.push(this.createSuggestion({
        type: 'refactor',
        priority: 'high',
        title: 'Address Complexity and Anti-patterns',
        description: 'This file has both high complexity and detected anti-patterns. Refactoring could significantly improve code quality.',
        location: { file: file.path, line: 1, column: 1 },
        reasoning: 'The combination of high complexity and anti-patterns indicates code that urgently needs refactoring for maintainability.',
        examples: []
      }));
    }

    return suggestions;
  }

  private createSuggestion(params: SuggestionParams): Suggestion {
    return {
      id: this.generateSuggestionId(),
      type: params.type,
      priority: params.priority,
      title: params.title,
      description: params.description,
      location: params.location,
      examples: params.examples || [],
      reasoning: params.reasoning
    };
  }

  private prioritizeAndDeduplicate(suggestions: Suggestion[]): Suggestion[] {
    // Remove duplicates based on location and type
    const unique = suggestions.filter((suggestion, index, array) =>
      index === array.findIndex(s =>
        s.location.file === suggestion.location.file &&
        s.location.line === suggestion.location.line &&
        s.type === suggestion.type
      )
    );

    // Sort by priority (critical first) and then by type
    const priorityOrder = { 'critical': 0, 'high': 1, 'medium': 2, 'low': 3 };

    return unique.sort((a, b) => {
      const priorityDiff = priorityOrder[a.priority] - priorityOrder[b.priority];
      if (priorityDiff !== 0) return priorityDiff;

      return a.type.localeCompare(b.type);
    });
  }

  private initializeSuggestionRules(): void {
    // Future: Add rule-based suggestion generation for more sophisticated recommendations
  }

  private initializeEducationalContent(): void {
    // Future: Add educational content mapping for pattern explanations
  }

  private generateSuggestionId(): string {
    return 'suggestion_' + Math.random().toString(36).substr(2, 9);
  }
}

// Supporting interfaces
interface SuggestionParams {
  type: SuggestionType;
  priority: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  location: CodeLocation;
  reasoning: string;
  examples?: CodeExample[];
}

interface SuggestionRule {
  name: string;
  condition: (patterns: DetectedPattern[], metrics: QualityMetrics, dependencies: DependencyInfo[]) => boolean;
  generator: (file: CodeFile, patterns: DetectedPattern[], metrics: QualityMetrics, dependencies: DependencyInfo[]) => Suggestion[];
}

interface EducationalContent {
  pattern: string;
  explanation: string;
  benefits: string[];
  drawbacks: string[];
  alternatives: string[];
  resources: string[];
}
#!/usr/bin/env node

/**
 * CodeMentor Analysis Engine Demo
 *
 * This demo showcases the intelligent code analysis capabilities of CodeMentor's
 * analysis engine, including:
 * - Pattern detection (architectural, design, anti-patterns, security)
 * - Quality metrics calculation
 * - Dependency analysis
 * - Educational suggestions generation
 * - Learning path recommendations
 */

import { AnalysisEngine } from '../src/analysis/AnalysisEngine.js';
import { CodeFile } from '../src/types/core.js';

// Sample problematic code to analyze
const sampleProblematicCode = `
class UserManager {
  private static instance: UserManager;
  private database: any;
  private emailService: any;
  private logger: any;
  private users: any[] = [];

  private constructor() {
    this.database = require('database-connection');
    this.emailService = require('email-service');
    this.logger = require('logger');
  }

  static getInstance(): UserManager {
    if (!UserManager.instance) {
      UserManager.instance = new UserManager();
    }
    return UserManager.instance;
  }

  // God object - doing too much
  async createUser(name: string, email: string, password: string, age: number,
                   address: string, phone: string, preferences: any, settings: any) {
    // SQL Injection vulnerability
    const query = \`INSERT INTO users (name, email) VALUES ('\${name}', '\${email}')\`;
    await this.database.execute(query);

    // N+1 query problem
    const users = await this.getUsers();
    for (const user of users) {
      user.profile = await this.getUserProfile(user.id);
    }

    // Magic number
    if (age >= 18) {
      await this.sendWelcomeEmail(email);
    }

    // Hardcoded credentials
    const apiKey = 'sk-1234567890abcdef';

    // Complex conditional logic (high complexity)
    if (preferences && preferences.notifications) {
      if (settings && settings.emailOptIn) {
        if (age >= 18 && age <= 65) {
          if (address && address.includes('US')) {
            this.logger.log('US adult user created');
          } else if (address && address.includes('EU')) {
            this.logger.log('EU adult user created');
          }
        }
      }
    }
  }

  async validateUser(email: string) {
    // More validation logic here...
  }

  async saveToDatabase(userData: any) {
    // Database persistence logic...
  }

  async sendWelcomeEmail(email: string) {
    // Email sending logic...
  }

  async generateUserReport(userId: number) {
    // Reporting logic...
  }

  async getUsers() {
    return this.database.query('SELECT * FROM users');
  }

  async getUserProfile(userId: number) {
    return this.database.query('SELECT * FROM profiles WHERE user_id = ?', [userId]);
  }
}

// XSS vulnerability example
function displayUserContent(userInput: string) {
  document.getElementById('content').innerHTML = '<div>' + userInput + '</div>';
}

// Factory pattern example (good pattern)
interface PaymentProcessor {
  processPayment(amount: number): Promise<boolean>;
}

class CreditCardProcessor implements PaymentProcessor {
  async processPayment(amount: number): Promise<boolean> {
    // Credit card processing logic
    return true;
  }
}

class PayPalProcessor implements PaymentProcessor {
  async processPayment(amount: number): Promise<boolean> {
    // PayPal processing logic
    return true;
  }
}

class PaymentFactory {
  static createProcessor(type: string): PaymentProcessor {
    switch (type) {
      case 'credit-card':
        return new CreditCardProcessor();
      case 'paypal':
        return new PayPalProcessor();
      default:
        throw new Error('Unknown payment type');
    }
  }
}
`;

const sampleGoodCode = `
// Well-structured code example
export interface UserRepository {
  save(user: User): Promise<void>;
  findById(id: string): Promise<User | null>;
  findByEmail(email: string): Promise<User | null>;
}

export interface EmailService {
  sendWelcomeEmail(email: string): Promise<void>;
}

export interface Logger {
  log(message: string): void;
  error(error: Error): void;
}

export class User {
  constructor(
    public readonly id: string,
    public readonly name: string,
    public readonly email: string,
    public readonly age: number
  ) {}

  isAdult(): boolean {
    const LEGAL_AGE = 18;
    return this.age >= LEGAL_AGE;
  }
}

export class UserService {
  constructor(
    private userRepository: UserRepository,
    private emailService: EmailService,
    private logger: Logger
  ) {}

  async createUser(userData: CreateUserData): Promise<User> {
    const user = new User(
      generateId(),
      userData.name,
      userData.email,
      userData.age
    );

    await this.userRepository.save(user);

    if (user.isAdult()) {
      await this.emailService.sendWelcomeEmail(user.email);
    }

    this.logger.log(\`User created: \${user.id}\`);
    return user;
  }

  async getUserById(id: string): Promise<User | null> {
    return this.userRepository.findById(id);
  }
}

interface CreateUserData {
  name: string;
  email: string;
  age: number;
}

function generateId(): string {
  return Math.random().toString(36).substr(2, 9);
}
`;

async function runDemo() {
  console.log('🚀 CodeMentor Analysis Engine Demo\n');
  console.log('=' .repeat(80));

  try {
    // Initialize the analysis engine
    const engine = new AnalysisEngine();
    await engine.initialize();

    console.log('✅ Analysis Engine initialized successfully\n');

    // Create sample files for analysis
    const problematicFile: CodeFile = {
      id: 'problematic-code',
      path: 'src/problematic/UserManager.ts',
      content: sampleProblematicCode,
      language: 'typescript',
      lastModified: new Date()
    };

    const goodFile: CodeFile = {
      id: 'good-code',
      path: 'src/services/UserService.ts',
      content: sampleGoodCode,
      language: 'typescript',
      lastModified: new Date()
    };

    console.log('📊 Analyzing Problematic Code...\n');
    console.log('-'.repeat(50));

    // Analyze the problematic code
    const problematicAnalysis = await engine.analyzeFile(problematicFile);

    console.log('🔍 ANALYSIS RESULTS FOR PROBLEMATIC CODE:');
    console.log(`File: ${problematicFile.path}`);
    console.log(`Patterns detected: ${problematicAnalysis.patterns.length}`);
    console.log(`Suggestions generated: ${problematicAnalysis.suggestions.length}\n`);

    // Display detected patterns
    console.log('📋 DETECTED PATTERNS:');
    for (const pattern of problematicAnalysis.patterns) {
      const icon = getPatternIcon(pattern.type);
      console.log(`${icon} ${pattern.name} (${pattern.type})`);
      console.log(`   Confidence: ${(pattern.confidence * 100).toFixed(1)}%`);
      console.log(`   Location: Line ${pattern.location.line}`);
      console.log(`   ${pattern.description}\n`);
    }

    // Display quality metrics
    console.log('📈 QUALITY METRICS:');
    const metrics = problematicAnalysis.metrics;
    console.log(`   Complexity: ${metrics.complexity}/10 ${getScoreEmoji(metrics.complexity, true)}`);
    console.log(`   Maintainability: ${metrics.maintainability}/10 ${getScoreEmoji(metrics.maintainability)}`);
    console.log(`   Testability: ${metrics.testability}/10 ${getScoreEmoji(metrics.testability)}`);
    console.log(`   Readability: ${metrics.readability}/10 ${getScoreEmoji(metrics.readability)}`);
    console.log(`   Performance: ${metrics.performance}/10 ${getScoreEmoji(metrics.performance)}\n`);

    // Display dependencies
    console.log('🔗 DEPENDENCIES ANALYZED:');
    console.log(`   Import dependencies: ${problematicAnalysis.dependencies.filter(d => d.type === 'import').length}`);
    console.log(`   Function calls: ${problematicAnalysis.dependencies.filter(d => d.type === 'function-call').length}`);
    console.log(`   Composition relationships: ${problematicAnalysis.dependencies.filter(d => d.type === 'composition').length}\n`);

    // Display top suggestions
    console.log('💡 TOP SUGGESTIONS:');
    const topSuggestions = problematicAnalysis.suggestions
      .sort((a, b) => getPriorityWeight(a.priority) - getPriorityWeight(b.priority))
      .slice(0, 5);

    for (const suggestion of topSuggestions) {
      const priorityIcon = getPriorityIcon(suggestion.priority);
      console.log(`${priorityIcon} ${suggestion.title}`);
      console.log(`   Priority: ${suggestion.priority.toUpperCase()}`);
      console.log(`   Type: ${suggestion.type}`);
      console.log(`   ${suggestion.description}`);
      if (suggestion.reasoning) {
        console.log(`   💭 Why: ${suggestion.reasoning}`);
      }
      console.log();
    }

    console.log('=' .repeat(80));
    console.log('📊 Analyzing Well-Structured Code...\n');
    console.log('-'.repeat(50));

    // Analyze the good code for comparison
    const goodAnalysis = await engine.analyzeFile(goodFile);

    console.log('🔍 ANALYSIS RESULTS FOR WELL-STRUCTURED CODE:');
    console.log(`File: ${goodFile.path}`);
    console.log(`Patterns detected: ${goodAnalysis.patterns.length}`);
    console.log(`Suggestions generated: ${goodAnalysis.suggestions.length}\n`);

    // Display quality metrics comparison
    console.log('📈 QUALITY METRICS COMPARISON:');
    console.log('                    Problematic | Well-Structured');
    console.log('                    ----------- | ---------------');
    console.log(`Complexity:         ${metrics.complexity.toFixed(1)}/10       | ${goodAnalysis.metrics.complexity.toFixed(1)}/10`);
    console.log(`Maintainability:    ${metrics.maintainability.toFixed(1)}/10       | ${goodAnalysis.metrics.maintainability.toFixed(1)}/10`);
    console.log(`Testability:        ${metrics.testability.toFixed(1)}/10       | ${goodAnalysis.metrics.testability.toFixed(1)}/10`);
    console.log(`Readability:        ${metrics.readability.toFixed(1)}/10       | ${goodAnalysis.metrics.readability.toFixed(1)}/10`);
    console.log(`Performance:        ${metrics.performance.toFixed(1)}/10       | ${goodAnalysis.metrics.performance.toFixed(1)}/10\n`);

    // Generate educational content
    console.log('🎓 EDUCATIONAL INSIGHTS:');
    const educationalSummary = engine.generateEducationalSummary(
      new Map([['problematic-code', problematicAnalysis]])
    );

    console.log(`Learning opportunities identified: ${educationalSummary.learningOpportunities.length}`);
    console.log(`Software principles involved: ${educationalSummary.principlesInvolved.length}`);
    console.log(`Architectural insights: ${educationalSummary.architecturalInsights.length}\n`);

    // Display learning opportunities
    console.log('📚 LEARNING OPPORTUNITIES:');
    for (const opportunity of educationalSummary.learningOpportunities.slice(0, 3)) {
      console.log(`• ${opportunity.pattern} (${opportunity.patternType})`);
      console.log(`  Key learnings: ${opportunity.keyLearnings[0]}`);
      console.log(`  Next steps: ${opportunity.nextSteps[0]}\n`);
    }

    // Display architectural insights
    if (educationalSummary.architecturalInsights.length > 0) {
      console.log('🏗️  ARCHITECTURAL INSIGHTS:');
      for (const insight of educationalSummary.architecturalInsights) {
        console.log(`• ${insight}`);
      }
      console.log();
    }

    // Project-level analysis
    console.log('=' .repeat(80));
    console.log('📈 PROJECT-LEVEL ANALYSIS\n');

    const projectResults = await engine.analyzeProject([problematicFile, goodFile]);
    const projectSummary = engine.getProjectSummary(projectResults);

    console.log('📊 PROJECT SUMMARY:');
    console.log(`Total files analyzed: ${projectSummary.totalFiles}`);
    console.log(`Average complexity: ${projectSummary.averageMetrics.complexity.toFixed(1)}/10`);
    console.log(`Average maintainability: ${projectSummary.averageMetrics.maintainability.toFixed(1)}/10`);
    console.log(`Critical issues found: ${projectSummary.criticalIssues.length}\n`);

    // Display critical issues
    if (projectSummary.criticalIssues.length > 0) {
      console.log('🚨 CRITICAL ISSUES:');
      for (const issue of projectSummary.criticalIssues) {
        console.log(`• ${issue.description} (${issue.severity})`);
      }
      console.log();
    }

    // Display recommended actions
    console.log('🎯 RECOMMENDED ACTIONS:');
    for (const action of projectSummary.recommendedActions) {
      console.log(`• ${action}`);
    }

    console.log('\n' + '=' .repeat(80));
    console.log('✅ Demo completed successfully!');
    console.log('\nCodeMentor Analysis Engine provides:');
    console.log('• Intelligent pattern detection');
    console.log('• Comprehensive quality metrics');
    console.log('• Educational context and explanations');
    console.log('• Actionable improvement suggestions');
    console.log('• Project-level architectural insights');

  } catch (error) {
    console.error('❌ Demo failed:', error);
    process.exit(1);
  }
}

// Helper functions for display formatting
function getPatternIcon(type: string): string {
  const icons = {
    'architectural': '🏗️',
    'design': '🎨',
    'anti-pattern': '⚠️',
    'security': '🔒',
    'performance': '⚡',
    'maintainability': '🔧'
  };
  return icons[type] || '📋';
}

function getScoreEmoji(score: number, inverted: boolean = false): string {
  const adjustedScore = inverted ? 10 - score : score;

  if (adjustedScore >= 8) return '🟢';
  if (adjustedScore >= 6) return '🟡';
  if (adjustedScore >= 4) return '🟠';
  return '🔴';
}

function getPriorityIcon(priority: string): string {
  const icons = {
    'critical': '🚨',
    'high': '🔴',
    'medium': '🟡',
    'low': '🟢'
  };
  return icons[priority] || '📌';
}

function getPriorityWeight(priority: string): number {
  const weights = { 'critical': 0, 'high': 1, 'medium': 2, 'low': 3 };
  return weights[priority] || 4;
}

// Run the demo if this file is executed directly
if (require.main === module) {
  runDemo().catch(console.error);
}

export { runDemo };
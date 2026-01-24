import Parser from 'tree-sitter';
import { CodeFile, DependencyInfo, CodeLocation } from '../types/core.js';

/**
 * Analyzes code dependencies and relationships
 *
 * The DependencyAnalyzer identifies and maps:
 * - Import/export relationships
 * - Function call dependencies
 * - Class inheritance and composition
 * - Module coupling and cohesion
 * - Circular dependencies
 */
export class DependencyAnalyzer {

  /**
   * Analyzes all dependencies in a code file
   */
  async analyzeDependencies(file: CodeFile, tree: Parser.Tree): Promise<DependencyInfo[]> {
    const dependencies: DependencyInfo[] = [];
    const rootNode = tree.rootNode;

    // Analyze different types of dependencies
    dependencies.push(...this.analyzeImports(file, rootNode));
    dependencies.push(...this.analyzeFunctionCalls(file, rootNode));
    dependencies.push(...this.analyzeInheritance(file, rootNode));
    dependencies.push(...this.analyzeComposition(file, rootNode));

    return dependencies;
  }

  /**
   * Analyzes import statements and external module dependencies
   */
  private analyzeImports(file: CodeFile, node: Parser.SyntaxNode): DependencyInfo[] {
    const dependencies: DependencyInfo[] = [];

    this.traverseNodes(node, (current) => {
      if (current.type === 'import_statement' || current.type === 'import_declaration') {
        const importText = this.getNodeText(current, file.content);
        const importedModule = this.extractModuleName(importText);

        if (importedModule) {
          dependencies.push({
            name: importedModule,
            type: 'import',
            source: this.nodeToLocation(file.path, current),
            target: importedModule
          });
        }

        // Extract individual imported symbols
        const symbols = this.extractImportedSymbols(importText);
        for (const symbol of symbols) {
          dependencies.push({
            name: symbol,
            type: 'import',
            source: this.nodeToLocation(file.path, current),
            target: `${importedModule}.${symbol}`
          });
        }
      }

      // Analyze require() calls (CommonJS)
      if (current.type === 'call_expression') {
        const callText = this.getNodeText(current, file.content);
        const requireMatch = callText.match(/require\s*\(\s*['"`]([^'"`]+)['"`]\s*\)/);

        if (requireMatch) {
          dependencies.push({
            name: requireMatch[1],
            type: 'import',
            source: this.nodeToLocation(file.path, current),
            target: requireMatch[1]
          });
        }
      }

      // Dynamic imports
      if (current.type === 'await_expression' || current.type === 'call_expression') {
        const text = this.getNodeText(current, file.content);
        const dynamicImportMatch = text.match(/import\s*\(\s*['"`]([^'"`]+)['"`]\s*\)/);

        if (dynamicImportMatch) {
          dependencies.push({
            name: dynamicImportMatch[1],
            type: 'import',
            source: this.nodeToLocation(file.path, current),
            target: dynamicImportMatch[1]
          });
        }
      }
    });

    return dependencies;
  }

  /**
   * Analyzes function call dependencies
   */
  private analyzeFunctionCalls(file: CodeFile, node: Parser.SyntaxNode): DependencyInfo[] {
    const dependencies: DependencyInfo[] = [];

    this.traverseNodes(node, (current) => {
      if (current.type === 'call_expression') {
        const callText = this.getNodeText(current, file.content);

        // Extract function name
        const functionName = this.extractFunctionName(current, file.content);
        if (functionName && !this.isBuiltinFunction(functionName)) {
          dependencies.push({
            name: functionName,
            type: 'function-call',
            source: this.nodeToLocation(file.path, current),
            target: functionName
          });
        }

        // Analyze method calls (object.method())
        const methodCallMatch = callText.match(/(\w+)\.(\w+)\s*\(/);
        if (methodCallMatch) {
          const [, object, method] = methodCallMatch;
          dependencies.push({
            name: `${object}.${method}`,
            type: 'function-call',
            source: this.nodeToLocation(file.path, current),
            target: `${object}.${method}`
          });
        }
      }
    });

    return dependencies;
  }

  /**
   * Analyzes class inheritance relationships
   */
  private analyzeInheritance(file: CodeFile, node: Parser.SyntaxNode): DependencyInfo[] {
    const dependencies: DependencyInfo[] = [];

    this.traverseNodes(node, (current) => {
      if (current.type === 'class_declaration') {
        const classText = this.getNodeText(current, file.content);

        // Check for extends keyword (inheritance)
        const extendsMatch = classText.match(/class\s+\w+\s+extends\s+(\w+)/);
        if (extendsMatch) {
          dependencies.push({
            name: extendsMatch[1],
            type: 'inheritance',
            source: this.nodeToLocation(file.path, current),
            target: extendsMatch[1]
          });
        }

        // Check for implements keyword (interface implementation)
        const implementsMatch = classText.match(/implements\s+([\w,\s]+)/);
        if (implementsMatch) {
          const interfaces = implementsMatch[1].split(',').map(i => i.trim());
          for (const interfaceName of interfaces) {
            dependencies.push({
              name: interfaceName,
              type: 'inheritance',
              source: this.nodeToLocation(file.path, current),
              target: interfaceName
            });
          }
        }
      }
    });

    return dependencies;
  }

  /**
   * Analyzes composition relationships (object creation and usage)
   */
  private analyzeComposition(file: CodeFile, node: Parser.SyntaxNode): DependencyInfo[] {
    const dependencies: DependencyInfo[] = [];

    this.traverseNodes(node, (current) => {
      // Object instantiation with 'new' keyword
      if (current.type === 'new_expression') {
        const newText = this.getNodeText(current, file.content);
        const classMatch = newText.match(/new\s+(\w+)/);

        if (classMatch) {
          dependencies.push({
            name: classMatch[1],
            type: 'composition',
            source: this.nodeToLocation(file.path, current),
            target: classMatch[1]
          });
        }
      }

      // Type annotations (TypeScript)
      if (current.type === 'type_annotation') {
        const typeText = this.getNodeText(current, file.content);
        const customTypes = this.extractCustomTypes(typeText);

        for (const typeName of customTypes) {
          dependencies.push({
            name: typeName,
            type: 'composition',
            source: this.nodeToLocation(file.path, current),
            target: typeName
          });
        }
      }

      // Generic type parameters
      if (current.type === 'type_parameters' || current.type === 'type_arguments') {
        const typeText = this.getNodeText(current, file.content);
        const genericTypes = this.extractGenericTypes(typeText);

        for (const typeName of genericTypes) {
          dependencies.push({
            name: typeName,
            type: 'composition',
            source: this.nodeToLocation(file.path, current),
            target: typeName
          });
        }
      }
    });

    return dependencies;
  }

  /**
   * Creates a dependency graph for visualization and analysis
   */
  createDependencyGraph(dependencies: DependencyInfo[]): DependencyGraph {
    const graph: DependencyGraph = {
      nodes: new Map(),
      edges: []
    };

    // Create nodes for each unique dependency
    for (const dep of dependencies) {
      if (!graph.nodes.has(dep.target)) {
        graph.nodes.set(dep.target, {
          id: dep.target,
          name: dep.name,
          type: dep.type,
          incomingCount: 0,
          outgoingCount: 0
        });
      }
    }

    // Create edges and update node counts
    for (const dep of dependencies) {
      const sourceFile = dep.source.file;
      const targetNode = graph.nodes.get(dep.target);

      if (targetNode) {
        targetNode.incomingCount++;

        graph.edges.push({
          source: sourceFile,
          target: dep.target,
          type: dep.type,
          weight: 1
        });
      }
    }

    return graph;
  }

  /**
   * Detects circular dependencies within a set of files
   */
  detectCircularDependencies(allDependencies: Map<string, DependencyInfo[]>): CircularDependency[] {
    const circular: CircularDependency[] = [];
    const visited = new Set<string>();
    const recursionStack = new Set<string>();

    const detectCycle = (fileId: string, path: string[]): boolean => {
      if (recursionStack.has(fileId)) {
        // Found a cycle
        const cycleStart = path.indexOf(fileId);
        const cyclePath = path.slice(cycleStart);
        cyclePath.push(fileId);

        circular.push({
          files: cyclePath,
          severity: this.calculateCircularDependencySeverity(cyclePath)
        });
        return true;
      }

      if (visited.has(fileId)) {
        return false;
      }

      visited.add(fileId);
      recursionStack.add(fileId);

      const dependencies = allDependencies.get(fileId) || [];
      for (const dep of dependencies) {
        if (dep.type === 'import' && detectCycle(dep.target, [...path, fileId])) {
          // Continue checking for more cycles
        }
      }

      recursionStack.delete(fileId);
      return false;
    };

    // Check each file for circular dependencies
    for (const fileId of allDependencies.keys()) {
      if (!visited.has(fileId)) {
        detectCycle(fileId, []);
      }
    }

    return circular;
  }

  /**
   * Calculates coupling metrics between modules
   */
  calculateCouplingMetrics(dependencies: DependencyInfo[]): CouplingMetrics {
    const moduleMap = new Map<string, Set<string>>();

    // Group dependencies by source module
    for (const dep of dependencies) {
      const sourceModule = this.extractModuleFromPath(dep.source.file);
      if (!moduleMap.has(sourceModule)) {
        moduleMap.set(sourceModule, new Set());
      }
      moduleMap.get(sourceModule)!.add(dep.target);
    }

    // Calculate metrics
    let totalCoupling = 0;
    let maxCoupling = 0;
    let modulesWithHighCoupling = 0;

    for (const [module, dependencies] of moduleMap) {
      const couplingCount = dependencies.size;
      totalCoupling += couplingCount;
      maxCoupling = Math.max(maxCoupling, couplingCount);

      if (couplingCount > 10) { // Threshold for high coupling
        modulesWithHighCoupling++;
      }
    }

    const averageCoupling = moduleMap.size > 0 ? totalCoupling / moduleMap.size : 0;

    return {
      averageCoupling,
      maxCoupling,
      totalModules: moduleMap.size,
      highCouplingModules: modulesWithHighCoupling,
      couplingDistribution: moduleMap
    };
  }

  // Helper methods
  private extractModuleName(importText: string): string | null {
    // Extract module name from import statement
    const patterns = [
      /from\s+['"`]([^'"`]+)['"`]/, // from 'module'
      /import\s+['"`]([^'"`]+)['"`]/, // import 'module'
      /require\s*\(\s*['"`]([^'"`]+)['"`]\s*\)/ // require('module')
    ];

    for (const pattern of patterns) {
      const match = importText.match(pattern);
      if (match) return match[1];
    }

    return null;
  }

  private extractImportedSymbols(importText: string): string[] {
    const symbols: string[] = [];

    // Extract named imports: import { a, b, c } from 'module'
    const namedImportMatch = importText.match(/import\s*\{\s*([^}]+)\s*\}/);
    if (namedImportMatch) {
      const namedImports = namedImportMatch[1]
        .split(',')
        .map(s => s.trim().split(' as ')[0].trim())
        .filter(s => s.length > 0);
      symbols.push(...namedImports);
    }

    // Extract default import: import defaultExport from 'module'
    const defaultImportMatch = importText.match(/import\s+(\w+)\s+from/);
    if (defaultImportMatch) {
      symbols.push(defaultImportMatch[1]);
    }

    return symbols;
  }

  private extractFunctionName(node: Parser.SyntaxNode, content: string): string | null {
    // Get the function being called
    const firstChild = node.children[0];
    if (!firstChild) return null;

    if (firstChild.type === 'identifier') {
      return this.getNodeText(firstChild, content);
    }

    if (firstChild.type === 'member_expression') {
      const memberText = this.getNodeText(firstChild, content);
      return memberText;
    }

    return null;
  }

  private isBuiltinFunction(functionName: string): boolean {
    const builtins = [
      'console', 'parseInt', 'parseFloat', 'isNaN', 'isFinite',
      'setTimeout', 'setInterval', 'clearTimeout', 'clearInterval',
      'JSON', 'Math', 'Date', 'Array', 'Object', 'String', 'Number', 'Boolean',
      'Promise', 'Error', 'RegExp'
    ];

    return builtins.some(builtin => functionName.startsWith(builtin));
  }

  private extractCustomTypes(typeText: string): string[] {
    const types: string[] = [];

    // Simple heuristic: extract identifiers that start with uppercase (likely custom types)
    const typeMatches = typeText.match(/\b[A-Z]\w+/g);
    if (typeMatches) {
      types.push(...typeMatches.filter(type =>
        !['String', 'Number', 'Boolean', 'Array', 'Object', 'Date', 'Promise'].includes(type)
      ));
    }

    return types;
  }

  private extractGenericTypes(typeText: string): string[] {
    const types: string[] = [];

    // Extract types from generic parameters: <Type1, Type2>
    const genericMatch = typeText.match(/<([^>]+)>/);
    if (genericMatch) {
      const genericTypes = genericMatch[1]
        .split(',')
        .map(t => t.trim())
        .filter(t => /^[A-Z]/.test(t)); // Custom types typically start with uppercase

      types.push(...genericTypes);
    }

    return types;
  }

  private calculateCircularDependencySeverity(cyclePath: string[]): 'low' | 'medium' | 'high' {
    const cycleLength = cyclePath.length - 1; // Subtract 1 because first and last are the same

    if (cycleLength <= 2) return 'low';
    if (cycleLength <= 4) return 'medium';
    return 'high';
  }

  private extractModuleFromPath(filePath: string): string {
    // Extract module name from file path
    const parts = filePath.split('/');
    return parts[parts.length - 1].replace(/\.[^.]+$/, ''); // Remove extension
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
      line: node.startPosition.row + 1,
      column: node.startPosition.column + 1,
      endLine: node.endPosition.row + 1,
      endColumn: node.endPosition.column + 1
    };
  }
}

// Supporting interfaces
export interface DependencyGraph {
  nodes: Map<string, DependencyNode>;
  edges: DependencyEdge[];
}

export interface DependencyNode {
  id: string;
  name: string;
  type: 'import' | 'function-call' | 'inheritance' | 'composition';
  incomingCount: number;
  outgoingCount: number;
}

export interface DependencyEdge {
  source: string;
  target: string;
  type: 'import' | 'function-call' | 'inheritance' | 'composition';
  weight: number;
}

export interface CircularDependency {
  files: string[];
  severity: 'low' | 'medium' | 'high';
}

export interface CouplingMetrics {
  averageCoupling: number;
  maxCoupling: number;
  totalModules: number;
  highCouplingModules: number;
  couplingDistribution: Map<string, Set<string>>;
}
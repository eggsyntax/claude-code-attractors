"use strict";
/**
 * Alice's Dependency Analysis Module
 * Focuses on micro-level dependencies, import patterns, and code relationships
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.DependencyAnalyzer = void 0;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
class DependencyAnalyzer {
    constructor() {
        this.dependencyMap = new Map();
        this.fileContents = new Map();
        this.moduleStructures = new Map();
    }
    async analyzeDependencies(projectPath) {
        const files = await this.getSourceFiles(projectPath);
        // First pass: analyze each file's structure
        for (const file of files) {
            await this.analyzeFileStructure(file);
        }
        // Second pass: build dependency relationships
        const dependencies = await this.buildDependencyGraph(files);
        // Third pass: analyze patterns
        const circularDeps = this.detectCircularDependencies(dependencies);
        const chains = this.findDependencyChains(dependencies);
        return {
            dependencies,
            modules: Array.from(this.moduleStructures.values()),
            circularDependencies: circularDeps,
            dependencyChains: chains
        };
    }
    async getSourceFiles(projectPath) {
        const files = [];
        const walk = async (dir) => {
            try {
                const entries = await fs.promises.readdir(dir, { withFileTypes: true });
                for (const entry of entries) {
                    const fullPath = path.join(dir, entry.name);
                    if (entry.isDirectory() && !entry.name.startsWith('.') && entry.name !== 'node_modules') {
                        await walk(fullPath);
                    }
                    else if (entry.isFile() && this.isSourceFile(entry.name)) {
                        files.push(fullPath);
                    }
                }
            }
            catch (error) {
                // Skip inaccessible directories
            }
        };
        await walk(projectPath);
        return files;
    }
    isSourceFile(filename) {
        const extensions = ['.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'];
        return extensions.some(ext => filename.endsWith(ext));
    }
    async analyzeFileStructure(filePath) {
        try {
            const content = await fs.promises.readFile(filePath, 'utf-8');
            this.fileContents.set(filePath, content);
            const structure = {
                file: filePath,
                exports: this.extractExports(content),
                imports: this.extractImports(content),
                size: this.calculateSize(content),
                responsibilities: this.inferResponsibilities(content)
            };
            this.moduleStructures.set(filePath, structure);
        }
        catch (error) {
            console.warn(`Could not analyze file ${filePath}:`, error);
        }
    }
    extractExports(content) {
        const exports = {
            functions: [],
            classes: [],
            constants: [],
            types: []
        };
        // Export function declarations
        const funcExports = content.match(/export\s+(?:async\s+)?function\s+(\w+)/g) || [];
        exports.functions.push(...funcExports.map(match => match.match(/function\s+(\w+)/)?.[1] || ''));
        // Export class declarations
        const classExports = content.match(/export\s+(?:abstract\s+)?class\s+(\w+)/g) || [];
        exports.classes.push(...classExports.map(match => match.match(/class\s+(\w+)/)?.[1] || ''));
        // Export const/let/var
        const constExports = content.match(/export\s+(?:const|let|var)\s+(\w+)/g) || [];
        exports.constants.push(...constExports.map(match => match.match(/(?:const|let|var)\s+(\w+)/)?.[1] || ''));
        // Export type/interface
        const typeExports = content.match(/export\s+(?:type|interface)\s+(\w+)/g) || [];
        exports.types.push(...typeExports.map(match => match.match(/(?:type|interface)\s+(\w+)/)?.[1] || ''));
        // Named exports
        const namedExports = content.match(/export\s*{\s*([^}]+)\s*}/g) || [];
        namedExports.forEach(exportBlock => {
            const names = exportBlock.match(/{\s*([^}]+)\s*}/)?.[1]
                ?.split(',')
                .map(name => name.trim().split(' as ')[0]) || [];
            exports.constants.push(...names);
        });
        return exports;
    }
    extractImports(content) {
        const imports = [];
        // ES6 imports
        const importMatches = content.match(/import\s+.*?from\s+['"`]([^'"`]+)['"`]/g) || [];
        for (const importMatch of importMatches) {
            const fromMatch = importMatch.match(/from\s+['"`]([^'"`]+)['"`]/);
            if (!fromMatch)
                continue;
            const from = fromMatch[1];
            const isDefault = importMatch.includes('import ') && !importMatch.includes('{');
            let items = [];
            if (importMatch.includes('{')) {
                const itemsMatch = importMatch.match(/{([^}]+)}/);
                if (itemsMatch) {
                    items = itemsMatch[1].split(',').map(item => item.trim().split(' as ')[0]);
                }
            }
            else {
                const defaultMatch = importMatch.match(/import\s+(\w+)/);
                if (defaultMatch) {
                    items = [defaultMatch[1]];
                }
            }
            imports.push({ from, items, isDefault });
        }
        // CommonJS requires
        const requireMatches = content.match(/require\s*\(\s*['"`]([^'"`]+)['"`]\s*\)/g) || [];
        for (const requireMatch of requireMatches) {
            const moduleMatch = requireMatch.match(/['"`]([^'"`]+)['"`]/);
            if (moduleMatch) {
                imports.push({ from: moduleMatch[1], items: [], isDefault: true });
            }
        }
        return imports;
    }
    calculateSize(content) {
        const lines = content.split('\n').length;
        const functions = (content.match(/\bfunction\b/g) || []).length +
            (content.match(/=>\s*{/g) || []).length;
        const classes = (content.match(/\bclass\b/g) || []).length;
        return { lines, functions, classes };
    }
    inferResponsibilities(content) {
        const responsibilities = [];
        // Check for common patterns
        if (content.includes('express') || content.includes('app.')) {
            responsibilities.push('Web Server');
        }
        if (content.includes('database') || content.includes('db.') || content.includes('query')) {
            responsibilities.push('Data Access');
        }
        if (content.includes('test') || content.includes('expect') || content.includes('jest')) {
            responsibilities.push('Testing');
        }
        if (content.includes('config') || content.includes('environment')) {
            responsibilities.push('Configuration');
        }
        if (content.includes('auth') || content.includes('login') || content.includes('password')) {
            responsibilities.push('Authentication');
        }
        if (content.includes('log') || content.includes('console.')) {
            responsibilities.push('Logging');
        }
        if (content.includes('util') || content.includes('helper')) {
            responsibilities.push('Utility');
        }
        return responsibilities.length > 0 ? responsibilities : ['General'];
    }
    async buildDependencyGraph(files) {
        const dependencies = [];
        for (const file of files) {
            const structure = this.moduleStructures.get(file);
            if (!structure)
                continue;
            for (const importInfo of structure.imports) {
                // Resolve relative imports to absolute paths
                let targetFile = importInfo.from;
                if (importInfo.from.startsWith('.')) {
                    targetFile = path.resolve(path.dirname(file), importInfo.from);
                    // Try adding common extensions
                    const extensions = ['.js', '.ts', '.jsx', '.tsx', '/index.js', '/index.ts'];
                    for (const ext of extensions) {
                        const testPath = targetFile + ext;
                        if (files.includes(testPath)) {
                            targetFile = testPath;
                            break;
                        }
                    }
                }
                const relation = {
                    source: file,
                    target: targetFile,
                    type: 'import',
                    weight: importInfo.items.length || 1,
                    depth: this.calculateDependencyDepth(file, targetFile, files),
                    isCircular: false // Will be set by circular dependency detection
                };
                dependencies.push(relation);
            }
        }
        return dependencies;
    }
    calculateDependencyDepth(source, target, allFiles) {
        // Simple depth calculation - can be enhanced with graph traversal
        return 1;
    }
    detectCircularDependencies(dependencies) {
        const graph = new Map();
        const visited = new Set();
        const recursionStack = new Set();
        const cycles = [];
        // Build adjacency list
        for (const dep of dependencies) {
            if (!graph.has(dep.source)) {
                graph.set(dep.source, []);
            }
            graph.get(dep.source).push(dep.target);
        }
        const dfs = (node, path) => {
            if (recursionStack.has(node)) {
                const cycleStart = path.indexOf(node);
                if (cycleStart !== -1) {
                    cycles.push(path.slice(cycleStart).concat([node]));
                }
                return true;
            }
            if (visited.has(node)) {
                return false;
            }
            visited.add(node);
            recursionStack.add(node);
            const neighbors = graph.get(node) || [];
            for (const neighbor of neighbors) {
                if (dfs(neighbor, [...path, node])) {
                    // Mark dependencies as circular
                    const cyclicDep = dependencies.find(d => d.source === node && d.target === neighbor);
                    if (cyclicDep) {
                        cyclicDep.isCircular = true;
                    }
                }
            }
            recursionStack.delete(node);
            return false;
        };
        for (const node of graph.keys()) {
            if (!visited.has(node)) {
                dfs(node, []);
            }
        }
        return cycles;
    }
    findDependencyChains(dependencies) {
        // Find longest dependency chains to identify potential architectural issues
        const chains = [];
        // This would implement chain detection algorithm
        // For now, return empty array - implementation would go here
        return chains;
    }
}
exports.DependencyAnalyzer = DependencyAnalyzer;

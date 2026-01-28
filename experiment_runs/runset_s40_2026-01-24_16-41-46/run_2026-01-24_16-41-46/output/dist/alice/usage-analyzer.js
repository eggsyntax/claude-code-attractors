"use strict";
/**
 * Alice's Usage Pattern Analysis Module
 * Analyzes function calls, class instantiations, and usage patterns
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.UsageAnalyzer = void 0;
class UsageAnalyzer {
    constructor() {
        this.functionUsage = new Map();
        this.classUsage = new Map();
        this.callGraph = new Map();
    }
    async analyzeUsage(fileContents) {
        const functions = [];
        const classes = [];
        for (const [filePath, content] of fileContents.entries()) {
            const fileFunctions = await this.analyzeFunctions(filePath, content);
            const fileClasses = await this.analyzeClasses(filePath, content);
            functions.push(...fileFunctions);
            classes.push(...fileClasses);
        }
        // Analyze cross-file usage patterns
        await this.buildCallGraph(fileContents);
        await this.calculateUsageMetrics(functions, classes);
        const patterns = await this.detectUsagePatterns(fileContents, functions, classes);
        return { functions, classes, patterns };
    }
    async analyzeFunctions(filePath, content) {
        const functions = [];
        // Regular function declarations
        const functionDeclarations = content.matchAll(/(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)/g);
        for (const match of functionDeclarations) {
            const [fullMatch, name, params] = match;
            const line = this.getLineNumber(content, match.index || 0);
            const functionBody = this.extractFunctionBody(content, match.index || 0);
            functions.push({
                name,
                file: filePath,
                line,
                complexity: this.calculateCyclomaticComplexity(functionBody),
                linesOfCode: this.countLines(functionBody),
                parameters: this.countParameters(params),
                callCount: 0, // Will be calculated later
                callers: [],
                callees: this.extractFunctionCalls(functionBody),
                isExported: fullMatch.includes('export'),
                isAsync: fullMatch.includes('async')
            });
        }
        // Arrow functions
        const arrowFunctions = content.matchAll(/(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>/g);
        for (const match of arrowFunctions) {
            const [fullMatch, name, params] = match;
            const line = this.getLineNumber(content, match.index || 0);
            const functionBody = this.extractArrowFunctionBody(content, match.index || 0);
            functions.push({
                name,
                file: filePath,
                line,
                complexity: this.calculateCyclomaticComplexity(functionBody),
                linesOfCode: this.countLines(functionBody),
                parameters: this.countParameters(params),
                callCount: 0,
                callers: [],
                callees: this.extractFunctionCalls(functionBody),
                isExported: fullMatch.includes('export'),
                isAsync: fullMatch.includes('async')
            });
        }
        return functions;
    }
    async analyzeClasses(filePath, content) {
        const classes = [];
        const classMatches = content.matchAll(/(?:export\s+)?(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w,\s]+))?\s*{([^{}]*(?:{[^{}]*}[^{}]*)*)}/g);
        for (const match of classMatches) {
            const [fullMatch, name, extendsClass, implementsInterfaces, body] = match;
            const line = this.getLineNumber(content, match.index || 0);
            const methods = this.countMethods(body);
            const properties = this.countProperties(body);
            const inheritance = this.extractInheritance(extendsClass, implementsInterfaces);
            classes.push({
                name,
                file: filePath,
                line,
                methods,
                properties,
                inheritance,
                usageCount: 0, // Will be calculated later
                cohesion: this.calculateCohesion(body),
                coupling: this.calculateCoupling(body),
                isAbstract: fullMatch.includes('abstract')
            });
        }
        return classes;
    }
    getLineNumber(content, index) {
        return content.substring(0, index).split('\n').length;
    }
    extractFunctionBody(content, startIndex) {
        // Find the opening brace and extract the complete function body
        const remaining = content.substring(startIndex);
        const braceIndex = remaining.indexOf('{');
        if (braceIndex === -1)
            return '';
        let braceCount = 0;
        let i = braceIndex;
        for (; i < remaining.length; i++) {
            if (remaining[i] === '{')
                braceCount++;
            if (remaining[i] === '}')
                braceCount--;
            if (braceCount === 0)
                break;
        }
        return remaining.substring(braceIndex, i + 1);
    }
    extractArrowFunctionBody(content, startIndex) {
        const remaining = content.substring(startIndex);
        const arrowIndex = remaining.indexOf('=>');
        if (arrowIndex === -1)
            return '';
        // Check if it's a block body or expression body
        const afterArrow = remaining.substring(arrowIndex + 2).trim();
        if (afterArrow.startsWith('{')) {
            return this.extractFunctionBody(content, startIndex + arrowIndex + 2);
        }
        else {
            // Expression body - find the end (semicolon or newline)
            const endMatch = afterArrow.match(/^[^;\n]*/);
            return endMatch ? endMatch[0] : '';
        }
    }
    calculateCyclomaticComplexity(code) {
        let complexity = 1; // Base complexity
        // Count decision points
        const decisionKeywords = ['if', 'else if', 'while', 'for', 'switch', 'case', 'catch', '&&', '||', '?'];
        for (const keyword of decisionKeywords) {
            const regex = new RegExp(`\\b${keyword}\\b`, 'g');
            const matches = code.match(regex) || [];
            complexity += matches.length;
        }
        return complexity;
    }
    countLines(code) {
        return code.split('\n').filter(line => line.trim() !== '').length;
    }
    countParameters(paramString) {
        if (!paramString.trim())
            return 0;
        return paramString.split(',').length;
    }
    extractFunctionCalls(code) {
        const calls = [];
        // Function call pattern: identifier followed by parentheses
        const callMatches = code.matchAll(/(\w+)\s*\(/g);
        for (const match of callMatches) {
            const functionName = match[1];
            // Filter out keywords and common false positives
            if (!['if', 'for', 'while', 'switch', 'catch', 'return'].includes(functionName)) {
                calls.push(functionName);
            }
        }
        return [...new Set(calls)]; // Remove duplicates
    }
    countMethods(classBody) {
        const methodMatches = classBody.match(/(?:async\s+)?(\w+)\s*\([^)]*\)\s*{/g) || [];
        return methodMatches.length;
    }
    countProperties(classBody) {
        const propertyMatches = classBody.match(/(?:private|protected|public)?\s*(\w+)\s*[:=]/g) || [];
        return propertyMatches.length;
    }
    extractInheritance(extendsClass, implementsInterfaces) {
        const inheritance = [];
        if (extendsClass)
            inheritance.push(extendsClass);
        if (implementsInterfaces) {
            inheritance.push(...implementsInterfaces.split(',').map(i => i.trim()));
        }
        return inheritance;
    }
    calculateCohesion(classBody) {
        // Simplified cohesion calculation based on shared property usage
        // Real implementation would be more sophisticated
        return Math.random() * 0.3 + 0.7; // Mock value between 0.7-1.0
    }
    calculateCoupling(classBody) {
        // Count external dependencies mentioned in the class
        const externalReferences = classBody.match(/\bthis\.\w+/g) || [];
        return Math.min(externalReferences.length / 10, 1); // Normalize to 0-1
    }
    async buildCallGraph(fileContents) {
        // Build a map of who calls whom across all files
        for (const [filePath, content] of fileContents.entries()) {
            const functions = await this.analyzeFunctions(filePath, content);
            for (const func of functions) {
                const callerKey = `${filePath}:${func.name}`;
                if (!this.callGraph.has(callerKey)) {
                    this.callGraph.set(callerKey, new Set());
                }
                for (const callee of func.callees) {
                    this.callGraph.get(callerKey).add(callee);
                }
            }
        }
    }
    async calculateUsageMetrics(functions, classes) {
        // Calculate call counts and usage metrics based on call graph
        for (const func of functions) {
            const funcKey = `${func.file}:${func.name}`;
            // Count how many times this function is called
            for (const [caller, callees] of this.callGraph.entries()) {
                if (callees.has(func.name)) {
                    func.callCount++;
                    func.callers.push(caller);
                }
            }
        }
        // Similar calculation for classes (instantiations)
        for (const cls of classes) {
            let usageCount = 0;
            for (const [filePath, content] of [...arguments][2] || []) {
                const newInstanceMatches = content.match(new RegExp(`new\\s+${cls.name}\\s*\\(`, 'g')) || [];
                usageCount += newInstanceMatches.length;
            }
            cls.usageCount = usageCount;
        }
    }
    async detectUsagePatterns(fileContents, functions, classes) {
        const patterns = [];
        // Pattern 1: God functions (too many lines)
        for (const func of functions) {
            if (func.linesOfCode > 100) {
                patterns.push({
                    pattern: 'God Function',
                    description: 'Function with too many lines of code',
                    locations: [{
                            file: func.file,
                            line: func.line,
                            context: `Function ${func.name} has ${func.linesOfCode} lines`
                        }],
                    frequency: 1,
                    impact: 'negative',
                    category: 'complexity'
                });
            }
        }
        // Pattern 2: Unused functions
        for (const func of functions) {
            if (func.callCount === 0 && !func.isExported) {
                patterns.push({
                    pattern: 'Dead Code',
                    description: 'Function that is never called',
                    locations: [{
                            file: func.file,
                            line: func.line,
                            context: `Function ${func.name} is never called`
                        }],
                    frequency: 1,
                    impact: 'negative',
                    category: 'reuse'
                });
            }
        }
        // Pattern 3: High complexity functions
        for (const func of functions) {
            if (func.complexity > 10) {
                patterns.push({
                    pattern: 'High Complexity',
                    description: 'Function with high cyclomatic complexity',
                    locations: [{
                            file: func.file,
                            line: func.line,
                            context: `Function ${func.name} has complexity ${func.complexity}`
                        }],
                    frequency: 1,
                    impact: 'negative',
                    category: 'complexity'
                });
            }
        }
        // Pattern 4: Well-used utility functions
        for (const func of functions) {
            if (func.callCount > 10 && func.complexity <= 5) {
                patterns.push({
                    pattern: 'Utility Function',
                    description: 'Reusable function with low complexity',
                    locations: [{
                            file: func.file,
                            line: func.line,
                            context: `Function ${func.name} is called ${func.callCount} times`
                        }],
                    frequency: func.callCount,
                    impact: 'positive',
                    category: 'reuse'
                });
            }
        }
        return patterns;
    }
}
exports.UsageAnalyzer = UsageAnalyzer;

"use strict";
/**
 * Alice's Code Complexity Analysis Module
 * Analyzes various complexity metrics and identifies hotspots
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.ComplexityAnalyzer = void 0;
class ComplexityAnalyzer {
    analyzeComplexity(functions, classes, fileContents) {
        const overall = this.calculateOverallComplexity(functions, classes);
        const hotspots = this.identifyHotspots(functions, classes, fileContents);
        const distribution = this.calculateComplexityDistribution(functions);
        return { overall, hotspots, distribution };
    }
    analyzeReusability(functions, classes, fileContents) {
        const mostReused = this.findMostReusedElements(functions, classes);
        const duplicateCode = this.detectDuplicateCode(fileContents);
        const unusedCode = this.findUnusedCode(functions, classes);
        return { mostReused, duplicateCode, unusedCode };
    }
    calculateOverallComplexity(functions, classes) {
        if (functions.length === 0 && classes.length === 0)
            return 0;
        const functionComplexity = functions.reduce((sum, f) => sum + f.complexity, 0);
        const classComplexity = classes.reduce((sum, c) => sum + (c.methods * 2) + c.coupling * 10, 0);
        const totalElements = functions.length + classes.length;
        return Math.round((functionComplexity + classComplexity) / totalElements * 100) / 100;
    }
    identifyHotspots(functions, classes, fileContents) {
        const fileScores = new Map();
        // Initialize file scores
        for (const filePath of fileContents.keys()) {
            fileScores.set(filePath, { score: 0, reasons: [] });
        }
        // Score based on function complexity
        for (const func of functions) {
            const fileData = fileScores.get(func.file);
            if (func.complexity > 10) {
                fileData.score += func.complexity * 2;
                fileData.reasons.push(`High complexity function: ${func.name} (${func.complexity})`);
            }
            if (func.linesOfCode > 100) {
                fileData.score += func.linesOfCode / 10;
                fileData.reasons.push(`Large function: ${func.name} (${func.linesOfCode} lines)`);
            }
            if (func.parameters > 7) {
                fileData.score += func.parameters * 3;
                fileData.reasons.push(`Too many parameters: ${func.name} (${func.parameters})`);
            }
        }
        // Score based on class complexity
        for (const cls of classes) {
            const fileData = fileScores.get(cls.file);
            if (cls.methods > 20) {
                fileData.score += cls.methods;
                fileData.reasons.push(`Large class: ${cls.name} (${cls.methods} methods)`);
            }
            if (cls.coupling > 0.7) {
                fileData.score += cls.coupling * 50;
                fileData.reasons.push(`High coupling: ${cls.name} (${Math.round(cls.coupling * 100)}%)`);
            }
            if (cls.cohesion < 0.5) {
                fileData.score += (1 - cls.cohesion) * 30;
                fileData.reasons.push(`Low cohesion: ${cls.name} (${Math.round(cls.cohesion * 100)}%)`);
            }
        }
        // Score based on file size
        for (const [filePath, content] of fileContents.entries()) {
            const lines = content.split('\n').length;
            const fileData = fileScores.get(filePath);
            if (lines > 500) {
                fileData.score += lines / 100;
                fileData.reasons.push(`Large file: ${lines} lines`);
            }
        }
        // Convert to array and sort by score
        const hotspots = Array.from(fileScores.entries())
            .map(([file, data]) => ({
            file,
            score: Math.round(data.score * 100) / 100,
            reasons: data.reasons
        }))
            .filter(hotspot => hotspot.score > 10) // Only include files with significant issues
            .sort((a, b) => b.score - a.score)
            .slice(0, 10); // Top 10 hotspots
        return hotspots;
    }
    calculateComplexityDistribution(functions) {
        const ranges = [
            { range: '1-5', min: 1, max: 5 },
            { range: '6-10', min: 6, max: 10 },
            { range: '11-20', min: 11, max: 20 },
            { range: '21-50', min: 21, max: 50 },
            { range: '50+', min: 51, max: Infinity }
        ];
        return ranges.map(range => ({
            range: range.range,
            count: functions.filter(f => f.complexity >= range.min && f.complexity <= range.max).length
        }));
    }
    findMostReusedElements(functions, classes) {
        const reusedElements = [
            ...functions.map(f => ({ name: f.name, count: f.callCount, type: 'function' })),
            ...classes.map(c => ({ name: c.name, count: c.usageCount, type: 'class' }))
        ];
        return reusedElements
            .filter(element => element.count > 0)
            .sort((a, b) => b.count - a.count)
            .slice(0, 10);
    }
    detectDuplicateCode(fileContents) {
        const duplicates = [];
        const codeBlocks = new Map();
        // Extract code blocks (functions, classes) and normalize them
        for (const [filePath, content] of fileContents.entries()) {
            const functions = this.extractCodeBlocks(content, 'function');
            const classes = this.extractCodeBlocks(content, 'class');
            [...functions, ...classes].forEach(block => {
                const normalized = this.normalizeCode(block);
                if (normalized.length > 50) { // Only consider substantial blocks
                    if (!codeBlocks.has(normalized)) {
                        codeBlocks.set(normalized, []);
                    }
                    codeBlocks.get(normalized).push(filePath);
                }
            });
        }
        // Find duplicates
        for (const [normalizedCode, locations] of codeBlocks.entries()) {
            if (locations.length > 1) {
                const severity = this.assessDuplicationSeverity(normalizedCode, locations.length);
                duplicates.push({
                    pattern: this.createDuplicateDescription(normalizedCode),
                    locations,
                    severity
                });
            }
        }
        return duplicates.sort((a, b) => {
            const severityOrder = { high: 3, medium: 2, low: 1 };
            return severityOrder[b.severity] - severityOrder[a.severity];
        });
    }
    extractCodeBlocks(content, type) {
        const blocks = [];
        if (type === 'function') {
            const functionMatches = content.matchAll(/(?:function\s+\w+\s*\([^)]*\)\s*{[^{}]*(?:{[^{}]*}[^{}]*)*})|(?:\w+\s*=\s*\([^)]*\)\s*=>\s*{[^{}]*(?:{[^{}]*}[^{}]*)*})/g);
            for (const match of functionMatches) {
                blocks.push(match[0]);
            }
        }
        else {
            const classMatches = content.matchAll(/class\s+\w+[^{]*{[^{}]*(?:{[^{}]*}[^{}]*)*}/g);
            for (const match of classMatches) {
                blocks.push(match[0]);
            }
        }
        return blocks;
    }
    normalizeCode(code) {
        return code
            .replace(/\s+/g, ' ') // Normalize whitespace
            .replace(/\/\/.*$/gm, '') // Remove single-line comments
            .replace(/\/\*[\s\S]*?\*\//g, '') // Remove multi-line comments
            .replace(/\b\w+\b/g, (word) => {
            // Replace variable names with placeholders to focus on structure
            if (['const', 'let', 'var', 'function', 'class', 'if', 'else', 'for', 'while', 'return'].includes(word)) {
                return word;
            }
            return 'VAR';
        })
            .trim();
    }
    assessDuplicationSeverity(code, occurrences) {
        const length = code.length;
        if (length > 200 || occurrences > 3)
            return 'high';
        if (length > 100 || occurrences > 2)
            return 'medium';
        return 'low';
    }
    createDuplicateDescription(normalizedCode) {
        const lines = normalizedCode.split('\n').length;
        const chars = normalizedCode.length;
        if (normalizedCode.includes('function')) {
            return `Duplicate function pattern (~${lines} lines, ${chars} chars)`;
        }
        if (normalizedCode.includes('class')) {
            return `Duplicate class pattern (~${lines} lines, ${chars} chars)`;
        }
        return `Duplicate code block (~${lines} lines, ${chars} chars)`;
    }
    findUnusedCode(functions, classes) {
        const unused = [];
        // Unused functions (not called and not exported)
        for (const func of functions) {
            if (func.callCount === 0 && !func.isExported) {
                unused.push({
                    file: func.file,
                    item: func.name,
                    type: 'function'
                });
            }
        }
        // Unused classes (never instantiated and not exported)
        for (const cls of classes) {
            if (cls.usageCount === 0 && !this.isClassExported(cls)) {
                unused.push({
                    file: cls.file,
                    item: cls.name,
                    type: 'class'
                });
            }
        }
        return unused;
    }
    isClassExported(cls) {
        // This would need to be determined during the class analysis
        // For now, assume classes are exported if they have inheritance (likely public API)
        return cls.inheritance.length > 0;
    }
}
exports.ComplexityAnalyzer = ComplexityAnalyzer;

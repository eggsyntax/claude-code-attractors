"use strict";
/**
 * Alice's Main Structural Analysis Framework
 * Orchestrates micro-level code analysis and integrates with Bob's architectural insights
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.StructuralAnalyzer = void 0;
const dependency_analyzer_js_1 = require("./dependency-analyzer.js");
const usage_analyzer_js_1 = require("./usage-analyzer.js");
const complexity_analyzer_js_1 = require("./complexity-analyzer.js");
class StructuralAnalyzer {
    constructor() {
        this.dependencyAnalyzer = new dependency_analyzer_js_1.DependencyAnalyzer();
        this.usageAnalyzer = new usage_analyzer_js_1.UsageAnalyzer();
        this.complexityAnalyzer = new complexity_analyzer_js_1.ComplexityAnalyzer();
    }
    async analyzeProject(projectPath) {
        const timestamp = new Date().toISOString();
        console.log('🔍 Alice: Starting structural analysis...');
        // Phase 1: Analyze dependencies and module structure
        console.log('📊 Phase 1: Analyzing dependencies and modules');
        const dependencyResults = await this.dependencyAnalyzer.analyzeDependencies(projectPath);
        // Phase 2: Build file contents map for usage analysis
        const fileContents = await this.buildFileContentsMap(projectPath);
        // Phase 3: Analyze usage patterns
        console.log('🔄 Phase 2: Analyzing usage patterns');
        const usageResults = await this.usageAnalyzer.analyzeUsage(fileContents);
        // Phase 4: Calculate complexity and reusability metrics
        console.log('📈 Phase 3: Calculating complexity metrics');
        const complexityResults = this.complexityAnalyzer.analyzeComplexity(usageResults.functions, usageResults.classes, fileContents);
        const reusabilityResults = this.complexityAnalyzer.analyzeReusability(usageResults.functions, usageResults.classes, fileContents);
        console.log('✅ Alice: Structural analysis complete');
        // Assemble the complete analysis
        const structuralAnalysis = {
            timestamp,
            analyzer: 'alice',
            filePath: projectPath,
            analysisType: 'structural',
            dependencies: dependencyResults.dependencies,
            functions: usageResults.functions,
            classes: usageResults.classes,
            modules: dependencyResults.modules,
            patterns: usageResults.patterns,
            complexity: complexityResults,
            reusability: reusabilityResults
        };
        return structuralAnalysis;
    }
    async buildFileContentsMap(projectPath) {
        // This would typically be done by the dependency analyzer
        // but we need it here for the usage analyzer
        const fileContents = new Map();
        // For now, we'll let each analyzer handle its own file reading
        // In a real implementation, this would be optimized to read files once
        return fileContents;
    }
    // Method to help with cross-referencing with Bob's architectural analysis
    generateArchitecturalCrossReferences(structuralAnalysis, architecturalPatterns // Bob's architectural patterns
    ) {
        const crossReferences = [];
        // Cross-reference 1: Complexity hotspots vs Architectural patterns
        for (const hotspot of structuralAnalysis.complexity.hotspots) {
            if (hotspot.score > 50) {
                crossReferences.push({
                    structuralFinding: `High complexity in ${hotspot.file} (score: ${hotspot.score})`,
                    architecturalFinding: 'Architectural pattern analysis needed',
                    relationship: 'extends',
                    insight: `Complex file may indicate architectural issues or missing abstractions. Reasons: ${hotspot.reasons.join(', ')}`
                });
            }
        }
        // Cross-reference 2: Circular dependencies vs Layer violations
        for (const dep of structuralAnalysis.dependencies) {
            if (dep.isCircular) {
                crossReferences.push({
                    structuralFinding: `Circular dependency: ${dep.source} -> ${dep.target}`,
                    architecturalFinding: 'Potential layer violation',
                    relationship: 'explains',
                    insight: 'Circular dependencies often indicate architectural layer violations or missing abstractions'
                });
            }
        }
        // Cross-reference 3: Unused code vs Architectural dead branches
        for (const unused of structuralAnalysis.reusability.unusedCode) {
            crossReferences.push({
                structuralFinding: `Unused ${unused.type}: ${unused.item} in ${unused.file}`,
                architecturalFinding: 'Dead code branch',
                relationship: 'supports',
                insight: 'Unused code may indicate incomplete feature removal or over-engineered architecture'
            });
        }
        // Cross-reference 4: High reuse patterns vs Good architectural design
        for (const reused of structuralAnalysis.reusability.mostReused.slice(0, 3)) {
            if (reused.count > 10) {
                crossReferences.push({
                    structuralFinding: `Highly reused ${reused.type}: ${reused.name} (${reused.count} uses)`,
                    architecturalFinding: 'Good architectural component',
                    relationship: 'supports',
                    insight: `High reuse indicates well-designed, architectural component that provides good abstraction`
                });
            }
        }
        // Cross-reference 5: Module responsibilities vs Architectural layers
        const modulesByResponsibility = new Map();
        for (const module of structuralAnalysis.modules) {
            for (const responsibility of module.responsibilities) {
                if (!modulesByResponsibility.has(responsibility)) {
                    modulesByResponsibility.set(responsibility, []);
                }
                modulesByResponsibility.get(responsibility).push(module.file);
            }
        }
        for (const [responsibility, files] of modulesByResponsibility.entries()) {
            if (files.length > 1) {
                crossReferences.push({
                    structuralFinding: `${responsibility} responsibility spread across ${files.length} modules`,
                    architecturalFinding: 'Potential layer or concern separation',
                    relationship: 'explains',
                    insight: `Multiple modules handling ${responsibility} suggests need for better architectural separation or shared abstraction`
                });
            }
        }
        return crossReferences;
    }
    // Method to generate insights that bridge structural and architectural analysis
    generateCollaborativeInsights(structuralAnalysis) {
        const insights = [];
        // Insight 1: Complexity distribution patterns
        const highComplexityCount = structuralAnalysis.complexity.distribution
            .filter(d => ['21-50', '50+'].includes(d.range))
            .reduce((sum, d) => sum + d.count, 0);
        if (highComplexityCount > 0) {
            insights.push(`🔍 Found ${highComplexityCount} high-complexity functions - Bob should check for missing architectural patterns that could simplify these`);
        }
        // Insight 2: Dependency patterns
        const circularCount = structuralAnalysis.dependencies.filter(d => d.isCircular).length;
        if (circularCount > 0) {
            insights.push(`🔄 Detected ${circularCount} circular dependencies - Bob's layer analysis should investigate architectural boundaries`);
        }
        // Insight 3: Reusability patterns
        const duplicateHigh = structuralAnalysis.reusability.duplicateCode.filter(d => d.severity === 'high').length;
        if (duplicateHigh > 0) {
            insights.push(`⚡ Found ${duplicateHigh} high-severity code duplications - Bob should analyze if architectural patterns could eliminate this duplication`);
        }
        // Insight 4: Module structure insights
        const avgModuleSize = structuralAnalysis.modules.reduce((sum, m) => sum + m.size.lines, 0) / structuralAnalysis.modules.length;
        if (avgModuleSize > 300) {
            insights.push(`📏 Average module size is ${Math.round(avgModuleSize)} lines - Bob should check if architectural refactoring could improve modularity`);
        }
        // Insight 5: Responsibility distribution
        const responsibilityMap = new Map();
        for (const module of structuralAnalysis.modules) {
            for (const responsibility of module.responsibilities) {
                responsibilityMap.set(responsibility, (responsibilityMap.get(responsibility) || 0) + 1);
            }
        }
        const mostCommonResponsibility = [...responsibilityMap.entries()]
            .sort((a, b) => b[1] - a[1])[0];
        if (mostCommonResponsibility && mostCommonResponsibility[1] > 3) {
            insights.push(`🎯 "${mostCommonResponsibility[0]}" responsibility appears in ${mostCommonResponsibility[1]} modules - Bob should verify if this aligns with intended architecture`);
        }
        return insights;
    }
}
exports.StructuralAnalyzer = StructuralAnalyzer;

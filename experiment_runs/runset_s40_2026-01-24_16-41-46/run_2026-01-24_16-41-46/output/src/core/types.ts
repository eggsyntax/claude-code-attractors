/**
 * Core type definitions for CodeMirror analysis tool
 * Designed for collaborative AI analysis workflow
 */

// Base interfaces for analysis results
export interface AnalysisResult {
  timestamp: string;
  analyzer: 'alice' | 'bob';
  filePath: string;
  analysisType: string;
}

// Bob's architectural analysis types
export interface ArchitecturalPattern {
  name: string;
  description: string;
  files: string[];
  confidence: number;
  implications: string[];
}

export interface PerformanceInsight {
  type: 'bottleneck' | 'optimization' | 'anti-pattern';
  severity: 'low' | 'medium' | 'high';
  location: {
    file: string;
    line?: number;
    function?: string;
  };
  description: string;
  recommendation: string;
}

export interface ArchitecturalAnalysis extends AnalysisResult {
  analysisType: 'architectural';
  patterns: ArchitecturalPattern[];
  performance: PerformanceInsight[];
  layerAnalysis: {
    layer: string;
    files: string[];
    responsibilities: string[];
    coupling: 'low' | 'medium' | 'high';
  }[];
  scalabilityFactors: {
    factor: string;
    impact: 'positive' | 'negative' | 'neutral';
    details: string;
  }[];
}

// Alice's structural analysis types
export interface DependencyRelation {
  source: string;
  target: string;
  type: 'import' | 'extends' | 'implements' | 'calls' | 'instantiates';
  weight: number; // frequency or importance
  isCircular?: boolean;
  depth: number; // degrees of separation
}

export interface FunctionMetrics {
  name: string;
  file: string;
  line: number;
  complexity: number; // cyclomatic complexity
  linesOfCode: number;
  parameters: number;
  callCount: number; // how often it's called
  callers: string[]; // which functions call this
  callees: string[]; // which functions this calls
  isExported: boolean;
  isAsync: boolean;
}

export interface ClassMetrics {
  name: string;
  file: string;
  line: number;
  methods: number;
  properties: number;
  inheritance: string[]; // extends/implements
  usageCount: number; // how often instantiated/imported
  cohesion: number; // 0-1, how related are the methods
  coupling: number; // how many external dependencies
  isAbstract: boolean;
}

export interface ModuleStructure {
  file: string;
  exports: {
    functions: string[];
    classes: string[];
    constants: string[];
    types: string[];
  };
  imports: {
    from: string;
    items: string[];
    isDefault: boolean;
  }[];
  size: {
    lines: number;
    functions: number;
    classes: number;
  };
  responsibilities: string[]; // inferred from exports/functionality
}

export interface CodePattern {
  pattern: string;
  description: string;
  locations: {
    file: string;
    line: number;
    context: string;
  }[];
  frequency: number;
  impact: 'positive' | 'negative' | 'neutral';
  category: 'structure' | 'naming' | 'complexity' | 'reuse';
}

export interface StructuralAnalysis extends AnalysisResult {
  analysisType: 'structural';
  dependencies: DependencyRelation[];
  functions: FunctionMetrics[];
  classes: ClassMetrics[];
  modules: ModuleStructure[];
  patterns: CodePattern[];
  complexity: {
    overall: number;
    hotspots: { file: string; score: number; reasons: string[] }[];
    distribution: { range: string; count: number }[];
  };
  reusability: {
    mostReused: { name: string; count: number; type: 'function' | 'class' }[];
    duplicateCode: { pattern: string; locations: string[]; severity: 'low' | 'medium' | 'high' }[];
    unusedCode: { file: string; item: string; type: 'function' | 'class' | 'variable' }[];
  };
}

// Cross-reference system for collaboration
export interface CrossReference {
  structuralFinding: string;
  architecturalFinding: string;
  relationship: 'supports' | 'conflicts' | 'explains' | 'extends';
  insight: string;
}

// Combined analysis result
export interface UnifiedAnalysis {
  timestamp: string;
  projectPath: string;
  structural: StructuralAnalysis[];
  architectural: ArchitecturalAnalysis[];
  crossReferences: CrossReference[];
  summary: {
    keyFindings: string[];
    recommendations: string[];
    collaborationNotes: string[];
  };
}
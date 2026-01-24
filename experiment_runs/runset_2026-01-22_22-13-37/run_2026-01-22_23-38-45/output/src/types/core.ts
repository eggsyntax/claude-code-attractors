/**
 * Core type definitions for CodeMentor
 */

export interface CodeFile {
  id: string;
  path: string;
  content: string;
  language: string;
  lastModified: Date;
}

export interface AnalysisResult {
  fileId: string;
  patterns: DetectedPattern[];
  metrics: QualityMetrics;
  dependencies: DependencyInfo[];
  suggestions: Suggestion[];
  timestamp: Date;
}

export interface DetectedPattern {
  id: string;
  name: string;
  type: PatternType;
  description: string;
  location: CodeLocation;
  confidence: number;
  examples?: string[];
}

export type PatternType =
  | 'architectural'
  | 'design'
  | 'anti-pattern'
  | 'security'
  | 'performance'
  | 'maintainability';

export interface QualityMetrics {
  complexity: number;
  maintainability: number;
  testability: number;
  readability: number;
  performance: number;
}

export interface DependencyInfo {
  name: string;
  type: 'import' | 'function-call' | 'inheritance' | 'composition';
  source: CodeLocation;
  target: string;
}

export interface Suggestion {
  id: string;
  type: SuggestionType;
  priority: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  location: CodeLocation;
  examples?: CodeExample[];
  reasoning: string;
}

export type SuggestionType =
  | 'refactor'
  | 'performance'
  | 'security'
  | 'best-practice'
  | 'architecture'
  | 'testing';

export interface CodeExample {
  title: string;
  before?: string;
  after?: string;
  explanation: string;
}

export interface CodeLocation {
  file: string;
  line: number;
  column: number;
  endLine?: number;
  endColumn?: number;
}

export interface Review {
  id: string;
  projectId: string;
  title: string;
  description: string;
  files: string[]; // file IDs
  status: ReviewStatus;
  author: string;
  reviewers: string[];
  comments: Comment[];
  createdAt: Date;
  updatedAt: Date;
}

export type ReviewStatus = 'draft' | 'pending' | 'in-progress' | 'approved' | 'rejected';

export interface Comment {
  id: string;
  reviewId: string;
  author: string;
  content: string;
  location?: CodeLocation;
  replies: Comment[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  repository?: string;
  files: CodeFile[];
  reviews: Review[];
  collaborators: string[];
  createdAt: Date;
  updatedAt: Date;
}
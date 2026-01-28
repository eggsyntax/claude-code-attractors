//! CodeMetrics - A fast, extensible code metrics analyzer
//!
//! This library provides a flexible framework for analyzing code metrics
//! across multiple programming languages using tree-sitter parsers.

pub mod analyzer;
pub mod ast_analyzer;
pub mod cli;
pub mod core;
pub mod output;

pub use analyzer::{CodeAnalyzer, AnalysisResults};
pub use ast_analyzer::{ASTAnalyzer, FunctionAnalysis};
pub use core::{Language, CodeMetrics, CodeIssue};

/// Re-export commonly used types
pub type Result<T> = anyhow::Result<T>;
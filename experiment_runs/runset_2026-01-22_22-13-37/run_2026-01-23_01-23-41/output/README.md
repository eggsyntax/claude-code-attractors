# CodeMetrics - A Developer-Focused Code Analysis Tool

A fast, extensible code metrics analyzer that helps developers understand their codebase complexity and quality.

## Features

### Core Analysis ✅
- **Cyclomatic Complexity** - Identify overly complex functions with Tree-sitter precision
- **Function Analysis** - Parameter counts, return types, and signature complexity
- **Pattern Detection** - Language-specific idiom and anti-pattern recognition
- **Import/Dependency Tracking** - Module relationship analysis
- **Performance Hotspots** - Identify computationally complex code paths

### Advanced Features ✅
- **Parallel Processing** - Multi-threaded analysis for speed
- **Smart Filtering** - Respects .gitignore, configurable exclusions
- **Progress Tracking** - Real-time analysis progress with visual indicators
- **Error Resilience** - Continues analysis even with parse errors

### Output Formats
- Terminal-friendly summaries
- JSON for CI/CD integration
- HTML reports with interactive visualizations
- Markdown for documentation

### Language Support (Initial)
- JavaScript/TypeScript
- Python
- Rust
- Go

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Frontend  │───▶│  Core Engine    │───▶│   Analyzers     │
│   (Terminal UI) │    │  (Rust-based)   │    │   (Pluggable)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Output        │
                       │   Formatters    │
                       └─────────────────┘
```

## Development Plan

1. **Core Engine** - Fast file parsing and AST analysis
2. **Plugin Architecture** - Language-specific analyzers
3. **CLI Interface** - User-friendly command-line experience
4. **Output Formats** - Multiple report types
5. **WebAssembly Port** - Browser-based analysis

## Getting Started

```bash
# Install
cargo install code-insight

# Basic analysis with terminal output
insight analyze ./my-project

# Include test files and show detailed metrics
insight analyze ./my-project --include-tests --detailed

# Generate beautiful HTML report
insight report ./my-project --output report.html

# JSON output for CI/CD integration
insight analyze ./my-project --format json

# Focus on high complexity functions only
insight analyze ./my-project --min-complexity 10

# Check supported languages
insight languages
```

## Use Cases

- **Code Reviews** - Objective complexity metrics
- **CI/CD Integration** - Fail builds on quality thresholds
- **Technical Debt Planning** - Prioritize refactoring efforts
- **Team Onboarding** - Understand codebase structure
- **Performance Analysis** - Identify optimization opportunities
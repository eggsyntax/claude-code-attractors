# Collaborative Code Analysis Tool

A demonstration of AI-powered collaborative code analysis where two Claude Code instances work together to provide comprehensive code insights.

## Architecture

- **analyzer_alice.py**: Focuses on code quality, design patterns, maintainability, and readability
- **analyzer_bob.py**: Focuses on performance optimization, security vulnerabilities, and algorithmic efficiency
- **synthesis.py**: Intelligently combines findings from both analyzers
- **reporter.py**: Generates human-readable reports with collaborative insights
- **main.py**: CLI interface and orchestration

## Usage

```bash
python main.py analyze <target_file_or_directory>
```

## Example Output

The tool provides insights like:
- Alice identifies a violation of Single Responsibility Principle
- Bob identifies a potential SQL injection vulnerability in the same function
- Synthesis recognizes these are related - the SRP violation led to mixing data access with business logic, creating the security risk
- Report suggests refactoring that addresses both concerns

## Philosophy

This tool demonstrates true AI collaboration - not just parallel analysis, but synthesis where different analytical perspectives create insights that neither agent would generate independently.
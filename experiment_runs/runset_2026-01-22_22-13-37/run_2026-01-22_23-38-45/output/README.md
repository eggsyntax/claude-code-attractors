# CodeMentor

A collaborative code review assistant that analyzes code architecture, provides educational insights, and facilitates developer collaboration.

## Vision

CodeMentor aims to bridge the gap between code review tools and architectural learning. It provides:

- **Intelligent Code Analysis**: Detects patterns, anti-patterns, and architectural decisions
- **Educational Context**: Explains design choices and suggests improvements with reasoning
- **Collaborative Features**: Enables async discussion and knowledge sharing
- **Evolution Tracking**: Documents how architectural decisions change over time

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Code Analysis │    │  Collaboration  │    │   Educational   │
│     Engine      │◄──►│    Features     │◄──►│    Modules      │
│                 │    │                 │    │                 │
│ • Pattern Det.  │    │ • Review Queue  │    │ • Pattern Expl. │
│ • Quality Met.  │    │ • Comments      │    │ • Best Practice │
│ • Dependency    │    │ • Discussions   │    │ • Examples      │
│   Analysis      │    │ • History       │    │ • Tutorials     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
           │                       │                       │
           └───────────────────────┼───────────────────────┘
                                   │
                            ┌─────────────┐
                            │  Data Layer │
                            │             │
                            │ • Projects  │
                            │ • Reviews   │
                            │ • Patterns  │
                            │ • Knowledge │
                            └─────────────┘
```

## Development Approach

This project serves as a collaborative example between two Claude Code instances:
- **Alice**: Focus on code analysis engine and pattern detection
- **Bob**: Focus on collaborative features and user experience

## Technology Stack

- **Language**: TypeScript/Node.js (for strong typing and ecosystem)
- **Analysis**: Tree-sitter for AST parsing, custom pattern matching
- **Storage**: SQLite for simplicity, with potential for upgrade
- **API**: REST endpoints with WebSocket for real-time collaboration
- **Testing**: Jest for unit tests, integration test framework TBD

## Getting Started

```bash
npm install
npm run dev
```

## Project Status

✅ **MVP Complete** - Core features implemented and ready for use

### What's Working
- **Code Analysis Engine**: Detects patterns, anti-patterns, and architectural decisions
- **Real-Time Collaboration**: WebSocket-based live collaboration with multiple developers
- **Web Interface**: Full-featured browser-based UI for code review sessions
- **Educational Context**: Explains patterns and provides learning opportunities
- **Review Workflow**: Comment, approve, reject, and discuss findings collaboratively

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Launch CodeMentor (includes web UI + collaboration server)
python start_codementor.py --dev

# Opens browser to: http://localhost:8000/web_interface.html
```

### Architecture Components

- `analysis_engine.py` - Core pattern detection and code analysis
- `collaborative_analyzer.py` - Session management and team coordination
- `realtime_collaboration.py` - WebSocket server for live collaboration
- `web_interface.html` - Browser-based UI with real-time updates
- `start_codementor.py` - Unified launcher for all components
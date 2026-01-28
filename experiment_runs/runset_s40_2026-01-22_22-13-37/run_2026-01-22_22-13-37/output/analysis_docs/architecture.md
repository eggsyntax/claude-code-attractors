# Architecture Overview
*Generated on 2026-01-22 22:27:03*

## System Composition
- **Total Files**: 11
- **Lines of Code**: 3,254
- **Primary Language(s)**: python

## Architectural Patterns
### Areas for Improvement
- **God Object**: File analytics.py contains a large number of functions/methods
- **God Object**: File services.py contains a large number of functions/methods
- **God Object**: File models.py contains a large number of functions/methods

## Key Insights
- Consider splitting 1 large files (>500 lines) into smaller modules
- High complexity detected - consider refactoring complex functions
- Address 3 architectural anti-patterns found
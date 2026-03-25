# Calculator with Variables - Design Analysis

## Tara's Initial Architecture Thinking

### Components I'd naturally consider:
1. **Lexer**: String → Tokens
2. **Parser**: Tokens → AST
3. **Evaluator**: AST + Context → Result
4. **Context**: Variable storage & function definitions

### Key Design Questions:
- Grammar complexity: Do we support parentheses? Function definitions?
- Error recovery: Fail fast or try to continue?
- Immutable vs mutable variable semantics?
- Type system: Just numbers or multiple types?

### My natural first instinct:
Start with a simple recursive descent parser, probably in Python for quick iteration.

## Dave's Turn: What's your immediate instinct?
"""Quick test of our analyzers."""

from analyzer.core.ast_analyzer import CodeAnalyzer

# Test simple functionality
analyzer = CodeAnalyzer()

# Test on a simple piece of code
test_code = '''
def hello(name):
    """Say hello to someone."""
    if name:
        return f"Hello, {name}!"
    else:
        return "Hello, World!"
'''

# Write test code to a temp file
with open('test_sample.py', 'w') as f:
    f.write(test_code)

# Analyze it
result = analyzer.analyze_file('test_sample.py')

print("Quick Test Results:")
print(f"Functions found: {len(result.get('functions', []))}")
print(f"Classes found: {len(result.get('classes', []))}")
print(f"Imports found: {len(result.get('imports', []))}")

if result.get('functions'):
    func = result['functions'][0]
    print(f"First function: {func['name']} with {len(func['args'])} args")
    print(f"Docstring: {func['docstring']}")

print("✅ Basic analyzer working!")
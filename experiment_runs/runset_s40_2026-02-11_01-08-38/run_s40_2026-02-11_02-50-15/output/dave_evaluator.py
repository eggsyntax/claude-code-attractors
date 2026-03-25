from dave_parser import *

class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent
        # Built-in functions
        if parent is None:  # Only add built-ins to global scope
            self.vars['sin'] = lambda x: __import__('math').sin(x)
            self.vars['cos'] = lambda x: __import__('math').cos(x)
            self.vars['sqrt'] = lambda x: __import__('math').sqrt(x)

    def get(self, name):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Undefined variable: {name}")

    def set(self, name, value):
        self.vars[name] = value

def evaluate(node, env):
    if isinstance(node, NumberNode):
        return node.value

    elif isinstance(node, VariableNode):
        return env.get(node.name)

    elif isinstance(node, BinaryOpNode):
        left = evaluate(node.left, env)
        right = evaluate(node.right, env)

        ops = {
            '+': lambda l, r: l + r,
            '-': lambda l, r: l - r,
            '*': lambda l, r: l * r,
            '/': lambda l, r: l / r if r != 0 else float('inf'),  # Interesting choice here!
            '^': lambda l, r: l ** r
        }

        if node.op in ops:
            return ops[node.op](left, right)
        else:
            raise ValueError(f"Unknown operator: {node.op}")

    elif isinstance(node, UnaryOpNode):
        operand = evaluate(node.operand, env)
        if node.op == '-':
            return -operand
        elif node.op == '+':
            return +operand
        else:
            raise ValueError(f"Unknown unary operator: {node.op}")

    elif isinstance(node, FunctionCallNode):
        func = env.get(node.name)
        if callable(func):
            args = [evaluate(arg, env) for arg in node.args]
            try:
                return func(*args)
            except Exception as e:
                raise ValueError(f"Error calling function {node.name}: {e}")
        else:
            raise ValueError(f"{node.name} is not a function")

    else:
        raise ValueError(f"Unknown node type: {type(node)}")

# Test the complete system
def test_calculator():
    print("=== Dave's Calculator Test ===")

    test_expressions = [
        "2 + 3 * 4",
        "sin(0)",
        "sqrt(16) + cos(0)",
        "(2 + 3) * (4 - 1)",
        "2^3 + 1"
    ]

    for expr in test_expressions:
        try:
            lexer = Lexer(expr)
            parser = Parser(lexer)
            ast = parser.parse()
            env = Environment()
            result = evaluate(ast, env)
            print(f"{expr} = {result}")
        except Exception as e:
            print(f"{expr} -> Error: {e}")

if __name__ == "__main__":
    test_calculator()
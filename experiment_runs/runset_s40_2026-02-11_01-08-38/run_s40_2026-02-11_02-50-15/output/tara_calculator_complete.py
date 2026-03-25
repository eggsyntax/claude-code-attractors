import math
import re

class Token:
    def __init__(self, type, value, position=0):
        self.type = type
        self.value = value
        self.position = position

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def advance(self):
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def peek(self, offset=1):
        peek_pos = self.pos + offset
        return self.text[peek_pos] if peek_pos < len(self.text) else None

    def skip_whitespace(self):
        while self.current_char and self.current_char.isspace():
            self.advance()

    def number(self):
        result = ''
        while self.current_char and (self.current_char.isdigit() or self.current_char == '.'):
            result += self.current_char
            self.advance()
        return float(result)

    def identifier(self):
        result = ''
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return result

    def get_next_token(self):
        while self.current_char:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token('NUMBER', self.number())

            if self.current_char.isalpha():
                name = self.identifier()
                # Check if it's a function call by looking ahead for '('
                if self.current_char == '(':
                    return Token('FUNCTION', name)
                else:
                    return Token('IDENTIFIER', name)

            if self.current_char == '+':
                self.advance()
                return Token('PLUS', '+')

            if self.current_char == '-':
                self.advance()
                return Token('MINUS', '-')

            if self.current_char == '*':
                self.advance()
                return Token('MULTIPLY', '*')

            if self.current_char == '/':
                self.advance()
                return Token('DIVIDE', '/')

            if self.current_char == '(':
                self.advance()
                return Token('LPAREN', '(')

            if self.current_char == ')':
                self.advance()
                return Token('RPAREN', ')')

            if self.current_char == '=':
                self.advance()
                return Token('ASSIGN', '=')

            if self.current_char == ',':
                self.advance()
                return Token('COMMA', ',')

            raise ValueError(f"Unexpected character: {self.current_char}")

        return Token('EOF', None)

# AST Node classes
class NumberNode:
    def __init__(self, value):
        self.value = value

class BinaryOpNode:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class UnaryOpNode:
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr

class VariableNode:
    def __init__(self, name):
        self.name = name

class AssignmentNode:
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

class FunctionCallNode:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class FunctionDefNode:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def consume(self, expected_type):
        if self.current_token.type == expected_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise ValueError(f"Expected {expected_type}, got {self.current_token.type}")

    def parse(self):
        # Handle assignment or expression
        if (self.current_token.type == 'IDENTIFIER' and
            self.lexer.current_char == '='):
            return self.assignment()
        elif (self.current_token.type == 'IDENTIFIER' and
              self.lexer.current_char == '(' and
              self.lexer.peek() != ')'):  # Function definition
            return self.function_def()
        else:
            return self.expression()

    def assignment(self):
        name = self.current_token.value
        self.consume('IDENTIFIER')
        self.consume('ASSIGN')
        expr = self.expression()
        return AssignmentNode(name, expr)

    def function_def(self):
        name = self.current_token.value
        self.consume('IDENTIFIER')
        self.consume('LPAREN')

        params = []
        if self.current_token.type != 'RPAREN':
            params.append(self.current_token.value)
            self.consume('IDENTIFIER')
            while self.current_token.type == 'COMMA':
                self.consume('COMMA')
                params.append(self.current_token.value)
                self.consume('IDENTIFIER')

        self.consume('RPAREN')
        self.consume('ASSIGN')
        body = self.expression()
        return FunctionDefNode(name, params, body)

    def expression(self):
        return self.term()

    def term(self):
        result = self.factor()

        while self.current_token.type in ('PLUS', 'MINUS'):
            op = self.current_token.type
            self.consume(op)
            result = BinaryOpNode(result, op, self.factor())

        return result

    def factor(self):
        result = self.power()

        while self.current_token.type in ('MULTIPLY', 'DIVIDE'):
            op = self.current_token.type
            self.consume(op)
            result = BinaryOpNode(result, op, self.power())

        return result

    def power(self):
        return self.atom()

    def atom(self):
        token = self.current_token

        if token.type == 'NUMBER':
            self.consume('NUMBER')
            return NumberNode(token.value)

        elif token.type == 'MINUS':
            self.consume('MINUS')
            return UnaryOpNode('MINUS', self.atom())

        elif token.type == 'PLUS':
            self.consume('PLUS')
            return UnaryOpNode('PLUS', self.atom())

        elif token.type == 'LPAREN':
            self.consume('LPAREN')
            result = self.expression()
            self.consume('RPAREN')
            return result

        elif token.type == 'IDENTIFIER':
            name = token.value
            self.consume('IDENTIFIER')
            return VariableNode(name)

        elif token.type == 'FUNCTION':
            name = token.value
            self.consume('FUNCTION')
            self.consume('LPAREN')

            args = []
            if self.current_token.type != 'RPAREN':
                args.append(self.expression())
                while self.current_token.type == 'COMMA':
                    self.consume('COMMA')
                    args.append(self.expression())

            self.consume('RPAREN')
            return FunctionCallNode(name, args)

        else:
            raise ValueError(f"Unexpected token: {token.type}")

class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.vars = {}
        self.functions = {}

    def get_var(self, name):
        if name in self.vars:
            return self.vars[name]
        elif self.parent:
            return self.parent.get_var(name)
        else:
            raise ValueError(f"Undefined variable: {name}")

    def set_var(self, name, value):
        self.vars[name] = value

    def get_function(self, name):
        if name in self.functions:
            return self.functions[name]
        elif self.parent:
            return self.parent.get_function(name)
        else:
            return None

    def set_function(self, name, params, body):
        self.functions[name] = (params, body)

class UserFunction:
    def __init__(self, params, body, closure_env):
        self.params = params
        self.body = body
        self.closure_env = closure_env

class Evaluator:
    def __init__(self):
        self.global_env = Environment()
        # Built-in functions
        self.builtins = {
            'sin': math.sin,
            'cos': math.cos,
            'sqrt': math.sqrt,
            'abs': abs,
            'log': math.log,
            'exp': math.exp
        }

    def evaluate(self, node, env=None):
        if env is None:
            env = self.global_env

        if isinstance(node, NumberNode):
            return node.value

        elif isinstance(node, VariableNode):
            return env.get_var(node.name)

        elif isinstance(node, BinaryOpNode):
            left = self.evaluate(node.left, env)
            right = self.evaluate(node.right, env)

            if node.op == 'PLUS':
                return left + right
            elif node.op == 'MINUS':
                return left - right
            elif node.op == 'MULTIPLY':
                return left * right
            elif node.op == 'DIVIDE':
                if right == 0:
                    raise ValueError("Division by zero")
                return left / right

        elif isinstance(node, UnaryOpNode):
            expr_val = self.evaluate(node.expr, env)
            if node.op == 'MINUS':
                return -expr_val
            elif node.op == 'PLUS':
                return expr_val

        elif isinstance(node, AssignmentNode):
            value = self.evaluate(node.expr, env)
            env.set_var(node.name, value)
            return value

        elif isinstance(node, FunctionCallNode):
            # Check built-ins first
            if node.name in self.builtins:
                args = [self.evaluate(arg, env) for arg in node.args]
                return self.builtins[node.name](*args)

            # Check user-defined functions
            func_def = env.get_function(node.name)
            if func_def:
                params, body = func_def
                if len(node.args) != len(params):
                    raise ValueError(f"Function {node.name} expects {len(params)} args, got {len(node.args)}")

                # Create new environment for function execution
                func_env = Environment(env)
                for param, arg in zip(params, node.args):
                    func_env.set_var(param, self.evaluate(arg, env))

                return self.evaluate(body, func_env)

            raise ValueError(f"Unknown function: {node.name}")

        elif isinstance(node, FunctionDefNode):
            env.set_function(node.name, node.params, node.body)
            return f"Function {node.name} defined"

        else:
            raise ValueError(f"Unknown node type: {type(node)}")

def calculate(expression):
    """Main function to evaluate mathematical expressions with variables and functions."""
    try:
        lexer = Lexer(expression)
        parser = Parser(lexer)
        ast = parser.parse()

        evaluator = Evaluator()
        result = evaluator.evaluate(ast)

        return result
    except Exception as e:
        return f"Error: {str(e)}"

# Interactive calculator
def interactive_calculator():
    """Run an interactive calculator session."""
    evaluator = Evaluator()
    print("Enhanced Calculator (type 'quit' to exit)")
    print("Supports: +, -, *, /, variables, functions")
    print("Built-ins: sin, cos, sqrt, abs, log, exp")
    print("Examples:")
    print("  > 2 + 3 * 4")
    print("  > x = 5")
    print("  > y = x * 2 + 1")
    print("  > sin(3.14159/2)")
    print("  > f(x) = x * x + 1")
    print("  > f(5)")

    while True:
        try:
            expr = input("> ").strip()
            if expr.lower() == 'quit':
                break
            if not expr:
                continue

            lexer = Lexer(expr)
            parser = Parser(lexer)
            ast = parser.parse()

            result = evaluator.evaluate(ast)
            print(f"  {result}")

        except Exception as e:
            print(f"  Error: {str(e)}")

if __name__ == "__main__":
    # Test the calculator
    test_cases = [
        "2 + 3 * 4",
        "x = 10",
        "y = x + 5",
        "sin(1.5708)",
        "f(x) = x * x",
        "f(3)",
        "g(x, y) = x + y * 2",
        "g(1, 2)"
    ]

    evaluator = Evaluator()
    for expr in test_cases:
        try:
            lexer = Lexer(expr)
            parser = Parser(lexer)
            ast = parser.parse()
            result = evaluator.evaluate(ast)
            print(f"{expr} = {result}")
        except Exception as e:
            print(f"{expr} -> Error: {e}")
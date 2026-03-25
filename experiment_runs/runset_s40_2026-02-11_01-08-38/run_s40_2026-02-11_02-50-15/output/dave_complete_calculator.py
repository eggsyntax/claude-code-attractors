# Dave's Complete Calculator Implementation
from enum import Enum

# LEXER
class TokenType(Enum):
    NUMBER = "NUMBER"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    POWER = "POWER"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    IDENTIFIER = "IDENTIFIER"
    COMMA = "COMMA"
    EOF = "EOF"

class Token:
    def __init__(self, type_, value, position):
        self.type = type_
        self.value = value
        self.position = position

    def __repr__(self):
        return f'Token({self.type}, {self.value}, {self.position})'

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def error(self, message):
        raise Exception(f"Lexer error at position {self.pos}: {message}")

    def advance(self):
        """Move to the next character"""
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def peek_ahead(self, steps=1):
        """Look ahead without advancing position"""
        peek_pos = self.pos + steps
        if peek_pos < len(self.text):
            return self.text[peek_pos]
        return None

    def skip_whitespace(self):
        """Skip whitespace characters"""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def read_number(self):
        """Read a number (integer or float)"""
        result = ''
        start_pos = self.pos

        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            result += self.current_char
            self.advance()

        try:
            if '.' in result:
                return Token(TokenType.NUMBER, float(result), start_pos)
            else:
                return Token(TokenType.NUMBER, int(result), start_pos)
        except ValueError:
            self.error(f"Invalid number format: {result}")

    def read_identifier(self):
        """Read an identifier (variable or function name)"""
        result = ''
        start_pos = self.pos

        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()

        return Token(TokenType.IDENTIFIER, result, start_pos)

    def get_next_token(self):
        """Get the next token from the input"""
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return self.read_number()

            if self.current_char.isalpha() or self.current_char == '_':
                return self.read_identifier()

            current_pos = self.pos

            if self.current_char == '+':
                self.advance()
                return Token(TokenType.PLUS, '+', current_pos)

            if self.current_char == '-':
                self.advance()
                return Token(TokenType.MINUS, '-', current_pos)

            if self.current_char == '*':
                self.advance()
                return Token(TokenType.MULTIPLY, '*', current_pos)

            if self.current_char == '/':
                self.advance()
                return Token(TokenType.DIVIDE, '/', current_pos)

            if self.current_char == '^':
                self.advance()
                return Token(TokenType.POWER, '^', current_pos)

            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(', current_pos)

            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')', current_pos)

            if self.current_char == ',':
                self.advance()
                return Token(TokenType.COMMA, ',', current_pos)

            self.error(f"Unexpected character: '{self.current_char}'")

        return Token(TokenType.EOF, None, self.pos)

# PARSER
class NumberNode:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f'NumberNode({self.value})'

class VariableNode:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f'VariableNode({self.name})'

class BinaryOpNode:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self):
        return f'BinaryOpNode({self.left}, {self.op}, {self.right})'

class UnaryOpNode:
    def __init__(self, op, operand):
        self.op = op
        self.operand = operand
    def __repr__(self):
        return f'UnaryOpNode({self.op}, {self.operand})'

class FunctionCallNode:
    def __init__(self, name, args):
        self.name = name
        self.args = args
    def __repr__(self):
        return f'FunctionCallNode({self.name}, {self.args})'

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self, message):
        raise Exception(f"Parser error at token {self.current_token}: {message}")

    def eat(self, token_type):
        """Consume a token of the expected type"""
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Expected {token_type}, got {self.current_token.type}")

    def parse(self):
        """Parse the expression"""
        return self.expression()

    def expression(self):
        """expression: term ((PLUS | MINUS) term)*"""
        node = self.term()

        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            self.eat(token.type)
            node = BinaryOpNode(left=node, op=token.value, right=self.term())

        return node

    def term(self):
        """term: power ((MULTIPLY | DIVIDE) power)*"""
        node = self.power()

        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            token = self.current_token
            self.eat(token.type)
            node = BinaryOpNode(left=node, op=token.value, right=self.power())

        return node

    def power(self):
        """power: factor (POWER factor)*"""
        node = self.factor()

        while self.current_token.type == TokenType.POWER:
            token = self.current_token
            self.eat(TokenType.POWER)
            node = BinaryOpNode(left=node, op=token.value, right=self.factor())

        return node

    def factor(self):
        """factor: (PLUS | MINUS) factor | NUMBER | LPAREN expression RPAREN | function_call | IDENTIFIER"""
        token = self.current_token

        if token.type == TokenType.PLUS:
            self.eat(TokenType.PLUS)
            node = UnaryOpNode('+', self.factor())
            return node

        elif token.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            node = UnaryOpNode('-', self.factor())
            return node

        elif token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return NumberNode(token.value)

        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expression()
            self.eat(TokenType.RPAREN)
            return node

        elif token.type == TokenType.IDENTIFIER:
            name = token.value
            self.eat(TokenType.IDENTIFIER)

            # Check if this is a function call
            if self.current_token.type == TokenType.LPAREN:
                self.eat(TokenType.LPAREN)
                args = []
                if self.current_token.type != TokenType.RPAREN:
                    args.append(self.expression())
                    while self.current_token.type == TokenType.COMMA:
                        self.eat(TokenType.COMMA)
                        args.append(self.expression())
                self.eat(TokenType.RPAREN)
                return FunctionCallNode(name, args)
            else:
                return VariableNode(name)

        self.error(f"Unexpected token in factor: {token}")

# EVALUATOR
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
            '/': lambda l, r: l / r if r != 0 else float('inf'),
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

# TEST
def test_calculator():
    print("=== Dave's Complete Calculator Test ===")

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
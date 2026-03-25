import re
from enum import Enum
from typing import Dict, Any, Optional

class TokenType(Enum):
    NUMBER = "NUMBER"
    IDENTIFIER = "IDENTIFIER"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    POWER = "POWER"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    ASSIGN = "ASSIGN"  # Adding assignment operator
    EOF = "EOF"

class Token:
    def __init__(self, type_: TokenType, value: Any):
        self.type = type_
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def advance(self):
        """Move to the next character"""
        self.pos += 1
        if self.pos >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def peek_ahead(self, steps=1):
        """Look ahead without advancing position"""
        peek_pos = self.pos + steps
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def read_number(self):
        """Read a number (integer or float)"""
        result = ''
        while (self.current_char is not None and
               (self.current_char.isdigit() or self.current_char == '.')):
            result += self.current_char
            self.advance()

        if '.' in result:
            return float(result)
        return int(result)

    def read_identifier(self):
        """Read an identifier (variable or function name)"""
        result = ''
        while (self.current_char is not None and
               (self.current_char.isalnum() or self.current_char == '_')):
            result += self.current_char
            self.advance()
        return result

    def get_next_token(self):
        """Get the next token from the input"""
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(TokenType.NUMBER, self.read_number())

            if self.current_char.isalpha() or self.current_char == '_':
                identifier = self.read_identifier()
                return Token(TokenType.IDENTIFIER, identifier)

            if self.current_char == '+':
                self.advance()
                return Token(TokenType.PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(TokenType.MINUS, '-')

            if self.current_char == '*':
                next_char = self.peek_ahead()
                if next_char == '*':
                    self.advance()
                    self.advance()
                    return Token(TokenType.POWER, '**')
                else:
                    self.advance()
                    return Token(TokenType.MULTIPLY, '*')

            if self.current_char == '/':
                self.advance()
                return Token(TokenType.DIVIDE, '/')

            if self.current_char == '(':
                self.advance()
                return Token(TokenType.LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(TokenType.RPAREN, ')')

            # Tara's addition: Assignment operator
            if self.current_char == '=':
                self.advance()
                return Token(TokenType.ASSIGN, '=')

            raise ValueError(f"Invalid character: {self.current_char}")

        return Token(TokenType.EOF, None)

# AST Node classes
class ASTNode:
    pass

class Number(ASTNode):
    def __init__(self, value):
        self.value = value

class BinaryOp(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class UnaryOp(ASTNode):
    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

class Variable(ASTNode):
    def __init__(self, name):
        self.name = name

class FunctionCall(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args

# Tara's addition: Assignment node
class Assignment(ASTNode):
    def __init__(self, variable, value):
        self.variable = variable
        self.value = value

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self, message="Invalid syntax"):
        raise SyntaxError(f"Parser error: {message}")

    def eat(self, token_type: TokenType):
        """Consume a token of the expected type"""
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Expected {token_type}, got {self.current_token.type}")

    def peek_ahead_token(self):
        """Look at the next token without consuming current one"""
        current_pos = self.lexer.pos
        current_char = self.lexer.current_char
        next_token = self.lexer.get_next_token()

        # Restore lexer state
        self.lexer.pos = current_pos
        self.lexer.current_char = current_char

        return next_token

    def factor(self):
        """Parse factor: number, variable, function call, or parenthesized expression"""
        token = self.current_token

        if token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return Number(token.value)

        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expression()
            self.eat(TokenType.RPAREN)
            return node

        elif token.type == TokenType.IDENTIFIER:
            name = token.value
            self.eat(TokenType.IDENTIFIER)

            # Check if it's a function call
            if self.current_token.type == TokenType.LPAREN:
                self.eat(TokenType.LPAREN)
                args = []

                if self.current_token.type != TokenType.RPAREN:
                    args.append(self.expression())
                    while self.current_token.type == TokenType.MULTIPLY:  # Using * as argument separator for simplicity
                        self.eat(TokenType.MULTIPLY)
                        args.append(self.expression())

                self.eat(TokenType.RPAREN)
                return FunctionCall(name, args)
            else:
                return Variable(name)

        elif token.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            return UnaryOp(token, self.factor())

        elif token.type == TokenType.PLUS:
            self.eat(TokenType.PLUS)
            return UnaryOp(token, self.factor())

        else:
            self.error(f"Unexpected token: {token}")

    def power(self):
        """Parse power operations (right associative)"""
        node = self.factor()

        if self.current_token.type == TokenType.POWER:
            operator = self.current_token
            self.eat(TokenType.POWER)
            # Right associative - don't loop, just recurse
            right = self.power()
            node = BinaryOp(node, operator, right)

        return node

    def term(self):
        """Parse multiplication and division"""
        node = self.power()

        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            operator = self.current_token
            if operator.type == TokenType.MULTIPLY:
                self.eat(TokenType.MULTIPLY)
            elif operator.type == TokenType.DIVIDE:
                self.eat(TokenType.DIVIDE)

            node = BinaryOp(left=node, operator=operator, right=self.power())

        return node

    def expression(self):
        """Parse addition and subtraction"""
        node = self.term()

        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            operator = self.current_token
            if operator.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            elif operator.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)

            node = BinaryOp(left=node, operator=operator, right=self.term())

        return node

    # Tara's addition: Parse assignment statements
    def statement(self):
        """Parse a statement (assignment or expression)"""
        if (self.current_token.type == TokenType.IDENTIFIER and
            self.peek_ahead_token().type == TokenType.ASSIGN):

            var_name = self.current_token.value
            self.eat(TokenType.IDENTIFIER)
            self.eat(TokenType.ASSIGN)
            value = self.expression()
            return Assignment(var_name, value)
        else:
            return self.expression()

    def parse(self):
        """Parse the entire expression"""
        return self.statement()

class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.variables: Dict[str, float] = {}

    def get(self, name: str) -> float:
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            raise NameError(f"Variable '{name}' is not defined")

    def set(self, name: str, value: float):
        self.variables[name] = value

class Calculator:
    def __init__(self):
        self.environment = Environment()
        # Built-in functions - keeping Dave's approach
        self.functions = {
            'sin': lambda x: __import__('math').sin(x),
            'cos': lambda x: __import__('math').cos(x),
            'tan': lambda x: __import__('math').tan(x),
            'sqrt': lambda x: __import__('math').sqrt(x),
            'abs': lambda x: abs(x),
            'log': lambda x: __import__('math').log(x),
        }

    def evaluate(self, node: ASTNode) -> float:
        """Evaluate an AST node"""
        if isinstance(node, Number):
            return float(node.value)

        elif isinstance(node, Variable):
            try:
                return self.environment.get(node.name)
            except NameError:
                raise NameError(f"Variable '{node.name}' is not defined")

        elif isinstance(node, BinaryOp):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)

            if node.operator.type == TokenType.PLUS:
                return left + right
            elif node.operator.type == TokenType.MINUS:
                return left - right
            elif node.operator.type == TokenType.MULTIPLY:
                return left * right
            elif node.operator.type == TokenType.DIVIDE:
                if right == 0:
                    return float('inf')  # Keeping Dave's approach here
                return left / right
            elif node.operator.type == TokenType.POWER:
                return left ** right

        elif isinstance(node, UnaryOp):
            operand = self.evaluate(node.operand)
            if node.operator.type == TokenType.MINUS:
                return -operand
            elif node.operator.type == TokenType.PLUS:
                return operand

        elif isinstance(node, FunctionCall):
            if node.name in self.functions:
                args = [self.evaluate(arg) for arg in node.args]
                try:
                    return self.functions[node.name](*args)
                except Exception as e:
                    raise ValueError(f"Error calling function '{node.name}': {str(e)}")
            else:
                raise NameError(f"Unknown function: {node.name}")

        # Tara's addition: Handle assignments
        elif isinstance(node, Assignment):
            value = self.evaluate(node.value)
            self.environment.set(node.variable, value)
            return value  # Assignment returns the assigned value

        raise ValueError(f"Unknown node type: {type(node)}")

    def calculate(self, expression: str) -> float:
        """Calculate the result of an expression"""
        try:
            lexer = Lexer(expression)
            parser = Parser(lexer)
            ast = parser.parse()
            return self.evaluate(ast)
        except Exception as e:
            raise ValueError(f"Error evaluating expression '{expression}': {str(e)}")

# Test the extended calculator
if __name__ == "__main__":
    calc = Calculator()

    print("Testing Dave's original functionality:")
    print(f"2 + 3 * 4 = {calc.calculate('2 + 3 * 4')}")
    print(f"sin(0) = {calc.calculate('sin(0)')}")
    print(f"2 ** 3 = {calc.calculate('2 ** 3')}")

    print("\nTesting Tara's assignment extension:")
    print(f"x = 5: {calc.calculate('x = 5')}")
    print(f"x + 3 = {calc.calculate('x + 3')}")
    print(f"y = x * 2: {calc.calculate('y = x * 2')}")
    print(f"y = {calc.calculate('y')}")
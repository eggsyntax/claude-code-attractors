class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        """Parse the tokens into an AST"""
        return self.expression()

    def expression(self):
        """Parse expressions with operator precedence"""
        return self.term()

    def term(self):
        """Handle addition and subtraction (lowest precedence)"""
        node = self.factor()

        while self.current < len(self.tokens) and self.tokens[self.current].type in ['PLUS', 'MINUS']:
            op = self.tokens[self.current]
            self.current += 1
            right = self.factor()
            node = BinaryOp(node, op, right)

        return node

    def factor(self):
        """Handle multiplication and division (higher precedence)"""
        node = self.primary()

        while self.current < len(self.tokens) and self.tokens[self.current].type in ['MULTIPLY', 'DIVIDE']:
            op = self.tokens[self.current]
            self.current += 1
            right = self.primary()
            node = BinaryOp(node, op, right)

        return node

    def primary(self):
        """Handle numbers, variables, parentheses, and function calls"""
        token = self.tokens[self.current]

        if token.type == 'NUMBER':
            self.current += 1
            return NumberNode(float(token.value))

        elif token.type == 'IDENTIFIER':
            # Look ahead to see if this is a function call
            if self.current + 1 < len(self.tokens) and self.tokens[self.current + 1].type == 'LPAREN':
                return self.function_call()
            else:
                self.current += 1
                return VariableNode(token.value)

        elif token.type == 'LPAREN':
            self.current += 1  # consume '('
            node = self.expression()
            if self.current < len(self.tokens) and self.tokens[self.current].type == 'RPAREN':
                self.current += 1  # consume ')'
            return node

        else:
            raise SyntaxError(f"Unexpected token: {token}")

    def function_call(self):
        """Parse function calls like sin(x) or pow(2, 3)"""
        func_name = self.tokens[self.current].value
        self.current += 1  # consume function name
        self.current += 1  # consume '('

        args = []
        while self.current < len(self.tokens) and self.tokens[self.current].type != 'RPAREN':
            args.append(self.expression())
            if self.current < len(self.tokens) and self.tokens[self.current].type == 'COMMA':
                self.current += 1  # consume ','

        self.current += 1  # consume ')'
        return FunctionCallNode(func_name, args)

# AST Node classes
class NumberNode:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Number({self.value})"

class VariableNode:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Variable({self.name})"

class BinaryOp:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f"BinaryOp({self.left}, {self.op.type}, {self.right})"

class FunctionCallNode:
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"FunctionCall({self.name}, {self.args})"
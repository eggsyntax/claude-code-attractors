from dave_lexer import Lexer, Token, TokenType

class ASTNode:
    pass

class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"NumberNode({self.value})"

class VariableNode(ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"VariableNode({self.name})"

class BinaryOpNode(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"BinaryOpNode({self.left}, {self.operator}, {self.right})"

class FunctionCallNode(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"FunctionCallNode({self.name}, {self.args})"

class AssignmentNode(ASTNode):
    def __init__(self, variable, value):
        self.variable = variable
        self.value = value

    def __repr__(self):
        return f"AssignmentNode({self.variable}, {self.value})"

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self, message="Invalid syntax"):
        raise Exception(f"Parse error: {message} at token {self.current_token}")

    def consume(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(f"Expected {token_type}, got {self.current_token.type}")

    def parse(self):
        """Parse a statement (assignment or expression)"""
        if (self.current_token.type == TokenType.IDENTIFIER and
            self.peek_ahead() == TokenType.ASSIGN):
            return self.assignment()
        else:
            return self.expression()

    def peek_ahead(self):
        """Look ahead one token without consuming"""
        saved_pos = self.lexer.pos
        saved_char = self.lexer.current_char
        next_token = self.lexer.get_next_token()

        # Restore lexer state
        self.lexer.pos = saved_pos
        self.lexer.current_char = saved_char

        return next_token.type

    def assignment(self):
        """Parse variable assignment: identifier = expression"""
        var_name = self.current_token.value
        self.consume(TokenType.IDENTIFIER)
        self.consume(TokenType.ASSIGN)
        value = self.expression()
        return AssignmentNode(var_name, value)

    def expression(self):
        """Parse expression with addition/subtraction precedence"""
        node = self.term()

        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current_token
            self.consume(op.type)
            right = self.term()
            node = BinaryOpNode(node, op.value, right)

        return node

    def term(self):
        """Parse term with multiplication/division precedence"""
        node = self.factor()

        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            op = self.current_token
            self.consume(op.type)
            right = self.factor()
            node = BinaryOpNode(node, op.value, right)

        return node

    def factor(self):
        """Parse factor (numbers, variables, parenthesized expressions, function calls)"""
        token = self.current_token

        if token.type == TokenType.NUMBER:
            self.consume(TokenType.NUMBER)
            return NumberNode(token.value)

        elif token.type == TokenType.IDENTIFIER:
            name = token.value
            self.consume(TokenType.IDENTIFIER)

            # Check if it's a function call
            if self.current_token.type == TokenType.LPAREN:
                return self.function_call(name)
            else:
                return VariableNode(name)

        elif token.type == TokenType.LPAREN:
            self.consume(TokenType.LPAREN)
            node = self.expression()
            self.consume(TokenType.RPAREN)
            return node

        else:
            self.error(f"Unexpected token {token.type}")

    def function_call(self, name):
        """Parse function call: identifier(arg1, arg2, ...)"""
        self.consume(TokenType.LPAREN)

        args = []
        if self.current_token.type != TokenType.RPAREN:
            args.append(self.expression())

            while self.current_token.type == TokenType.COMMA:
                self.consume(TokenType.COMMA)
                args.append(self.expression())

        self.consume(TokenType.RPAREN)
        return FunctionCallNode(name, args)

# Test the parser
if __name__ == "__main__":
    test_expressions = [
        "2 + 3 * 4",
        "x = 5 + 3",
        "sin(x)",
        "max(1, 2, 3)",
        "(2 + 3) * 4"
    ]

    for expr in test_expressions:
        print(f"\nParsing: {expr}")
        lexer = Lexer(expr)
        parser = Parser(lexer)
        try:
            ast = parser.parse()
            print(f"AST: {ast}")
        except Exception as e:
            print(f"Error: {e}")
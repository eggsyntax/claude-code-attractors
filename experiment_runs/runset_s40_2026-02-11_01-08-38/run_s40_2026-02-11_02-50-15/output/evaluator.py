class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.functions = {}
        self.parent = parent

    def get_var(self, name):
        if name in self.vars:
            return self.vars[name]
        elif self.parent:
            return self.parent.get_var(name)
        else:
            raise NameError(f"Variable '{name}' not found")

    def set_var(self, name, value):
        self.vars[name] = value

    def get_function(self, name):
        if name in self.functions:
            return self.functions[name]
        elif self.parent:
            return self.parent.get_function(name)
        else:
            raise NameError(f"Function '{name}' not found")

    def set_function(self, name, params, body):
        self.functions[name] = (params, body)

class Evaluator:
    def __init__(self):
        self.global_env = Environment()
        # Add built-in functions
        self.global_env.set_function('sqrt', ['x'], 'builtin')
        self.global_env.set_function('abs', ['x'], 'builtin')

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

            if node.op == '+':
                return left + right
            elif node.op == '-':
                return left - right
            elif node.op == '*':
                return left * right
            elif node.op == '/':
                if right == 0:
                    raise ZeroDivisionError("Division by zero")
                return left / right

        elif isinstance(node, UnaryOpNode):
            operand = self.evaluate(node.operand, env)
            if node.op == '-':
                return -operand
            elif node.op == '+':
                return operand

        elif isinstance(node, FunctionCallNode):
            func_name = node.name
            args = [self.evaluate(arg, env) for arg in node.args]

            # Handle built-ins
            if func_name == 'sqrt':
                import math
                return math.sqrt(args[0])
            elif func_name == 'abs':
                return abs(args[0])

            # Handle user-defined functions
            params, body = env.get_function(func_name)
            if len(args) != len(params):
                raise ValueError(f"Function '{func_name}' expects {len(params)} arguments, got {len(args)}")

            # Create new environment for function execution
            func_env = Environment(env)
            for param, arg in zip(params, args):
                func_env.set_var(param, arg)

            return self.evaluate(body, func_env)

        elif isinstance(node, AssignmentNode):
            value = self.evaluate(node.value, env)
            env.set_var(node.var_name, value)
            return value

        elif isinstance(node, FunctionDefNode):
            env.set_function(node.name, node.params, node.body)
            return f"Function '{node.name}' defined"

        else:
            raise TypeError(f"Unknown node type: {type(node)}")
import lark
import esolang.level3_functions

grammar = esolang.level3_functions.grammar + r"""
    %extend start: if_stmt
        | while_loop

    if_stmt: "if" "(" expr ")" block ("else" block)?
    while_loop: "while" "(" expr ")" block

    %override function_def: "lambda" parameters ":" start

    parameters: "(" [NAME ("," NAME)*] ")"

    %override range: "range" "(" expr ("," expr ("," expr)?)? ")"

    ?expr: sum
        | expr "==" sum        -> eq
        | expr "!=" sum        -> neq
        | expr "<" sum         -> lt
        | expr ">" sum         -> gt
        | expr "<=" sum        -> le
        | expr ">=" sum        -> ge

    %extend ?product:
        | product "%" atom    -> mod
"""

parser = lark.Lark(grammar)

class Interpreter(esolang.level3_functions.Interpreter):
    '''
    >>> interpreter = Interpreter()
    >>> interpreter.visit(parser.parse("if (1) {a=5}; a"))
    5
    >>> interpreter.visit(parser.parse("if (0) {a=5} else {a=10}; a"))
    10
    >>> interpreter.visit(parser.parse("a=0; while (a<5) {a = a + 1}; a"))
    5
    >>> interpreter.visit(parser.parse("for i in range(1+2) {print(i)}"))
    0
    1
    2
    >>> interpreter.visit(parser.parse("a=3; for i in range(a*2) {print(i)}"))
    0
    1
    2
    3
    4
    5
    >>> interpreter.visit(parser.parse("for i in range(2, 5) {print(i)}"))
    2
    3
    4
    >>> interpreter.visit(parser.parse("for i in range(2, 10, 3) {print(i)}"))
    2
    5
    8
    >>> _ = interpreter.visit(parser.parse("for n in range(2, 20) { is_prime = 1; for i in range(2, n) { if (n % i == 0) { is_prime = 0; } }; if (is_prime) { print(n); } }"))
    2
    3
    5
    7
    11
    13
    17
    19
    '''
    def eq(self, tree):
        return int(self.visit(tree.children[0]) == self.visit(tree.children[1]))

    def neq(self, tree):
        return int(self.visit(tree.children[0]) != self.visit(tree.children[1]))

    def lt(self, tree):
        return int(self.visit(tree.children[0]) < self.visit(tree.children[1]))

    def gt(self, tree):
        return int(self.visit(tree.children[0]) > self.visit(tree.children[1]))

    def le(self, tree):
        return int(self.visit(tree.children[0]) <= self.visit(tree.children[1]))

    def ge(self, tree):
        return int(self.visit(tree.children[0]) >= self.visit(tree.children[1]))

    def mod(self, tree):
        return self.visit(tree.children[0]) % self.visit(tree.children[1])

    def if_stmt(self, tree):
        condition = self.visit(tree.children[0])
        if condition:
            res = self.execute_block_in_current_scope(tree.children[1])
        elif len(tree.children) > 2:
            res = self.execute_block_in_current_scope(tree.children[2])
        else:
            res = None
        return res

    def while_loop(self, tree):
        result = None
        while self.visit(tree.children[0]):
            result = self.execute_block_in_current_scope(tree.children[1])
        return result

    def execute_block_in_current_scope(self, block_tree):
        res = None
        for child in block_tree.children:
            res = self.visit(child)
        return res

    def range(self, tree):
        args = [self.visit(child) for child in tree.children]
        return range(*args)

    def forloop(self, tree):
        varname = tree.children[0].value
        xs = self.visit(tree.children[1])
        result = None
        for x in xs:
            self.stack.append({varname: x})
            result = self.visit(tree.children[2])
            self.stack.pop()
        return result

    def assign_var(self, tree):
        name = tree.children[0].value
        value_node = tree.children[1]
        
        # Handle function definition
        if isinstance(value_node, lark.Tree) and value_node.data == 'function_def':
            value_node.func_name = name
        
        value = self.visit(value_node)
        self._assign_to_stack(name, value)
        return value

    def function_def(self, tree):
        params_tree = tree.children[0]
        body = tree.children[1]

        if params_tree.children:
            names = [param.value for param in params_tree.children if isinstance(param, lark.Token) and param.type == 'NAME']
        else:
            names = []

        func_name = getattr(tree, 'func_name', None)

        def foo(*args):
            if len(args) != len(names):
                raise ValueError(f"Expected {len(names)} arguments, got {len(args)}")
            
            # Create new scope with parent scope's content
            local_scope = self.stack[-1].copy()
            
            # Add parameters to local scope
            for name, arg in zip(names, args):
                local_scope[name] = arg
                
            # Push the new scope
            self.stack.append(local_scope)
            try:
                ret = self.visit(body)
            finally:
                self.stack.pop()
            return ret

        # If this is a named function, add it to the current scope
        if func_name is not None:
            self._assign_to_stack(func_name, foo)
            
        return foo

    def _get_from_stack(self, name):
        # Start from the most recent scope and work backwards
        for scope in reversed(self.stack):
            if name in scope:
                return scope[name]
        raise NameError(f"Name '{name}' is not defined")

    def mul(self, tree):
        v0 = self.visit(tree.children[0])
        v1 = self.visit(tree.children[1])
        if isinstance(v0, int) and isinstance(v1, int):
            return v0 * v1
        raise TypeError("Multiplication is only supported for integers")
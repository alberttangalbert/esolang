import lark
import pprint
import esolang.level2_loops


grammar = esolang.level2_loops.grammar + r"""
    %extend start: function_call
        | function_def

    function_def: "lambda" NAME ("," NAME)* ":" start

    ?args_list: start ("," start)*

    function_call: NAME "(" args_list ")"
        | NAME "(" ")"
"""
parser = lark.Lark(grammar)


class Interpreter(esolang.level2_loops.Interpreter):
    '''
    >>> interpreter = Interpreter()
    >>> interpreter.visit(parser.parse("a=3; print(a)"))
    3
    >>> interpreter.visit(parser.parse("a=4; b=5; stack()"))
    [{'a': 4, 'b': 5}]
    >>> interpreter.visit(parser.parse("a=4; b=5; {c=6}; stack()"))
    [{'a': 4, 'b': 5}]
    >>> interpreter.visit(parser.parse("print(10)"))
    10
    >>> interpreter.visit(parser.parse("for i in range(10) {print(i)}"))
    0
    1
    2
    3
    4
    5
    6
    7
    8
    9
    >>> interpreter.visit(parser.parse(r"f = lambda x : x; f(5)"))
    5
    >>> interpreter.visit(parser.parse(r"f = lambda x,y : x+y; f(5, 6)"))
    11
    >>> interpreter.visit(parser.parse(r"f = lambda x,y,z : x+y-z; f(5, 6, 7)"))
    4
    >>> interpreter.visit(parser.parse(r"f = lambda x,y,z : {print(x); print(y); print(z); {z = 10; print(z);}; print(z);}; f(5, 6, 7)"))
    5
    6
    7
    10
    10
    '''
    def __init__(self):
        super().__init__()

        # we add a new level to the stack
        # the top-most level will be for "built-in" functions
        # all lower levels will be for user-defined functions/variables
        # the stack() function will only print the user defined functions
        self.stack.append({})
        self.stack[0]['print'] = print
        self.stack[0]['stack'] = lambda: pprint.pprint(self.stack[1:])

    def function_def(self, tree):
        names = [token.value for token in tree.children[:-1]]
        body = tree.children[-1]
        def foo(*args):
            self.stack.append({})
            for name, arg in zip(names, args):
                self._assign_to_stack(name, arg)
            ret = self.visit(body)
            self.stack.pop()
            return ret
        return foo

    def function_call(self, tree):
        name = tree.children[0]

        # the tree can be structured in different ways depending on the number of arguments;
        # the following lines convert the params list into a single flat list
        params = [self.visit(child) for child in tree.children[1:]]
        params = [param for param in params if param is not None]
        if len(params) > 0 and isinstance(params[-1], list):
            params = params[0]

        return self._get_from_stack(name)(*params)
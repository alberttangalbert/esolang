import lark
import pprint
import esolang.level2_loops
from collections import ChainMap

grammar = esolang.level2_loops.grammar + r"""
    %extend start: function_def

    %extend atom: function_call

    function_def: "lambda" param_list ":" start

    param_list: NAME ("," NAME)*

    args_list: start ("," start)*

    function_call: NAME "(" [args_list] ")"
"""

parser = lark.Lark(grammar)

class Interpreter(esolang.level2_loops.Interpreter):
    '''
    [Your existing doctests remain unchanged]
    '''

    def __init__(self):
        super().__init__()
        self.stack.append({})
        self.stack[0]['print'] = print
        self.stack[0]['stack'] = lambda: pprint.pprint(self.stack[1:])

    def function_def(self, tree):
        param_list = tree.children[0]
        names = [child.value for child in param_list.children]
        body = tree.children[1]

        def foo(*args):
            local_scope = dict(zip(names, args))
            # Use ChainMap to combine local and outer scopes
            self.stack.append(ChainMap(local_scope, *self.stack))
            ret = self.visit(body)
            self.stack.pop()
            return ret

        return foo

    def function_call(self, tree):
        name = tree.children[0].value
        func = self._get_from_stack(name)
        args = []
        if len(tree.children) > 1:
            args_list = tree.children[1]
            args = [self.visit(arg) for arg in args_list.children]
        return func(*args)

    def assign_var(self, tree):
        name = tree.children[0].value
        value = self.visit(tree.children[1])
        self._assign_to_stack(name, value)
        return value
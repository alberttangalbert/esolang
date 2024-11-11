import lark
import esolang.level3_functions

grammar = esolang.level3_functions.grammar + r"""
    %extend start: if_stmt
        | while_loop
        | forloop

    if_stmt: "if" condition block ("else" block)?
    condition: "(" comparison ")"
    while_loop: "while" condition block

    %override forloop: "for" NAME "in" range block
    %override range: "range" "(" start ("," start ("," start)?)? ")"

    ?comparison: sum
        | comparison "<" sum   -> lt
        | comparison ">" sum   -> gt
        | comparison "==" sum  -> eq
        | comparison "<=" sum  -> le
        | comparison ">=" sum  -> ge
        | comparison "!=" sum  -> ne
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
    >>> interpreter.visit(parser.parse("factorial = lambda n : { if (n <= 1) {1} else {n * factorial(n - 1)} }; print(factorial(5))"))
    120
    '''
    def condition(self, tree):
        return self.visit(tree.children[0])

    def if_stmt(self, tree):
        condition = self.visit(tree.children[0])
        if condition:
            return self.visit(tree.children[1])
        elif len(tree.children) == 3:
            return self.visit(tree.children[2])
        else:
            return None

    def while_loop(self, tree):
        result = None
        while self.visit(tree.children[0]):
            result = self.visit(tree.children[1])
        return result

    def lt(self, tree):
        return self.visit(tree.children[0]) < self.visit(tree.children[1])

    def gt(self, tree):
        return self.visit(tree.children[0]) > self.visit(tree.children[1])

    def eq(self, tree):
        return self.visit(tree.children[0]) == self.visit(tree.children[1])

    def le(self, tree):
        return self.visit(tree.children[0]) <= self.visit(tree.children[1])

    def ge(self, tree):
        return self.visit(tree.children[0]) >= self.visit(tree.children[1])

    def ne(self, tree):
        return self.visit(tree.children[0]) != self.visit(tree.children[1])

    def range(self, tree):
        args = [self.visit(child) for child in tree.children]
        return range(*args)

    def forloop(self, tree):
        varname = tree.children[0].value
        xs = self.visit(tree.children[1])
        self.stack.append({})
        for x in xs:
            self.stack[-1][varname] = x
            result = self.visit(tree.children[2])
        self.stack.pop()
        return result
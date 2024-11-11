import lark
import esolang.level1_statements


grammar = esolang.level1_statements.grammar + r"""
    %extend start: forloop

    forloop: "for" NAME "in" range block

    range: "range" "(" NUMBER ")"
"""
parser = lark.Lark(grammar)


class Interpreter(esolang.level1_statements.Interpreter):
    '''
    >>> interpreter = Interpreter()
    >>> interpreter.visit(parser.parse("for i in range(10) {i}"))
    9
    >>> interpreter.visit(parser.parse("a=0; for i in range(10) {a = a + i}"))
    45
    >>> interpreter.visit(parser.parse("a=0; for i in range(10) {a = a + i}; a"))
    45
    >>> interpreter.visit(parser.parse("a=0; for i in range(10) {a = a + i}; i")) # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    ValueError: Variable i undefined
    '''
    def range(self, tree):
        return range(int(tree.children[0].value))

    def forloop(self, tree):
        varname = tree.children[0].value
        xs = self.visit(tree.children[1])

        # Execute the loop, modifying the outer scope variable `a`
        for x in xs:
            self._assign_to_stack(varname, x)  # Assign loop variable in outer scope
            result = self.visit(tree.children[2])
        
        # Remove loop variable after the loop finishes
        if varname in self.stack[-1]:
            del self.stack[-1][varname]
        
        return result
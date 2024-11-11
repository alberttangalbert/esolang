# esolang ![](https://github.com/alberttangalbert/esolang/actions/workflows/tests.yml/badge.svg)

A simple esolang for experimenting with different syntax and semantics of programming languages.

Level4 tests: add "if" and "while" functions and override "for" and "range" functions

Trying:
    interpreter = Interpreter()
Expecting nothing
ok
Trying:
    interpreter.visit(parser.parse("if (1) {a=5}; a"))
Expecting:
    5
ok
Trying:
    interpreter.visit(parser.parse("if (0) {a=5} else {a=10}; a"))
Expecting:
    10
ok
Trying:
    interpreter.visit(parser.parse("a=0; while (a<5) {a = a + 1}; a"))
Expecting:
    5
ok
Trying:
    interpreter.visit(parser.parse("for i in range(1+2) {print(i)}"))
Expecting:
    0
    1
    2
ok
Trying:
    interpreter.visit(parser.parse("a=3; for i in range(a*2) {print(i)}"))
Expecting:
    0
    1
    2
    3
    4
    5
ok
Trying:
    interpreter.visit(parser.parse("for i in range(2, 5) {print(i)}"))
Expecting:
    2
    3
    4
ok
Trying:
    interpreter.visit(parser.parse("for i in range(2, 10, 3) {print(i)}"))
Expecting:
    2
    5
    8
ok
Trying:
    interpreter.visit(parser.parse("factorial = lambda n : { if (n <= 1) {1} else {n * factorial(n - 1)} }; print(factorial(5))"))
Expecting:
    120
ok
12 items had no tests:
    level4_logic
    level4_logic.Interpreter.condition
    level4_logic.Interpreter.eq
    level4_logic.Interpreter.forloop
    level4_logic.Interpreter.ge
    level4_logic.Interpreter.gt
    level4_logic.Interpreter.if_stmt
    level4_logic.Interpreter.le
    level4_logic.Interpreter.lt
    level4_logic.Interpreter.ne
    level4_logic.Interpreter.range
    level4_logic.Interpreter.while_loop
1 items passed all tests:
   9 tests in level4_logic.Interpreter
9 tests in 13 items.
9 passed and 0 failed.
Test passed.

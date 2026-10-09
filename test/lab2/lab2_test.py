import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from language import (
    AstPrinter,
    Binary,
    Grouping,
    Literal,
    Token,
    TokenType,
    Unary,
)


def operator(lexeme):
    return Token(TokenType.OPERATOR, lexeme, lexeme)


printer = AstPrinter()


# Binary arithmetic, unary negation, grouping, and numeric literals.
arithmetic = Binary(
    Unary(operator("-"), Literal(1)),
    operator("*"),
    Grouping(
        Binary(
            Binary(Literal(45.67), operator("+"), Literal(2)),
            operator("/"),
            Binary(Literal(8), operator("%"), Literal(3)),
        )
    ),
)

# Equality and comparison operators with boolean and nil literals.
comparisons = Binary(
    Binary(
        Binary(Literal(True), operator("=="), Literal(False)),
        operator("!="),
        Literal(None),
    ),
    operator("=="),
    Binary(
        Binary(Literal(1), operator("<"), Literal(2)),
        operator(">="),
        Binary(Literal(3), operator("<="), Literal(4)),
    ),
)

# String literals, logical negation, and nested arithmetic/comparisons.
nested = Unary(
    operator("!"),
    Grouping(
        Binary(
            Binary(Literal("working"), operator("=="), Literal("language")),
            operator("!="),
            Binary(
                Binary(Literal(10), operator("-"), Literal(4)),
                operator(">"),
                Binary(Literal(2), operator("+"), Literal(3)),
            ),
        )
    ),
)


print("Arithmetic Expression:")
print(printer.print(arithmetic) + "\n")

print("\nComparison Expression:")
print(printer.print(comparisons) + "\n")

print("\nNested Expression:")
print(printer.print(nested) + "\n")
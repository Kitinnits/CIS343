import sys
import enum

args = sys.argv[1:]

class TokenType(enum.Enum):
    IDENTIFIER = "IDENTIFIER"
    OPERATOR = "OPERATOR"
    LITERAL = "LITERAL"
    KEYWORD = "KEYWORD"
    EOF = "EOF"

class Token:
    def __init__(self, type, value, lexeme=None, line=None):
        self.type = type
        self.value = value
        self.lexeme = lexeme
        self.line = line

    def __repr__(self):
        return f"Token(type={self.type}, value={self.value}, lexeme={self.lexeme}, line={self.line})"


class Expr:
    pass


class Literal(Expr):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Literal({self.value!r})"


class Unary(Expr):
    def __init__(self, operator, right):
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"Unary({self.operator.lexeme!r}, {self.right!r})"


class Binary(Expr):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return (
            f"Binary({self.left!r}, {self.operator.lexeme!r}, "
            f"{self.right!r})"
        )


class Grouping(Expr):
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f"Grouping({self.expression!r})"


class AstPrinter:

    def print(self, expression):
        if isinstance(expression, Binary):
            return self.visit_binary(expression)
        if isinstance(expression, Grouping):
            return self.visit_grouping(expression)
        if isinstance(expression, Literal):
            return self.visit_literal(expression)
        if isinstance(expression, Unary):
            return self.visit_unary(expression)
        raise TypeError(f"Unsupported expression type: {type(expression).__name__}")

    def visit_binary(self, expression):
        return self.parenthesize(
            expression.operator.lexeme,
            expression.left,
            expression.right,
        )

    def visit_grouping(self, expression):
        return self.parenthesize("group", expression.expression)

    def visit_literal(self, expression):
        if expression.value is None:
            return "none"
        if isinstance(expression.value, bool):
            return str(expression.value).lower()
        return str(expression.value)

    def visit_unary(self, expression):
        return self.parenthesize(expression.operator.lexeme, expression.right)

    def parenthesize(self, name, *expressions):
        parts = [f"({name}"]
        parts.extend(f" {self.print(expression)}" for expression in expressions)
        parts.append(")")
        return "".join(parts)


class ParseError(Exception):
    pass


class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        expression = self.expression()
        if not self.is_at_end():
            raise self.error(self.peek(), "Expected end of expression.")
        return expression

    def expression(self):
        return self.equality()

    def equality(self):
        expression = self.comparison()

        while self.match_lexemes("!=", "=="):
            operator = self.previous()
            right = self.comparison()
            expression = Binary(expression, operator, right)

        return expression

    def comparison(self):
        expression = self.term()

        while self.match_lexemes(">", ">=", "<", "<="):
            operator = self.previous()
            right = self.term()
            expression = Binary(expression, operator, right)

        return expression

    def term(self):
        expression = self.factor()

        while self.match_lexemes("-", "+"):
            operator = self.previous()
            right = self.factor()
            expression = Binary(expression, operator, right)

        return expression

    def factor(self):
        expression = self.unary()

        while self.match_lexemes("/", "*", "%"):
            operator = self.previous()
            right = self.unary()
            expression = Binary(expression, operator, right)

        return expression

    def unary(self):
        if self.match_lexemes("!", "-"):
            operator = self.previous()
            return Unary(operator, self.unary())

        return self.primary()

    def primary(self):
        if self.match_lexemes("false"):
            return Literal(False)
        if self.match_lexemes("true"):
            return Literal(True)
        if self.match_lexemes("none"):
            return Literal(None)
        if self.check(TokenType.LITERAL):
            return Literal(self.advance().value)
        if self.match_lexemes("("):
            expression = self.expression()
            self.consume_lexeme(")", "Expected ')' after expression.")
            return Grouping(expression)

        raise self.error(self.peek(), "Expected expression.")

    def match_lexemes(self, *lexemes):
        for lexeme in lexemes:
            if self.check_lexeme(lexeme):
                self.advance()
                return True
        return False

    def consume_lexeme(self, lexeme, message):
        if self.check_lexeme(lexeme):
            return self.advance()
        raise self.error(self.peek(), message)

    def check(self, token_type):
        return not self.is_at_end() and self.peek().type == token_type

    def check_lexeme(self, lexeme):
        return not self.is_at_end() and self.peek().lexeme == lexeme

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def peek(self):
        return self.tokens[self.current]

    def previous(self):
        return self.tokens[self.current - 1]

    def error(self, token, message):
        location = f" at line {token.line}" if token.line is not None else ""
        return ParseError(f"{message}{location}")


class Scanner:
    KEYWORDS = {
        "and", "class", "else", "false", "for", "def", "if", "none",
        "or", "print", "return", "super", "this", "true", "var", "while",
    }

    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self):
        while self.current < len(self.source):
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token(TokenType.EOF, None, "", self.line))
        return self.tokens

    def scan_token(self):
        char = self.advance()

        if char in " \r\t":
            return
        if char == "\n":
            self.line += 1
            return

        if char == "/" and self.match("/"):
            while self.peek() not in ("\n", ""):
                self.advance()
            return

        if char == '"':
            self.string()
            return
        if self.is_digit(char):
            self.number()
            return
        if self.is_alpha(char):
            self.identifier()
            return

        if char in "(){}[],.;+-*/%":
            self.add_token(TokenType.OPERATOR)
            return
        if char in "=!<>":
            if self.match("="):
                self.add_token(TokenType.OPERATOR)
            else:
                self.add_token(TokenType.OPERATOR)
            return
        if char == "&" and self.match("&"):
            self.add_token(TokenType.OPERATOR)
            return
        if char == "|" and self.match("|"):
            self.add_token(TokenType.OPERATOR)
            return

        print(f"Unrecognized character {char!r} at line {self.line}")

    def advance(self):
        char = self.source[self.current]
        self.current += 1
        return char

    def peek(self):
        if self.current >= len(self.source):
            return ""
        return self.source[self.current]

    def match(self, expected):
        if self.peek() != expected:
            return False
        self.current += 1
        return True

    def add_token(self, token_type, value=None):
        lexeme = self.source[self.start:self.current]
        if value is None:
            value = lexeme
        self.tokens.append(Token(token_type, value, lexeme, self.line))

    def string(self):
        while self.peek() not in ('"', ""):
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.peek() == "":
            print(f"Unterminated string at line {self.line}")
            return

        self.advance()
        value = self.source[self.start + 1:self.current - 1]
        self.add_token(TokenType.LITERAL, value)

    def number(self):
        while self.is_digit(self.peek()):
            self.advance()

        if self.peek() == "." and self.is_digit(self.peek_next()):
            self.advance()
            while self.is_digit(self.peek()):
                self.advance()

        lexeme = self.source[self.start:self.current]
        value = float(lexeme) if "." in lexeme else int(lexeme)
        self.add_token(TokenType.LITERAL, value)

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return ""
        return self.source[self.current + 1]

    def identifier(self):
        while self.is_alpha(self.peek()) or self.is_digit(self.peek()):
            self.advance()

        lexeme = self.source[self.start:self.current]
        token_type = TokenType.KEYWORD if lexeme in self.KEYWORDS else TokenType.IDENTIFIER
        self.add_token(token_type)

    def is_digit(self, char):
        return "0" <= char <= "9"

    def is_alpha(self, char):
        return ("a" <= char <= "z") or ("A" <= char <= "Z") or char == "_"

if __name__ == "__main__":
    print(f"{len(args)} arguments provided: {args}")

    if len(args) < 1:
        try:
            print("Entering REPL mode. Press Ctrl+C to exit.")
            while True:
                user_input = input(">>> ")
                scanner = Scanner(user_input)
                tokens = scanner.scan_tokens()
                print(tokens)
        except KeyboardInterrupt:
            print("\nExiting...")
            sys.exit(0)

    if len(args) == 1:
        file_path = args[0]
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                print(content)
                scanner = Scanner(content)
                tokens = scanner.scan_tokens()
                print(tokens)
                sys.exit(0)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            sys.exit(1)

    else:
        print("Error: Too many arguments provided. Correct usage:\nopen in repl mode: python language.py\nopen a file: python language.py <file_path>")
        sys.exit(1)

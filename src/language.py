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

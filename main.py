#! python3
# author: Justin Salsbery

from io import TextIOWrapper
from sys import argv, stderr
from enum import Enum, auto
from dataclasses import dataclass


EXIT_FAILURE = 1


def main() -> None:
    paths = argv[1:]

    for path in paths:
        try:

            with open(path, "r") as file:
                tokenizer = Tokenizer(file)
                while True:
                    token = tokenizer.get_token()
                    if token.type == TokenType.EOF:
                        break

                    print(token)

        except FileNotFoundError as e:
            print(f"{e}")

# *****************************************************************************
# *** TOKENS ******************************************************************
# *****************************************************************************


class TokenType(Enum):  # Minimal set.
    WORD = auto()  # Must start with a letter or _.
    KEYWORD = auto()  # WORD that is reserved by Golang.
    SYMBOL = auto()  # Catch all with +, =, &, ), etc.
    NUMBER = auto()  # Starts with a number.
    QUOTE = auto()  # Starts with a ', ", or `.
    LPAREN = auto()  # ( -- note that ) is a SYMBOL.
    EOF = auto()  # End of file.


@dataclass
class Token:
    type: TokenType
    body: str
    line_number: int


class Tokenizer():
    def __init__(self, file: TextIOWrapper):
        self.line_number = 1
        self.file = file

    def get_token(self) -> Token:
        peak = self.peak_next()

        while peak.isspace():  # Remove whitespace.
            if peak == "\n":
                self.line_number += 1

            self.file.read(1)
            peak = self.peak_next()

        if self.is_word(peak):
            string = self.read_word()
            if self.is_keyword(string):
                return Token(TokenType.KEYWORD, string, self.line_number)
            return Token(TokenType.WORD, string, self.line_number)
        elif peak.isdigit():
            string = self.read_number()
            return Token(TokenType.NUMBER, string, self.line_number)
        elif peak == '(':
            char = self.file.read(1)
            return Token(TokenType.LPAREN, char, self.line_number)
        elif peak == "'":
            self.file.read(1)  # Remove first quote.
            string, _ = self.read_until("'")
            return Token(TokenType.QUOTE, string, self.line_number)
        elif peak == '"':
            self.file.read(1)  # Remove first quote.
            string, _ = self.read_until('"')
            return Token(TokenType.QUOTE, string, self.line_number)
        elif peak == '`':
            self.file.read(1)  # Remove first quote.
            string, _ = self.read_until('`')
            return Token(TokenType.QUOTE, string, self.line_number)
        elif peak == "/" and self.peak_next(2) == "//":
            self.read_until("\n")
            return self.get_token()  # Return next token.
        elif peak == "/" and self.peak_next(2) == "/*":
            self.read_until("*/")
            return self.get_token()  # Return next token.
        elif self.is_symbol(peak):  # Must be after comment handling!
            string = self.read_symbol()
            return Token(TokenType.SYMBOL, string, self.line_number)
        elif peak == "":
            return Token(TokenType.EOF, "", self.line_number)

        print(f"Error: Unexpected character {peak} in {self.file}.",
              file=stderr)
        exit(EXIT_FAILURE)

    # Returns an empty string, "", if the end of the file is reached.
    def peak_next(self, count: int = 1) -> str:
        position = self.file.tell()
        string = self.file.read(count)

        self.file.seek(position)
        return string

    # Returns (read, error).
    def read_until(self, end: str) -> tuple[str, bool]:
        escapes = 0
        escapes_in_ending = end.count("\\")

        string = ""
        while True:
            char = self.file.read(1)
            if char == "":
                break
            if char == "\n":
                self.line_number += 1

            string += char

            if char == "\\":
                escapes += 1  # TODO: Clean and verify.

            # Repeatedly calling endswith() is inefficient. A deterministic finite automaton would
            # be superior.

            if string.endswith(end) and (escapes - escapes_in_ending) % 2 == 0:
                return (string, False)

            if char != "\\":
                escapes = 0  # Reset

        return (string, True)

    def read_word(self) -> str:
        string = ""

        char = self.peak_next()
        while self.is_word(char) or char.isdigit():
            string += self.file.read(1)
            char = self.peak_next()

        return string

    def read_number(self) -> str:
        string = ""

        char = self.peak_next()
        while char.isdigit() or char == ".":
            string += self.file.read(1)
            char = self.peak_next()

        return string

    def read_symbol(self) -> str:
        string = ""

        while self.is_symbol(self.peak_next()):
            string += self.file.read(1)

        return string

    def is_word(self, char: str) -> bool:
        return char.isalpha() or char == "_"

    def is_keyword(self, string: str) -> bool:
        if string == "break" or string == "default" or string == "func" \
                or string == "case" or string == "defer" or string == "go" \
                or string == "map" or string == "struct" or string == "chan" \
                or string == "else" or string == "goto" or string == "package" \
                or string == "switch" or string == "const" or string == "fallthrough" \
                or string == "if" or string == "range" or string == "type" \
                or string == "continue" or string == "for" or string == "import" \
                or string == "return" or string == "var":  # Complete.
            return True
        return False

    def is_symbol(self, char: str) -> bool:
        if char == "+" or char == "-" or char == "=" \
                or char == ":" or char == "!" or char == "<" \
                or char == ">" or char == "*" or char == "/" \
                or char == "%" or char == "&" or char == "|" \
                or char == "^" or char == "~" or char == "." \
                or char == "," or char == "[" or char == "]" \
                or char == "{" or char == "}" or char == ")" \
                or char == "$" or char == "@" or char == "?":  # Incomplete.
            return True
        return False


if __name__ == "__main__":
    main()

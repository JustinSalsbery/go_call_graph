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
        self.__line_number = 1
        self.__file = file

    def get_token(self) -> Token:
        peak = self.__peak_next()

        while peak.isspace():  # Remove whitespace.
            if peak == "\n":
                self.__line_number += 1

            self.__file.read(1)
            peak = self.__peak_next()

        if self.__is_word(peak):
            string = self.__read_word()
            if self.__is_keyword(string):
                return Token(TokenType.KEYWORD, string, self.__line_number)
            return Token(TokenType.WORD, string, self.__line_number)
        elif peak.isdigit():
            string = self.__read_number()
            return Token(TokenType.NUMBER, string, self.__line_number)
        elif peak == '(':
            char = self.__file.read(1)
            return Token(TokenType.LPAREN, char, self.__line_number)
        elif peak == "'":
            self.__file.read(1)  # Remove first quote.
            string, _ = self.__read_until("'")
            return Token(TokenType.QUOTE, string, self.__line_number)
        elif peak == '"':
            self.__file.read(1)  # Remove first quote.
            string, _ = self.__read_until('"')
            return Token(TokenType.QUOTE, string, self.__line_number)
        elif peak == '`':
            self.__file.read(1)  # Remove first quote.
            string, _ = self.__read_until('`')
            return Token(TokenType.QUOTE, string, self.__line_number)
        elif peak == "/" and self.__peak_next(2) == "//":
            self.__read_until("\n")
            return self.get_token()  # Return next token.
        elif peak == "/" and self.__peak_next(2) == "/*":
            self.__read_until("*/")
            return self.get_token()  # Return next token.
        elif self.__is_symbol(peak):  # Must be after comment handling!
            string = self.__read_symbol()
            return Token(TokenType.SYMBOL, string, self.__line_number)
        elif peak == "":
            return Token(TokenType.EOF, "", self.__line_number)

        print(f"Error: Unexpected character {peak} in {self.__file}.",
              file=stderr)
        exit(EXIT_FAILURE)

    # Returns an empty string, "", if the end of the file is reached.
    def __peak_next(self, count: int = 1) -> str:
        position = self.__file.tell()
        string = self.__file.read(count)

        self.__file.seek(position)
        return string

    # Returns (read, error).
    def __read_until(self, end: str) -> tuple[str, bool]:
        escapes = 0
        escapes_in_ending = end.count("\\")

        string = ""
        while True:
            char = self.__file.read(1)
            if char == "":
                break
            if char == "\n":
                self.__line_number += 1

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

    def __read_word(self) -> str:
        string = ""

        char = self.__peak_next()
        while self.__is_word(char) or char.isdigit():
            string += self.__file.read(1)
            char = self.__peak_next()

        return string

    def __read_number(self) -> str:
        string = ""

        char = self.__peak_next()
        while char.isdigit() or char == ".":
            string += self.__file.read(1)
            char = self.__peak_next()

        return string

    def __read_symbol(self) -> str:
        string = ""

        while self.__is_symbol(self.__peak_next()):
            string += self.__file.read(1)

        return string

    def __is_word(self, char: str) -> bool:
        return char.isalpha() or char == "_"

    def __is_keyword(self, string: str) -> bool:
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

    def __is_symbol(self, char: str) -> bool:
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

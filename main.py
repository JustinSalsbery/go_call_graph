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
                while True:
                    token = get_token(file)
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


def get_token(file: TextIOWrapper) -> Token:
    peak = peak_next(file)

    while peak.isspace():
        file.read(1)  # Remove whitespace.
        peak = peak_next(file)

    if is_word(peak):
        string = read_word(file)
        if is_keyword(string):
            return Token(TokenType.KEYWORD, string)
        return Token(TokenType.WORD, string)
    elif peak.isdigit():
        string = read_number(file)
        return Token(TokenType.NUMBER, string)
    elif peak == '(':
        char = file.read(1)
        return Token(TokenType.LPAREN, char)
    elif peak == "'":
        file.read(1)  # Remove first quote.
        string, _ = read_until(file, "'")
        return Token(TokenType.QUOTE, string)
    elif peak == '"':
        file.read(1)  # Remove first quote.
        string, _ = read_until(file, '"')
        return Token(TokenType.QUOTE, string)
    elif peak == '`':
        file.read(1)  # Remove first quote.
        string, _ = read_until(file, '`')
        return Token(TokenType.QUOTE, string)
    elif peak == "/" and peak_next(file, 2) == "//":
        read_until(file, "\n")
        return get_token(file)  # Return next token.
    elif peak == "/" and peak_next(file, 2) == "/*":
        read_until(file, "*/")
        return get_token(file)  # Return next token.
    elif is_symbol(peak):  # Must be after comment handling!
        string = read_symbol(file)
        return Token(TokenType.SYMBOL, string)
    elif peak == "":
        return Token(TokenType.EOF, "")

    print(f"Error: Unexpected character {peak} in {file}.", file=stderr)
    exit(EXIT_FAILURE)


# Returns an empty string, "", if the end of the file is reached.
def peak_next(file: TextIOWrapper, count: int = 1) -> str:
    position = file.tell()
    string = file.read(count)

    file.seek(position)
    return string


# Returns (read, error).
def read_until(file: TextIOWrapper, end: str) -> tuple[str, bool]:
    escapes = 0
    escapes_in_ending = end.count("\\")

    read = ""
    while True:
        char = file.read(1)
        if char == "":
            break

        read += char

        if char == "\\":
            escapes += 1

        # Repeatedly calling endswith() is inefficient. A deterministic finite automaton would
        # be superior.

        if read.endswith(end) and (escapes - escapes_in_ending) % 2 == 0:
            return (read, False)

        if char != "\\":
            escapes = 0  # Reset

    return (read, True)


def read_word(file: TextIOWrapper) -> str:
    string = ""

    char = peak_next(file)
    while is_word(char) or char.isdigit():
        string += file.read(1)
        char = peak_next(file)

    return string


def read_number(file: TextIOWrapper) -> str:
    string = ""

    while peak_next(file).isdigit():
        string += file.read(1)

    return string


def read_symbol(file: TextIOWrapper) -> str:
    string = ""

    while is_symbol(peak_next(file)):
        string += file.read(1)

    return string


def is_word(char: str) -> bool:
    return char.isalpha() or char == "_"


def is_keyword(string: str) -> bool:
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


def is_symbol(char: str) -> bool:
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

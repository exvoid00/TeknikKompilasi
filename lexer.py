"""
lexer.py — Tahap 1: Lexical Analysis (Scanner)
Mengubah source code (string) menjadi deretan token.
"""

from enum import Enum, auto


class TokenType(Enum):
    # Literals
    NUMBER = auto()
    IDENTIFIER = auto()
    STRING = auto()
    # Keywords
    KEYWORD = auto()
    # Operators & punctuation
    OPERATOR = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    SEMICOLON = auto()
    COMMA = auto()
    ASSIGN = auto()
    # Special
    EOF = auto()


# Keyword bahasa Minang  ->  makna
#   jiko    = if          lain   = else       indak  = else (alias)
#   salamo  = while       baliak = return
#   cetak   = print/output  baco = input
#   bulek   = int         pacahan = float     kato   = string (tipe teks)
KEYWORDS = {"jiko", "lain", "indak", "salamo", "baliak",
            "bulek", "pacahan", "kato", "cetak", "baco", "akar"}


class Token:
    def __init__(self, type_, value, line=0, col=0):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, ln={self.line})"


class Lexer:
    def __init__(self, source: str):
        # Buang BOM (penanda tak terlihat dari file UTF-8 Notepad) bila ada
        self.source = source.lstrip("﻿")
        self.pos = 0
        self.line = 1
        self.col = 1

    def error(self, msg):
        raise SyntaxError(f"[Lexer] Baris {self.line}: {msg}")

    def advance(self):
        c = self.source[self.pos]
        self.pos += 1
        if c == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return c

    def peek(self):
        return self.source[self.pos] if self.pos < len(self.source) else ""

    def tokenize(self) -> list[Token]:
        """Hasilkan list token dari source code."""
        tokens = []
        single = {
            "(": TokenType.LPAREN, ")": TokenType.RPAREN,
            "{": TokenType.LBRACE, "}": TokenType.RBRACE,
            ";": TokenType.SEMICOLON, ",": TokenType.COMMA,
            "=": TokenType.ASSIGN,
        }
        while self.pos < len(self.source):
            c = self.peek()
            ln, col = self.line, self.col

            if c in " \t\r\n":                       # whitespace
                self.advance()
            elif c.isdigit():                        # angka (int/float)
                num = ""
                while self.peek().isdigit() or self.peek() == ".":
                    num += self.advance()
                value = float(num) if "." in num else int(num)
                tokens.append(Token(TokenType.NUMBER, value, ln, col))
            elif c == '"':                           # string literal "..."
                self.advance()                        # buang kutip pembuka
                text = ""
                while self.peek() != '"':
                    if self.peek() == "":
                        self.error("String belum ditutup dengan '\"'")
                    ch = self.advance()
                    if ch == "\\":                    # escape: \n \t \" \\
                        esc = self.advance()
                        text += {"n": "\n", "t": "\t",
                                 '"': '"', "\\": "\\"}.get(esc, esc)
                    else:
                        text += ch
                self.advance()                        # buang kutip penutup
                tokens.append(Token(TokenType.STRING, text, ln, col))
            elif c.isalpha() or c == "_":            # identifier / keyword
                word = ""
                while self.peek().isalnum() or self.peek() == "_":
                    word += self.advance()
                ttype = TokenType.KEYWORD if word in KEYWORDS else TokenType.IDENTIFIER
                tokens.append(Token(ttype, word, ln, col))
            elif c in "+-*/":                         # operator aritmatika
                tokens.append(Token(TokenType.OPERATOR, self.advance(), ln, col))
            elif c in "<>=!":                          # operator perbandingan
                op = self.advance()
                if self.peek() == "=":                 # ==, !=, <=, >=
                    op += self.advance()
                elif op == "=":                        # '=' tunggal = assign
                    tokens.append(Token(TokenType.ASSIGN, "=", ln, col))
                    continue
                elif op == "!":
                    self.error("Operator '!' harus diikuti '='")
                tokens.append(Token(TokenType.OPERATOR, op, ln, col))
            elif c in single:                         # tanda baca tunggal
                tokens.append(Token(single[c], self.advance(), ln, col))
            else:
                self.error(f"Karakter tak dikenal: {c!r}")

        tokens.append(Token(TokenType.EOF, None, self.line, self.col))
        return tokens


if __name__ == "__main__":
    src = "int x = 10;"
    for tok in Lexer(src).tokenize():
        print(tok)

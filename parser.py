"""
parser.py — Tahap 2: Syntax Analysis (Parser)
Tujuan: mengecek URUTAN token apakah sesuai grammar, lalu membangun
PARSE TREE (concrete syntax tree). Lihat grammar.py untuk aturannya.
Pendekatan: Recursive Descent Parser.

Catatan: AST dibangun TERPISAH dari parse tree (lihat ast_builder.py),
sesuai ketentuan tugas: Parser -> Parse Tree -> AST.
"""

from lexer import TokenType
from parse_tree import ParseTreeNode


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    @property
    def current(self):
        return self.tokens[self.pos]

    def error(self, msg):
        raise SyntaxError(f"[Parser] {msg} (dapat {self.current})")

    def eat(self, type_):
        """Konsumsi token jika tipenya cocok -> jadikan daun parse tree."""
        if self.current.type == type_:
            tok = self.current
            self.pos += 1
            return ParseTreeNode(type_.name, tok.value)
        self.error(f"Diharapkan {type_.name}")

    def _kw(self, word):
        """Cek apakah token sekarang keyword tertentu."""
        return self.current.type == TokenType.KEYWORD and self.current.value == word

    # ---------- Aturan Grammar ----------
    def parse(self):
        """program ::= statement* EOF"""
        node = ParseTreeNode("program")
        while self.current.type != TokenType.EOF:
            node.add(self.statement())
        node.add(self.eat(TokenType.EOF))
        return node

    def statement(self):
        node = ParseTreeNode("statement")
        if self._kw("bulek") or self._kw("pacahan") or self._kw("kato"):
            node.add(self.var_decl())
        elif self._kw("cetak"):
            node.add(self.print_stmt())
        elif self._kw("baco"):
            node.add(self.input_stmt())
        elif self._kw("jiko"):
            node.add(self.if_stmt())
        elif self._kw("salamo"):
            node.add(self.while_stmt())
        elif self.current.type == TokenType.IDENTIFIER:
            node.add(self.assignment())
        else:
            self.error("Statement tidak valid")
        return node

    def var_decl(self):
        """var_decl ::= type IDENTIFIER ( "=" expression )? ";" """
        node = ParseTreeNode("var_decl")
        node.add(self.eat(TokenType.KEYWORD))      # type (bulek/pacahan)
        node.add(self.eat(TokenType.IDENTIFIER))   # nama
        if self.current.type == TokenType.ASSIGN:
            node.add(self.eat(TokenType.ASSIGN))
            node.add(self.expression())
        node.add(self.eat(TokenType.SEMICOLON))
        return node

    def assignment(self):
        """assignment ::= IDENTIFIER "=" expression ";" """
        node = ParseTreeNode("assignment")
        node.add(self.eat(TokenType.IDENTIFIER))
        node.add(self.eat(TokenType.ASSIGN))
        node.add(self.expression())
        node.add(self.eat(TokenType.SEMICOLON))
        return node

    def print_stmt(self):
        """print_stmt ::= "cetak" "(" expression ( "," expression )* ")" ";" """
        node = ParseTreeNode("print_stmt")
        node.add(self.eat(TokenType.KEYWORD))
        node.add(self.eat(TokenType.LPAREN))
        node.add(self.expression())
        while self.current.type == TokenType.COMMA:
            node.add(self.eat(TokenType.COMMA))
            node.add(self.expression())
        node.add(self.eat(TokenType.RPAREN))
        node.add(self.eat(TokenType.SEMICOLON))
        return node

    def input_stmt(self):
        """input_stmt ::= "baco" "(" IDENTIFIER ")" ";" """
        node = ParseTreeNode("input_stmt")
        node.add(self.eat(TokenType.KEYWORD))
        node.add(self.eat(TokenType.LPAREN))
        node.add(self.eat(TokenType.IDENTIFIER))
        node.add(self.eat(TokenType.RPAREN))
        node.add(self.eat(TokenType.SEMICOLON))
        return node

    def if_stmt(self):
        """if_stmt ::= "jiko" "(" expression ")" block ( ("indak"|"lain") block )? """
        node = ParseTreeNode("if_stmt")
        node.add(self.eat(TokenType.KEYWORD))      # jiko
        node.add(self.eat(TokenType.LPAREN))
        node.add(self.expression())
        node.add(self.eat(TokenType.RPAREN))
        node.add(self.block())
        if self._kw("indak") or self._kw("lain"):  # else: 'indak' atau 'lain'
            node.add(self.eat(TokenType.KEYWORD))  # indak / lain
            node.add(self.block())
        return node

    def while_stmt(self):
        """while_stmt ::= "salamo" "(" expression ")" block"""
        node = ParseTreeNode("while_stmt")
        node.add(self.eat(TokenType.KEYWORD))      # salamo
        node.add(self.eat(TokenType.LPAREN))
        node.add(self.expression())
        node.add(self.eat(TokenType.RPAREN))
        node.add(self.block())
        return node

    def block(self):
        """block ::= "{" statement* "}" """
        node = ParseTreeNode("block")
        node.add(self.eat(TokenType.LBRACE))
        while self.current.type != TokenType.RBRACE:
            node.add(self.statement())
        node.add(self.eat(TokenType.RBRACE))
        return node

    # ---------- Expression (dengan presedensi) ----------
    def expression(self):
        """expression ::= comparison"""
        node = ParseTreeNode("expression")
        node.add(self.comparison())
        return node

    def comparison(self):
        """comparison ::= additive ( ('<'|'>'|'=='|'!='|'<='|'>=') additive )*"""
        node = ParseTreeNode("comparison")
        node.add(self.additive())
        rel = ("<", ">", "==", "!=", "<=", ">=")
        while self.current.type == TokenType.OPERATOR and self.current.value in rel:
            node.add(self.eat(TokenType.OPERATOR))
            node.add(self.additive())
        return node

    def additive(self):
        """additive ::= term ( ('+'|'-') term )*"""
        node = ParseTreeNode("additive")
        node.add(self.term())
        while self.current.type == TokenType.OPERATOR and self.current.value in ("+", "-"):
            node.add(self.eat(TokenType.OPERATOR))
            node.add(self.term())
        return node

    def term(self):
        """term ::= factor ( ('*'|'/') factor )*"""
        node = ParseTreeNode("term")
        node.add(self.factor())
        while self.current.type == TokenType.OPERATOR and self.current.value in ("*", "/"):
            node.add(self.eat(TokenType.OPERATOR))
            node.add(self.factor())
        return node

    def factor(self):
        """factor ::= NUMBER | STRING | IDENTIFIER | "akar" "(" expression ")" | "(" expression ")" """
        node = ParseTreeNode("factor")
        if self._kw("akar"):                       # fungsi bawaan: akar(x)
            node.add(self.eat(TokenType.KEYWORD))  # akar
            node.add(self.eat(TokenType.LPAREN))
            node.add(self.expression())
            node.add(self.eat(TokenType.RPAREN))
        elif self.current.type == TokenType.NUMBER:
            node.add(self.eat(TokenType.NUMBER))
        elif self.current.type == TokenType.STRING:
            node.add(self.eat(TokenType.STRING))
        elif self.current.type == TokenType.IDENTIFIER:
            node.add(self.eat(TokenType.IDENTIFIER))
        elif self.current.type == TokenType.LPAREN:
            node.add(self.eat(TokenType.LPAREN))
            node.add(self.expression())
            node.add(self.eat(TokenType.RPAREN))
        else:
            self.error("Factor tidak valid")
        return node


if __name__ == "__main__":
    from lexer import Lexer
    from parse_tree import print_parse_tree
    tokens = Lexer("bulek x = 1 + 2;").tokenize()
    tree = Parser(tokens).parse()
    print_parse_tree(tree)

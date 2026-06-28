"""
parse_tree.py — Concrete Syntax Tree (Parse Tree)
Berbeda dengan AST: Parse Tree menyimpan SEMUA simbol sesuai aturan
grammar (termasuk tanda kurung, titik koma, keyword), sedangkan AST
hanya menyimpan inti maknanya.

Alur tugas: Parser -> Parse Tree -> (AST Builder) -> AST
"""


class ParseTreeNode:
    def __init__(self, symbol, value=None):
        self.symbol = symbol      # nama nonterminal ("expression") / terminal ("NUMBER")
        self.value = value        # isi token untuk terminal (mis. 'jiko', 10)
        self.children = []

    def add(self, *nodes):
        for n in nodes:
            if n is not None:
                self.children.append(n)
        return self

    def is_terminal(self):
        return not self.children and self.value is not None

    def child(self, symbol):
        """Ambil 1 anak pertama dengan simbol tertentu."""
        for c in self.children:
            if c.symbol == symbol:
                return c
        return None

    def children_by(self, symbol):
        """Ambil semua anak dengan simbol tertentu."""
        return [c for c in self.children if c.symbol == symbol]

    def __repr__(self):
        return f"<{self.symbol}{'='+repr(self.value) if self.value is not None else ''}>"


def print_parse_tree(node, indent=0):
    """Cetak parse tree berbentuk pohon."""
    pad = "  " * indent
    if node.is_terminal():
        print(f"{pad}{node.symbol}: {node.value!r}")
    else:
        print(f"{pad}{node.symbol}")
        for c in node.children:
            print_parse_tree(c, indent + 1)

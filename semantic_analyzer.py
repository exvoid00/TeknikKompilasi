"""
semantic_analyzer.py — Tahap 3: Semantic Analysis
Mengecek arti/makna program: deklarasi variabel, tipe data,
scope, penggunaan variabel yang belum dideklarasikan, dll.
Biasanya memakai Symbol Table.
"""

import ast


class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent

    def define(self, name, type_):
        self.symbols[name] = type_

    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None


class SemanticError(Exception):
    pass


class SemanticAnalyzer:
    def __init__(self):
        self.scope = SymbolTable()
        self.errors = []

    def analyze(self, node):
        """Telusuri AST dan validasi semantiknya."""
        node.accept(self)
        if self.errors:
            raise SemanticError("\n".join(self.errors))
        return True

    def generic_visit(self, node):
        # Default: kunjungi anak-anak node bila ada
        for value in vars(node).values():
            if isinstance(value, ast.Node):
                value.accept(self)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.Node):
                        item.accept(self)

    def visit_VarDecl(self, node):
        # cek nilai dulu (mis. bulek x = y + 1 -> y harus sudah ada)
        self.generic_visit(node)
        if self.scope.lookup(node.name) is not None:
            self.errors.append(f"Variabel '{node.name}' dideklarasikan ulang.")
        self.scope.define(node.name, node.var_type)

    def visit_Assign(self, node):
        if self.scope.lookup(node.name) is None:
            self.errors.append(f"Variabel '{node.name}' belum dideklarasikan.")
        self.generic_visit(node)

    def visit_Identifier(self, node):
        if self.scope.lookup(node.name) is None:
            self.errors.append(f"Variabel '{node.name}' dipakai tapi belum dideklarasikan.")

    def visit_Input(self, node):
        if self.scope.lookup(node.name) is None:
            self.errors.append(f"Variabel '{node.name}' (baco) belum dideklarasikan.")

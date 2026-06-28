"""
evaluator.py — Interpreter (menjalankan AST secara langsung).
Berbeda dengan code_generator (yang hanya menerjemahkan), interpreter
ini BENAR-BENAR mengeksekusi program: menghitung, mencabang (jiko/lain),
mengulang (salamo), membaca input (baco), dan mencetak (cetak).
"""

import ast
import math


class Evaluator:
    def __init__(self):
        self.env = {}     # tempat menyimpan nilai variabel

    def run(self, program):
        self.execute(program)

    # ---- jalankan statement ----
    def execute(self, node):
        method = "exec_" + type(node).__name__
        getattr(self, method)(node)

    def exec_Program(self, node):
        for stmt in node.statements:
            self.execute(stmt)

    def exec_Block(self, node):
        for stmt in node.statements:
            self.execute(stmt)

    def exec_VarDecl(self, node):
        self.env[node.name] = self.eval(node.value) if node.value is not None else 0

    def exec_Assign(self, node):
        self.env[node.name] = self.eval(node.value)

    def exec_Print(self, node):
        # gabung semua argumen tanpa pemisah: cetak("Umur: ", x) -> "Umur: 5"
        print("".join(str(self.eval(a)) for a in node.args))

    def exec_Input(self, node):
        raw = input(f"Masukkan nilai untuk '{node.name}': ")
        try:
            value = int(raw)
        except ValueError:
            try:
                value = float(raw)
            except ValueError:
                value = 0
        self.env[node.name] = value

    def exec_If(self, node):
        if self.eval(node.condition):
            self.execute(node.then_block)
        elif node.else_block is not None:
            self.execute(node.else_block)

    def exec_While(self, node):
        while self.eval(node.condition):
            self.execute(node.body)

    # ---- hitung nilai expression ----
    def eval(self, node):
        method = "eval_" + type(node).__name__
        return getattr(self, method)(node)

    def eval_Number(self, node):
        return node.value

    def eval_String(self, node):
        return node.value

    def eval_Identifier(self, node):
        if node.name not in self.env:
            raise NameError(f"Variabel '{node.name}' belum dideklarasikan.")
        return self.env[node.name]

    def eval_Sqrt(self, node):
        nilai = self.eval(node.arg)
        if nilai < 0:
            raise ValueError("akar dari bilangan negatif tidak valid.")
        return math.sqrt(nilai)

    def eval_BinaryOp(self, node):
        a = self.eval(node.left)
        b = self.eval(node.right)
        ops = {
            "+": a + b, "-": a - b, "*": a * b,
            "/": (a / b if b != 0 else 0),
            "<": a < b, ">": a > b, "==": a == b,
            "!=": a != b, "<=": a <= b, ">=": a >= b,
        }
        return ops[node.op]


if __name__ == "__main__":
    from lexer import Lexer
    from parser import Parser
    from ast_builder import ASTBuilder
    src = "bulek x = 5; jiko (x > 3) { cetak(x); } lain { cetak(0); }"
    tokens = Lexer(src).tokenize()
    tree = ASTBuilder().build(Parser(tokens).parse())
    Evaluator().run(tree)

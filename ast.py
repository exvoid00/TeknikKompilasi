"""
ast.py — Definisi Abstract Syntax Tree (AST)
Berisi node-node yang dipakai parser untuk membangun pohon sintaks.
Catatan: 'ast' juga nama modul bawaan Python. Jangan 'import ast'
di dalam project ini agar tidak bentrok.
"""


class Node:
    """Base class untuk semua node AST."""
    def accept(self, visitor):
        method = "visit_" + type(self).__name__
        return getattr(visitor, method, visitor.generic_visit)(self)


# ---- Expressions ----
class Number(Node):
    def __init__(self, value):
        self.value = value


class String(Node):
    """Literal teks, mis. "Apo kaba"."""
    def __init__(self, value):
        self.value = value


class Identifier(Node):
    def __init__(self, name):
        self.name = name


class BinaryOp(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class Sqrt(Node):
    """akar(x) -> akar kuadrat dari x (fungsi bawaan)."""
    def __init__(self, arg):
        self.arg = arg


# ---- Statements ----
class Assign(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value


class VarDecl(Node):
    def __init__(self, var_type, name, value=None):
        self.var_type = var_type
        self.name = name
        self.value = value


class Print(Node):
    """cetak(a, b, ...) -> cetak beberapa nilai dalam satu baris."""
    def __init__(self, args):
        self.args = args            # daftar expression


class Input(Node):
    """baco(x); -> baca input dari user ke variabel x"""
    def __init__(self, name):
        self.name = name


class If(Node):
    def __init__(self, condition, then_block, else_block=None):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block


class While(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body


class Block(Node):
    def __init__(self, statements):
        self.statements = statements


class Program(Node):
    def __init__(self, statements):
        self.statements = statements

"""
code_optimizer.py — Tahap 4: Code Optimization
Memperbaiki kode antara (IR) / AST agar lebih efisien tanpa
mengubah hasil. Contoh teknik:
  - Constant Folding   : 2 + 3  -> 5
  - Constant Propagation
  - Dead Code Elimination
  - Strength Reduction : x * 2  -> x + x
"""

import ast
import math


class Optimizer:
    def __init__(self):
        self.changes = 0

    def optimize(self, node):
        """Kembalikan node hasil optimasi."""
        return self.visit(node)

    def visit(self, node):
        method = "visit_" + type(node).__name__
        return getattr(self, method, self.generic_visit)(node)

    def generic_visit(self, node):
        for name, value in vars(node).items():
            if isinstance(value, ast.Node):
                setattr(node, name, self.visit(value))
            elif isinstance(value, list):
                setattr(node, name, [self.visit(v) if isinstance(v, ast.Node) else v
                                     for v in value])
        return node

    def visit_BinaryOp(self, node):
        # Optimasi anak dulu (bottom-up)
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)

        # Constant Folding
        if isinstance(node.left, ast.Number) and isinstance(node.right, ast.Number):
            a, b = node.left.value, node.right.value
            result = {"+": a + b, "-": a - b, "*": a * b}.get(node.op)
            if node.op == "/" and b != 0:
                result = a / b
            if result is not None:
                self.changes += 1
                return ast.Number(result)
        return node

    def visit_Sqrt(self, node):
        # Optimasi argumen dulu (bottom-up)
        node.arg = self.visit(node.arg)
        # Constant folding: akar dari angka tetap -> hitung langsung
        if isinstance(node.arg, ast.Number) and node.arg.value >= 0:
            self.changes += 1
            return ast.Number(math.sqrt(node.arg.value))
        return node

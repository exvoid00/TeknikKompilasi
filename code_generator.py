"""
code_generator.py — Tahap 5: Code Generation
Menghasilkan kode target dari AST (yang sudah dioptimasi).
Target bisa berupa: assembly, bytecode, three-address code (TAC),
atau bahasa lain. Di sini contohnya Three-Address Code.
"""

import ast


class CodeGenerator:
    def __init__(self):
        self.instructions = []
        self.temp_count = 0

    def new_temp(self):
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self):
        if not hasattr(self, "label_count"):
            self.label_count = 0
        self.label_count += 1
        return f"L{self.label_count}"

    def generate(self, node):
        """Hasilkan kode target dari root AST."""
        self.visit(node)
        return self.instructions

    def emit(self, instr):
        self.instructions.append(instr)

    def visit(self, node):
        method = "visit_" + type(node).__name__
        return getattr(self, method, self.generic_visit)(node)

    def generic_visit(self, node):
        for value in vars(node).values():
            if isinstance(value, ast.Node):
                self.visit(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, ast.Node):
                        self.visit(item)

    def visit_Number(self, node):
        return str(node.value)

    def visit_String(self, node):
        return f'"{node.value}"'

    def visit_Identifier(self, node):
        return node.name

    def visit_BinaryOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        temp = self.new_temp()
        self.emit(f"{temp} = {left} {node.op} {right}")
        return temp

    def visit_Sqrt(self, node):
        val = self.visit(node.arg)
        temp = self.new_temp()
        self.emit(f"{temp} = SQRT {val}")
        return temp

    def visit_VarDecl(self, node):
        if node.value is not None:
            src = self.visit(node.value)
            self.emit(f"{node.name} = {src}")

    def visit_Assign(self, node):
        src = self.visit(node.value)
        self.emit(f"{node.name} = {src}")

    def visit_Print(self, node):
        srcs = [self.visit(a) for a in node.args]
        self.emit(f"PRINT {', '.join(srcs)}")

    def visit_Input(self, node):
        self.emit(f"READ {node.name}")

    def visit_Block(self, node):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_If(self, node):
        cond = self.visit(node.condition)
        if node.else_block is not None:
            l_else, l_end = self.new_label(), self.new_label()
            self.emit(f"IF_FALSE {cond} GOTO {l_else}")
            self.visit(node.then_block)
            self.emit(f"GOTO {l_end}")
            self.emit(f"{l_else}:")
            self.visit(node.else_block)
            self.emit(f"{l_end}:")
        else:
            l_end = self.new_label()
            self.emit(f"IF_FALSE {cond} GOTO {l_end}")
            self.visit(node.then_block)
            self.emit(f"{l_end}:")

    def visit_While(self, node):
        l_start, l_end = self.new_label(), self.new_label()
        self.emit(f"{l_start}:")
        cond = self.visit(node.condition)
        self.emit(f"IF_FALSE {cond} GOTO {l_end}")
        self.visit(node.body)
        self.emit(f"GOTO {l_start}")
        self.emit(f"{l_end}:")


if __name__ == "__main__":
    print("Three-Address Code generator siap dipakai.")

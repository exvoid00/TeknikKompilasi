"""
ast_builder.py — Membangun AST dari Parse Tree.
Sesuai ketentuan tugas: "AST dibuat berdasarkan parse tree".

Parse Tree (concrete) menyimpan semua simbol grammar; di sini kita
ringkas menjadi AST (abstract) yang hanya berisi inti makna program.
"""

import ast

# rule biner -> simbol operand-nya
_BINARY = {"comparison": "additive", "additive": "term", "term": "factor"}


class ASTBuilder:
    def build(self, pt):
        """pt = parse tree node 'program' -> ast.Program"""
        stmts = [self._statement(s) for s in pt.children_by("statement")]
        return ast.Program(stmts)

    def _statement(self, node):
        prod = node.children[0]          # statement membungkus 1 produksi
        return getattr(self, "_" + prod.symbol)(prod)

    # ---- statements ----
    def _var_decl(self, n):
        var_type = n.children[0].value
        name = n.children[1].value
        expr = n.child("expression")
        value = self._expr(expr) if expr else None
        return ast.VarDecl(var_type, name, value)

    def _assignment(self, n):
        name = n.children[0].value
        return ast.Assign(name, self._expr(n.child("expression")))

    def _print_stmt(self, n):
        args = [self._expr(e) for e in n.children_by("expression")]
        return ast.Print(args)

    def _input_stmt(self, n):
        # baco ( IDENTIFIER ) ;
        name = n.children_by("IDENTIFIER")[0].value
        return ast.Input(name)

    def _if_stmt(self, n):
        cond = self._expr(n.child("expression"))
        blocks = n.children_by("block")
        then_block = self._block(blocks[0])
        else_block = self._block(blocks[1]) if len(blocks) > 1 else None
        return ast.If(cond, then_block, else_block)

    def _while_stmt(self, n):
        cond = self._expr(n.child("expression"))
        return ast.While(cond, self._block(n.child("block")))

    def _block(self, n):
        return ast.Block([self._statement(s) for s in n.children_by("statement")])

    # ---- expressions ----
    def _expr(self, node):
        s = node.symbol
        if s == "expression":
            return self._expr(node.children[0])      # -> comparison
        if s in _BINARY:
            operand_sym = _BINARY[s]
            operands = node.children_by(operand_sym)
            ops = node.children_by("OPERATOR")
            left = self._expr(operands[0])
            for i, op in enumerate(ops):             # asosiatif kiri
                left = ast.BinaryOp(left, op.value, self._expr(operands[i + 1]))
            return left
        if s == "factor":
            first = node.children[0]
            if first.symbol == "KEYWORD" and first.value == "akar":   # akar(expr)
                return ast.Sqrt(self._expr(node.child("expression")))
            if first.symbol == "NUMBER":
                return ast.Number(first.value)
            if first.symbol == "STRING":
                return ast.String(first.value)
            if first.symbol == "IDENTIFIER":
                return ast.Identifier(first.value)
            if first.symbol == "LPAREN":             # ( expression )
                return self._expr(node.child("expression"))
        raise ValueError(f"Tidak bisa membangun AST dari simbol: {s}")

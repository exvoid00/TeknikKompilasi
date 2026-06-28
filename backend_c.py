"""
backend_c.py — Backend "kompiler nyata": menerjemahkan AST bahasa Minang
menjadi KODE SUMBER C. Berbeda dengan code_generator.py (yang hanya
menghasilkan Three-Address Code untuk dipelajari), output di sini bisa
dikompilasi gcc menjadi file .exe yang berjalan TANPA Python.

Alur: AST  ->  kode C  ->  (gcc, lihat bangun.py)  ->  program.exe

Pemetaan tipe:
    bulek   -> int       pacahan -> double      kato -> char*

Catatan desain:
  * Semua variabel dideklarasikan di awal main() agar cocok dengan
    interpreter (env datar): variabel yang dibuat di dalam blok tetap
    dikenal di luar blok.
  * Tipe variabel disimpulkan otomatis: jika sebuah variabel pernah
    diisi teks, tipenya menjadi char* (string).
"""

import ast

# rank tipe: makin besar makin "kuat" saat digabung
_RANK = {"int": 0, "double": 1, "char*": 2}
_FROM_KEYWORD = {"bulek": "int", "pacahan": "double", "kato": "char*"}


def _c_escape(text: str) -> str:
    """Ubah string Python menjadi literal string C yang aman."""
    out = []
    for ch in text:
        out.append({"\\": "\\\\", '"': '\\"', "\n": "\\n",
                    "\t": "\\t", "\r": "\\r"}.get(ch, ch))
    return '"' + "".join(out) + '"'


class CBackend:
    def __init__(self):
        self.var_types = {}   # nama variabel -> tipe C
        self.lines = []       # baris isi main()
        self.level = 1        # indentasi (1 = di dalam main)

    # ================= API utama =================
    def generate(self, program) -> str:
        self._infer(program)                 # tahap 1: simpulkan tipe variabel
        for stmt in program.statements:      # tahap 2: hasilkan kode
            self._gen(stmt)

        decls = []
        for name, t in self.var_types.items():
            default = '""' if t == "char*" else "0"
            decl = f"char *{name}" if t == "char*" else f"{t} {name}"
            decls.append(f"    {decl} = {default};")

        head = ["#include <stdio.h>", "#include <math.h>", "", "int main(void) {"]
        if decls:
            head += ["    /* deklarasi variabel */"] + decls + [""]
        return "\n".join(head + self.lines + ["    return 0;", "}", ""])

    # ================= Tahap 1: inferensi tipe =================
    def _merge(self, name, t):
        old = self.var_types.get(name)
        if old is None or _RANK[t] > _RANK[old]:
            self.var_types[name] = t

    def _infer(self, node):
        cls = type(node).__name__
        if cls == "VarDecl":
            t = _FROM_KEYWORD.get(node.var_type, "int")
            if node.value is not None and self._etype(node.value) == "char*":
                t = "char*"
            self._merge(node.name, t)
        elif cls == "Assign":
            if self._etype(node.value) == "char*":
                self._merge(node.name, "char*")
        # telusuri anak-anak
        for v in vars(node).values():
            if isinstance(v, ast.Node):
                self._infer(v)
            elif isinstance(v, list):
                for it in v:
                    if isinstance(it, ast.Node):
                        self._infer(it)

    def _etype(self, e) -> str:
        """Simpulkan tipe C dari sebuah expression."""
        cls = type(e).__name__
        if cls == "String":
            return "char*"
        if cls == "Number":
            return "double" if isinstance(e.value, float) else "int"
        if cls == "Identifier":
            return self.var_types.get(e.name, "int")
        if cls == "Sqrt":
            return "double"                  # akar selalu menghasilkan pecahan
        if cls == "BinaryOp":
            if e.op in ("<", ">", "==", "!=", "<=", ">="):
                return "int"                 # hasil perbandingan = boolean
            lt, rt = self._etype(e.left), self._etype(e.right)
            return max((lt, rt), key=lambda x: _RANK[x])
        return "int"

    # ================= Tahap 2: hasilkan kode =================
    def _emit(self, line):
        self.lines.append("    " * self.level + line)

    def _gen(self, node):
        getattr(self, "_gen_" + type(node).__name__)(node)

    def _gen_VarDecl(self, node):
        if node.value is not None:           # deklarasi sudah di atas; ini isinya
            self._emit(f"{node.name} = {self._expr(node.value)};")

    def _gen_Assign(self, node):
        self._emit(f"{node.name} = {self._expr(node.value)};")

    def _gen_Print(self, node):
        spec = {"char*": "%s", "double": "%g", "int": "%d"}
        fmt = "".join(spec[self._etype(a)] for a in node.args)
        vals = ", ".join(self._expr(a) for a in node.args)
        self._emit(f'printf("{fmt}\\n", {vals});')

    def _gen_Input(self, node):
        t = self.var_types.get(node.name, "int")
        if t == "char*":
            raise NotImplementedError(
                f"baco({node.name}): input untuk tipe teks (kato) belum didukung "
                f"di backend C. Pakai bulek/pacahan untuk input.")
        spec = "%lf" if t == "double" else "%d"
        self._emit(f'scanf("{spec}", &{node.name});')

    def _gen_Block(self, node):
        for stmt in node.statements:
            self._gen(stmt)

    def _gen_If(self, node):
        self._emit(f"if ({self._expr(node.condition)}) {{")
        self.level += 1
        self._gen(node.then_block)
        self.level -= 1
        if node.else_block is not None:
            self._emit("} else {")
            self.level += 1
            self._gen(node.else_block)
            self.level -= 1
        self._emit("}")

    def _gen_While(self, node):
        self._emit(f"while ({self._expr(node.condition)}) {{")
        self.level += 1
        self._gen(node.body)
        self.level -= 1
        self._emit("}")

    # ---- expression -> teks C ----
    def _expr(self, e) -> str:
        cls = type(e).__name__
        if cls == "Number":
            return str(e.value)
        if cls == "String":
            return _c_escape(e.value)
        if cls == "Identifier":
            return e.name
        if cls == "Sqrt":
            return f"sqrt((double)({self._expr(e.arg)}))"
        if cls == "BinaryOp":
            return f"({self._expr(e.left)} {e.op} {self._expr(e.right)})"
        raise ValueError(f"Tidak bisa menerjemahkan ke C: {cls}")


if __name__ == "__main__":
    from lexer import Lexer
    from parser import Parser
    from ast_builder import ASTBuilder
    src = 'kato p = "halo"; cetak(p); bulek x = 2 + 3; jiko (x>1){cetak(x);} indak {cetak(0);}'
    tree = ASTBuilder().build(Parser(Lexer(src).tokenize()).parse())
    print(CBackend().generate(tree))

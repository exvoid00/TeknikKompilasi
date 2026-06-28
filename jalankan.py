"""
jalankan.py — Menjalankan program berbahasa Minang dari sebuah file.

Inilah cara "memakai" bahasa kita: tulis kode di file .mng, lalu jalankan.

    python jalankan.py contoh.mng

Alur internal: baca file -> Lexer -> Parser -> AST -> (eksekusi via Evaluator)
"""

import sys
import os
from lexer import Lexer
from parser import Parser
from ast_builder import ASTBuilder
from semantic_analyzer import SemanticAnalyzer, SemanticError
from evaluator import Evaluator


def jalankan_file(path):
    if not os.path.exists(path):
        print(f"File tidak ditemukan: {path}")
        return
    with open(path, encoding="utf-8") as f:
        source = f.read()

    # Pipeline kompilasi -> AST, lalu dieksekusi
    try:
        tokens = Lexer(source).tokenize()
        ast_tree = ASTBuilder().build(Parser(tokens).parse())
        # Cek semantik dulu (variabel belum dideklarasi, deklarasi ganda)
        SemanticAnalyzer().analyze(ast_tree)
    except (SyntaxError, SemanticError) as e:
        print(f"[ERROR] {e}")
        return

    print(f"--- Menjalankan {os.path.basename(path)} ---")
    try:
        Evaluator().run(ast_tree)
    except (NameError, ValueError, ZeroDivisionError) as e:
        print(f"[ERROR saat dijalankan] {e}")
        return
    print("--- Selesai ---")


if __name__ == "__main__":
    # Ambil nama file dari argumen, default ke 'contoh.mng'
    nama_file = sys.argv[1] if len(sys.argv) > 1 else "contoh.mng"
    jalankan_file(nama_file)

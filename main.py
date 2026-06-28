"""
main.py — Pipeline utama Compiler Mini (Project UAS Teknik Kompilasi)
Bahasa pemrograman memakai KEYWORD BAHASA MINANG.

Alur lengkap (sesuai ketentuan tugas):
    source code
        -> Lexer                 (lexer.py)            7+ jenis token
        -> Parser  -> PARSE TREE (parser.py)           cek urutan token
        -> AST Builder -> AST    (ast_builder.py)      dari parse tree
        -> Semantic Analysis     (semantic_analyzer.py)
        -> Optimization          (code_optimizer.py)
        -> Code Generation       (code_generator.py)   Three-Address Code
"""

from lexer import Lexer
from parser import Parser
from parse_tree import print_parse_tree
from ast_builder import ASTBuilder
from semantic_analyzer import SemanticAnalyzer, SemanticError
from code_optimizer import Optimizer
from code_generator import CodeGenerator
import ast


def dump_ast(node, indent=0):
    """Cetak AST secara rapi."""
    pad = "  " * indent
    fields, children = [], []
    for name, value in vars(node).items():
        if isinstance(value, (ast.Node, list)):
            children.append(value)
        else:
            fields.append(f"{name}={value!r}")
    print(f"{pad}{type(node).__name__}({', '.join(fields)})")
    for value in children:
        items = value if isinstance(value, list) else [value]
        for item in items:
            if isinstance(item, ast.Node):
                dump_ast(item, indent + 1)


def section(title):
    print("\n" + "=" * 55)
    print(title)
    print("=" * 55)


def compile_source(source: str):
    section("SOURCE CODE (Bahasa Minang)")
    print(source.strip())

    # --- Tahap 1: Lexical Analysis ---
    section("[1] LEXICAL ANALYSIS  (Lexer)")
    tokens = Lexer(source).tokenize()
    jenis = sorted({t.type.name for t in tokens})
    print(f"Total {len(tokens)} token, {len(jenis)} jenis: {', '.join(jenis)}\n")
    for tok in tokens:
        print("   ", tok)

    # --- Tahap 2: Syntax Analysis -> Parse Tree ---
    section("[2] SYNTAX ANALYSIS  (Parser -> Parse Tree)")
    parse_tree = Parser(tokens).parse()
    print_parse_tree(parse_tree)

    # --- Tahap 3: AST (dibangun DARI parse tree) ---
    section("[3] ABSTRACT SYNTAX TREE  (AST dari Parse Tree)")
    tree = ASTBuilder().build(parse_tree)
    dump_ast(tree)

    # --- Tahap 4: Semantic Analysis ---
    section("[4] SEMANTIC ANALYSIS")
    try:
        SemanticAnalyzer().analyze(tree)
        print("OK - tidak ada error semantik.")
    except SemanticError as e:
        print(f"Error semantik:\n{e}")
        return

    # --- Tahap 5: Optimization ---
    section("[5] CODE OPTIMIZATION")
    optimizer = Optimizer()
    tree = optimizer.optimize(tree)
    print(f"{optimizer.changes} optimasi diterapkan (constant folding).")
    dump_ast(tree)

    # --- Tahap 6: Code Generation ---
    section("[6] CODE GENERATION  (Three-Address Code)")
    code = CodeGenerator().generate(tree)
    for instr in code:
        print("   ", instr)


if __name__ == "__main__":
    # Program contoh — keyword Minang:
    #   bulek=int  pacahan=float  kato=string  cetak=print  baco=input
    #   jiko=if    indak/lain=else            salamo=while
    program = """
    kato pesan = "Apo kaba";
    cetak(pesan);

    bulek x = 2 + 3 * 4;
    baco(x);

    jiko (x > 10) {
        cetak("gadang");
    } indak {
        cetak("ketek");
    }

    bulek i = 0;
    salamo (i < 3) {
        cetak(i);
        i = i + 1;
    }
    """
    compile_source(program)

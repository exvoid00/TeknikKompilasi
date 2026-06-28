"""
grammar.py — Definisi Grammar (Tata Bahasa)  [Bahasa MINANG]
Mendokumentasikan aturan produksi bahasa yang dipakai parser.
Notasi: EBNF.

    Keyword Minang:
        jiko = if      lain = else     salamo = while
        cetak = print  baco = input    bulek = int    pacahan = float

    Fungsi bawaan: cetak (OUTPUT/print), baco (INPUT)

    program     ::= statement* EOF

    statement   ::= var_decl
                  | assignment
                  | print_stmt
                  | input_stmt
                  | if_stmt
                  | while_stmt

    var_decl    ::= type IDENTIFIER ( "=" expression )? ";"
    assignment  ::= IDENTIFIER "=" expression ";"
    print_stmt  ::= "cetak" "(" expression ")" ";"
    input_stmt  ::= "baco" "(" IDENTIFIER ")" ";"
    if_stmt     ::= "jiko" "(" expression ")" block ( "lain" block )?
    while_stmt  ::= "salamo" "(" expression ")" block
    block       ::= "{" statement* "}"

    expression  ::= comparison
    comparison  ::= additive ( ( "<"|">"|"=="|"!="|"<="|">=" ) additive )*
    additive    ::= term ( ( "+" | "-" ) term )*
    term        ::= factor ( ( "*" | "/" ) factor )*
    factor      ::= NUMBER
                  | IDENTIFIER
                  | "(" expression ")"

    type        ::= "bulek" | "pacahan"
"""

# Aturan produksi dalam bentuk dictionary (opsional, bisa dipakai
# untuk membangun parsing table atau dokumentasi otomatis).
GRAMMAR = {
    "program":    [["statement*", "EOF"]],
    "statement":  [["var_decl"], ["assignment"], ["print_stmt"],
                   ["input_stmt"], ["if_stmt"], ["while_stmt"]],
    "var_decl":   [["type", "IDENTIFIER", "=", "expression", ";"]],
    "assignment": [["IDENTIFIER", "=", "expression", ";"]],
    "print_stmt": [["cetak", "(", "expression", ")", ";"]],
    "input_stmt": [["baco", "(", "IDENTIFIER", ")", ";"]],
    "if_stmt":    [["jiko", "(", "expression", ")", "block", "(lain block)?"]],
    "while_stmt": [["salamo", "(", "expression", ")", "block"]],
    "block":      [["{", "statement*", "}"]],
    "expression": [["comparison"]],
    "comparison": [["additive", "(rel_op additive)*"]],
    "additive":   [["term", "(('+'|'-') term)*"]],
    "term":       [["factor", "(('*'|'/') factor)*"]],
    "factor":     [["NUMBER"], ["IDENTIFIER"], ["(", "expression", ")"]],
    "type":       [["bulek"], ["pacahan"]],
}

# Terminal symbols
TERMINALS = {"NUMBER", "IDENTIFIER", "+", "-", "*", "/",
             "<", ">", "==", "!=", "<=", ">=",
             "(", ")", "{", "}", ";", "=",
             "bulek", "pacahan", "cetak", "baco",
             "jiko", "lain", "salamo", "EOF"}

# Start symbol
START = "program"

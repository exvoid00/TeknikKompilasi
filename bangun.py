"""
bangun.py — "Kompiler nyata": ubah program Minang (.mng) jadi file .exe.

    python bangun.py contoh.mng           # hasilkan build/contoh.exe
    python bangun.py contoh.mng --jalan   # langsung jalankan setelah dibangun

Alur lengkap:
    .mng  -> Lexer -> Parser -> AST -> Optimizer
          -> backend_c (kode C)  -> gcc  -> .exe
"""

import os
import sys
import glob
import shutil
import subprocess

from lexer import Lexer
from parser import Parser
from ast_builder import ASTBuilder
from code_optimizer import Optimizer
from backend_c import CBackend


def cari_gcc():
    """Temukan gcc: cek PATH dulu, lalu lokasi instalasi WinLibs (winget)."""
    found = shutil.which("gcc")
    if found:
        return found
    pola = os.path.join(
        os.environ.get("LOCALAPPDATA", ""),
        "Microsoft", "WinGet", "Packages",
        "BrechtSanders.WinLibs*", "**", "gcc.exe",
    )
    hasil = glob.glob(pola, recursive=True)
    return hasil[0] if hasil else None


def bangun(path, jalan=False):
    if not os.path.exists(path):
        print(f"File tidak ditemukan: {path}")
        return 1

    with open(path, encoding="utf-8") as f:
        source = f.read()

    # --- Kompilasi sampai AST, lalu optimasi ---
    tokens = Lexer(source).tokenize()
    tree = ASTBuilder().build(Parser(tokens).parse())
    Optimizer().optimize(tree)

    # --- Terjemahkan ke C ---
    kode_c = CBackend().generate(tree)

    nama = os.path.splitext(os.path.basename(path))[0]
    out_dir = os.path.join(os.path.dirname(os.path.abspath(path)), "build")
    os.makedirs(out_dir, exist_ok=True)
    file_c = os.path.join(out_dir, nama + ".c")
    file_exe = os.path.join(out_dir, nama + ".exe")

    with open(file_c, "w", encoding="utf-8") as f:
        f.write(kode_c)
    print(f"[1/2] Kode C ditulis : {file_c}")

    # --- Panggil gcc ---
    gcc = cari_gcc()
    if not gcc:
        print("gcc tidak ditemukan. Instal dulu:")
        print("  winget install -e --id BrechtSanders.WinLibs.POSIX.UCRT")
        print(f"(Kode C tetap tersimpan di {file_c})")
        return 1

    proses = subprocess.run([gcc, file_c, "-o", file_exe, "-lm"],
                            capture_output=True, text=True)
    if proses.returncode != 0:
        print("[2/2] GAGAL kompilasi gcc:\n" + proses.stderr)
        return 1
    print(f"[2/2] Executable    : {file_exe}")
    print("Selesai! Jalankan dengan:")
    print(f"  {file_exe}")

    if jalan:
        print("\n--- Output program ---")
        sys.stdout.flush()
        subprocess.run([file_exe])
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    jalan = "--jalan" in sys.argv
    nama_file = args[0] if args else "contoh.mng"
    sys.exit(bangun(nama_file, jalan))

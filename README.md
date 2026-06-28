# Mini-Compiler Bahasa Minang

Project UAS mata kuliah **Teknik Kompilasi**: sebuah **mini-compiler** sederhana
yang bahasanya memakai **keyword Bahasa Minang**, dibangun dengan **Python**.

## 🌼 Keyword Bahasa Minang
| Minang | Arti |
|--------|------|
| `bulek` | int (bilangan bulat) |
| `pacahan` | float (bilangan pecahan) |
| `kato` | string (teks) |
| `cetak` | print (output) |
| `baco` | input |
| `jiko` | if |
| `indak` | else |
| `salamo` | while |
| `akar` | akar kuadrat (fungsi bawaan) |

## 🔧 Enam Tahap Compiler
1. **Lexical Analysis** (`lexer.py`) — memecah kode menjadi token
2. **Syntax Analysis** (`parser.py`) — membentuk Parse Tree (recursive descent)
3. **AST** (`ast_builder.py`) — dibangun dari parse tree
4. **Semantic Analysis** (`semantic_analyzer.py`) — pengecekan makna pakai Symbol Table
5. **Optimization** (`code_optimizer.py`) — constant folding
6. **Code Generation** (`code_generator.py`) — Three-Address Code

## ▶️ Cara Menjalankan
Butuh **Python 3**. Untuk compile ke `.exe` butuh **GCC**.

```bash
# 1) Tampilkan 6 tahap compiler
python main.py

# 2) Jalankan program .mng langsung (interpreter)
python jalankan.py hitung.mng

# 3) Compile program .mng menjadi file .exe lalu jalankan
python bangun.py hitung.mng --jalan
```

## 📂 Contoh Program (.mng)
- `contoh.mng` — program lengkap (input, percabangan, perulangan)
- `hitung.mng` — kalkulator (tambah, kurang, kali, bagi, akar)
- `salah.mng` — contoh program yang error (untuk demo deteksi semantik)

## 📝 Contoh Kode
```
bulek a = 2;
jiko (a > 1) {
    cetak("gadang");
} indak {
    cetak("ketek");
}
pacahan r = akar(16);   // hasil 4
cetak(r);
```

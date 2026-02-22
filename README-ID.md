# ₿ Bitcoin Wallet Analyzer

> **Professional `wallet.dat` analysis & hash extraction tool**  
> SHA-512 Iterative · AES-256-CBC · BerkeleyDB · HashCat `-m 11300`

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Version](https://img.shields.io/badge/Version-1.0%20PRO-orange?style=flat-square)
![Tested](https://img.shields.io/badge/Tested%20on-Python%203.10.11-success?style=flat-square)

---

## 📸 Screenshot

```
╔══════════════════════════════════════════════════════════════╗
║  ₿  Bitcoin Wallet Analyzer                    v1.0 PRO     ║
║     wallet.dat · SHA-512 · AES-256-CBC · BerkeleyDB         ║
╠══════════════════════════════════════════════════════════════╣
║  [ Overview ] [ BDB Structure ] [ Crypto Info ] [ Hash ]    ║
║  [ Addresses ] [ Hex Viewer ] [ Recovery Guide ]            ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 📖 Deskripsi

**Bitcoin Wallet Analyzer** adalah tool berbasis GUI (Graphical User Interface) yang dibuat dengan Python dan Tkinter untuk menganalisis file `wallet.dat` milik Bitcoin Core. Tool ini membantu pengguna memahami struktur internal wallet, mengekstrak informasi kriptografi, dan mempersiapkan hash untuk proses pemulihan password.

Tool ini **berjalan 100% secara lokal** — tidak ada data yang dikirim ke server manapun.

### Fitur Utama

| Tab | Fungsi |
|-----|--------|
| **Overview** | Ringkasan lengkap file wallet: ukuran, format, enkripsi, checksum MD5/SHA-256, jumlah key |
| **BDB Structure** | Parsing struktur internal BerkeleyDB: page metadata, magic bytes, LSN, flags, record markers, strings scan, entropy analysis |
| **Crypto Info** | Informasi kriptografi lengkap: cipher AES-256-CBC, KDF SHA-512, iterasi, BIP32/HD detection, script type hints, randomness test |
| **Hash Extraction** | Ekstrak hash menggunakan script resmi `bitcoin2john.py` dalam format HashCat `-m 11300` |
| **Addresses** | Ekstraksi alamat Bitcoin: P2PKH (`1...`), P2SH (`3...`), SegWit bech32 (`bc1q...`), Taproot (`bc1p...`) |
| **Hex Viewer** | Raw hex dump 16-byte per baris dengan panel ASCII, navigasi offset |
| **Recovery Guide** | Panduan pemulihan wallet terenkripsi maupun tidak terenkripsi |

---

## ⚙️ Persyaratan Sistem

### Python Version
- **Python 3.10.x** (tested & verified ✅)
- Python 3.8+ seharusnya kompatibel

### Modul Python

Tool ini menggunakan **hanya modul bawaan Python (standard library)** — tidak perlu install library tambahan:

| Modul | Keterangan | Bawaan? |
|-------|-----------|---------|
| `tkinter` | GUI framework | ✅ Built-in |
| `tkinter.ttk` | Themed widget | ✅ Built-in |
| `tkinter.scrolledtext` | Scrollable text widget | ✅ Built-in |
| `tkinter.filedialog` | File browser dialog | ✅ Built-in |
| `tkinter.messagebox` | Popup message box | ✅ Built-in |
| `struct` | Binary data parsing | ✅ Built-in |
| `math` | Kalkulasi entropy | ✅ Built-in |
| `re` | Regex untuk ekstraksi alamat | ✅ Built-in |
| `hashlib` | MD5, SHA-1, SHA-256 checksum | ✅ Built-in |
| `pathlib` | Path handling | ✅ Built-in |
| `collections` | Counter untuk byte frequency | ✅ Built-in |
| `threading` | Background analysis (non-blocking UI) | ✅ Built-in |
| `datetime` | Timestamp file info | ✅ Built-in |
| `subprocess` | Menjalankan `bitcoin2john.py` | ✅ Built-in |
| `urllib.request` | Download `bitcoin2john.py` otomatis | ✅ Built-in |
| `numpy` | Advanced pattern analysis *(opsional)* | ⚪ Optional |

> **Catatan:** `numpy` bersifat opsional. Tool tetap berjalan penuh tanpa numpy.

---

## 🚀 Instalasi & Cara Menjalankan

### Windows

```batch
:: Pastikan Python sudah terinstall
python --version

:: Download / clone repository
git clone https://github.com/syabiz/bitcoin-wallet-analyzer.git
cd bitcoin-wallet-analyzer

:: Jalankan langsung (tidak perlu install apapun)
python bitcoin_wallet_analyzer.py
```

### Linux / macOS

```bash
# Pastikan tkinter tersedia (Linux mungkin perlu install)
sudo apt install python3-tk      # Ubuntu/Debian
sudo dnf install python3-tkinter # Fedora

# Clone dan jalankan
git clone https://github.com/syabiz/bitcoin-wallet-analyzer.git
cd bitcoin-wallet-analyzer
python3 bitcoin_wallet_analyzer.py
```

---

## 📋 Tutorial Penggunaan

### Step 1 — Buka File Wallet

1. Jalankan `python bitcoin_wallet_analyzer.py`
2. Klik tombol **Browse...** di bagian atas
3. Pilih file `wallet.dat` dari komputer Anda
4. Klik **⚡ Analyze Wallet**

> File `wallet.dat` biasanya ada di:
> - **Windows:** `%APPDATA%\Bitcoin\wallet.dat`
> - **Linux:** `~/.bitcoin/wallet.dat`
> - **macOS:** `~/Library/Application Support/Bitcoin/wallet.dat`

---

### Step 2 — Baca Hasil di Tab Overview

Setelah analisis selesai, tab **Overview** menampilkan:

```
File: C:\Users\...\wallet.dat
Size: 262,144 bytes (256.00 KB)
MD5:  a1b2c3d4...
SHA-256: e5f6g7h8...

Format: Berkeley DB v9 (BTree)
Encrypted: YES  (password protected)
Keys found: 101
```

**Stat Cards** di bagian atas menampilkan ringkasan cepat:
- `File Size` — Ukuran file
- `Format` — Format database (BDB v8/v9 atau SQLite)
- `Encrypted` — Status enkripsi (`YES` / `NO`)
- `Est. Keys` — Perkiraan jumlah private key
- `Entropy` — Nilai Shannon entropy (0–8)

---

### Step 3 — Analisis Struktur BDB

Tab **BDB Structure** menampilkan:

- **BDB Page Metadata** — pagesize, version, magic, flags, jumlah record
- **Key-Value Record Markers** — semua marker yang ditemukan (`mkey`, `ckey`, `name`, `tx`, `pool`, `hdchain`, dll) beserta jumlah dan posisi offset
- **Printable Strings** — string yang terbaca di dalam binary file
- **Entropy Analysis** — Shannon entropy dengan visualisasi bar
- **File Checksums** — MD5, SHA-1, SHA-256

---

### Step 4 — Informasi Kriptografi

Tab **Crypto Info** menampilkan:

- **Encryption Status** — Apakah wallet terenkripsi dan posisi `mkey`
- **Master Key Details** — Hex dump record `mkey` + estimasi iterasi KDF
- **Key Inventory** — Jumlah `ckey`, `key`, `wkey`, `pool`, `hdchain`
- **Cipher Details** — AES-256-CBC, SHA-512 KDF, salt size, padding PKCS7
- **HD Wallet Detection** — Deteksi BIP32 xprv/xpub, hdchain, hdseed
- **Script Type Hints** — P2PKH, P2SH, SegWit, Taproot
- **Randomness Test** — Runs test untuk kualitas enkripsi

---

### Step 5 — Ekstrak Hash (untuk password recovery)

Tab **Hash Extraction**:

1. Klik **Extract Hash via bitcoin2john.py**
2. Jika `bitcoin2john.py` belum ada, tool akan menawarkan untuk download otomatis dari repo resmi John the Ripper
3. Hash akan tampil dalam format:
   ```
   wallet.dat:$bitcoin$64$abcdef....$16$deadbeef....$35714$2$00$2$00
   ```
4. Klik **Copy Hash** atau **Save Hash** untuk menyimpan

**Crack dengan HashCat:**
```bash
hashcat -m 11300 hash.txt rockyou.txt
hashcat -m 11300 hash.txt rockyou.txt -r rules/best64.rule
```

**Crack dengan John the Ripper:**
```bash
john --format=bitcoin-core hash.txt --wordlist=wordlist.txt
```

---

### Step 6 — Ekstrak Alamat Bitcoin

Tab **Addresses**:

1. Klik **Extract Addresses**
2. Tool akan mencari semua pola alamat Bitcoin:
   - `1...` dan `3...` (Legacy P2PKH / P2SH)
   - `bc1q...` (SegWit bech32)
   - `bc1p...` (Taproot)
3. Klik **Save List** untuk simpan ke file `.txt`

> ⚠️ Ekstraksi alamat menggunakan regex pattern matching. Hasilnya bersifat **perkiraan** dan mungkin mengandung false positives.

---

### Step 7 — Hex Viewer

Tab **Hex Viewer** menampilkan raw binary dalam format hex:

```
Offset      00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F   ASCII
─────────────────────────────────────────────────────────────────────────
0x00000000  62 31 05 00 00 00 00 00  00 00 00 00 09 00 00 00   b1..............
0x00000010  00 10 00 00 09 00 00 00  00 00 00 00 00 00 00 00   ................
```

- Masukkan offset (dalam hex) di field **Offset** lalu klik **Go** untuk navigasi
- Default menampilkan 8 KB pertama (512 rows)

---

## 🔐 Algoritma Kriptografi (Referensi Teknis)

```
Password Recovery Flow:
──────────────────────────────────────────────────────
1. KDF (Key Derivation):
   hash[0] = SHA512(password + salt)
   hash[N] = SHA512(hash[N-1])        ← diulang sebanyak iterations kali
   key = hash_final[0..31]            ← 32 bytes untuk AES-256
   iv  = hash_final[32..47]           ← 16 bytes untuk CBC IV

2. Decryption:
   plaintext = AES-256-CBC-Decrypt(encrypted_key, key, iv)

3. Validation:
   plaintext[-16:] == b'\x10' * 16    ← PKCS7 padding check

HashCat mode : -m 11300
John mode    : --format=bitcoin-core
```

---

## 📁 Struktur File

```
bitcoin-wallet-analyzer/
├── bitcoin_wallet_analyzer.py   # Script utama
├── README.md                    # Dokumentasi ini
├── LICENSE                      # MIT License
└── bitcoin2john.py              # (opsional, download otomatis)
```

---

## ⚠️ Disclaimer

- Tool ini dibuat untuk tujuan **edukasi dan pemulihan wallet milik sendiri**
- **Jangan** gunakan untuk mengakses wallet orang lain tanpa izin tertulis
- Akses tidak sah ke wallet cryptocurrency adalah **ilegal**
- Ekstraksi alamat bersifat perkiraan — gunakan `bitcoin-cli dumpwallet` untuk hasil lengkap
- Tool berjalan 100% offline — tidak ada data yang dikirim ke server

---

## 💰 Donasi

Jika tool ini membantu Anda, traktir saya kopi atau pizza via crypto:

| Coin | Address |
|------|---------|
| **Bitcoin (BTC)** | `bc1qn6t8hy8memjfzp4y3sh6fvadjdtqj64vfvlx58` |
| **Ethereum (ETH)** | `0x512936ca43829C8f71017aE47460820Fe703CAea` |
| **Solana (SOL)** | `6ZZrRmeGWMZSmBnQFWXG2UJauqbEgZnwb4Ly9vLYr7mi` |
| **PayPal** | `syabiz@yandex.com` |

---

## 📞 Kontak

- **GitHub Issues:** [github.com/syabiz/bitcoin-wallet-analyzer/issues](https://github.com/syabiz/bitcoin-wallet-analyzer/issues)
- **Email:** syabiz@yandex.com
- **Website:** [syabiz.github.io](https://syabiz.github.io)

---

## 📄 License

MIT License — lihat file [LICENSE](LICENSE) untuk detail lengkap.

---

<div align="center">

Made with ❤️ for Bitcoin education and learning — **by Syabiz**  
*Last updated: February 2026*

</div>

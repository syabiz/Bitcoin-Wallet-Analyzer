# Bitcoin Wallet Analyzer

> **Professional `wallet.dat` analysis & hash extraction tool**  
> SHA-512 Iterative · AES-256-CBC · BerkeleyDB · HashCat `-m 11300`

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Version](https://img.shields.io/badge/Version-1.0%20PRO-orange?style=flat-square)
![Tested](https://img.shields.io/badge/Tested%20on-Python%203.10.11-success?style=flat-square)

---

## Description

**Bitcoin Wallet Analyzer** is a Python-based GUI tool built with Tkinter for analyzing Bitcoin Core `wallet.dat` files. It helps users understand the internal structure of a wallet, extract cryptographic information, examine raw binary data, and prepare password hashes for recovery.

This tool runs **100% locally** — no data is ever sent to any server.

---

## Features

| Tab | Description |
|-----|-------------|
| **Overview** | Full file summary: size, format, encryption status, MD5/SHA-256 checksums, key count |
| **BDB Structure** | BerkeleyDB internal parsing: page metadata, magic bytes, LSN, flags, record markers with offsets, strings scan, entropy analysis |
| **Crypto Info** | Full cryptographic details: AES-256-CBC cipher, SHA-512 KDF, iteration count, BIP32/HD detection, script type hints, randomness test |
| **Hash Extraction** | Extract hash using the official `bitcoin2john.py` script in HashCat `-m 11300` format |
| **Addresses** | Bitcoin address extraction: P2PKH (`1...`), P2SH (`3...`), SegWit bech32 (`bc1q...`), Taproot (`bc1p...`) |
| **Hex Viewer** | Raw hex dump, 16 bytes per row with ASCII panel, offset navigation |
| **Recovery Guide** | Step-by-step guide for recovering encrypted and unencrypted wallets |

---

## Requirements

### Python Version

- **Python 3.10.x** — tested & verified on Python 3.10.11
- Python 3.8+ should be compatible

### Python Modules

This tool uses **only Python standard library modules** — no external packages required:

| Module | Purpose | Built-in? |
|--------|---------|-----------|
| `tkinter` | GUI framework | Yes |
| `tkinter.ttk` | Themed widgets | Yes |
| `tkinter.scrolledtext` | Scrollable text widget | Yes |
| `tkinter.filedialog` | File browser dialog | Yes |
| `tkinter.messagebox` | Popup dialogs | Yes |
| `struct` | Binary data parsing | Yes |
| `math` | Entropy calculation | Yes |
| `re` | Regex for address extraction | Yes |
| `hashlib` | MD5, SHA-1, SHA-256 checksums | Yes |
| `pathlib` | File path handling | Yes |
| `collections` | Byte frequency counter | Yes |
| `threading` | Background analysis (non-blocking UI) | Yes |
| `datetime` | File timestamp info | Yes |
| `subprocess` | Running `bitcoin2john.py` | Yes |
| `urllib.request` | Auto-download `bitcoin2john.py` | Yes |
| `numpy` | Advanced pattern analysis | Optional |

> `numpy` is optional. The tool runs fully without it.

---

## Installation & Running

### Windows

```batch
:: Check Python version
python --version

:: Clone the repository
git clone https://github.com/syabiz/bitcoin-wallet-analyzer.git
cd bitcoin-wallet-analyzer

:: Run directly — no pip install needed
python bitcoin_wallet_analyzer.py
```

### Linux / macOS

```bash
# Make sure tkinter is available
sudo apt install python3-tk        # Ubuntu / Debian
sudo dnf install python3-tkinter   # Fedora

# Clone and run
git clone https://github.com/syabiz/bitcoin-wallet-analyzer.git
cd bitcoin-wallet-analyzer
python3 bitcoin_wallet_analyzer.py
```

---

## How to Use

### Step 1 — Open a Wallet File

1. Launch the tool: `python bitcoin_wallet_analyzer.py`
2. Click **Browse...** at the top
3. Select your `wallet.dat` file
4. Click **Analyze Wallet**

Default `wallet.dat` locations:

| OS | Path |
|----|------|
| Windows | `%APPDATA%\Bitcoin\wallet.dat` |
| Linux | `~/.bitcoin/wallet.dat` |
| macOS | `~/Library/Application Support/Bitcoin/wallet.dat` |

---

### Step 2 — Overview Tab

After analysis completes, the **Overview** tab displays a full summary along with five stat cards at the top:

| Card | Description |
|------|-------------|
| `File Size` | Size of the wallet file |
| `Format` | Database format (BDB v8/v9 or SQLite) |
| `Encrypted` | Encryption status (YES / NO) |
| `Est. Keys` | Estimated number of private keys |
| `Entropy` | Shannon entropy value (0 to 8 scale) |

Example output:

```
File    : C:\Users\...\wallet.dat
Size    : 262,144 bytes  (256.00 KB)
MD5     : a1b2c3d4e5f6...
SHA-256 : 9f8e7d6c5b4a...

Format    : Berkeley DB v9 (BTree)
Encrypted : YES  (password protected)
Keys found: 101
```

---

### Step 3 — BDB Structure Tab

Parses BerkeleyDB internals including:

- **Page Metadata** — page size, version, magic number, LSN, flags, record counts
- **Key-Value Record Markers** — all found markers (`mkey`, `ckey`, `name`, `tx`, `pool`, `hdchain`, etc.) with occurrence count and hex offsets
- **Printable Strings** — readable strings found in the binary data
- **Entropy Analysis** — Shannon entropy with visual bar chart
- **File Checksums** — MD5, SHA-1, SHA-256

---

### Step 4 — Crypto Info Tab

Provides full cryptographic analysis:

- **Encryption Status** — whether the wallet is encrypted and position of `mkey` record
- **Master Key Details** — hex dump of `mkey` record with estimated KDF iteration count and cracking speed estimate
- **Key Inventory** — counts for `ckey`, `key`, `wkey`, `pool`, `hdchain`
- **Cipher Details** — AES-256-CBC, SHA-512 KDF, 8-byte salt, PKCS7 padding, HashCat mode
- **HD Wallet Detection** — BIP32 xprv/xpub, hdchain, hdseed markers
- **Script Type Hints** — P2PKH, P2SH, SegWit, Taproot bytecode detection
- **Randomness Test** — runs test for encryption quality assessment

---

### Step 5 — Hash Extraction Tab

1. Click **Extract Hash via bitcoin2john.py**
2. If `bitcoin2john.py` is not present, the tool will offer to **download it automatically** from the official John the Ripper repository
3. The extracted hash appears in HashCat format:

```
wallet.dat:$bitcoin$64$abcdef....$16$deadbeef....$35714$2$00$2$00
```

4. Click **Copy Hash** or **Save Hash** to export it

**Cracking with HashCat:**

```bash
# Dictionary attack
hashcat -m 11300 hash.txt rockyou.txt

# Dictionary + mutation rules
hashcat -m 11300 hash.txt rockyou.txt -r rules/best64.rule

# Brute force up to 8 characters
hashcat -m 11300 hash.txt -a 3 ?a?a?a?a?a?a?a?a
```

**Cracking with John the Ripper:**

```bash
john --format=bitcoin-core hash.txt --wordlist=wordlist.txt
john --show hash.txt
```

Recommended wordlists:
- [rockyou.txt](https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt) — 14 million common passwords
- [SecLists](https://github.com/danielmiessler/SecLists) — comprehensive collection
- [CrackStation](https://crackstation.net/crackstation-wordlist-password-cracking-dictionary.htm) — 15 GB mega list

---

### Step 6 — Addresses Tab

1. Click **Extract Addresses**
2. The tool scans for Bitcoin address patterns across all types:
   - `1...` and `3...` — Legacy P2PKH and P2SH
   - `bc1q...` — SegWit bech32 (P2WPKH / P2WSH)
   - `bc1p...` — Taproot (P2TR)
3. Click **Save List** to export as a `.txt` file

> Address extraction uses regex pattern matching on raw binary. Results are approximate and may include false positives. For a complete and verified list, use `bitcoin-cli dumpwallet`.

---

### Step 7 — Hex Viewer Tab

Displays the raw binary file content as a classic hex dump:

```
Offset      00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F   ASCII
────────────────────────────────────────────────────────────────────────
0x00000000  62 31 05 00 00 00 00 00  00 00 00 00 09 00 00 00   b1..............
0x00000010  00 10 00 00 09 00 00 00  00 00 00 00 00 00 00 00   ................
```

- Enter an offset (in hexadecimal) in the Offset field and click **Go** to jump to a specific location
- Default view shows the first 8 KB of the file

---

## Technical Reference — Cryptographic Algorithm

```
Bitcoin Core wallet.dat Password Recovery Flow
──────────────────────────────────────────────────────────────────

1. Key Derivation Function (KDF):
   hash[0]   = SHA512(password + salt)
   hash[N]   = SHA512(hash[N-1])        <- repeated N times (iterations)
   key       = hash_final[0..31]        <- 32 bytes  ->  AES-256 key
   iv        = hash_final[32..47]       <- 16 bytes  ->  AES-CBC IV

2. Decryption:
   plaintext = AES-256-CBC-Decrypt(encrypted_key, key, iv)

3. Validation:
   plaintext[-16:] == b'\x10' * 16      <- PKCS7 padding check = password correct

HashCat mode : -m 11300
John mode    : --format=bitcoin-core
```

---

## Repository Structure

```
bitcoin-wallet-analyzer/
├── bitcoin_wallet_analyzer.py   # Main script
├── README.md                    # This documentation
├── LICENSE                      # MIT License
└── bitcoin2john.py              # Optional — auto-downloaded if missing
```

---

## Disclaimer

- This tool is intended **only for educational purposes** and for recovering wallets you legally own
- **Do not** use this tool to access wallets that do not belong to you
- Unauthorized access to cryptocurrency wallets may be **illegal** under applicable laws in your jurisdiction
- Address extraction results are approximate — use `bitcoin-cli dumpwallet` for a complete verified list
- This tool runs entirely offline — no data is transmitted to any external server

---

## Donate

If this tool has been useful, feel free to support development:

| Coin | Address |
|------|---------|
| **Bitcoin (BTC)** | `bc1qn6t8hy8memjfzp4y3sh6fvadjdtqj64vfvlx58` |
| **Ethereum (ETH)** | `0x512936ca43829C8f71017aE47460820Fe703CAea` |
| **Solana (SOL)** | `6ZZrRmeGWMZSmBnQFWXG2UJauqbEgZnwb4Ly9vLYr7mi` |
| **PayPal** | `syabiz@yandex.com` |

Donations help support new features, documentation, and maintenance.

---

## Contact

- **GitHub Issues:** [github.com/syabiz/bitcoin-wallet-analyzer/issues](https://github.com/syabiz/bitcoin-wallet-analyzer/issues)
- **Email:** syabiz@yandex.com
- **Twitter:** @syabiz
- **Website:** [syabiz.github.io](https://syabiz.github.io)

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Made with love for Bitcoin education and learning — **by Syabiz**  
*Last updated: February 2026*

</div>

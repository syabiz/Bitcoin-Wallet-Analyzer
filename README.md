# Bitcoin Wallet Analyzer v2.0 PRO

> **by Syabiz** · [syabiz.github.io](https://syabiz.github.io)

A powerful, offline Bitcoin `wallet.dat` forensic analyzer built with Python and Tkinter. Parses BerkeleyDB structure, decodes cryptographic parameters, validates addresses, and generates detailed statistical reports — all from a clean dark-themed GUI.

---

## Features

### Core Analysis
| Feature | Description |
|---|---|
| **BDB Structure Parser** | Accurate BerkeleyDB v8/v9 metadata — magic, byte order, page size, BTree root, unique DB ID |
| **mkey Record Decoder** | Heuristic decoder for master key record: encrypted key (48B), salt (8B), KDF iterations, derive method |
| **Crypto Info** | AES-256-CBC specs, SHA-512 KDF params, BIP32/49/84 extended key detection, script bytecodes |
| **Hash Extraction** | Integrates with official `bitcoin2john.py`; auto-downloads if missing |
| **Address Extraction** | Regex scan + **Base58Check checksum validation** for legacy; format heuristic for Bech32/Taproot |

### Statistical Analysis
| Test | Details |
|---|---|
| **Shannon Entropy** | Per-byte entropy score with visual progress bar (0–8.0 bits/byte) |
| **Chi-Square Test** | χ² statistic vs uniform distribution (DOF=255) with p-value interpretation |
| **Runs Test** | Wald-Wolfowitz test with Z-score — detects non-randomness |
| **Byte Histogram** | 16×16 ASCII density grid for all 256 byte values |
| **Region Entropy Map** | File split into blocks; per-block entropy rendered as color-coded heat bar |

### Output & Export
- Color-coded rich-text output per tab (green / yellow / red / cyan / purple)
- **JSON export** of all analysis results
- Copy-to-clipboard and Save-to-file for every tab
- Full checksums: MD5, SHA-1, SHA-256, SHA-512

---

## Tabs

| Tab | Contents |
|---|---|
| **Overview** | Stat cards + full report: file info, format, encryption, key counts, entropy, next steps |
| **BDB Structure** | Magic, page metadata, BTree details, wallet markers with offsets, string scan, checksums |
| **Crypto & KDF** | mkey decode, key inventory, AES-256-CBC specs, BIP32/49/84 detection, script patterns |
| **Hash Extraction** | Official `bitcoin2john.py` output + 10-field hash breakdown + cracking command reference |
| **Addresses** | Base58Check-validated P2PKH/P2SH + Bech32 P2WPKH/P2WSH/P2TR + Testnet |
| **Entropy Map** | Shannon entropy, chi-square, runs test, byte histogram, region heat map |
| **Hex Viewer** | Configurable offset/rows hex dump with ASCII panel |
| **Recovery Guide** | Step-by-step: encrypted, unencrypted, HD, and corrupt wallet scenarios |

---

## Requirements

| Requirement | Version |
|---|---|
| Python | 3.7 or newer |
| Tkinter | Included with standard Python |
| numpy | Optional (not required) |

> **No third-party pip packages required.** Everything runs on Python stdlib.

---

## Installation
```bash
# 1. Clone or download this repository
git clone https://github.com/syabiz/bitcoin-wallet-analyzer.git
cd bitcoin-wallet-analyzer

# 2. (Optional) Place bitcoin2john.py in the same folder
#    or let the app download it automatically on first use

# 3. Run
python bitcoin_wallet_analyzer_v2.py
```

**Linux** — if Tkinter is missing:
```bash
sudo apt install python3-tk
```

**macOS** with Homebrew Python:
```bash
brew install python-tk
```

---

## Usage

1. Click **Browse…** and select your `wallet.dat` file
2. Click **⚡ Analyze Wallet** — runs in background thread
3. Navigate tabs for detailed results
4. On **Hash Extraction** tab → **⚡ Extract Hash via bitcoin2john.py**
5. Save hash and crack with HashCat or John the Ripper
6. Click **💾 Export JSON** to save full analysis

---

## Hash Cracking Quick Reference
```bash
# HashCat — GPU accelerated (recommended)
hashcat -m 11300 hash.txt rockyou.txt
hashcat -m 11300 hash.txt rockyou.txt -r rules/best64.rule
hashcat -m 11300 hash.txt -a 3 ?a?a?a?a?a?a?a?a        # brute-force 8 chars
hashcat -m 11300 hash.txt -a 3 --increment ?l?l?l?d?d?d  # mask attack

# John the Ripper — CPU
john --format=bitcoin-core hash.txt --wordlist=rockyou.txt
john --restore
john --show hash.txt
```

> HashCat mode **`-m 11300`** = Bitcoin/Litecoin `wallet.dat`

---

## Encryption Scheme
```
User Passphrase
      │
      ▼
SHA-512( passphrase ‖ salt )  ← repeated N times (KDF iterations)
      │
      ├─── bytes [0..31]  →  AES-256 key
      └─── bytes [32..47] →  IV
              │
              ▼
AES-256-CBC decrypt  ←  48-byte encrypted master key (from mkey record)
              │
              ▼
        Master Key (32 bytes)
              │
              ▼
AES-256-CBC decrypt  ←  ckey records (encrypted private keys)
              │
              ▼
        Private Keys
```

| Parameter | Value |
|---|---|
| Cipher | AES-256-CBC |
| Block size | 128 bits (16 bytes) |
| Key size | 256 bits (32 bytes) |
| KDF | SHA-512 iterative (Bitcoin Core custom) |
| Salt | 8 bytes random, stored in `mkey` record |
| Padding | PKCS#7 |
| Validation | Last 16 bytes of decrypted mkey = `0x10` |
| HashCat mode | `-m 11300` |
| John mode | `--format=bitcoin-core` |

---

## Wallet Record Reference

| Record | Description |
|---|---|
| `mkey` | Master key — encrypted with user passphrase (AES-256-CBC) |
| `ckey` | Encrypted private key (AES-256-CBC with master key) |
| `key\x00` | **Plaintext** private key — CRITICAL risk if present |
| `wkey` | Watch-only key (public key, no spending power) |
| `pool` | Pre-generated key pool for privacy |
| `tx\x00` | Raw transaction data |
| `hdchain` | BIP32 HD derivation chain metadata |
| `hdseed` | BIP32 HD master seed |
| `keymeta` | Key metadata: birth time, HD derivation path |
| `version\x00` | Wallet version integer |
| `defaultkey` | Currently active default key |
| `bestblock` | Best chain tip known to this wallet |
| `walletdescriptor` | Descriptor wallet record (Bitcoin Core ≥ 0.21) |
| `name` | Human-readable address label |
| `lockedcoins` | Locked (frozen) coin outpoints |

---

## Tools & Resources

| Tool | URL |
|---|---|
| HashCat | https://hashcat.net |
| John the Ripper | https://www.openwall.com/john/ |
| bitcoin2john.py | https://github.com/openwall/john |
| PyWallet | https://github.com/jackjack-jj/pywallet |
| BTCRecover | https://github.com/gurnec/btcrecover |
| Bitcoin Core | https://bitcoin.org/en/download |
| Mempool Explorer | https://mempool.space |

---

## Disclaimer

> This tool is intended for **educational purposes and recovery of your own wallets only.**  
> Unauthorized access to Bitcoin wallets belonging to others is **illegal** in most jurisdictions.  
> The author assumes no responsibility for any misuse of this software.

---

## Donate · Support Development

If this tool helped you recover your funds, consider supporting:

| Network | Address |
|---|---|
| ₿ Bitcoin | `bc1qn6t8hy8memjfzp4y3sh6fvadjdtqj64vfvlx58` |
| Ξ Ethereum | `0x512936ca43829C8f71017aE47460820Fe703CAea` |
| ◎ Solana | `6ZZrRmeGWMZSmBnQFWXG2UJauqbEgZnwb4Ly9vLYr7mi` |
| PayPal | syabiz@yandex.com |

---

## License

MIT License — free to use, modify, and distribute with attribution.

---

*Made with ❤ by [Syabiz](https://syabiz.github.io)*

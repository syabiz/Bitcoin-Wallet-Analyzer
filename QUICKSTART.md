# 🚀 QUICK START GUIDE - Bitcoin Wallet Analyzer

## Instalasi Cepat

### Windows
```batch
1. Download semua file ke folder
2. Double-click run.bat
3. Aplikasi akan terbuka otomatis
```

### Linux/Mac
```bash
1. Buka terminal di folder aplikasi
2. Jalankan: chmod +x run.sh
3. Jalankan: ./run.sh
```

### Manual
```bash
# Windows
python bitcoin_wallet_analyzer_gui.py

# Linux/Mac
python3 bitcoin_wallet_analyzer_gui.py
```

## Penggunaan 3 Langkah

### 1️⃣ ANALISIS WALLET
```
1. Klik "Browse..." atau paste path wallet.dat
2. Klik "🔍 Analyze Wallet"
3. Lihat hasil di tab "Overview"
```

### 2️⃣ EXTRACT HASH (untuk wallet terenkripsi)
```
1. Buka tab "🔑 Hash Extraction"
2. Klik "🔓 Extract Hash"
3. Klik "📋 Copy Hash" atau "💾 Save Hash"
4. Gunakan untuk cracking:
   
   hashcat -m 11300 hash.txt rockyou.txt
   atau
   john --format=bitcoin-core hash.txt
```

### 3️⃣ EXTRACT ALAMAT
```
1. Buka tab "💰 Addresses"
2. Klik "🔍 Extract Addresses"
3. Copy atau save hasilnya
```

## Tips Cepat

### 🔍 Mengecek Enkripsi
- Tab Overview → bagian "ENCRYPTION STATUS"
- ✓ = Terenkripsi (perlu password)
- ⚠️ = Tidak terenkripsi (langsung accessible)

### 🔑 Password Cracking
```bash
# Download wordlist rockyou.txt dulu
wget https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt

# Crack dengan hashcat (GPU - CEPAT)
hashcat -m 11300 hash.txt rockyou.txt

# Atau dengan john (CPU - LAMBAT)
john --format=bitcoin-core hash.txt --wordlist=rockyou.txt
```

### 💰 Cek Balance Alamat
```
1. Extract alamat dari tab Addresses
2. Buka: https://blockchain.com
3. Paste alamat untuk cek balance
```

## Troubleshooting Cepat

### ❌ "tkinter not found"
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS
brew install python-tk

# Windows
Reinstall Python dengan checkbox "tcl/tk" enabled
```

### ❌ "Permission denied" (Linux/Mac)
```bash
chmod +x bitcoin_wallet_analyzer_gui.py
python3 bitcoin_wallet_analyzer_gui.py
```

### ❌ "No hash found"
Wallet tidak terenkripsi atau format tidak standar.
Coba ekstrak langsung dengan Bitcoin Core atau PyWallet.

### ❌ Application freeze
Normal untuk file besar. Tunggu beberapa menit.
Status bar akan update ketika selesai.

## Workflow Lengkap Recovery

```
┌─────────────────────────────────────────────────┐
│  1. ANALYZE WALLET                               │
│     • Cek enkripsi status                       │
│     • Lihat key count                           │
│     • Check wallet version                      │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  2. JIKA ENCRYPTED                              │
│     • Extract hash                              │
│     • Crack dengan hashcat/john                 │
│     • Atau coba password yang diingat           │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  3. EXTRACT DATA                                │
│     • Extract addresses                         │
│     • Check balance di blockchain               │
│     • Import ke Bitcoin Core jika ada balance   │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  4. RECOVERY                                    │
│     • Gunakan PyWallet / Bitcoin Core           │
│     • Export private keys                       │
│     • Transfer ke wallet baru                   │
└─────────────────────────────────────────────────┘
```

## Commands Paling Berguna

### Hashcat (Recommended - Pakai GPU)
```bash
# Basic wordlist attack
hashcat -m 11300 hash.txt rockyou.txt

# Wordlist + rules (coba variasi)
hashcat -m 11300 hash.txt rockyou.txt -r rules/best64.rule

# Kombinasi wordlist + tahun
hashcat -m 11300 hash.txt rockyou.txt -a 6 ?d?d?d?d

# Show cracked password
hashcat -m 11300 hash.txt --show
```

### John the Ripper
```bash
# Auto detect dan crack
john --format=bitcoin-core hash.txt

# Dengan wordlist
john --format=bitcoin-core hash.txt --wordlist=rockyou.txt

# Show hasil
john --show hash.txt
```

### PyWallet (Extract langsung)
```bash
# Dump semua keys
python pywallet.py --dumpwallet --wallet=wallet.dat

# Recovery mode
python pywallet.py --recover --recov_size=500Mo --recov_device=/dev/sda1
```

### Bitcoin Core
```bash
# Info wallet
bitcoin-cli -wallet=wallet.dat getwalletinfo

# Dump wallet
bitcoin-cli -wallet=wallet.dat dumpwallet backup.txt

# Import private key
bitcoin-cli importprivkey <private_key>
```

## ⚠️ PENTING!

### ✅ DO
- Backup wallet.dat SEBELUM apa pun
- Test dengan wallet dummy dulu
- Keep private keys AMAN
- Gunakan strong password untuk wallet baru

### ❌ DON'T
- Share wallet.dat dengan siapa pun
- Share private keys
- Percaya "recovery services" yang minta wallet file
- Lupa backup sebelum experiment

## 📚 Resources Penting

### Wordlists
- rockyou.txt: https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt
- SecLists: https://github.com/danielmiessler/SecLists

### Tools
- Hashcat: https://hashcat.net/hashcat/
- John: https://www.openwall.com/john/
- PyWallet: https://github.com/jackjack-jj/pywallet
- Bitcoin Core: https://bitcoin.org/en/download

### Help
- BitcoinTalk: https://bitcointalk.org/
- Reddit: https://reddit.com/r/Bitcoin
- Stack Exchange: https://bitcoin.stackexchange.com/

## 🎯 Next Steps

Setelah berhasil extract hash atau addresses:

1. **Jika Punya Password**
   → Import wallet ke Bitcoin Core
   → Export private keys
   → Transfer ke wallet baru

2. **Jika Lupa Password**
   → Crack hash dengan hashcat
   → Coba variasi password yang diingat
   → Pertimbangkan professional recovery jika balance besar

3. **Jika Wallet Tidak Terenkripsi**
   → Extract dengan PyWallet
   → Import private keys langsung
   → Secure wallet baru dengan password kuat

---

**Need Help?** 
Check README.md untuk dokumentasi lengkap atau buka tab "Recovery Guide" di aplikasi!

Good luck! 🍀

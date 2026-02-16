# Bitcoin Wallet Analyzer - GUI Version

A professional GUI application for analyzing Bitcoin Core wallet.dat files with a hash extraction feature for password cracking.

## 🌟 Key Features

### 1. **Comprehensive Analysis**
- Database format detection (Berkeley DB / SQLite)
- Wallet structure analysis
- Encryption identification
- Key and transaction inventory
- Entropy and data pattern analysis

### 2. **Bitcoin Hash Extraction**
- Format compatible with bitcoin2john
- Hash ready for hashcat and John the Ripper
- Format: `$bitcoin$<length>$<data>$<iterations>$<salt>$`
- Automatic iteration count detection
- Detailed information for cracking

### 3. **Bitcoin Address Extraction**
- Automatic P2PKH address scan (1...)
- P2SH address scan (3...)
- Automatic filtering and validation
- Export to text file

### 4. **Recovery Guide**
- Complete wallet recovery guide
- Step-by-step instructions
- Links to necessary tools
- Tips and best practices

### 5. **User-Friendly Interface**
- Tab-based navigation
- Copy to clipboard with 1 click
- Save reports to file
- Real-time status
- Threading to prevent UI freezes

## 📋 Requirements

### Minimum:
```
Python 3.6+
tkinter (usually included with Python)
```

### Optional (for advanced analysis):
```
numpy (for better pattern detection)
```

## 🚀 Installation

### Windows:
```bash
# Make sure Python is installed
python --version

# Install (optional)
pip install numpy

# Run the application
python main.pyw
```

### Linux/Mac:
```bash
# Make sure Python 3 and tkinter are installed
sudo apt-get install python3-tk # Debian/Ubuntu
# or
brew install python-tk # macOS

# Install numpy (optional)
pip3 install numpy

# Run the application
python3 main.pyw
```

## 💻 How to Use

### 1. Wallet Analysis

1. **Open the Application**
- Run `python main.pyw`

2. **Select Wallet File**
- Click the "Browse..." button
- Select the wallet.dat file
- Or type the path directly

3. **Analyze**
- Click "🔍 Analyze Wallet"
- Wait for the process to complete
- View the results in the Overview tab

### 2. Hash Extraction

1. **Hash Extraction Tab**
- Open the "🔑 Hash Extraction" tab

2. **Extract Hash**
- Click "🔓 Extract Hash"
- The hash will appear in bitcoin2john format

3. **Copy or Save**
- Click "📋 Copy Hash" to copy to the clipboard
- Click "💾 Save Hash" to save to a file

4. **Use for Cracking**
```bash
# With Hashcat
hashcat -m 11300 hash.txt wordlist.txt

# With John the Ripper
john --format=bitcoin-core hash.txt
```

### 3. Address Extraction

1. **Addresses Tab**
- Open the "💰 Addresses" tab

2. **Extract Addresses**
- Click "🔍 Extract Addresses"
- A list of addresses will appear

3. **Save Addresses**
- Click "💾 Save List" to export

### 4. Recovery Guide

- Open the "💡 Recovery Guide" tab
- Read the guide according to your wallet type
- Follow the step-by-step instructions

## 🔓 Password Cracking

### Preparation

1. **Extract Hash** from wallet
2. **Select the appropriate Wordlist**
3. **Select Tool**: Hashcat (GPU) or John the Ripper (CPU)

### Hashcat (Recommended)

```bash
# Basic attack with wordlist
hashcat -m 11300 hash.txt rockyou.txt

# With rules
hashcat -m 11300 hash.txt rockyou.txt -r rules/best64.rule

# Brute force (slow)
hashcat -m 11300 hash.txt -a 3 ?a?a?a?a?a?a

# Combination of wordlist + mask
hashcat -m 11300 hash.txt rockyou.txt -a 6 ?d?d?d?d
```

### John the Ripper

```bash
# Basic attack
john --format=bitcoin-core hash.txt

# With wordlist
john --format=bitcoin-core hash.txt --wordlist=rockyou.txt

# Resumes
john --restore

# Show cracked passwords
john --show hash.txt
```

### Wordlists Recommended

1. **rockyou.txt** - Most common password (14M passwords) 
```bash 
wget https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt 
```

2. **SecLists** - Complete collections 
```bash 
git clone https://github.com/danielmiessler/SecLists 
```

3. **CrackStation** - Large Wordlist (15GB) 
- Download from: https://crackstation.net/crackstation-wordlist-password-cracking-dictionary.htm

## 📊 Output Examples

### Hashes Format
```
$bitcoin$128$abcdef1234567890....$100000$a1b2c3d4e5f67890$ 
↑ ↑ ↑ ↑ 
| | | └─ Salt (hex) 
| | └───────── Iterations 
| └───────────────────────────── Encrypted data 
└────────────────────?
```

### Bitcoin Address
```
1. 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa (P2PKH)
2. 3J98t1WpEZ73CNmYviecrnyiWrnqRhWNLy (P2SH)
3. 1BoatSLRHtKNngkdXEeobR76b53LETtpyT (P2PKH)
```

## 🛠️ Supporting Tools

### Bitcoin2John (Original)
```bash
# Downloads
wget https://raw.githubusercontent.com/openwall/john/bleeding-jumbo/run/bitcoin2john.py

# Use
python bitcoin2john.py wallet.dat > hash.txt
```

### PyWallet
```bash
# Clone
git clone https://github.com/jackjack-jj/pywallet

# Dump wallet
python pywallet.py --dumpwallet --wallet=wallet.dat
```

### Bitcoin Core
- Download: https://bitcoin.org/en/download
- For modern wallets (0.16+)

## ⚠️ Important Notes

### Security
- **DO NOT** share wallet.dat or private keys with anyone
- Use this tool only for your own wallet
- Backup wallet.dat before doing anything

### Legal
- Only crack wallets you own
- Unauthorized access to other people's wallets is ILLEGAL
- This tool is for recovery, not hacking

### Limitations
- Hash extraction is a simplified version
- For best results, use the official bitcoin2john.py
- Some modern wallets may not be supported
- HD wallets require a different approach

## 🐛 Troubleshooting

### "Module 'tkinter' not found"
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS
brew install python-tk

# Windows - reinstall Python with the "tcl/tk" checkbox checked
```

### "Permission denied"
```bash
# Linux/Mac
chmod +x main.pyw
python3 main.pyw

# Windows - run as Administrator
```

### "File not found" during analysis
- Make sure the file path is correct
- Check file permissions
- Try copying wallet.dat to the same folder as the script

### Hash extraction failed
- Wallet may not be encrypted
- Wallet format is not standard
- Try using the original bitcoin2john.py

## 📚 Resources

### Documentation
- Bitcoin Core: https://bitcoin.org/en/developer-documentation
- BIP32 (HD Wallets): https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
- Berkeley DB: https://docs.oracle.com/cd/E17276_01/html/index.html

### Tools
- Hashcat: https://hashcat.net/hashcat/
- John the Ripper: https://www.openwall.com/john/
- PyWallet: https://github.com/jackjack-jj/pywallet
- BTCRecover: https://github.com/gurnec/btcrecover

### 💰 Donation
Donate to Developer
• Bitcoin.org - Official documentation
• Bitcoin (BTC) : bc1qn6t8hy8memjfzp4y3sh6fvadjdtqj64vfvlx58")
• Ethereum (ETH) : 0x512936ca43829C8f71017aE47460820Fe703CAea")
• Solana (SOL) : 6ZZrRmeGWMZSmBnQFWXG2UJauqbEgZnwb4Ly9vLYr7mi")


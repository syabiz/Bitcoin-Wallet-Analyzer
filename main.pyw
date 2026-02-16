import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import struct
import math
import re
from pathlib import Path
from collections import Counter
import threading
import base64

# Try to import numpy for advanced analysis
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


class BitcoinWalletAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Bitcoin Wallet Analyzer - Professional Edition - by Syabiz")
        self.root.geometry("1024x600")
        
        # Configure style
        self.setup_styles()
        
        # Variables
        self.filepath = tk.StringVar()
        self.current_data = None
        
        # Create UI
        self.create_widgets()
        
    def setup_styles(self):
        """Setup UI styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), 
                       background='#2c3e50', foreground='white', padding=10)
        style.configure('Success.TLabel', foreground='#27ae60', font=('Arial', 10, 'bold'))
        style.configure('Warning.TLabel', foreground='#e67e22', font=('Arial', 10, 'bold'))
        style.configure('Error.TLabel', foreground='#e74c3c', font=('Arial', 10, 'bold'))
        
    def create_widgets(self):
        """Create all UI widgets"""
        
        # Header Frame
        header_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🔐 Bitcoin Wallet Analyzer", 
                              font=('Arial', 18, 'bold'), bg='#2c3e50', fg='white')
        title_label.pack(pady=5)
        
        subtitle = tk.Label(header_frame, text="Professional wallet.dat analysis & hash extraction tool", 
                           font=('Arial', 10), bg='#2c3e50', fg='#ecf0f1')
        subtitle.pack()
        
        # Main Container
        main_container = ttk.Frame(self.root, padding=10)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # File Selection Frame
        file_frame = ttk.LabelFrame(main_container, text="📁 Wallet File", padding=10)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        file_entry = ttk.Entry(file_frame, textvariable=self.filepath, width=80)
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        browse_btn = ttk.Button(file_frame, text="Browse...", command=self.browse_file)
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        analyze_btn = ttk.Button(file_frame, text="🔍 Analyze Wallet", 
                                command=self.start_analysis, style='Accent.TButton')
        analyze_btn.pack(side=tk.LEFT)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Overview
        self.overview_tab = self.create_overview_tab()
        self.notebook.add(self.overview_tab, text="📊 Overview")
        
        # Tab 2: Hash Extraction
        self.hash_tab = self.create_hash_tab()
        self.notebook.add(self.hash_tab, text="🔑 Hash Extraction")
        
        # Tab 3: Detailed Analysis
        self.detail_tab = self.create_detail_tab()
        self.notebook.add(self.detail_tab, text="🔬 Detailed Analysis")
        
        # Tab 4: Addresses
        self.address_tab = self.create_address_tab()
        self.notebook.add(self.address_tab, text="💰 Addresses")
        
        # Tab 5: Recovery Guide
        self.recovery_tab = self.create_recovery_tab()
        self.notebook.add(self.recovery_tab, text="💡 Recovery Guide")
        
        # Status Bar
        self.status_bar = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_overview_tab(self):
        """Create overview tab"""
        frame = ttk.Frame(self.notebook, padding=10)
        
        # Create scrolled text
        self.overview_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, 
                                                       font=('Consolas', 10), 
                                                       background='#f8f9fa')
        self.overview_text.pack(fill=tk.BOTH, expand=True)
        
        # Button frame
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(btn_frame, text="📋 Copy All", 
                  command=lambda: self.copy_to_clipboard(self.overview_text)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💾 Save Report", 
                  command=lambda: self.save_report(self.overview_text)).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="🗑️ Clear", 
                  command=lambda: self.overview_text.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=5)
        
        return frame
    
    def create_hash_tab(self):
        """Create hash extraction tab"""
        frame = ttk.Frame(self.notebook, padding=10)
        
        # Info label
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_label = ttk.Label(info_frame, 
                              text="⚠️  IMPORTANT: This tool uses ONLY the official bitcoin2john.py script.\n"
                                   "Custom hash parsers are unreliable and produce incorrect hashes.\n"
                                   "Always use bitcoin2john.py for accurate hash extraction!",
                              font=('Arial', 9), foreground='#d9534f', background='#fff3cd',
                              wraplength=700, justify=tk.LEFT, padding=10)
        info_label.pack(anchor=tk.W, fill=tk.X)
        
        # Hash display
        hash_label = ttk.Label(frame, text="🔑 Extracted Hash:", font=('Arial', 10, 'bold'))
        hash_label.pack(anchor=tk.W, pady=(5, 5))
        
        self.hash_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=8,
                                                   font=('Consolas', 9), 
                                                   background='#fff3cd')
        self.hash_text.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        hash_btn_frame = ttk.Frame(frame)
        hash_btn_frame.pack(fill=tk.X)
        
        ttk.Button(hash_btn_frame, text="🔓 Extract Hash (bitcoin2john.py)", 
                  command=self.use_bitcoin2john).pack(side=tk.LEFT, padx=5)
        ttk.Button(hash_btn_frame, text="📋 Copy Hash", 
                  command=lambda: self.copy_to_clipboard(self.hash_text)).pack(side=tk.LEFT)
        ttk.Button(hash_btn_frame, text="💾 Save Hash", 
                  command=lambda: self.save_hash()).pack(side=tk.LEFT, padx=5)
        
        # Cracking instructions
        crack_label = ttk.Label(frame, text="\n🛠️ Cracking Instructions:", 
                               font=('Arial', 10, 'bold'))
        crack_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.crack_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=12,
                                                    font=('Consolas', 9),
                                                    background='#f8f9fa')
        self.crack_text.pack(fill=tk.BOTH, expand=True)
        
        # Insert default instructions
        self.show_default_crack_instructions()
        
        return frame
    
    def create_detail_tab(self):
        """Create detailed analysis tab"""
        frame = ttk.Frame(self.notebook, padding=10)
        
        self.detail_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD,
                                                     font=('Consolas', 9),
                                                     background='#f8f9fa')
        self.detail_text.pack(fill=tk.BOTH, expand=True)
        
        # Button frame
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(btn_frame, text="📋 Copy All", 
                  command=lambda: self.copy_to_clipboard(self.detail_text)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💾 Save Report", 
                  command=lambda: self.save_report(self.detail_text)).pack(side=tk.LEFT)
        
        return frame
    
    def create_address_tab(self):
        """Create address extraction tab"""
        frame = ttk.Frame(self.notebook, padding=10)
        
        # Warning/Info
        warning_frame = ttk.Frame(frame)
        warning_frame.pack(fill=tk.X, pady=(0, 10))
        
        warning_label = ttk.Label(warning_frame, 
                                 text="⚠️  DISCLAIMER: Address extraction uses pattern matching (regex).\n"
                                      "May include false positives or miss some addresses.\n"
                                      "For complete address list, use Bitcoin Core 'dumpwallet' command.",
                                 font=('Arial', 9), foreground='#856404', background='#fff3cd',
                                 wraplength=700, justify=tk.LEFT, padding=10)
        warning_label.pack(anchor=tk.W, fill=tk.X)
        
        # Info
        info_label = ttk.Label(frame, text="💰 Extracted Bitcoin Addresses (Approximate)", 
                              font=('Arial', 11, 'bold'))
        info_label.pack(anchor=tk.W, pady=(5, 10))
        
        self.address_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD,
                                                      font=('Consolas', 9),
                                                      background='#f8f9fa')
        self.address_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(btn_frame, text="🔍 Extract Addresses", 
                  command=self.extract_addresses).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📋 Copy Addresses", 
                  command=lambda: self.copy_to_clipboard(self.address_text)).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="💾 Save List", 
                  command=lambda: self.save_addresses()).pack(side=tk.LEFT, padx=5)
        
        return frame
    
    def create_recovery_tab(self):
        """Create recovery guide tab"""
        frame = ttk.Frame(self.notebook, padding=10)
        
        self.recovery_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD,
                                                       font=('Consolas', 10),
                                                       background='#f8f9fa')
        self.recovery_text.pack(fill=tk.BOTH, expand=True)
        
        # Show default guide
        self.show_default_recovery_guide()
        
        return frame
    
    def browse_file(self):
        """Open file browser"""
        filename = filedialog.askopenfilename(
            title="Select Bitcoin Wallet File",
            filetypes=[("Wallet files", "*.dat"), ("All files", "*.*")]
        )
        if filename:
            self.filepath.set(filename)
    
    def start_analysis(self):
        """Start wallet analysis in background thread"""
        if not self.filepath.get():
            messagebox.showwarning("No File", "Please select a wallet.dat file first!")
            return
        
        # Run in thread to prevent UI freeze
        thread = threading.Thread(target=self.analyze_wallet, daemon=True)
        thread.start()
    
    def update_status(self, message):
        """Update status bar"""
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def analyze_wallet(self):
        """Main wallet analysis function"""
        filepath = self.filepath.get()
        
        try:
            self.update_status("🔍 Reading wallet file...")
            
            # Validate file
            path = Path(filepath)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {filepath}")
            
            file_size = path.stat().st_size
            if file_size == 0:
                raise ValueError("File is empty")
            
            # Read file
            with open(filepath, 'rb') as f:
                self.current_data = f.read()
            
            self.update_status("📊 Analyzing wallet structure...")
            
            # Clear previous results
            self.overview_text.delete(1.0, tk.END)
            self.detail_text.delete(1.0, tk.END)
            
            # Perform analysis
            overview = self.perform_overview_analysis(filepath, self.current_data)
            details = self.perform_detailed_analysis(self.current_data)
            
            # Display results
            self.overview_text.insert(1.0, overview)
            self.detail_text.insert(1.0, details)
            
            self.update_status("✅ Analysis complete!")
            messagebox.showinfo("Success", "Wallet analysis completed successfully!")
            
        except Exception as e:
            self.update_status(f"❌ Error: {str(e)}")
            messagebox.showerror("Analysis Error", f"Error analyzing wallet:\n{str(e)}")
    
    def perform_overview_analysis(self, filepath, data):
        """Perform overview analysis"""
        output = []
        output.append("=" * 70)
        output.append(" BITCOIN WALLET ANALYZER - OVERVIEW")
        output.append("=" * 70)
        output.append(f"\nFile: {filepath}")
        output.append(f"Size: {len(data):,} bytes ({len(data)/1024:.2f} KB)")
        output.append("")
        
        # Database format
        output.append("=" * 70)
        output.append(" DATABASE FORMAT")
        output.append("=" * 70)
        
        magic = data[:8]
        output.append(f"Magic Bytes: {magic.hex()}")
        
        if len(data) > 14 and data[12:14] == b'\x09\x00':
            output.append("✓ Berkeley DB Version: 9")
            output.append("  Compatible with: Bitcoin Core 0.8.x - 0.15.x")
        elif data[0:4] == b'\x00\x00\x00\x00':
            output.append("✓ SQLite Format (descriptor wallet)")
            output.append("  Compatible with: Bitcoin Core 0.16.x+")
        else:
            output.append("? Unknown database format")
        
        # Key markers
        output.append("\n" + "=" * 70)
        output.append(" KEY MARKERS FOUND")
        output.append("=" * 70)
        
        markers = {
            b'mkey': 'Master Encryption Key',
            b'ckey': 'Encrypted Private Key',
            b'key\x00': 'Private Key (unencrypted)',
            b'name': 'Address Label',
            b'tx': 'Transaction',
            b'pool': 'Key Pool',
        }
        
        found_markers = {}
        for marker, desc in markers.items():
            pos = data.find(marker)
            if pos != -1:
                found_markers[marker] = (pos, desc)
                output.append(f"✓ {desc:<30} @ position {pos:,}")
        
        # Encryption status
        output.append("\n" + "=" * 70)
        output.append(" ENCRYPTION STATUS")
        output.append("=" * 70)
        
        if b'mkey' in found_markers:
            output.append("\n✓ WALLET IS ENCRYPTED")
            output.append("  Password protection is enabled")
            
            ckey_count = data.count(b'ckey')
            if ckey_count > 0:
                output.append(f"  Found {ckey_count} encrypted private keys")
        else:
            output.append("\n⚠️  WALLET IS NOT ENCRYPTED")
            output.append("  Private keys are stored in plaintext!")
        
        # Key inventory
        output.append("\n" + "=" * 70)
        output.append(" KEY INVENTORY")
        output.append("=" * 70)
        
        ckey_count = data.count(b'ckey')
        key_count = data.count(b'key\x00')
        name_count = data.count(b'name')
        tx_count = data.count(b'tx\x00')
        
        output.append(f"Encrypted keys (ckey): {ckey_count}")
        output.append(f"Private key markers: {key_count}")
        output.append(f"Address labels: {name_count}")
        output.append(f"Transactions: {tx_count}")
        
        if ckey_count > 0:
            output.append(f"\n💰 Estimated addresses: ~{ckey_count}")
        elif key_count > 0:
            output.append(f"\n💰 Estimated addresses: ~{key_count}")
        
        # Entropy analysis
        output.append("\n" + "=" * 70)
        output.append(" ENTROPY ANALYSIS")
        output.append("=" * 70)
        
        sample_size = min(1024*1024, len(data))
        sample = data[:sample_size]
        
        byte_freq = Counter(sample)
        entropy = 0.0
        for count in byte_freq.values():
            if count > 0:
                p = count / len(sample)
                entropy -= p * math.log2(p)
        
        output.append(f"Shannon entropy: {entropy:.4f} bits/byte (max: 8.0)")
        
        if entropy < 6.0:
            output.append("  📝 Moderate entropy - structured data")
        elif entropy < 7.5:
            output.append("  🔐 Good entropy - encrypted data")
        else:
            output.append("  🔒 High entropy - strongly encrypted")
        
        output.append("\n" + "=" * 70)
        output.append(" ANALYSIS COMPLETE")
        output.append("=" * 70)
        output.append("")
        output.append("⚠️  DISCLAIMER:")
        output.append("This analysis provides approximate information based on pattern matching.")
        output.append("For complete and accurate wallet data:")
        output.append("  • Use Bitcoin Core's 'dumpwallet' command")
        output.append("  • Use PyWallet for detailed extraction")
        output.append("  • Hash extraction: ONLY use bitcoin2john.py (built-in)")
        
        output.append("\n" + "=" * 70)
        output.append(" DONATE TO DEVELOPER")
        output.append("=" * 70)
        output.append("")
        output.append("💰  DONATE:")
        output.append("If this tool helps you analyze and get the information you expect, treat me to")
        output.append("a cup of coffee or a plate of pizza via Crypto Currency:")
        output.append("  • Bitcoin (BTC) : bc1qn6t8hy8memjfzp4y3sh6fvadjdtqj64vfvlx58")
        output.append("  • Ethereum (ETH) : 0x512936ca43829C8f71017aE47460820Fe703CAea")
        output.append("  • Solana (SOL) : 6ZZrRmeGWMZSmBnQFWXG2UJauqbEgZnwb4Ly9vLYr7mi")
        
        return "\n".join(output)
    
    def perform_detailed_analysis(self, data):
        """Perform detailed analysis"""
        output = []
        output.append("=" * 70)
        output.append(" DETAILED WALLET ANALYSIS")
        output.append("=" * 70)
        
        # Byte distribution
        output.append("\n📊 BYTE FREQUENCY ANALYSIS")
        output.append("-" * 70)
        
        sample_size = min(1024*1024, len(data))
        sample = data[:sample_size]
        byte_freq = Counter(sample)
        
        output.append(f"\nTop 10 most common bytes:")
        for byte, count in byte_freq.most_common(10):
            pct = (count / len(sample)) * 100
            if 32 <= byte <= 126:
                output.append(f"  0x{byte:02x} ('{chr(byte)}'): {count:8,} ({pct:.2f}%)")
            else:
                output.append(f"  0x{byte:02x}: {count:8,} ({pct:.2f}%)")
        
        # Null byte analysis
        null_count = sample.count(b'\x00')
        null_pct = (null_count / len(sample)) * 100
        output.append(f"\nNull bytes (0x00): {null_count:,} ({null_pct:.2f}%)")
        
        # ASCII content
        ascii_count = sum(1 for b in sample if 32 <= b <= 126)
        ascii_pct = (ascii_count / len(sample)) * 100
        output.append(f"Printable ASCII: {ascii_count:,} ({ascii_pct:.2f}%)")
        
        # Pattern detection
        output.append("\n🔬 PATTERN DETECTION")
        output.append("-" * 70)
        
        if HAS_NUMPY:
            try:
                analysis_size = min(10000, len(sample))
                byte_array = np.frombuffer(sample[:analysis_size], dtype=np.uint8)
                diffs = np.diff(byte_array)
                std_dev = np.std(diffs)
                
                output.append(f"Standard deviation: {std_dev:.2f}")
                
                if std_dev < 10:
                    output.append("  ⚠️  Highly structured - possible patterns")
                elif std_dev > 50:
                    output.append("  🔒 Random-looking - good encryption")
                else:
                    output.append("  📝 Mixed patterns - typical wallet data")
            except Exception as e:
                output.append(f"Pattern analysis error: {e}")
        else:
            output.append("NumPy not available - using basic analysis")
        
        # Search for specific patterns
        output.append("\n🔍 SEARCHING FOR SPECIFIC PATTERNS")
        output.append("-" * 70)
        
        patterns = {
            b'Bitcoin': 'Bitcoin string',
            b'wallet': 'Wallet string',
            b'\x04\x88\xad\xe4': 'BIP32 extended key marker',
            b'\x04\x88\xb2\x1e': 'BIP32 public key marker',
        }
        
        for pattern, desc in patterns.items():
            count = data.count(pattern)
            if count > 0:
                output.append(f"✓ Found '{desc}': {count} occurrences")
        
        return "\n".join(output)
    
    
    def use_bitcoin2john(self):
        """Use the official bitcoin2john.py script if available"""
        if not self.filepath.get():
            messagebox.showwarning("No File", "Please select a wallet file first!")
            return
        
        import subprocess
        import os
        
        wallet_path = self.filepath.get()
        
        # Check if bitcoin2john.py exists in common locations
        possible_paths = [
            'bitcoin2john.py',
            './bitcoin2john.py',
            '../bitcoin2john.py',
            os.path.join(os.getcwd(), 'bitcoin2john.py'),
            '/usr/local/bin/bitcoin2john.py',
            '/usr/bin/bitcoin2john.py',
        ]
        
        bitcoin2john_path = None
        for path in possible_paths:
            if os.path.exists(path):
                bitcoin2john_path = path
                break
        
        if not bitcoin2john_path:
            # Offer to download
            result = messagebox.askyesno(
                "bitcoin2john.py Not Found",
                "bitcoin2john.py not found in system.\n\n"
                "Would you like to download it?\n\n"
                "It will be downloaded from the official John the Ripper repository."
            )
            
            if result:
                try:
                    import urllib.request
                    url = "https://raw.githubusercontent.com/openwall/john/bleeding-jumbo/run/bitcoin2john.py"
                    target = os.path.join(os.getcwd(), 'bitcoin2john.py')
                    
                    self.update_status("⬇️ Downloading bitcoin2john.py...")
                    urllib.request.urlretrieve(url, target)
                    
                    if os.path.exists(target):
                        bitcoin2john_path = target
                        messagebox.showinfo("Success", f"Downloaded to:\n{target}")
                    else:
                        raise Exception("Download failed")
                        
                except Exception as e:
                    messagebox.showerror("Download Error", 
                        f"Could not download bitcoin2john.py:\n{str(e)}\n\n"
                        "Please download manually from:\n"
                        "https://raw.githubusercontent.com/openwall/john/bleeding-jumbo/run/bitcoin2john.py")
                    return
            else:
                return
        
        # Run bitcoin2john.py
        try:
            self.update_status("🔍 Running bitcoin2john.py...")
            
            # Try to run it
            result = subprocess.run(
                ['python3', bitcoin2john_path, wallet_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                # Try with python instead of python3
                result = subprocess.run(
                    ['python', bitcoin2john_path, wallet_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            
            if result.returncode == 0:
                output = result.stdout.strip()
                
                self.hash_text.delete(1.0, tk.END)
                self.hash_text.insert(1.0, "=" * 70 + "\n")
                self.hash_text.insert(tk.END, " OFFICIAL bitcoin2john.py OUTPUT\n")
                self.hash_text.insert(tk.END, "=" * 70 + "\n\n")
                self.hash_text.insert(tk.END, "🔑 EXTRACTED HASH:\n")
                self.hash_text.insert(tk.END, "-" * 70 + "\n")
                self.hash_text.insert(tk.END, output + "\n\n")
                
                # Parse the hash to show details
                if "$bitcoin$" in output:
                    parts = output.split('$')
                    if len(parts) >= 6:
                        self.hash_text.insert(tk.END, "=" * 70 + "\n")
                        self.hash_text.insert(tk.END, " HASH BREAKDOWN\n")
                        self.hash_text.insert(tk.END, "=" * 70 + "\n")
                        self.hash_text.insert(tk.END, f"Length: {parts[2]}\n")
                        self.hash_text.insert(tk.END, f"Encrypted data: {parts[3][:64]}...\n")
                        self.hash_text.insert(tk.END, f"Iterations: {parts[4]}\n")
                        if len(parts) > 5:
                            self.hash_text.insert(tk.END, f"Salt: {parts[5]}\n")
                        if len(parts) > 6:
                            self.hash_text.insert(tk.END, f"Verify: {parts[6]}\n")
                
                self.hash_text.insert(tk.END, "\n✅ This is the OFFICIAL hash from bitcoin2john.py\n")
                self.hash_text.insert(tk.END, "   Use this hash for cracking!\n")
                
                self.update_status("✅ Official hash extracted successfully!")
                
            else:
                error_msg = result.stderr if result.stderr else "Unknown error"
                messagebox.showerror("Extraction Failed", 
                    f"bitcoin2john.py failed:\n{error_msg}")
                
        except subprocess.TimeoutExpired:
            messagebox.showerror("Timeout", "bitcoin2john.py took too long to execute")
        except Exception as e:
            messagebox.showerror("Error", f"Error running bitcoin2john.py:\n{str(e)}")
    
    def extract_addresses(self):
        """Extract Bitcoin addresses"""
        if self.current_data is None:
            messagebox.showwarning("No Data", "Please analyze a wallet file first!")
            return
        
        try:
            self.update_status("💰 Extracting addresses...")
            
            data = self.current_data
            output = []
            
            output.append("=" * 70)
            output.append(" BITCOIN ADDRESS EXTRACTION")
            output.append("=" * 70)
            output.append("")
            
            # Method 1: ASCII scan for addresses
            try:
                ascii_data = data.decode('latin1', errors='ignore')
            except:
                ascii_data = ""
            
            # Bitcoin address regex (P2PKH and P2SH)
            pattern = r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b'
            potential_addrs = re.findall(pattern, ascii_data)
            
            if potential_addrs:
                unique_addrs = sorted(set(potential_addrs))
                output.append(f"💰 Found {len(unique_addrs)} potential addresses:\n")
                
                for i, addr in enumerate(unique_addrs, 1):
                    if 25 <= len(addr) <= 34:
                        addr_type = "P2PKH" if addr.startswith('1') else "P2SH"
                        output.append(f"{i:3}. {addr} ({addr_type})")
                
            else:
                output.append("❌ No addresses found in ASCII scan")
                output.append("\nThis may be a modern HD wallet where addresses")
                output.append("are derived from the master key, not stored directly.")
            
            output.append("\n" + "=" * 70)
            output.append(" EXTRACTION COMPLETE")
            output.append("=" * 70)
            output.append("")
            output.append("⚠️  IMPORTANT NOTES:")
            output.append("• This is APPROXIMATE extraction using pattern matching")
            output.append("• May include false positives (random strings that look like addresses)")
            output.append("• May MISS addresses stored in binary/compressed format")
            output.append("• For COMPLETE list, use: bitcoin-cli dumpwallet wallet_backup.txt")
            output.append("• Or use PyWallet for detailed extraction")
            
            self.address_text.delete(1.0, tk.END)
            self.address_text.insert(1.0, "\n".join(output))
            
            self.update_status("✅ Address extraction complete!")
            
        except Exception as e:
            messagebox.showerror("Extraction Error", f"Error extracting addresses:\n{str(e)}")
            self.update_status(f"❌ Error: {str(e)}")
    
    def show_default_crack_instructions(self):
        """Show default cracking instructions"""
        instructions = """
═══════════════════════════════════════════════════════════════════
 PASSWORD CRACKING INSTRUCTIONS
═══════════════════════════════════════════════════════════════════

🔑 STEP 1: EXTRACT HASH
──────────────────────────────────────────────
Click the "🔓 Extract Hash (bitcoin2john.py)" button above.

This uses the OFFICIAL bitcoin2john.py script from John the Ripper.
The hash will be 100% accurate and compatible with hashcat/john.

If bitcoin2john.py is not found, the tool will automatically download it
from the official repository.


🔹 STEP 2: CRACK WITH HASHCAT (Recommended - GPU accelerated)
──────────────────────────────────────────────
After extracting the hash:

1. Save the hash to a file:
   • Click "💾 Save Hash" button
   • Or copy and paste to hash.txt

2. Basic dictionary attack:
   hashcat -m 11300 hash.txt wordlist.txt

3. With rules (try variations):
   hashcat -m 11300 hash.txt wordlist.txt -r rules/best64.rule

4. Brute force (8 characters max, very slow):
   hashcat -m 11300 hash.txt -a 3 ?a?a?a?a?a?a?a?a

5. Check progress:
   Press 's' during cracking to see status

Mode: 11300 = Bitcoin/Litecoin wallet.dat


🔹 STEP 3: CRACK WITH JOHN THE RIPPER
──────────────────────────────────────────────
Alternative method (CPU-based):

1. Save hash to file (hash.txt)

2. Crack with wordlist:
   john --format=bitcoin-core hash.txt --wordlist=wordlist.txt

3. Resume session:
   john --restore

4. Show cracked password:
   john --show hash.txt


📚 RECOMMENDED WORDLISTS
──────────────────────────────────────────────
• rockyou.txt - Most common passwords (14M entries)
  Download: https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt

• SecLists - Comprehensive password lists
  https://github.com/danielmiessler/SecLists

• CrackStation - Very large wordlist (15GB)
  https://crackstation.net/crackstation-wordlist-password-cracking-dictionary.htm


💡 TIPS FOR SUCCESS
──────────────────────────────────────────────
✓ Start with small wordlists first (rockyou.txt)
✓ Use GPU acceleration for 100x faster cracking
✓ Try common patterns: bitcoin123, wallet2020, crypto$$$
✓ Consider birth years, pet names if you know the owner
✓ Bitcoin-specific words work well: satoshi, hodl, btc, moon

✗ Don't brute force without trying wordlists first
✗ Don't use weak CPU if you have GPU available
✗ Don't forget the iterations count affects speed


⚠️  LEGAL NOTICE
──────────────────────────────────────────────
Only crack wallets you own or have explicit permission to access.
Unauthorized access to cryptocurrency wallets is illegal.


═══════════════════════════════════════════════════════════════════
 NEED HELP?
═══════════════════════════════════════════════════════════════════

Hashcat documentation: https://hashcat.net/wiki/
John the Ripper: https://www.openwall.com/john/
Bitcoin forums: https://bitcointalk.org/


💰 DONATE TO DEVELOPER
──────────────────────────────────────────────
• Bitcoin.org - Official documentation
• Bitcoin (BTC) : bc1qn6t8hy8memjfzp4y3sh6fvadjdtqj64vfvlx58")
• Ethereum (ETH) : 0x512936ca43829C8f71017aE47460820Fe703CAea")
• Solana (SOL) : 6ZZrRmeGWMZSmBnQFWXG2UJauqbEgZnwb4Ly9vLYr7mi")
"""
        self.crack_text.delete(1.0, tk.END)
        self.crack_text.insert(1.0, instructions)
    
    def show_default_recovery_guide(self):
        """Show default recovery guide"""
        guide = """
═══════════════════════════════════════════════════════════════════
 BITCOIN WALLET RECOVERY GUIDE
═══════════════════════════════════════════════════════════════════

🔐 ENCRYPTED WALLET RECOVERY
──────────────────────────────────────────────
If your wallet is encrypted (has master key):

1. Extract the hash using the "Hash Extraction" tab

2. Try password cracking:
   • Use hashcat or John the Ripper (see Hash tab)
   • Start with passwords you commonly use
   • Try variations with numbers/symbols

3. If you remember the password:
   • Import wallet into Bitcoin Core
   • Use: bitcoin-cli walletpassphrase "<password>" 600
   • Then export private keys


📂 UNENCRYPTED WALLET RECOVERY
──────────────────────────────────────────────
If wallet has no encryption:

1. Use PyWallet to dump keys:
   python pywallet.py --dumpwallet --wallet=wallet.dat

2. Or extract with Bitcoin Core:
   bitcoin-cli dumpwallet "wallet_backup.txt"

3. Import keys to new wallet:
   bitcoin-cli importprivkey <private_key>


🆕 MODERN HD WALLET (Bitcoin Core 0.16+)
──────────────────────────────────────────────
For descriptor wallets:

1. Use Bitcoin Core directly:
   bitcoin-wallet -wallet=wallet.dat info
   bitcoin-wallet -wallet=wallet.dat dump

2. Load in Bitcoin Core:
   bitcoin-cli loadwallet "wallet.dat"
   bitcoin-cli getwalletinfo


🛠️ USEFUL TOOLS
──────────────────────────────────────────────
• PyWallet - Python wallet manipulation
  https://github.com/jackjack-jj/pywallet

• Bitcoin Core - Official client
  https://bitcoin.org/en/download

• BTCRecover - Specialized recovery tool
  https://github.com/gurnec/btcrecover


💡 PREVENTION TIPS
──────────────────────────────────────────────
• Always backup wallet.dat in multiple locations
• Keep backup of your password in a safe place
• Use strong but memorable passwords
• Consider hardware wallets for large amounts
• Test recovery process before storing significant funds


⚠️  IMPORTANT NOTES
──────────────────────────────────────────────
• Never share your wallet.dat or private keys
• Be cautious of "recovery services" - many are scams
• If wallet is very old, funds may already be lost
• Check blockchain to see if addresses have balance
• Consider professional recovery for large amounts


🔗 USEFUL LINKS
──────────────────────────────────────────────
• Bitcoin.org - Official documentation
• BitcoinTalk.org - Community forums
• Reddit r/Bitcoin - Support community
• blockchain.com - Block explorer to check addresses


💰 DONATE TO DEVELOPER
──────────────────────────────────────────────
• Bitcoin.org - Official documentation
• Bitcoin (BTC) : bc1qn6t8hy8memjfzp4y3sh6fvadjdtqj64vfvlx58")
• Ethereum (ETH) : 0x512936ca43829C8f71017aE47460820Fe703CAea")
• Solana (SOL) : 6ZZrRmeGWMZSmBnQFWXG2UJauqbEgZnwb4Ly9vLYr7mi")
"""
        self.recovery_text.delete(1.0, tk.END)
        self.recovery_text.insert(1.0, guide)
    
    def copy_to_clipboard(self, text_widget):
        """Copy text widget content to clipboard"""
        try:
            content = text_widget.get(1.0, tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.update_status("📋 Copied to clipboard!")
            messagebox.showinfo("Copied", "Content copied to clipboard!")
        except Exception as e:
            messagebox.showerror("Copy Error", f"Error copying to clipboard:\n{str(e)}")
    
    def save_report(self, text_widget):
        """Save report to file"""
        try:
            content = text_widget.get(1.0, tk.END)
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.update_status(f"💾 Report saved to {filename}")
                messagebox.showinfo("Saved", f"Report saved successfully to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving report:\n{str(e)}")
    
    def save_hash(self):
        """Save extracted hash to file"""
        try:
            content = self.hash_text.get(1.0, tk.END)
            
            if "$bitcoin$" not in content:
                messagebox.showwarning("No Hash", "No hash has been extracted yet!")
                return
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                initialfile="bitcoin_hash.txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.update_status(f"💾 Hash saved to {filename}")
                messagebox.showinfo("Saved", f"Hash saved successfully!\n\nYou can now use:\nhashcat -m 11300 {filename} wordlist.txt")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving hash:\n{str(e)}")
    
    def save_addresses(self):
        """Save extracted addresses to file"""
        try:
            content = self.address_text.get(1.0, tk.END)
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                initialfile="bitcoin_addresses.txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.update_status(f"💾 Addresses saved to {filename}")
                messagebox.showinfo("Saved", f"Addresses saved successfully to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving addresses:\n{str(e)}")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = BitcoinWalletAnalyzer(root)
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import struct
import math
import re
import os
import hashlib
import datetime
from pathlib import Path
from collections import Counter
import threading

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


# ─────────────────────────────────────────────
#  COLOR PALETTE (matching syabiz.github.io)
# ─────────────────────────────────────────────
BG_DARK    = "#0d0d0d"
BG_CARD    = "#111111"
BG_PANEL   = "#1a1a1a"
BG_INPUT   = "#0f0f0f"
ACCENT     = "#f7931a"   # Bitcoin orange
ACCENT2    = "#ffb347"   # lighter orange
GREEN      = "#00ff88"
RED        = "#ff4444"
YELLOW     = "#ffd700"
BLUE       = "#4fc3f7"
TEXT_MAIN  = "#f0f0f0"
TEXT_DIM   = "#888888"
TEXT_MUTED = "#555555"
BORDER     = "#2a2a2a"
MONO_FONT  = ("Consolas", 9)
MONO_FONT2 = ("Consolas", 10)
TITLE_FONT = ("Courier New", 18, "bold")
HEADER_FONT= ("Courier New", 11, "bold")
LABEL_FONT = ("Courier New", 9)


class BitcoinWalletAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Bitcoin Wallet Analyzer - by Syabiz")
        self.root.geometry("1180x700")
        self.root.configure(bg=BG_DARK)
        self.root.minsize(900, 600)

        self.filepath = tk.StringVar()
        self.current_data = None
        self.analysis_cache = {}

        self._setup_ttk_styles()
        self._build_ui()

    # ──────────────────────────────────────────
    #  TTK STYLE SETUP
    # ──────────────────────────────────────────
    def _setup_ttk_styles(self):
        s = ttk.Style()
        s.theme_use("clam")

        # General
        s.configure(".", background=BG_DARK, foreground=TEXT_MAIN,
                    fieldbackground=BG_INPUT, troughcolor=BG_PANEL,
                    bordercolor=BORDER, darkcolor=BG_PANEL, lightcolor=BG_PANEL,
                    insertcolor=ACCENT, font=LABEL_FONT)

        # Notebook
        s.configure("TNotebook", background=BG_DARK, borderwidth=0)
        s.configure("TNotebook.Tab",
                    background=BG_PANEL, foreground=TEXT_DIM,
                    padding=[14, 6], font=LABEL_FONT)
        s.map("TNotebook.Tab",
              background=[("selected", BG_CARD)],
              foreground=[("selected", ACCENT)],
              expand=[("selected", [1, 1, 1, 0])])

        # Frame
        s.configure("TFrame", background=BG_DARK)
        s.configure("Card.TFrame", background=BG_CARD, relief="flat")
        s.configure("Panel.TFrame", background=BG_PANEL, relief="flat")

        # LabelFrame
        s.configure("TLabelframe", background=BG_CARD, bordercolor=BORDER,
                    foreground=ACCENT, font=HEADER_FONT)
        s.configure("TLabelframe.Label", background=BG_CARD,
                    foreground=ACCENT, font=HEADER_FONT)

        # Button
        s.configure("TButton",
                    background=BG_PANEL, foreground=TEXT_MAIN,
                    bordercolor=BORDER, relief="flat", padding=[10, 5],
                    font=LABEL_FONT)
        s.map("TButton",
              background=[("active", ACCENT), ("pressed", "#c87010")],
              foreground=[("active", "#000000")])

        s.configure("Orange.TButton",
                    background=ACCENT, foreground="#000000",
                    font=("Courier New", 9, "bold"), padding=[12, 6])
        s.map("Orange.TButton",
              background=[("active", ACCENT2)],
              foreground=[("active", "#000000")])

        # Entry
        s.configure("TEntry", fieldbackground=BG_INPUT, foreground=TEXT_MAIN,
                    insertcolor=ACCENT, bordercolor=BORDER)

        # Progressbar
        s.configure("TProgressbar", troughcolor=BG_PANEL,
                    background=ACCENT, bordercolor=BORDER)

        # Scrollbar
        s.configure("TScrollbar", background=BG_PANEL,
                    troughcolor=BG_DARK, bordercolor=BORDER,
                    arrowcolor=TEXT_DIM)
        s.map("TScrollbar", background=[("active", ACCENT)])

        # Label
        s.configure("TLabel", background=BG_DARK, foreground=TEXT_MAIN, font=LABEL_FONT)
        s.configure("Dim.TLabel", background=BG_DARK, foreground=TEXT_DIM, font=LABEL_FONT)
        s.configure("Accent.TLabel", background=BG_DARK, foreground=ACCENT,
                    font=("Courier New", 9, "bold"))

    # ──────────────────────────────────────────
    #  UI CONSTRUCTION
    # ──────────────────────────────────────────
    def _build_ui(self):
        # ── HEADER BAR ──
        header = tk.Frame(self.root, bg=BG_CARD, height=72)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        # left: logo + title
        left_hdr = tk.Frame(header, bg=BG_CARD)
        left_hdr.pack(side=tk.LEFT, padx=20, pady=10)

        logo_lbl = tk.Label(left_hdr, text="BTC", font=("Courier New", 28, "bold"),
                            bg=BG_CARD, fg=ACCENT)
        logo_lbl.pack(side=tk.LEFT, padx=(0, 10))

        title_frame = tk.Frame(left_hdr, bg=BG_CARD)
        title_frame.pack(side=tk.LEFT)
        tk.Label(title_frame, text="Bitcoin Wallet Analyzer",
                 font=("Courier New", 16, "bold"), bg=BG_CARD, fg=TEXT_MAIN).pack(anchor="w")
        tk.Label(title_frame, text="wallet.dat  ·  SHA-512  ·  AES-256-CBC  ·  BerkeleyDB  ·  by Syabiz",
                 font=LABEL_FONT, bg=BG_CARD, fg=TEXT_DIM).pack(anchor="w")

        # right: version badge
        right_hdr = tk.Frame(header, bg=BG_CARD)
        right_hdr.pack(side=tk.RIGHT, padx=20)
        tk.Label(right_hdr, text="v1.0 PRO",
                 font=("Courier New", 9, "bold"),
                 bg=ACCENT, fg="#000000", padx=8, pady=3).pack()

        # ── ORANGE SEPARATOR LINE ──
        tk.Frame(self.root, bg=ACCENT, height=2).pack(fill=tk.X)

        # ── FILE SELECTOR BAR ──
        file_bar = tk.Frame(self.root, bg=BG_PANEL, pady=10)
        file_bar.pack(fill=tk.X, padx=0)

        inner_file = tk.Frame(file_bar, bg=BG_PANEL)
        inner_file.pack(fill=tk.X, padx=16)

        tk.Label(inner_file, text="WALLET FILE", font=("Courier New", 8, "bold"),
                 bg=BG_PANEL, fg=ACCENT).pack(side=tk.LEFT, padx=(0, 8))

        entry_bg = tk.Frame(inner_file, bg=BORDER, padx=1, pady=1)
        entry_bg.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self._file_entry = tk.Entry(entry_bg, textvariable=self.filepath,
                                    bg=BG_INPUT, fg=TEXT_MAIN, insertbackground=ACCENT,
                                    relief="flat", font=MONO_FONT, bd=4)
        self._file_entry.pack(fill=tk.X)

        ttk.Button(inner_file, text="Browse...", command=self.browse_file).pack(side=tk.LEFT, padx=4)
        ttk.Button(inner_file, text="⚡ Analyze Wallet",
                   command=self.start_analysis, style="Orange.TButton").pack(side=tk.LEFT, padx=4)

        # progress bar (hidden until analysis)
        self._progress_var = tk.DoubleVar()
        self._progress_bar = ttk.Progressbar(self.root, variable=self._progress_var,
                                             maximum=100, mode="determinate")
        self._progress_bar.pack(fill=tk.X, padx=0)

        # ── NOTEBOOK ──
        nb_frame = tk.Frame(self.root, bg=BG_DARK)
        nb_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=(4, 0))

        self.nb = ttk.Notebook(nb_frame)
        self.nb.pack(fill=tk.BOTH, expand=True)

        self.nb.add(self._tab_overview(),    text="  Overview ")
        self.nb.add(self._tab_bdb(),         text="  BDB Structure ")
        self.nb.add(self._tab_crypto(),      text="  Crypto Info ")
        self.nb.add(self._tab_hash(),        text="  Hash Extraction ")
        self.nb.add(self._tab_addresses(),   text="  Addresses ")
        self.nb.add(self._tab_hex(),         text="  Hex Viewer ")
        self.nb.add(self._tab_recovery(),    text="  Recovery Guide ")

        # ── STATUS BAR ──
        status_bar = tk.Frame(self.root, bg=BG_PANEL, height=26)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        status_bar.pack_propagate(False)
        self._status_var = tk.StringVar(value="[*] Ready  --  Select a wallet.dat file to begin")
        tk.Label(status_bar, textvariable=self._status_var,
                 font=LABEL_FONT, bg=BG_PANEL, fg=TEXT_DIM, anchor="w",
                 padx=12).pack(fill=tk.BOTH, expand=True)

    # ── Helper: styled scrolled text ──
    def _make_stext(self, parent, height=None, fg=TEXT_MAIN, bg=BG_INPUT):
        kwargs = dict(wrap=tk.WORD, font=MONO_FONT2, bg=bg, fg=fg,
                      insertbackground=ACCENT, selectbackground=ACCENT,
                      selectforeground="#000", relief="flat",
                      borderwidth=0, highlightthickness=1,
                      highlightbackground=BORDER, highlightcolor=ACCENT)
        if height:
            kwargs["height"] = height
        st = scrolledtext.ScrolledText(parent, **kwargs)
        # Safe scrollbar styling for Windows compatibility
        try:
            st.vbar.config(bg=BG_PANEL, troughcolor=BG_DARK,
                           activebackground=ACCENT, highlightthickness=0, bd=0)
        except Exception:
            pass
        return st

    def _btn_row(self, parent, buttons):
        """buttons = list of (label, cmd)"""
        row = tk.Frame(parent, bg=BG_DARK)
        row.pack(fill=tk.X, pady=(6, 0))
        for label, cmd in buttons:
            # Detect primary action buttons for orange styling
            is_primary = any(k in label for k in ("Extract", "Analyze", "Start"))
            style = "Orange.TButton" if is_primary else "TButton"
            ttk.Button(row, text=label, command=cmd, style=style).pack(side=tk.LEFT, padx=(0, 4))
        return row

    # ──────────────────────────────────────────
    #  TABS
    # ──────────────────────────────────────────
    def _tab_overview(self):
        f = ttk.Frame(self.nb)
        f.configure(style="TFrame")

        # stats strip (top cards)
        self._stat_vars = {}
        stats_row = tk.Frame(f, bg=BG_DARK)
        stats_row.pack(fill=tk.X, padx=8, pady=(8, 6))

        for key, label in [("file_size","File Size"), ("format","Format"),
                            ("encrypted","Encrypted"), ("key_count","Est. Keys"),
                            ("entropy","Entropy")]:
            card = tk.Frame(stats_row, bg=BG_CARD, bd=0, padx=12, pady=8,
                            highlightbackground=BORDER, highlightthickness=1)
            card.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 6))
            tk.Label(card, text=label.upper(), font=("Courier New", 7, "bold"),
                     bg=BG_CARD, fg=TEXT_DIM).pack(anchor="w")
            var = tk.StringVar(value="─")
            self._stat_vars[key] = var
            tk.Label(card, textvariable=var, font=("Courier New", 13, "bold"),
                     bg=BG_CARD, fg=ACCENT).pack(anchor="w")

        # main text
        inner = tk.Frame(f, bg=BG_DARK)
        inner.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 6))
        self.overview_text = self._make_stext(inner)
        self.overview_text.pack(fill=tk.BOTH, expand=True)

        self._btn_row(inner, [
            ("📋 Copy All",   lambda: self._copy(self.overview_text)),
            ("💾 Save Report",lambda: self._save(self.overview_text)),
            ("🗑️ Clear",      lambda: self.overview_text.delete(1.0, tk.END)),
        ])
        return f

    def _tab_bdb(self):
        f = ttk.Frame(self.nb)

        inner = tk.Frame(f, bg=BG_DARK)
        inner.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        tk.Label(inner, text="BerkeleyDB Internal Structure",
                 font=HEADER_FONT, bg=BG_DARK, fg=ACCENT).pack(anchor="w", pady=(0, 4))
        tk.Label(inner, text="Detailed parsing of BDB page layout, metadata blocks, and key-value records",
                 font=LABEL_FONT, bg=BG_DARK, fg=TEXT_DIM).pack(anchor="w", pady=(0, 6))

        self.bdb_text = self._make_stext(inner)
        self.bdb_text.pack(fill=tk.BOTH, expand=True)

        self._btn_row(inner, [
            ("📋 Copy All", lambda: self._copy(self.bdb_text)),
            ("💾 Save",     lambda: self._save(self.bdb_text)),
        ])
        return f

    def _tab_crypto(self):
        f = ttk.Frame(self.nb)

        inner = tk.Frame(f, bg=BG_DARK)
        inner.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        tk.Label(inner, text="Cryptographic Information",
                 font=HEADER_FONT, bg=BG_DARK, fg=ACCENT).pack(anchor="w", pady=(0, 4))
        tk.Label(inner, text="Cipher details · KDF parameters · Encryption metadata · Integrity analysis",
                 font=LABEL_FONT, bg=BG_DARK, fg=TEXT_DIM).pack(anchor="w", pady=(0, 6))

        self.crypto_text = self._make_stext(inner)
        self.crypto_text.pack(fill=tk.BOTH, expand=True)

        self._btn_row(inner, [
            ("📋 Copy All", lambda: self._copy(self.crypto_text)),
            ("💾 Save",     lambda: self._save(self.crypto_text)),
        ])
        return f

    def _tab_hash(self):
        f = ttk.Frame(self.nb)

        inner = tk.Frame(f, bg=BG_DARK)
        inner.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        # warning banner
        warn = tk.Frame(inner, bg="#1a0f00",
                        highlightbackground=ACCENT, highlightthickness=1, padx=10, pady=8)
        warn.pack(fill=tk.X, pady=(0, 8))
        tk.Label(warn, text="⚠  This tab uses the official bitcoin2john.py script. "
                            "Custom parsers produce unreliable hashes. Always use bitcoin2john.py.",
                 font=LABEL_FONT, bg="#1a0f00", fg=ACCENT, wraplength=900, justify=tk.LEFT).pack()

        tk.Label(inner, text="Extracted Hash  (HashCat format)",
                 font=HEADER_FONT, bg=BG_DARK, fg=ACCENT).pack(anchor="w", pady=(0, 4))

        self.hash_text = self._make_stext(inner, height=9, bg="#0a0a00")
        self.hash_text.pack(fill=tk.X, pady=(0, 6))

        self._btn_row(inner, [
            ("⚡ Extract Hash via bitcoin2john.py", self.use_bitcoin2john),
            ("📋 Copy Hash",  lambda: self._copy(self.hash_text)),
            ("💾 Save Hash",  self.save_hash),
        ])

        tk.Label(inner, text="Cracking Instructions",
                 font=HEADER_FONT, bg=BG_DARK, fg=ACCENT).pack(anchor="w", pady=(12, 4))

        self.crack_text = self._make_stext(inner)
        self.crack_text.pack(fill=tk.BOTH, expand=True)
        self._show_crack_instructions()
        return f

    def _tab_addresses(self):
        f = ttk.Frame(self.nb)

        inner = tk.Frame(f, bg=BG_DARK)
        inner.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        warn = tk.Frame(inner, bg="#0d1a0d",
                        highlightbackground="#00aa55", highlightthickness=1, padx=10, pady=8)
        warn.pack(fill=tk.X, pady=(0, 8))
        tk.Label(warn, text="ℹ  Address extraction uses regex pattern matching. "
                            "May include false positives. For a complete list use: bitcoin-cli dumpwallet",
                 font=LABEL_FONT, bg="#0d1a0d", fg=GREEN, wraplength=900, justify=tk.LEFT).pack()

        tk.Label(inner, text="Bitcoin Addresses  (Approximate)",
                 font=HEADER_FONT, bg=BG_DARK, fg=ACCENT).pack(anchor="w", pady=(0, 4))

        self.address_text = self._make_stext(inner)
        self.address_text.pack(fill=tk.BOTH, expand=True)

        self._btn_row(inner, [
            ("⚡ Extract Addresses", self.extract_addresses),
            ("📋 Copy List",        lambda: self._copy(self.address_text)),
            ("💾 Save List",        self.save_addresses),
        ])
        return f

    def _tab_hex(self):
        f = ttk.Frame(self.nb)

        inner = tk.Frame(f, bg=BG_DARK)
        inner.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

        top_row = tk.Frame(inner, bg=BG_DARK)
        top_row.pack(fill=tk.X, pady=(0, 6))

        tk.Label(top_row, text="Hex Viewer — first 8 KB",
                 font=HEADER_FONT, bg=BG_DARK, fg=ACCENT).pack(side=tk.LEFT)

        # offset input
        tk.Label(top_row, text="Offset (hex):", font=LABEL_FONT,
                 bg=BG_DARK, fg=TEXT_DIM).pack(side=tk.LEFT, padx=(20, 4))
        self._hex_offset_var = tk.StringVar(value="0")
        off_entry = tk.Entry(top_row, textvariable=self._hex_offset_var,
                             width=10, bg=BG_INPUT, fg=TEXT_MAIN,
                             insertbackground=ACCENT, relief="flat", font=MONO_FONT)
        off_entry.pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(top_row, text="Go", command=self._hex_goto).pack(side=tk.LEFT)

        tk.Label(inner, text="Bytes per row: 16  ·  ASCII panel on right",
                 font=LABEL_FONT, bg=BG_DARK, fg=TEXT_DIM).pack(anchor="w", pady=(0, 4))

        self.hex_text = self._make_stext(inner, bg="#060606", fg="#b0ffb0")
        self.hex_text.pack(fill=tk.BOTH, expand=True)

        self._btn_row(inner, [
            ("📋 Copy Hex", lambda: self._copy(self.hex_text)),
            ("💾 Save Hex", lambda: self._save(self.hex_text, "hex_dump.txt")),
        ])
        return f

    def _tab_recovery(self):
        f = ttk.Frame(self.nb)
        inner = tk.Frame(f, bg=BG_DARK)
        inner.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        self.recovery_text = self._make_stext(inner)
        self.recovery_text.pack(fill=tk.BOTH, expand=True)
        self._show_recovery_guide()
        return f

    # ──────────────────────────────────────────
    #  FILE BROWSE
    # ──────────────────────────────────────────
    def browse_file(self):
        fn = filedialog.askopenfilename(
            title="Select Bitcoin Wallet File",
            filetypes=[("Wallet files", "*.dat"), ("All files", "*.*")])
        if fn:
            self.filepath.set(fn)

    # ──────────────────────────────────────────
    #  ANALYSIS ENTRY
    # ──────────────────────────────────────────
    def start_analysis(self):
        if not self.filepath.get():
            messagebox.showwarning("No File", "Please select a wallet.dat file first!")
            return
        threading.Thread(target=self._run_analysis, daemon=True).start()

    def _set_status(self, msg):
        self._status_var.set(f"[*] {msg}")
        self.root.update_idletasks()

    def _set_progress(self, v):
        self._progress_var.set(v)
        self.root.update_idletasks()

    def _set_stat(self, key, value, color=ACCENT):
        if key in self._stat_vars:
            self._stat_vars[key].set(value)

    def _run_analysis(self):
        fp = self.filepath.get()
        try:
            self._set_status("Reading file...")
            self._set_progress(5)

            path = Path(fp)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {fp}")
            if path.stat().st_size == 0:
                raise ValueError("File is empty")

            with open(fp, "rb") as fh:
                self.current_data = fh.read()

            data = self.current_data
            fsize = len(data)
            self._set_stat("file_size", self._fmt_size(fsize))
            self._set_progress(15)

            # ── Clear tabs ──
            for w in (self.overview_text, self.bdb_text, self.crypto_text,
                      self.hex_text, self.address_text):
                w.delete(1.0, tk.END)
            self.hash_text.delete(1.0, tk.END)

            self._set_status("Analyzing BerkeleyDB structure...")
            self._set_progress(25)
            bdb_info = self._analyze_bdb(data)

            self._set_status("Analyzing encryption / crypto info...")
            self._set_progress(45)
            crypto_info = self._analyze_crypto(data)

            self._set_status("Building overview...")
            self._set_progress(65)
            overview = self._build_overview(fp, data, bdb_info, crypto_info)

            self._set_status("Building hex dump...")
            self._set_progress(80)
            self._build_hex(data)

            self._set_progress(95)
            self.overview_text.insert(1.0, overview)
            self.bdb_text.insert(1.0, bdb_info["report"])
            self.crypto_text.insert(1.0, crypto_info["report"])

            # update stat cards
            enc_label = "YES ✓" if crypto_info["encrypted"] else "NO ✗"
            self._set_stat("encrypted", enc_label)
            self._set_stat("key_count", str(crypto_info["key_count"]))
            self._set_stat("format", bdb_info["db_format"])
            self._set_stat("entropy", f"{bdb_info['entropy']:.3f}")

            self._set_progress(100)
            self._set_status("[OK] Analysis complete  --  " + datetime.datetime.now().strftime("%H:%M:%S"))

        except Exception as e:
            self._set_status(f"[ERR] Error: {e}")
            messagebox.showerror("Error", f"Analysis failed:\n{e}")

    # ──────────────────────────────────────────
    #  BDB ANALYSIS
    # ──────────────────────────────────────────
    def _analyze_bdb(self, data):
        out = []
        result = {"db_format": "Unknown", "entropy": 0.0, "report": ""}

        # ── Magic & version ──
        out.append(self._section_header("BerkeleyDB STRUCTURE ANALYSIS"))

        magic = data[:4]
        out.append(f"Magic bytes (raw) : {magic.hex().upper()}  ({' '.join(f'{b:02X}' for b in magic)})")

        # BDB magic: 0x00053162 (LE) = b'\x62\x31\x05\x00'
        is_bdb = False
        db_fmt = "Unknown"

        if len(data) >= 16:
            page_type = data[25] if len(data) > 25 else 0
            if data[12:14] == b'\x09\x00':
                db_fmt = "Berkeley DB v9 (BTree)"
                is_bdb = True
            elif data[12:14] == b'\x08\x00':
                db_fmt = "Berkeley DB v8 (BTree)"
                is_bdb = True
            elif data[0:4] in (b'SQLi', b'SQLite'):
                db_fmt = "SQLite (Descriptor Wallet)"
            elif data[0:4] == b'\x62\x31\x05\x00':
                db_fmt = "Berkeley DB (BTree)"
                is_bdb = True

        result["db_format"] = db_fmt
        out.append(f"Database format   : {db_fmt}")

        if is_bdb:
            out.append("\n" + self._sub_header("BDB PAGE METADATA"))
            # BDB page header at offset 0
            if len(data) >= 512:
                try:
                    lsn_file  = struct.unpack_from("<I", data, 0)[0]
                    lsn_offset= struct.unpack_from("<I", data, 4)[0]
                    pgno      = struct.unpack_from("<I", data, 8)[0]
                    magic_val = struct.unpack_from("<I", data, 12)[0]
                    version   = struct.unpack_from("<I", data, 16)[0]
                    pagesize  = struct.unpack_from("<I", data, 20)[0]
                    encrypt_alg = data[24] if len(data) > 24 else 0
                    pg_type   = data[25] if len(data) > 25 else 0
                    metaflags = data[26] if len(data) > 26 else 0
                    free      = struct.unpack_from("<I", data, 28)[0]
                    last_pgno = struct.unpack_from("<I", data, 32)[0]
                    nparts    = struct.unpack_from("<I", data, 36)[0]
                    key_count = struct.unpack_from("<I", data, 40)[0]
                    record_cnt= struct.unpack_from("<I", data, 44)[0]
                    flags     = struct.unpack_from("<I", data, 48)[0]

                    out.append(f"  LSN File         : {lsn_file}")
                    out.append(f"  LSN Offset       : {lsn_offset}")
                    out.append(f"  Page No          : {pgno}")
                    out.append(f"  Magic            : 0x{magic_val:08X}")
                    out.append(f"  Version          : {version}")
                    out.append(f"  Page Size        : {pagesize} bytes")
                    out.append(f"  Encrypt Alg      : {encrypt_alg} ({'AES-128-CBC' if encrypt_alg==1 else 'None' if encrypt_alg==0 else f'Unknown({encrypt_alg})'})")
                    out.append(f"  Page Type        : {pg_type} ({'Metadata' if pg_type==9 else str(pg_type)})")
                    out.append(f"  Meta Flags       : 0x{metaflags:02X}")
                    out.append(f"  Free List Head   : {free}")
                    out.append(f"  Last Page No     : {last_pgno}")
                    out.append(f"  Key Count        : {key_count}")
                    out.append(f"  Record Count     : {record_cnt}")
                    out.append(f"  Flags            : 0x{flags:08X}")

                    result["page_size"] = pagesize
                    result["last_pgno"] = last_pgno

                    # Estimated total pages
                    if pagesize > 0:
                        total_pages = len(data) // pagesize
                        out.append(f"\n  Estimated pages  : {total_pages}")
                        out.append(f"  File / page size : {len(data)} / {pagesize} = {total_pages} pages")
                except Exception as e:
                    out.append(f"  [Parse error: {e}]")

        # ── Key markers scan ──
        out.append("\n" + self._sub_header("KEY-VALUE RECORD MARKERS"))
        markers = {
            b"mkey":         ("Master Encryption Key",     "🔐"),
            b"ckey":         ("Encrypted Private Key",     "🔑"),
            b"key\x00":      ("Raw Private Key (unencr.)", "⚠️"),
            b"wkey":         ("Watch Key",                 "👁"),
            b"name":         ("Address Label/Name",        "🏷"),
            b"tx\x00":       ("Transaction Record",        "💸"),
            b"pool":         ("Key Pool Entry",            "🏊"),
            b"version":      ("Version Record",            "📋"),
            b"minversion":   ("Min Version",               "📋"),
            b"setting":      ("Settings Record",           "⚙️"),
            b"bestblock":    ("Best Block Hash",           "⛓"),
            b"orderposnext": ("Order Position Next",       "🔢"),
            b"defaultkey":   ("Default Key",               "🗝"),
            b"acentry":      ("Account Entry",             "👤"),
            b"hdchain":      ("HD Chain (BIP32/44)",       "🌲"),
            b"cscript":      ("Compressed Script",         "📜"),
        }

        found_any = False
        for marker, (desc, icon) in markers.items():
            positions = [i for i in range(len(data)) if data[i:i+len(marker)] == marker]
            if positions:
                found_any = True
                pos_list = ", ".join(f"0x{p:X}" for p in positions[:5])
                if len(positions) > 5:
                    pos_list += f"  … +{len(positions)-5} more"
                out.append(f"  {icon} {desc:<30}  ×{len(positions):3}  @ [{pos_list}]")

        if not found_any:
            out.append("  No standard markers found — may be a descriptor/SQLite wallet")

        # ── Strings scan ──
        out.append("\n" + self._sub_header("PRINTABLE STRINGS (length ≥ 8)"))
        found_strings = self._extract_strings(data, min_len=8)[:30]
        for s in found_strings:
            out.append(f"  {repr(s)}")
        if not found_strings:
            out.append("  None found")

        # ── Entropy ──
        sample = data[:min(1024*1024, len(data))]
        byte_freq = Counter(sample)
        entropy = 0.0
        for cnt in byte_freq.values():
            if cnt > 0:
                p = cnt / len(sample)
                entropy -= p * math.log2(p)
        result["entropy"] = entropy

        out.append("\n" + self._sub_header("ENTROPY ANALYSIS"))
        out.append(f"  Shannon entropy  : {entropy:.6f} bits/byte  (max 8.0)")
        out.append(f"  Sample size      : {len(sample):,} bytes")
        bar_len = int(entropy / 8.0 * 40)
        bar = "█" * bar_len + "░" * (40 - bar_len)
        out.append(f"  [{bar}]  {entropy/8*100:.1f}%")
        if entropy < 5.5:
            out.append("  Interpretation   : Low entropy — mostly plaintext / structured data")
        elif entropy < 7.0:
            out.append("  Interpretation   : Medium entropy — mixed structured+encrypted")
        elif entropy < 7.8:
            out.append("  Interpretation   : High entropy — likely encrypted content")
        else:
            out.append("  Interpretation   : Very high entropy — compressed or strongly encrypted")

        # ── Checksums ──
        out.append("\n" + self._sub_header("FILE CHECKSUMS"))
        md5  = hashlib.md5(data).hexdigest()
        sha1 = hashlib.sha1(data).hexdigest()
        sha256= hashlib.sha256(data).hexdigest()
        out.append(f"  MD5     : {md5}")
        out.append(f"  SHA-1   : {sha1}")
        out.append(f"  SHA-256 : {sha256}")

        result["report"] = "\n".join(out)
        return result

    # ──────────────────────────────────────────
    #  CRYPTO ANALYSIS
    # ──────────────────────────────────────────
    def _analyze_crypto(self, data):
        out = []
        result = {"encrypted": False, "key_count": 0, "report": ""}

        out.append(self._section_header("CRYPTOGRAPHIC INFORMATION"))

        # ── Encryption status ──
        mkey_pos = data.find(b"mkey")
        encrypted = mkey_pos != -1
        result["encrypted"] = encrypted

        out.append(self._sub_header("ENCRYPTION STATUS"))
        if encrypted:
            out.append("  Status           : ✅  ENCRYPTED  (password protected)")
            out.append(f"  mkey position    : 0x{mkey_pos:X}  ({mkey_pos:,})")

            # Try to parse mkey record
            mkey_data = data[mkey_pos:]
            out.append("\n" + self._sub_header("MASTER KEY (mkey) RECORD DETAILS"))
            try:
                # mkey record: key type (1 byte "mkey"), then BDB record value
                # Structure: [encrypted_key_len:2][encrypted_key][salt_len:2][salt][derive_iters:4][derive_method:4]
                pos = mkey_pos + 4  # skip "mkey" marker
                # Look ahead for structure clues
                window = mkey_data[4:256]

                # Scan for iteration count patterns (common values: 25000-100000)
                for offset in range(0, len(window)-4):
                    val = struct.unpack_from("<I", window, offset)[0]
                    if 10000 <= val <= 500000:
                        out.append(f"  Possible derive iterations : {val:,}  (@ mkey+{4+offset})")
                        out.append(f"  Cracking speed estimate    : ~{self._crack_speed_est(val)}")
                        break

                # Encrypted key length hints
                out.append("\n  mkey record bytes (first 128 after marker):")
                chunk = mkey_data[4:132]
                for row_start in range(0, len(chunk), 16):
                    row = chunk[row_start:row_start+16]
                    hex_part = " ".join(f"{b:02X}" for b in row)
                    asc_part = "".join(chr(b) if 32 <= b < 127 else "." for b in row)
                    out.append(f"    0x{mkey_pos+4+row_start:06X} : {hex_part:<47}  |{asc_part}|")

            except Exception as e:
                out.append(f"  [Parse error: {e}]")
        else:
            out.append("  Status           : ⚠️  NOT ENCRYPTED  (private keys in plaintext!)")
            out.append("  Risk level       : CRITICAL — anyone with the file can steal funds")

        # ── Key counts ──
        out.append("\n" + self._sub_header("KEY INVENTORY"))
        ckey_count = data.count(b"ckey")
        raw_key_count = data.count(b"key\x00")
        wkey_count = data.count(b"wkey")
        pool_count = data.count(b"pool")
        hd_count   = data.count(b"hdchain")
        result["key_count"] = ckey_count or raw_key_count

        out.append(f"  Encrypted keys (ckey)      : {ckey_count}")
        out.append(f"  Raw private keys (key)     : {raw_key_count}")
        out.append(f"  Watch keys (wkey)          : {wkey_count}")
        out.append(f"  Key pool entries (pool)    : {pool_count}")
        out.append(f"  HD chain records (hdchain) : {hd_count}")
        out.append(f"  Transactions (tx)          : {data.count(b'tx' + b' ')}")

        total_keys = ckey_count + raw_key_count
        out.append(f"\n  Total estimated keys       : {total_keys}")
        if total_keys > 0:
            out.append(f"  Estimated BTC addresses    : ~{total_keys}")

        # ── Cipher details ──
        out.append("\n" + self._sub_header("CIPHER DETAILS (Standard Bitcoin Core)"))
        out.append("  Encryption algo  : AES-256-CBC")
        out.append("  Key derivation   : SHA-512 iterative (bitcoin2john format)")
        out.append("  KDF algo         : SHA-512 (not scrypt/pbkdf2)")
        out.append("  Salt size        : 8 bytes")
        out.append("  Encrypted key sz : 48 bytes (32-byte key + 16-byte padding)")
        out.append("  IV source        : bytes [32..47] of final KDF hash")
        out.append("  Key source       : bytes [0..31] of final KDF hash")
        out.append("  Padding          : PKCS7 (AES block = 16 bytes)")
        out.append("  Validation check : Last 16 bytes of decrypted data = 0x10")
        out.append("\n  HashCat mode     : -m 11300  (Bitcoin/Litecoin wallet.dat)")
        out.append("  John mode        : --format=bitcoin-core")

        # ── BIP32/HD info ──
        out.append("\n" + self._sub_header("HD WALLET / BIP32 DETECTION"))
        bip32_markers = {
            b"\x04\x88\xad\xe4": "BIP32 xprv (extended private key)",
            b"\x04\x88\xb2\x1e": "BIP32 xpub (extended public key)",
            b"\x04\x35\x83\x94": "BIP32 tprv (testnet private)",
            b"\x04\x35\x87\xcf": "BIP32 tpub (testnet public)",
            b"hdchain":           "HD chain record (Bitcoin Core internal)",
            b"hdseed":            "HD seed record",
        }
        found_bip = False
        for marker, desc in bip32_markers.items():
            if marker in data:
                out.append(f"  ✅ {desc}")
                found_bip = True
        if not found_bip:
            out.append("  No BIP32/HD markers found — likely legacy wallet")

        # ── Script types ──
        out.append("\n" + self._sub_header("SCRIPT TYPE HINTS"))
        addr_types = {
            b"cscript": "Compressed script entries (P2SH possible)",
            b"\x76\xa9": "P2PKH script bytecode (Pay-to-PubKeyHash)",
            b"\xa9\x14": "P2SH script bytecode (Pay-to-ScriptHash)",
            b"\x00\x14": "SegWit v0 P2WPKH bytecode",
            b"\x00\x20": "SegWit v0 P2WSH bytecode",
            b"\x51\x20": "Taproot P2TR bytecode",
        }
        found_script = False
        for pattern, desc in addr_types.items():
            if pattern in data:
                out.append(f"  ✅ {desc}")
                found_script = True
        if not found_script:
            out.append("  No specific script type patterns detected")

        # ── Randomness test ──
        out.append("\n" + self._sub_header("RANDOMNESS / QUALITY TESTS"))
        sample = data[:min(65536, len(data))]
        runs_test = self._runs_test(sample)
        out.append(f"  Runs test score  : {runs_test}")

        byte_freq = Counter(sample)
        unique_bytes = len(byte_freq)
        out.append(f"  Unique byte values: {unique_bytes} / 256")
        if unique_bytes == 256:
            out.append("  Coverage         : Full — all 256 byte values present ✅")
        else:
            out.append(f"  Coverage         : {unique_bytes/256*100:.1f}%")

        result["report"] = "\n".join(out)
        return result

    # ──────────────────────────────────────────
    #  OVERVIEW BUILD
    # ──────────────────────────────────────────
    def _build_overview(self, fp, data, bdb_info, crypto_info):
        out = []
        out.append(self._section_header("BITCOIN WALLET ANALYZER — OVERVIEW"))

        path = Path(fp)
        fsize = len(data)
        mtime = datetime.datetime.fromtimestamp(path.stat().st_mtime)
        ctime = datetime.datetime.fromtimestamp(path.stat().st_ctime)

        out.append(self._sub_header("FILE INFORMATION"))
        out.append(f"  Path             : {fp}")
        out.append(f"  Filename         : {path.name}")
        out.append(f"  Size             : {fsize:,} bytes  ({self._fmt_size(fsize)})")
        out.append(f"  Modified         : {mtime.strftime('%Y-%m-%d  %H:%M:%S')}")
        out.append(f"  Created          : {ctime.strftime('%Y-%m-%d  %H:%M:%S')}")
        out.append(f"  MD5              : {hashlib.md5(data).hexdigest()}")
        out.append(f"  SHA-256          : {hashlib.sha256(data).hexdigest()}")

        out.append("\n" + self._sub_header("DATABASE FORMAT"))
        out.append(f"  Format           : {bdb_info['db_format']}")
        out.append(f"  Magic (hex)      : {data[:8].hex().upper()}")
        if "page_size" in bdb_info:
            out.append(f"  Page size        : {bdb_info['page_size']} bytes")
        if "last_pgno" in bdb_info:
            out.append(f"  Last page no.    : {bdb_info['last_pgno']}")

        out.append("\n" + self._sub_header("ENCRYPTION SUMMARY"))
        enc = crypto_info["encrypted"]
        out.append(f"  Encrypted        : {'YES  ✅  (password protected)' if enc else 'NO   ⚠️  (plaintext keys!)'}")
        out.append(f"  Key algorithm    : AES-256-CBC")
        out.append(f"  KDF              : SHA-512 iterative")
        out.append(f"  Keys found       : {crypto_info['key_count']}")

        out.append("\n" + self._sub_header("QUICK STATISTICS"))
        markers = [
            (b"mkey",  "Master keys"),
            (b"ckey",  "Encrypted private keys"),
            (b"key\x00","Raw private keys"),
            (b"name",  "Address labels"),
            (b"tx\x00","Transactions"),
            (b"pool",  "Key pool slots"),
            (b"hdchain","HD chain records"),
        ]
        for marker, label in markers:
            n = data.count(marker)
            if n:
                out.append(f"  {label:<30} : {n}")

        out.append("\n" + self._sub_header("ENTROPY"))
        out.append(f"  Shannon entropy  : {bdb_info['entropy']:.4f} bits/byte")
        bar_len = int(bdb_info['entropy'] / 8.0 * 40)
        out.append(f"  [{('█' * bar_len) + ('░' * (40-bar_len))}]")

        out.append("\n" + self._sub_header("NEXT STEPS"))
        if enc:
            out.append("  1. Go to 🔑 Hash Extraction tab → click Extract Hash via bitcoin2john.py")
            out.append("  2. Use hashcat -m 11300 hash.txt wordlist.txt  to crack the password")
            out.append("  3. Once password found → import wallet into Bitcoin Core")
        else:
            out.append("  1. Wallet is NOT encrypted — private keys may be directly extractable")
            out.append("  2. Use PyWallet: python pywallet.py --dumpwallet --wallet=wallet.dat")
            out.append("  3. Or: bitcoin-cli dumpwallet wallet_backup.txt")

        out.append("\n" + self._section_header("DONATE  ·  Support Development"))
        out.append("  ₿  BTC  : bc1qn6t8hy8memjfzp4y3sh6fvadjdtqj64vfvlx58")
        out.append("  Ξ  ETH  : 0x512936ca43829C8f71017aE47460820Fe703CAea")
        out.append("  ◎  SOL  : 6ZZrRmeGWMZSmBnQFWXG2UJauqbEgZnwb4Ly9vLYr7mi")
        out.append("  PayPal  : syabiz@yandex.com")

        return "\n".join(out)

    # ──────────────────────────────────────────
    #  HEX DUMP
    # ──────────────────────────────────────────
    def _build_hex(self, data, offset=0, rows=512):
        self.hex_text.delete(1.0, tk.END)
        chunk = data[offset:offset + rows*16]
        lines = []
        lines.append(f"{'Offset':10}  {'00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F':<48}  ASCII")
        lines.append("─" * 78)
        for i in range(0, len(chunk), 16):
            row = chunk[i:i+16]
            addr = offset + i
            hex_parts = []
            for j, b in enumerate(row):
                hex_parts.append(f"{b:02X}")
                if j == 7:
                    hex_parts.append(" ")
            hex_str = " ".join(hex_parts).ljust(49)
            asc = "".join(chr(b) if 32 <= b < 127 else "·" for b in row)
            lines.append(f"0x{addr:08X}  {hex_str}  {asc}")
        self.hex_text.insert(1.0, "\n".join(lines))

    def _hex_goto(self):
        if not self.current_data:
            return
        try:
            offset = int(self._hex_offset_var.get(), 16)
            self._build_hex(self.current_data, offset)
        except ValueError:
            pass

    # ──────────────────────────────────────────
    #  ADDRESS EXTRACTION
    # ──────────────────────────────────────────
    def extract_addresses(self):
        if not self.current_data:
            messagebox.showwarning("No Data", "Analyze a wallet file first!")
            return
        threading.Thread(target=self._do_extract_addresses, daemon=True).start()

    def _do_extract_addresses(self):
        data = self.current_data
        out = []
        out.append(self._section_header("BITCOIN ADDRESS EXTRACTION"))

        ascii_data = data.decode("latin1", errors="ignore")

        # P2PKH and P2SH
        legacy_pat = r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b'
        legacy = sorted(set(re.findall(legacy_pat, ascii_data)))

        # Bech32 (SegWit)
        bech32_pat = r'\bbc1[a-z0-9]{39,59}\b'
        bech32 = sorted(set(re.findall(bech32_pat, ascii_data)))

        # Taproot
        taproot_pat = r'\bbc1p[a-z0-9]{58}\b'
        taproot = sorted(set(re.findall(taproot_pat, ascii_data)))

        total = len(legacy) + len(bech32) + len(taproot)
        out.append(f"\n  Total patterns found : {total}")
        out.append(f"  Legacy (P2PKH/P2SH)  : {len(legacy)}")
        out.append(f"  SegWit bech32 (bc1q) : {len(bech32)}")
        out.append(f"  Taproot (bc1p)       : {len(taproot)}")

        if legacy:
            out.append("\n" + self._sub_header("LEGACY ADDRESSES (P2PKH / P2SH)"))
            for i, addr in enumerate(legacy, 1):
                atype = "P2PKH" if addr.startswith("1") else "P2SH"
                out.append(f"  {i:4}. {addr}  [{atype}]  len={len(addr)}")

        if bech32:
            out.append("\n" + self._sub_header("SEGWIT ADDRESSES (bech32 bc1q)"))
            for i, addr in enumerate(bech32, 1):
                out.append(f"  {i:4}. {addr}  [P2WPKH/P2WSH]")

        if taproot:
            out.append("\n" + self._sub_header("TAPROOT ADDRESSES (bc1p)"))
            for i, addr in enumerate(taproot, 1):
                out.append(f"  {i:4}. {addr}  [P2TR]")

        if total == 0:
            out.append("\n  No addresses found. Wallet may use HD derivation (addresses not stored directly).")

        out.append("\n" + self._sub_header("NOTES"))
        out.append("  ⚠  Pattern matching only — may include false positives")
        out.append("  ✅  Use: bitcoin-cli dumpwallet backup.txt  for complete list")

        self.address_text.delete(1.0, tk.END)
        self.address_text.insert(1.0, "\n".join(out))
        self._set_status(f"[OK] Address extraction done - {total} found")

    # ──────────────────────────────────────────
    #  HASH EXTRACTION
    # ──────────────────────────────────────────
    def use_bitcoin2john(self):
        if not self.filepath.get():
            messagebox.showwarning("No File", "Select a wallet file first!")
            return
        import subprocess

        wallet_path = self.filepath.get()
        possible = [
            "bitcoin2john.py", "./bitcoin2john.py", "../bitcoin2john.py",
            os.path.join(os.getcwd(), "bitcoin2john.py"),
            "/usr/local/bin/bitcoin2john.py", "/usr/bin/bitcoin2john.py",
        ]
        b2j = next((p for p in possible if os.path.exists(p)), None)

        if not b2j:
            if messagebox.askyesno("Download bitcoin2john.py",
                                   "bitcoin2john.py not found.\n\nDownload from the official John the Ripper repo?"):
                try:
                    import urllib.request
                    url = "https://raw.githubusercontent.com/openwall/john/bleeding-jumbo/run/bitcoin2john.py"
                    target = os.path.join(os.getcwd(), "bitcoin2john.py")
                    self._set_status("[>>] Downloading bitcoin2john.py...")
                    urllib.request.urlretrieve(url, target)
                    b2j = target
                    messagebox.showinfo("Downloaded", f"Saved to:\n{target}")
                except Exception as e:
                    messagebox.showerror("Download Error", str(e))
                    return
            else:
                return

        try:
            self._set_status("[>>] Running bitcoin2john.py...")
            for py in ("python3", "python"):
                try:
                    res = subprocess.run([py, b2j, wallet_path],
                                         capture_output=True, text=True, timeout=30)
                    if res.returncode == 0:
                        break
                except FileNotFoundError:
                    continue

            output = res.stdout.strip()
            self.hash_text.delete(1.0, tk.END)

            lines = []
            lines.append(self._section_header("bitcoin2john.py — OFFICIAL OUTPUT"))
            lines.append("\n  EXTRACTED HASH:\n")
            lines.append("  " + output)
            lines.append("")

            if "$bitcoin$" in output:
                parts = output.split("$")
                if len(parts) >= 7:
                    lines.append(self._sub_header("HASH BREAKDOWN"))
                    lines.append(f"  Format           : $bitcoin$")
                    lines.append(f"  mk_hex_len       : {parts[2]}")
                    lines.append(f"  mk_hex (partial) : {parts[3][:64]}…")
                    lines.append(f"  salt_hex_len     : {parts[4] if len(parts)>4 else '?'}")
                    lines.append(f"  Iterations       : {parts[5] if len(parts)>5 else '?'}")
                    if len(parts) > 6:
                        lines.append(f"  Field 6          : {parts[6]}")
                    if len(parts) > 8:
                        lines.append(f"  Verification     : {parts[8] if len(parts)>8 else ''}")
                    try:
                        iters = int(parts[5])
                        lines.append(f"\n  Crack speed est. : {self._crack_speed_est(iters)}")
                    except:
                        pass

            lines.append("\n  ✅  Use this hash with hashcat -m 11300 or john --format=bitcoin-core")
            self.hash_text.insert(1.0, "\n".join(lines))
            self._set_status("[OK] Hash extracted successfully!")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ──────────────────────────────────────────
    #  HELPERS
    # ──────────────────────────────────────────
    def _section_header(self, title):
        w = 70
        return ("═" * w + "\n  " + title + "\n" + "═" * w)

    def _sub_header(self, title):
        return f"  ── {title} " + "─" * max(0, 56 - len(title))

    def _fmt_size(self, n):
        if n < 1024:
            return f"{n} B"
        elif n < 1024**2:
            return f"{n/1024:.2f} KB"
        else:
            return f"{n/1024**2:.2f} MB"

    def _crack_speed_est(self, iters):
        # Rough: ~1M SHA512/s on CPU, 100M on GPU
        cpu_s = iters / 1_000_000
        gpu_s = iters / 100_000_000
        return f"~{1/cpu_s:.0f} pw/s (CPU)  /  ~{1/gpu_s:.0f} pw/s (GPU RTX-class)"

    def _runs_test(self, data):
        if len(data) < 10:
            return "N/A"
        bits = [1 if b > 127 else 0 for b in data[:1024]]
        runs = 1
        for i in range(1, len(bits)):
            if bits[i] != bits[i-1]:
                runs += 1
        n = len(bits)
        expected = (2*n - 1) / 3
        ratio = runs / expected
        if 0.8 <= ratio <= 1.2:
            return f"{runs} runs  (expected ~{expected:.0f})  ✅ Random-looking"
        elif ratio < 0.8:
            return f"{runs} runs  (expected ~{expected:.0f})  ⚠️ More structured than random"
        else:
            return f"{runs} runs  (expected ~{expected:.0f})  ⚠️ High-frequency switching"

    def _extract_strings(self, data, min_len=8):
        result = []
        current = []
        for b in data:
            if 32 <= b < 127:
                current.append(chr(b))
            else:
                if len(current) >= min_len:
                    s = "".join(current)
                    if not s.startswith("\x00"):
                        result.append(s)
                current = []
        if len(current) >= min_len:
            result.append("".join(current))
        return result

    # ──────────────────────────────────────────
    #  CLIPBOARD / SAVE
    # ──────────────────────────────────────────
    def _copy(self, widget):
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(widget.get(1.0, tk.END))
            self._set_status("[OK] Copied to clipboard")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _save(self, widget, default_name="report.txt"):
        try:
            fn = filedialog.asksaveasfilename(
                defaultextension=".txt",
                initialfile=default_name,
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if fn:
                with open(fn, "w", encoding="utf-8") as fh:
                    fh.write(widget.get(1.0, tk.END))
                self._set_status(f"[OK] Saved: {fn}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_hash(self):
        content = self.hash_text.get(1.0, tk.END)
        if "$bitcoin$" not in content:
            messagebox.showwarning("No Hash", "Extract a hash first!")
            return
        # extract just the hash line
        hash_line = next((l.strip() for l in content.splitlines() if "$bitcoin$" in l), "")
        fn = filedialog.asksaveasfilename(
            defaultextension=".txt", initialfile="bitcoin_hash.txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if fn:
            with open(fn, "w") as fh:
                fh.write(hash_line + "\n")
            self._set_status(f"[OK] Hash saved: {fn}")
            messagebox.showinfo("Saved", f"Hash saved to:\n{fn}\n\nNow run:\nhashcat -m 11300 {fn} wordlist.txt")

    def save_addresses(self):
        self._save(self.address_text, "bitcoin_addresses.txt")

    # ──────────────────────────────────────────
    #  STATIC CONTENT
    # ──────────────────────────────────────────
    def _show_crack_instructions(self):
        txt = """\
═══════════════════════════════════════════════════════════════════════
  PASSWORD CRACKING — STEP BY STEP
═══════════════════════════════════════════════════════════════════════

  STEP 1  Extract the hash
  ───────────────────────────────────────────────────────────────────
  Click the "⚡ Extract Hash via bitcoin2john.py" button above.
  The tool uses the OFFICIAL bitcoin2john.py from John the Ripper.
  Hash format:  $bitcoin$<mkLen>$<mkHex>$<saltLen>$<saltHex>$<iters>$…

  STEP 2  Crack with HashCat  (recommended — GPU accelerated)
  ───────────────────────────────────────────────────────────────────
  Mode 11300  =  Bitcoin/Litecoin wallet.dat

  Dictionary attack:
    hashcat -m 11300 hash.txt rockyou.txt

  Dictionary + rules:
    hashcat -m 11300 hash.txt rockyou.txt -r rules/best64.rule

  Brute force (all printable, max 8 chars):
    hashcat -m 11300 hash.txt -a 3 ?a?a?a?a?a?a?a?a

  Mask (lowercase + digits, 6-8 chars):
    hashcat -m 11300 hash.txt -a 3 --increment ?l?l?l?l?d?d?d?d

  Show status:   Press 's' while running
  Resume:        hashcat --restore

  STEP 3  Crack with John the Ripper  (CPU-based)
  ───────────────────────────────────────────────────────────────────
    john --format=bitcoin-core hash.txt --wordlist=wordlist.txt
    john --restore                   ← resume
    john --show hash.txt             ← show found

  RECOMMENDED WORDLISTS
  ───────────────────────────────────────────────────────────────────
  • rockyou.txt      — 14M common passwords
  • SecLists         — https://github.com/danielmiessler/SecLists
  • CrackStation     — https://crackstation.net  (15 GB)

  TIPS
  ───────────────────────────────────────────────────────────────────
  ✓ Start with rockyou.txt — covers most common passwords
  ✓ GPU is 100×+ faster than CPU for this KDF
  ✓ Try crypto-specific words: satoshi, hodl, bitcoin, moon, btc
  ✓ Try year patterns: bitcoin2013, wallet2015, crypto2017
  ✓ Try personal info if you know the owner

  ⚠  Only crack wallets you own or have explicit written permission
     to access.  Unauthorized access is illegal.

═══════════════════════════════════════════════════════════════════════
  RESOURCES
═══════════════════════════════════════════════════════════════════════
  HashCat docs     : https://hashcat.net/wiki/
  John the Ripper  : https://www.openwall.com/john/
  bitcoin2john.py  : https://github.com/openwall/john

  DONATE
  ───────────────────────────────────────────────────────────────────
  ₿  BTC  : bc1qn6t8hy8memjfzp4y3sh6fvadjdtqj64vfvlx58
  Ξ  ETH  : 0x512936ca43829C8f71017aE47460820Fe703CAea
  ◎  SOL  : 6ZZrRmeGWMZSmBnQFWXG2UJauqbEgZnwb4Ly9vLYr7mi
  PayPal  : syabiz@yandex.com
"""
        self.crack_text.insert(1.0, txt)

    def _show_recovery_guide(self):
        txt = """\
═══════════════════════════════════════════════════════════════════════
  BITCOIN WALLET RECOVERY GUIDE
═══════════════════════════════════════════════════════════════════════

  ENCRYPTED WALLET  (has mkey record)
  ───────────────────────────────────────────────────────────────────
  1. Go to 🔑 Hash Extraction tab
  2. Click "⚡ Extract Hash via bitcoin2john.py"
  3. Save the hash to hash.txt
  4. Crack:  hashcat -m 11300 hash.txt wordlist.txt
  5. Once found → bitcoin-cli walletpassphrase "<pw>" 600
  6. bitcoin-cli dumpwallet wallet_backup.txt

  UNENCRYPTED WALLET  (no mkey — CRITICAL risk)
  ───────────────────────────────────────────────────────────────────
  1. PyWallet:      python pywallet.py --dumpwallet --wallet=wallet.dat
  2. Bitcoin Core:  bitcoin-cli dumpwallet "backup.txt"
  3. Import keys:   bitcoin-cli importprivkey <private_key>

  MODERN HD WALLET  (Bitcoin Core ≥ 0.16  /  descriptor wallet)
  ───────────────────────────────────────────────────────────────────
  1. Info:   bitcoin-wallet -wallet=wallet.dat info
  2. Dump:   bitcoin-wallet -wallet=wallet.dat dump
  3. Load:   bitcoin-cli loadwallet "wallet.dat"
             bitcoin-cli getwalletinfo

  UNDERSTANDING THE WALLET FORMAT
  ───────────────────────────────────────────────────────────────────
  Record Type   Meaning
  ─────────────────────────────────────────────────────────────────
  mkey          Master key — encrypted with user password (AES-256-CBC)
  ckey          Encrypted private key (encrypted with master key)
  key           Plaintext private key (DANGEROUS if wallet is old)
  name          Human-readable label for an address
  pool          Key pool — pre-generated addresses for privacy
  tx            Raw transaction data
  bestblock     Hash of the best block seen by this wallet
  hdchain       BIP32 HD derivation chain metadata
  hdseed        BIP32 HD master seed
  version       Wallet version number
  defaultkey    Currently-active default key

  TOOLS
  ───────────────────────────────────────────────────────────────────
  PyWallet     : https://github.com/jackjack-jj/pywallet
  BTCRecover   : https://github.com/gurnec/btcrecover
  Bitcoin Core : https://bitcoin.org/en/download

  USEFUL LINKS
  ───────────────────────────────────────────────────────────────────
  Explorer     : https://blockchain.com / https://mempool.space
  BitcoinTalk  : https://bitcointalk.org
  Reddit       : https://reddit.com/r/Bitcoin

  DONATE
  ───────────────────────────────────────────────────────────────────
  ₿  BTC  : bc1qn6t8hy8memjfzp4y3sh6fvadjdtqj64vfvlx58
  Ξ  ETH  : 0x512936ca43829C8f71017aE47460820Fe703CAea
  ◎  SOL  : 6ZZrRmeGWMZSmBnQFWXG2UJauqbEgZnwb4Ly9vLYr7mi
  PayPal  : syabiz@yandex.com

═══════════════════════════════════════════════════════════════════════
  Made with ❤  for Bitcoin education and learning — by Syabiz
  Use only on your own wallet or with explicit written permission.
═══════════════════════════════════════════════════════════════════════
"""
        self.recovery_text.insert(1.0, txt)


# ──────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────
def main():
    root = tk.Tk()
    app = BitcoinWalletAnalyzer(root)

    # Center window
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()

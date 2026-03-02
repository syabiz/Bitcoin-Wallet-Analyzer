# -*- coding: utf-8 -*-
"""
Bitcoin Wallet Analyzer v2.0 PRO — by Syabiz
Enhanced: accurate BDB parsing, mkey record decode, Base58Check validation,
chi-square test, region entropy, JSON export, color-coded output.
"""

import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import struct
import math
import re
import os
import hashlib
import datetime
import json
from pathlib import Path
from collections import Counter
import threading

# ─────────────────────────────────────────────
#  COLOR PALETTE
# ─────────────────────────────────────────────
BG_DARK    = "#0d0d0d"
BG_CARD    = "#111111"
BG_PANEL   = "#1a1a1a"
BG_INPUT   = "#0f0f0f"
ACCENT     = "#f7931a"
ACCENT2    = "#ffb347"
GREEN      = "#00ff88"
RED        = "#ff4444"
YELLOW     = "#ffd700"
BLUE       = "#4fc3f7"
PURPLE     = "#c084fc"
CYAN       = "#67e8f9"
TEXT_MAIN  = "#f0f0f0"
TEXT_DIM   = "#888888"
TEXT_MUTED = "#555555"
BORDER     = "#2a2a2a"
MONO_FONT  = ("Consolas", 9)
MONO_FONT2 = ("Consolas", 10)
LABEL_FONT = ("Courier New", 9)
HEADER_FONT= ("Courier New", 11, "bold")

# ─────────────────────────────────────────────
#  BASE58 CHARSET & VALIDATION
# ─────────────────────────────────────────────
BASE58_CHARS = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

def base58_decode(s):
    alphabet = BASE58_CHARS
    n = 0
    for c in s:
        if c not in alphabet:
            return None
        n = n * 58 + alphabet.index(c)
    pad = len(s) - len(s.lstrip("1"))
    result = n.to_bytes(max(1, (n.bit_length() + 7) // 8), 'big')
    return b'\x00' * pad + result

def validate_base58check(address):
    try:
        decoded = base58_decode(address)
        if decoded is None or len(decoded) < 5:
            return False, "invalid", None
        payload, checksum = decoded[:-4], decoded[-4:]
        check = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
        if check != checksum:
            return False, "bad_checksum", None
        version = payload[0]
        if version == 0x00:   return True, "P2PKH (Pay-to-PubKey-Hash)", version
        elif version == 0x05: return True, "P2SH (Pay-to-Script-Hash)", version
        elif version == 0x6F: return True, "Testnet P2PKH", version
        elif version == 0xC4: return True, "Testnet P2SH", version
        else:                 return True, f"Unknown version 0x{version:02X}", version
    except Exception:
        return False, "error", None

def validate_bech32(address):
    addr = address.lower()
    if addr.startswith("bc1q") and 42 <= len(addr) <= 62:
        return True, "P2WPKH or P2WSH (SegWit v0)"
    elif addr.startswith("bc1p") and len(addr) == 62:
        return True, "P2TR (Taproot / SegWit v1)"
    elif addr.startswith("tb1"):
        return True, "Testnet Bech32"
    return False, "invalid_bech32"

# ─────────────────────────────────────────────
#  BDB CONSTANTS
# ─────────────────────────────────────────────
BDB_MAGIC = 0x00053162
PAGE_TYPE_NAMES = {
    0:"Invalid", 1:"Duplicate", 2:"Hash", 3:"Hash-Unsorted",
    5:"BTree-Leaf", 6:"BTree-Int.", 7:"Overflow", 8:"HashMeta",
    9:"BTree-Meta", 10:"Queue-Meta", 11:"Queue-Data",
}
ENCRYPT_ALG_NAMES = {0:"None", 1:"AES-128-CBC (DB env-level)"}

WALLET_MARKERS = {
    b"mkey":         ("Master Encryption Key",        "🔐", RED),
    b"ckey":         ("Encrypted Private Key",         "🔑", YELLOW),
    b"key\x00":      ("Raw Unencrypted Key",           "⚠️", RED),
    b"wkey":         ("Watch-Only Key",                "👁",  BLUE),
    b"name":         ("Address Label/Name",            "🏷",  TEXT_MAIN),
    b"tx\x00":       ("Transaction Record",            "💸", CYAN),
    b"pool":         ("Key Pool Entry",                "🏊", GREEN),
    b"version":      ("Wallet Version Record",         "📋", TEXT_DIM),
    b"minversion":   ("Minimum Version",               "📋", TEXT_DIM),
    b"setting":      ("Settings Record",               "⚙️", TEXT_DIM),
    b"bestblock":    ("Best Block Hash",               "⛓",  BLUE),
    b"orderposnext": ("Order Position Counter",        "🔢", TEXT_DIM),
    b"defaultkey":   ("Default Key",                   "🗝",  ACCENT),
    b"acentry":      ("Account Entry",                 "👤", TEXT_DIM),
    b"hdchain":      ("HD Chain (BIP32/44/49/84)",     "🌲", GREEN),
    b"hdseed":       ("HD Master Seed",                "🌱", GREEN),
    b"cscript":      ("Compressed Script (P2SH)",      "📜", PURPLE),
    b"keymeta":      ("Key Metadata (birth time)",     "🕐", TEXT_DIM),
    b"watchmeta":    ("Watch Key Metadata",            "👁",  BLUE),
    b"destdata":     ("Destination Data",              "📦", TEXT_DIM),
    b"walletdescriptor": ("Descriptor Wallet Record",  "📝", CYAN),
    b"flags":        ("Wallet Flags",                  "🚩", TEXT_DIM),
    b"lockedcoins":  ("Locked Coins",                  "🔒", YELLOW),
}


class BitcoinWalletAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Bitcoin Wallet Analyzer v2.0 PRO — by Syabiz")
        self.root.geometry("1220x720")
        self.root.configure(bg=BG_DARK)
        self.root.minsize(960, 640)
        self.filepath         = tk.StringVar()
        self.current_data     = None
        self.analysis_result  = {}
        self._setup_ttk_styles()
        self._build_ui()

    def _setup_ttk_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure(".", background=BG_DARK, foreground=TEXT_MAIN,
                    fieldbackground=BG_INPUT, troughcolor=BG_PANEL,
                    bordercolor=BORDER, darkcolor=BG_PANEL, lightcolor=BG_PANEL,
                    insertcolor=ACCENT, font=LABEL_FONT)
        s.configure("TNotebook", background=BG_DARK, borderwidth=0)
        s.configure("TNotebook.Tab", background=BG_PANEL, foreground=TEXT_DIM,
                    padding=[14, 6], font=LABEL_FONT)
        s.map("TNotebook.Tab",
              background=[("selected", BG_CARD)],
              foreground=[("selected", ACCENT)],
              expand=[("selected", [1, 1, 1, 0])])
        s.configure("TFrame", background=BG_DARK)
        s.configure("TLabelframe", background=BG_CARD, bordercolor=BORDER,
                    foreground=ACCENT, font=HEADER_FONT)
        s.configure("TLabelframe.Label", background=BG_CARD,
                    foreground=ACCENT, font=HEADER_FONT)
        s.configure("TButton", background=BG_PANEL, foreground=TEXT_MAIN,
                    bordercolor=BORDER, relief="flat", padding=[10, 5], font=LABEL_FONT)
        s.map("TButton",
              background=[("active", ACCENT), ("pressed", "#c87010")],
              foreground=[("active", "#000000")])
        s.configure("Orange.TButton", background=ACCENT, foreground="#000000",
                    font=("Courier New", 9, "bold"), padding=[12, 6])
        s.map("Orange.TButton",
              background=[("active", ACCENT2)], foreground=[("active", "#000000")])
        s.configure("TEntry", fieldbackground=BG_INPUT, foreground=TEXT_MAIN,
                    insertcolor=ACCENT, bordercolor=BORDER)
        s.configure("TProgressbar", troughcolor=BG_PANEL, background=ACCENT)
        s.configure("TScrollbar", background=BG_PANEL, troughcolor=BG_DARK,
                    bordercolor=BORDER, arrowcolor=TEXT_DIM)
        s.map("TScrollbar", background=[("active", ACCENT)])
        s.configure("TLabel", background=BG_DARK, foreground=TEXT_MAIN, font=LABEL_FONT)

    def _build_ui(self):
        header = tk.Frame(self.root, bg=BG_CARD, height=72)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        lhdr = tk.Frame(header, bg=BG_CARD)
        lhdr.pack(side=tk.LEFT, padx=20, pady=10)
        tk.Label(lhdr, text="₿", font=("Courier New", 30, "bold"),
                 bg=BG_CARD, fg=ACCENT).pack(side=tk.LEFT, padx=(0, 10))
        tf = tk.Frame(lhdr, bg=BG_CARD)
        tf.pack(side=tk.LEFT)
        tk.Label(tf, text="Bitcoin Wallet Analyzer",
                 font=("Courier New", 16, "bold"), bg=BG_CARD, fg=TEXT_MAIN).pack(anchor="w")
        tk.Label(tf, text="BerkeleyDB v8/v9  ·  AES-256-CBC  ·  SHA-512 KDF  ·  Base58Check  ·  BIP32/44/49/84  ·  by Syabiz",
                 font=LABEL_FONT, bg=BG_CARD, fg=TEXT_DIM).pack(anchor="w")
        rhdr = tk.Frame(header, bg=BG_CARD)
        rhdr.pack(side=tk.RIGHT, padx=20)
        tk.Label(rhdr, text="v2.0 PRO", font=("Courier New", 9, "bold"),
                 bg=ACCENT, fg="#000000", padx=8, pady=3).pack()
        tk.Frame(self.root, bg=ACCENT, height=2).pack(fill=tk.X)

        file_bar = tk.Frame(self.root, bg=BG_PANEL, pady=10)
        file_bar.pack(fill=tk.X)
        inner_file = tk.Frame(file_bar, bg=BG_PANEL)
        inner_file.pack(fill=tk.X, padx=16)
        tk.Label(inner_file, text="WALLET FILE", font=("Courier New", 8, "bold"),
                 bg=BG_PANEL, fg=ACCENT).pack(side=tk.LEFT, padx=(0, 8))
        eb = tk.Frame(inner_file, bg=BORDER, padx=1, pady=1)
        eb.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self._file_entry = tk.Entry(eb, textvariable=self.filepath,
                                    bg=BG_INPUT, fg=TEXT_MAIN, insertbackground=ACCENT,
                                    relief="flat", font=MONO_FONT, bd=4)
        self._file_entry.pack(fill=tk.X)
        ttk.Button(inner_file, text="Browse…",       command=self.browse_file).pack(side=tk.LEFT, padx=4)
        ttk.Button(inner_file, text="⚡  Analyze Wallet",
                   command=self.start_analysis, style="Orange.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(inner_file, text="💾  Export JSON",
                   command=self.export_json).pack(side=tk.LEFT, padx=4)

        self._progress_var = tk.DoubleVar()
        ttk.Progressbar(self.root, variable=self._progress_var,
                        maximum=100, mode="determinate").pack(fill=tk.X)

        nb_frame = tk.Frame(self.root, bg=BG_DARK)
        nb_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
        self.nb = ttk.Notebook(nb_frame)
        self.nb.pack(fill=tk.BOTH, expand=True)
        self.nb.add(self._tab_overview(),  text="  Overview ")
        self.nb.add(self._tab_bdb(),       text="  BDB Structure ")
        self.nb.add(self._tab_crypto(),    text="  Crypto & KDF ")
        self.nb.add(self._tab_hash(),      text="  Hash Extraction ")
        self.nb.add(self._tab_addresses(), text="  Addresses ")
        self.nb.add(self._tab_entropy(),   text="  Entropy Map ")
        self.nb.add(self._tab_hex(),       text="  Hex Viewer ")
        self.nb.add(self._tab_recovery(),  text="  Recovery Guide ")

        sb = tk.Frame(self.root, bg=BG_PANEL, height=26)
        sb.pack(fill=tk.X, side=tk.BOTTOM)
        sb.pack_propagate(False)
        self._status_var = tk.StringVar(value="[*] Ready — Select a wallet.dat file to begin")
        tk.Label(sb, textvariable=self._status_var, font=LABEL_FONT,
                 bg=BG_PANEL, fg=TEXT_DIM, anchor="w", padx=12).pack(fill=tk.BOTH, expand=True)

    def _make_stext(self, parent, height=None, fg=TEXT_MAIN, bg=BG_INPUT):
        kw = dict(wrap=tk.WORD, font=MONO_FONT2, bg=bg, fg=fg,
                  insertbackground=ACCENT, selectbackground=ACCENT,
                  selectforeground="#000", relief="flat", borderwidth=0,
                  highlightthickness=1, highlightbackground=BORDER, highlightcolor=ACCENT)
        if height: kw["height"] = height
        st = scrolledtext.ScrolledText(parent, **kw)
        try:
            st.vbar.config(bg=BG_PANEL, troughcolor=BG_DARK,
                           activebackground=ACCENT, highlightthickness=0, bd=0)
        except Exception: pass
        self._configure_tags(st)
        return st

    def _configure_tags(self, w):
        w.tag_configure("header", foreground=ACCENT,   font=("Courier New", 10, "bold"))
        w.tag_configure("sub",    foreground=CYAN,     font=("Courier New", 9, "bold"))
        w.tag_configure("green",  foreground=GREEN)
        w.tag_configure("red",    foreground=RED)
        w.tag_configure("yellow", foreground=YELLOW)
        w.tag_configure("blue",   foreground=BLUE)
        w.tag_configure("purple", foreground=PURPLE)
        w.tag_configure("accent", foreground=ACCENT)
        w.tag_configure("dim",    foreground=TEXT_DIM)
        w.tag_configure("muted",  foreground=TEXT_MUTED)
        w.tag_configure("mono",   font=("Consolas", 9))
        w.tag_configure("ok",     foreground=GREEN,  font=("Courier New", 9, "bold"))
        w.tag_configure("warn",   foreground=YELLOW, font=("Courier New", 9, "bold"))
        w.tag_configure("crit",   foreground=RED,    font=("Courier New", 9, "bold"))
        w.tag_configure("cyan",   foreground=CYAN)

    def _wi(self, w, text, tag=None):
        if tag: w.insert(tk.END, text, tag)
        else:   w.insert(tk.END, text)

    def _btn_row(self, parent, buttons):
        row = tk.Frame(parent, bg=BG_DARK)
        row.pack(fill=tk.X, pady=(6, 0))
        for label, cmd in buttons:
            is_p = any(k in label for k in ("⚡", "Extract", "Analyze"))
            ttk.Button(row, text=label, command=cmd,
                       style="Orange.TButton" if is_p else "TButton").pack(side=tk.LEFT, padx=(0,4))
        return row

    # ── TABS ──
    def _tab_overview(self):
        f = ttk.Frame(self.nb)
        self._stat_vars = {}
        sr = tk.Frame(f, bg=BG_DARK)
        sr.pack(fill=tk.X, padx=8, pady=(8,6))
        for key, label in [("file_size","File Size"),("format","Format"),
                            ("encrypted","Encrypted"),("key_count","Key Records"),
                            ("entropy","Entropy"),("pages","BDB Pages")]:
            card = tk.Frame(sr, bg=BG_CARD, bd=0, padx=12, pady=8,
                            highlightbackground=BORDER, highlightthickness=1)
            card.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0,5))
            tk.Label(card, text=label.upper(), font=("Courier New",7,"bold"),
                     bg=BG_CARD, fg=TEXT_DIM).pack(anchor="w")
            var = tk.StringVar(value="─")
            self._stat_vars[key] = var
            tk.Label(card, textvariable=var, font=("Courier New",12,"bold"),
                     bg=BG_CARD, fg=ACCENT).pack(anchor="w")
        inner = tk.Frame(f, bg=BG_DARK)
        inner.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0,6))
        self.overview_text = self._make_stext(inner)
        self.overview_text.pack(fill=tk.BOTH, expand=True)
        self._btn_row(inner, [
            ("📋 Copy All",    lambda: self._copy(self.overview_text)),
            ("💾 Save Report", lambda: self._save(self.overview_text)),
            ("🗑️  Clear",      lambda: self.overview_text.delete(1.0, tk.END)),
        ])
        return f

    def _tab_bdb(self):
        f = ttk.Frame(self.nb)
        inner = tk.Frame(f, bg=BG_DARK)
        inner.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        tk.Label(inner, text="BerkeleyDB Internal Structure Parser",
                 font=HEADER_FONT, bg=BG_DARK, fg=ACCENT).pack(anchor="w", pady=(0,4))
        tk.Label(inner, text="Page metadata · Magic · Version · BTree · Record markers · Checksums",
                 font=LABEL_FONT, bg=BG_DARK, fg=TEXT_DIM).pack(anchor="w", pady=(0,6))
        self.bdb_text = self._make_stext(inner)
        self.bdb_text.pack(fill=tk.BOTH, expand=True)
        self._btn_row(inner, [
            ("📋 Copy", lambda: self._copy(self.bdb_text)),
            ("💾 Save", lambda: self._save(self.bdb_text, "bdb_structure.txt")),
        ])
        return f

    def _tab_crypto(self):
        f = ttk.Frame(self.nb)
        inner = tk.Frame(f, bg=BG_DARK)
        inner.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        tk.Label(inner, text="Cryptographic & KDF Analysis",
                 font=HEADER_FONT, bg=BG_DARK, fg=ACCENT).pack(anchor="w", pady=(0,4))
        tk.Label(inner, text="AES-256-CBC · SHA-512 KDF · mkey decode · salt · iterations · cipher details",
                 font=LABEL_FONT, bg=BG_DARK, fg=TEXT_DIM).pack(anchor="w", pady=(0,6))
        self.crypto_text = self._make_stext(inner)
        self.crypto_text.pack(fill=tk.BOTH, expand=True)
        self._btn_row(inner, [
            ("📋 Copy", lambda: self._copy(self.crypto_text)),
            ("💾 Save", lambda: self._save(self.crypto_text, "crypto_info.txt")),
        ])
        return f

    def _tab_hash(self):
        f = ttk.Frame(self.nb)
        inner = tk.Frame(f, bg=BG_DARK)
        inner.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        warn = tk.Frame(inner, bg="#1a0f00",
                        highlightbackground=ACCENT, highlightthickness=1, padx=10, pady=8)
        warn.pack(fill=tk.X, pady=(0,8))
        tk.Label(warn, text="⚠  Hash extraction uses the official bitcoin2john.py (John the Ripper project).",
                 font=LABEL_FONT, bg="#1a0f00", fg=ACCENT, wraplength=950).pack()
        tk.Label(inner, text="Extracted Hash  (HashCat -m 11300 / John bitcoin-core)",
                 font=HEADER_FONT, bg=BG_DARK, fg=ACCENT).pack(anchor="w", pady=(0,4))
        self.hash_text = self._make_stext(inner, height=10, bg="#060600")
        self.hash_text.pack(fill=tk.X, pady=(0,6))
        self._btn_row(inner, [
            ("⚡ Extract Hash via bitcoin2john.py", self.use_bitcoin2john),
            ("📋 Copy Hash", lambda: self._copy(self.hash_text)),
            ("💾 Save Hash", self.save_hash),
        ])
        tk.Label(inner, text="Cracking Command Reference",
                 font=HEADER_FONT, bg=BG_DARK, fg=ACCENT).pack(anchor="w", pady=(10,4))
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
        warn.pack(fill=tk.X, pady=(0,8))
        tk.Label(warn, text="ℹ  Addresses validated with Base58Check checksum. Bech32 uses format heuristics.",
                 font=LABEL_FONT, bg="#0d1a0d", fg=GREEN, wraplength=950).pack()
        tk.Label(inner, text="Bitcoin Addresses  (Base58Check + Bech32 Validated)",
                 font=HEADER_FONT, bg=BG_DARK, fg=ACCENT).pack(anchor="w", pady=(0,4))
        self.address_text = self._make_stext(inner)
        self.address_text.pack(fill=tk.BOTH, expand=True)
        self._btn_row(inner, [
            ("⚡ Extract & Validate Addresses", self.extract_addresses),
            ("📋 Copy List",                   lambda: self._copy(self.address_text)),
            ("💾 Save List",                   self.save_addresses),
        ])
        return f

    def _tab_entropy(self):
        f = ttk.Frame(self.nb)
        inner = tk.Frame(f, bg=BG_DARK)
        inner.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        tk.Label(inner, text="Entropy Map & Statistical Tests",
                 font=HEADER_FONT, bg=BG_DARK, fg=ACCENT).pack(anchor="w", pady=(0,4))
        tk.Label(inner, text="Shannon entropy · Chi-square · Runs test · Byte histogram · Region heat map",
                 font=LABEL_FONT, bg=BG_DARK, fg=TEXT_DIM).pack(anchor="w", pady=(0,6))
        self.entropy_text = self._make_stext(inner)
        self.entropy_text.pack(fill=tk.BOTH, expand=True)
        self._btn_row(inner, [
            ("📋 Copy", lambda: self._copy(self.entropy_text)),
            ("💾 Save", lambda: self._save(self.entropy_text, "entropy_analysis.txt")),
        ])
        return f

    def _tab_hex(self):
        f = ttk.Frame(self.nb)
        inner = tk.Frame(f, bg=BG_DARK)
        inner.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)
        top = tk.Frame(inner, bg=BG_DARK)
        top.pack(fill=tk.X, pady=(0,6))
        tk.Label(top, text="Hex Viewer", font=HEADER_FONT, bg=BG_DARK, fg=ACCENT).pack(side=tk.LEFT)
        tk.Label(top, text="  Offset (hex):", font=LABEL_FONT, bg=BG_DARK, fg=TEXT_DIM).pack(side=tk.LEFT, padx=(20,4))
        self._hex_offset_var = tk.StringVar(value="0")
        tk.Entry(top, textvariable=self._hex_offset_var, width=10,
                 bg=BG_INPUT, fg=TEXT_MAIN, insertbackground=ACCENT,
                 relief="flat", font=MONO_FONT).pack(side=tk.LEFT, padx=(0,6))
        ttk.Button(top, text="Go", command=self._hex_goto).pack(side=tk.LEFT)
        tk.Label(top, text="  Rows:", font=LABEL_FONT, bg=BG_DARK, fg=TEXT_DIM).pack(side=tk.LEFT, padx=(12,4))
        self._hex_rows_var = tk.StringVar(value="256")
        tk.Entry(top, textvariable=self._hex_rows_var, width=6,
                 bg=BG_INPUT, fg=TEXT_MAIN, insertbackground=ACCENT,
                 relief="flat", font=MONO_FONT).pack(side=tk.LEFT)
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

    # ── BROWSE ──
    def browse_file(self):
        fn = filedialog.askopenfilename(
            title="Select Bitcoin Wallet File",
            filetypes=[("Wallet files", "*.dat"), ("All files", "*.*")])
        if fn: self.filepath.set(fn)

    # ── ANALYSIS ──
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

    def _set_stat(self, key, value):
        if key in self._stat_vars:
            self._stat_vars[key].set(value)

    def _run_analysis(self):
        fp = self.filepath.get()
        try:
            self._set_status("Reading file…")
            self._set_progress(5)
            path = Path(fp)
            if not path.exists(): raise FileNotFoundError(f"Not found: {fp}")
            if path.stat().st_size == 0: raise ValueError("File is empty")
            with open(fp, "rb") as fh:
                self.current_data = fh.read()
            data = self.current_data
            for w in (self.overview_text, self.bdb_text, self.crypto_text,
                      self.hex_text, self.address_text, self.entropy_text):
                w.delete(1.0, tk.END)
            self.hash_text.delete(1.0, tk.END)
            self._set_stat("file_size", self._fmt_size(len(data)))
            self._set_progress(10)

            self._set_status("Parsing BerkeleyDB structure…")
            self._set_progress(20)
            bdb_info = self._analyze_bdb(data)

            self._set_status("Analyzing cryptographic parameters…")
            self._set_progress(40)
            crypto_info = self._analyze_crypto(data)

            self._set_status("Running statistical & entropy tests…")
            self._set_progress(58)
            entropy_info = self._analyze_entropy(data)

            self._set_status("Building overview…")
            self._set_progress(72)
            self._build_overview(fp, data, bdb_info, crypto_info, entropy_info)

            self._set_status("Rendering hex dump…")
            self._set_progress(85)
            try:   rows = int(self._hex_rows_var.get())
            except: rows = 256
            self._build_hex(data, 0, rows)

            self._populate_bdb_tab(bdb_info)
            self._populate_crypto_tab(crypto_info)
            self._populate_entropy_tab(entropy_info)

            self._set_stat("encrypted", "YES ✓" if crypto_info["encrypted"] else "NO ✗")
            self._set_stat("key_count", str(crypto_info["key_count"]))
            self._set_stat("format",    bdb_info["db_format_short"])
            self._set_stat("entropy",   f"{entropy_info['global_entropy']:.3f}")
            self._set_stat("pages",     str(bdb_info.get("estimated_pages", "?")))

            self.analysis_result = {
                "file": fp, "size": len(data),
                "format": bdb_info["db_format"],
                "encrypted": crypto_info["encrypted"],
                "key_count": crypto_info["key_count"],
                "entropy":   entropy_info["global_entropy"],
                "chi2":      entropy_info["chi2"],
                "md5":       hashlib.md5(data).hexdigest(),
                "sha256":    hashlib.sha256(data).hexdigest(),
                "sha512":    hashlib.sha512(data).hexdigest(),
                "markers":   bdb_info["marker_counts"],
                "mkey_info": crypto_info.get("mkey_parsed", {}),
                "timestamp": datetime.datetime.now().isoformat(),
            }
            self._set_progress(100)
            self._set_status(f"[OK] Analysis complete — {datetime.datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            import traceback
            self._set_status(f"[ERR] {e}")
            messagebox.showerror("Error", f"Analysis failed:\n{e}\n\n{traceback.format_exc()[:600]}")

    # ── BDB ANALYSIS ──
    def _analyze_bdb(self, data):
        result = {"db_format":"Unknown","db_format_short":"Unknown",
                  "is_bdb":False,"marker_counts":{},"estimated_pages":0,
                  "report_sections":[]}
        lines = []

        lines.append(("  FILE FORMAT DETECTION\n", "sub"))
        db_format = "Unknown"; is_bdb = False; page_size = 4096

        if len(data) >= 20:
            magic_le = struct.unpack_from("<I", data, 12)[0]
            magic_be = struct.unpack_from(">I", data, 12)[0]
            ver_le   = struct.unpack_from("<I", data, 16)[0]
            ver_be   = struct.unpack_from(">I", data, 16)[0]

            if magic_le == BDB_MAGIC:
                is_bdb = True
                db_format = f"Berkeley DB BTree (little-endian, version {ver_le})"
                result["db_format_short"] = f"BDB v{ver_le} LE"
                result["byte_order"] = "little-endian"
                result["version_num"] = ver_le
            elif magic_be == BDB_MAGIC:
                is_bdb = True
                db_format = f"Berkeley DB BTree (big-endian, version {ver_be})"
                result["db_format_short"] = f"BDB v{ver_be} BE"
                result["byte_order"] = "big-endian"
                result["version_num"] = ver_be
            elif data[:6] == b"SQLite":
                db_format = "SQLite 3 (Descriptor Wallet — Bitcoin Core ≥ 0.21)"
                result["db_format_short"] = "SQLite3"
            else:
                for off in (512, 4096):
                    if len(data) > off + 20:
                        m = struct.unpack_from("<I", data, off + 12)[0]
                        if m == BDB_MAGIC:
                            is_bdb = True
                            v = struct.unpack_from("<I", data, off + 16)[0]
                            db_format = f"Berkeley DB BTree (found @+{off}, version {v})"
                            result["db_format_short"] = f"BDB v{v}"
                            break
                if not is_bdb:
                    result["db_format_short"] = "Unknown"

        result["db_format"] = db_format
        result["is_bdb"]    = is_bdb
        lines.append((f"  Format           : {db_format}\n", "accent"))
        lines.append((f"  Magic bytes[0:4] : {data[:4].hex().upper()}\n", None))
        lines.append((f"  Magic @offset 12 : {data[12:16].hex().upper() if len(data)>=16 else '?'}\n", None))

        if is_bdb and len(data) >= 512:
            lines.append(("\n  BDB METADATA PAGE  (offset 0)\n", "sub"))
            try:
                bo  = result.get("byte_order","little-endian")
                fmt = "<" if bo == "little-endian" else ">"
                lsn_file    = struct.unpack_from(f"{fmt}I", data, 0)[0]
                lsn_off     = struct.unpack_from(f"{fmt}I", data, 4)[0]
                pgno        = struct.unpack_from(f"{fmt}I", data, 8)[0]
                magic_val   = struct.unpack_from(f"{fmt}I", data, 12)[0]
                db_version  = struct.unpack_from(f"{fmt}I", data, 16)[0]
                pagesize    = struct.unpack_from(f"{fmt}I", data, 20)[0]
                encrypt_alg = data[24]
                pg_type     = data[25]
                meta_flags  = data[26]
                free_pg     = struct.unpack_from(f"{fmt}I", data, 28)[0]
                last_pgno   = struct.unpack_from(f"{fmt}I", data, 32)[0]
                nparts      = struct.unpack_from(f"{fmt}I", data, 36)[0]
                key_count   = struct.unpack_from(f"{fmt}I", data, 40)[0]
                rec_count   = struct.unpack_from(f"{fmt}I", data, 44)[0]
                flags       = struct.unpack_from(f"{fmt}I", data, 48)[0]
                uid_hex     = data[52:68].hex().upper() if len(data) >= 68 else ""
                page_size   = pagesize if 512 <= pagesize <= 65536 else 4096
                est_pages   = len(data) // page_size if page_size > 0 else 0
                result["page_size"] = page_size
                result["last_pgno"] = last_pgno
                result["estimated_pages"] = est_pages
                pt_name = PAGE_TYPE_NAMES.get(pg_type, f"Unknown({pg_type})")
                ea_name = ENCRYPT_ALG_NAMES.get(encrypt_alg, f"Unknown({encrypt_alg})")
                valid_magic = magic_val == BDB_MAGIC
                lines.append((f"  LSN File         : {lsn_file}\n", None))
                lines.append((f"  LSN Offset       : {lsn_off}\n", None))
                lines.append((f"  Page Number      : {pgno}\n", None))
                lines.append((f"  Magic            : 0x{magic_val:08X}  {'✅ Valid BDB' if valid_magic else '⚠ Mismatch'}\n",
                              "green" if valid_magic else "warn"))
                lines.append((f"  DB Version       : {db_version}\n", "accent"))
                lines.append((f"  Page Size        : {page_size} bytes\n", "accent"))
                lines.append((f"  Encrypt Alg      : {ea_name}\n", None))
                lines.append((f"  Page Type        : {pt_name}\n", None))
                lines.append((f"  Meta Flags       : 0x{meta_flags:02X}\n", None))
                lines.append((f"  Free List Head   : page {free_pg}\n", None))
                lines.append((f"  Last Page No     : {last_pgno}\n", "accent"))
                lines.append((f"  Partitions       : {nparts}\n", None))
                lines.append((f"  Key Count (meta) : {key_count}\n", "yellow"))
                lines.append((f"  Record Count     : {rec_count}\n", "yellow"))
                lines.append((f"  DB Flags         : 0x{flags:08X}\n", None))
                lines.append((f"  Unique DB ID     : {uid_hex}\n", "dim"))
                lines.append((f"\n  Estimated pages  : {est_pages}  ({len(data):,} / {page_size})\n", "green"))

                if pg_type == 9 and len(data) >= 92:
                    lines.append(("\n  BTREE METADATA\n", "sub"))
                    try:
                        maxkey = struct.unpack_from(f"{fmt}I", data, 72)[0]
                        minkey = struct.unpack_from(f"{fmt}I", data, 76)[0]
                        root   = struct.unpack_from(f"{fmt}I", data, 88)[0]
                        lines.append((f"  BTree Max Keys   : {maxkey}\n", None))
                        lines.append((f"  BTree Min Keys   : {minkey}\n", None))
                        lines.append((f"  Root Page No     : {root}\n", "accent"))
                    except Exception: pass
            except Exception as e:
                lines.append((f"  [Page parse error: {e}]\n", "red"))

        lines.append(("\n  WALLET RECORD MARKERS\n", "sub"))
        mc = {}
        for marker, (desc, icon, color) in WALLET_MARKERS.items():
            positions = []
            start = 0
            while True:
                pos = data.find(marker, start)
                if pos == -1: break
                positions.append(pos)
                start = pos + 1
            if positions:
                mc[marker.decode("latin1")] = len(positions)
                pos_str = "  ".join(f"0x{p:X}" for p in positions[:4])
                more    = f"  +{len(positions)-4} more" if len(positions) > 4 else ""
                tag = "red" if "⚠️" in icon or "🔐" in icon else "yellow" if "🔑" in icon else "green"
                lines.append((f"  {icon} {desc:<38} ×{len(positions):<4}  @ {pos_str}{more}\n", tag))
        result["marker_counts"] = mc
        if not mc:
            lines.append(("  No standard wallet markers found\n", "warn"))

        lines.append(("\n  PRINTABLE STRINGS (len ≥ 10)\n", "sub"))
        for s in self._extract_strings(data, min_len=10)[:40]:
            lines.append((f"  {repr(s)}\n", "dim"))

        lines.append(("\n  FILE CHECKSUMS\n", "sub"))
        lines.append((f"  MD5     : {hashlib.md5(data).hexdigest()}\n",    "dim"))
        lines.append((f"  SHA-1   : {hashlib.sha1(data).hexdigest()}\n",   "dim"))
        lines.append((f"  SHA-256 : {hashlib.sha256(data).hexdigest()}\n", "dim"))
        lines.append((f"  SHA-512 : {hashlib.sha512(data).hexdigest()}\n", "dim"))

        result["report_sections"] = lines
        return result

    def _populate_bdb_tab(self, bdb_info):
        w = self.bdb_text
        w.delete(1.0, tk.END)
        self._wi(w, "═" * 72 + "\n", "header")
        self._wi(w, "  BerkeleyDB STRUCTURE ANALYSIS\n", "header")
        self._wi(w, "═" * 72 + "\n\n", "header")
        for text, tag in bdb_info["report_sections"]:
            self._wi(w, text, tag)

    # ── CRYPTO ANALYSIS ──
    def _analyze_crypto(self, data):
        result = {"encrypted":False,"key_count":0,"mkey_parsed":{},"report_sections":[]}
        lines = []

        mkey_pos  = data.find(b"mkey")
        encrypted = mkey_pos != -1
        result["encrypted"] = encrypted

        lines.append(("  ENCRYPTION STATUS\n", "sub"))
        if encrypted:
            lines.append(("  Status           : ENCRYPTED  ✅  (password protected)\n", "green"))
            lines.append((f"  mkey offset      : 0x{mkey_pos:X}  ({mkey_pos:,})\n", "accent"))
            lines.append(("\n  MASTER KEY RECORD DECODE  (mkey)\n", "sub"))
            lines.append(("  Layout: [enckey_len=48][enckey 48B][salt_len=8][salt 8B][iters uint32][method uint32]\n", "dim"))
            try:
                mkey_region = data[mkey_pos:mkey_pos + 512]
                parsed = self._parse_mkey_record(mkey_region)
                result["mkey_parsed"] = parsed
                if parsed.get("encrypted_key"):
                    ek = parsed["encrypted_key"]
                    lines.append((f"  Encrypted key len: {len(ek)} bytes\n", "accent"))
                    lines.append((f"  Encrypted key    : {ek.hex().upper()}\n", "yellow"))
                if parsed.get("salt"):
                    s = parsed["salt"]
                    lines.append((f"  Salt length      : {len(s)} bytes\n", "accent"))
                    lines.append((f"  Salt (hex)       : {s.hex().upper()}\n", "yellow"))
                if parsed.get("derive_iters"):
                    iters = parsed["derive_iters"]
                    lines.append((f"  Derive iterations: {iters:,}\n", "accent"))
                    lines.append((f"  Crack estimate   : {self._crack_speed_est(iters)}\n", "yellow"))
                if parsed.get("derive_method") is not None:
                    m = parsed["derive_method"]
                    mname = "SHA-512 iterative" if m == 0 else f"Unknown({m})"
                    lines.append((f"  Derive method    : {m}  ({mname})\n", None))
                lines.append(("\n  Raw mkey region (160 bytes):\n", "dim"))
                chunk = mkey_region[4:164]
                for i in range(0, len(chunk), 16):
                    row  = chunk[i:i+16]
                    hp   = " ".join(f"{b:02X}" for b in row)
                    ap   = "".join(chr(b) if 32 <= b < 127 else "." for b in row)
                    lines.append((f"  0x{mkey_pos+4+i:06X} : {hp:<47}  |{ap}|\n", "mono"))
            except Exception as e:
                lines.append((f"  [mkey parse error: {e}]\n", "red"))
        else:
            lines.append(("  Status           : NOT ENCRYPTED  ⚠\n", "warn"))
            lines.append(("  RISK             : CRITICAL — private keys may be in plaintext!\n", "crit"))

        lines.append(("\n  KEY & RECORD INVENTORY\n", "sub"))
        ckey_cnt = data.count(b"ckey")
        raw_cnt  = data.count(b"key\x00")
        wkey_cnt = data.count(b"wkey")
        pool_cnt = data.count(b"pool")
        hd_cnt   = data.count(b"hdchain")
        hds_cnt  = data.count(b"hdseed")
        name_cnt = data.count(b"name")
        tx_cnt   = len(re.findall(b"tx\x00", data))
        km_cnt   = data.count(b"keymeta")
        desc_cnt = data.count(b"walletdescriptor")
        bestb_cnt= data.count(b"bestblock")
        result["key_count"] = ckey_cnt + raw_cnt

        ki_rows = [
            ("Encrypted priv keys (ckey)",    ckey_cnt,  "yellow"),
            ("Plaintext priv keys (key\\x00)", raw_cnt,   "red" if raw_cnt else "dim"),
            ("Watch-only keys (wkey)",         wkey_cnt,  "blue"),
            ("Key pool entries (pool)",        pool_cnt,  "green"),
            ("Key metadata (keymeta)",         km_cnt,    "dim"),
            ("HD chain records (hdchain)",     hd_cnt,    "green"),
            ("HD seed records (hdseed)",       hds_cnt,   "green"),
            ("Address labels (name)",          name_cnt,  "dim"),
            ("Transactions (tx\\x00)",          tx_cnt,    "cyan"),
            ("Descriptor records",             desc_cnt,  "purple"),
            ("Best block records",             bestb_cnt, "dim"),
        ]
        for label, count, color in ki_rows:
            lines.append((f"  {label:<38} : {count}\n",
                          color if count else "muted"))
        lines.append((f"\n  Total key records        : {ckey_cnt + raw_cnt}\n", "accent"))

        ver_pos = data.find(b"version\x00")
        if ver_pos != -1 and len(data) > ver_pos + 12:
            try:
                vv = struct.unpack_from("<I", data, ver_pos + 8)[0]
                lines.append((f"  Wallet version value     : {vv}\n", "accent"))
            except Exception: pass

        lines.append(("\n  CIPHER SPECIFICATIONS\n", "sub"))
        specs = [
            ("Encryption algorithm",   "AES-256-CBC"),
            ("Block size",             "128 bits (16 bytes)"),
            ("Key size",               "256 bits (32 bytes)"),
            ("Padding",                "PKCS#7"),
            ("IV derivation",          "bytes [32..47] of final SHA-512 hash"),
            ("AES key source",         "bytes [0..31] of final SHA-512 hash"),
            ("KDF algorithm",          "SHA-512 iterative (Bitcoin Core custom)"),
            ("KDF input",              "passphrase ‖ 8-byte salt"),
            ("Salt size",              "8 bytes (random, stored in mkey)"),
            ("Encrypted master key",   "48 bytes in mkey record"),
            ("Private key encryption", "ckey = AES-256-CBC(master_key, privkey)"),
            ("Validation check",       "Decrypt mkey → last 16 bytes = 0x10 (PKCS#7)"),
            ("HashCat mode",           "-m 11300  (Bitcoin/Litecoin wallet.dat)"),
            ("John the Ripper mode",   "--format=bitcoin-core"),
        ]
        for label, val in specs:
            lines.append((f"  {label:<30} : {val}\n", None))

        lines.append(("\n  HD WALLET / BIP32 DETECTION\n", "sub"))
        bip32_checks = [
            (b"\x04\x88\xad\xe4", "BIP32  xprv — extended private key (mainnet)"),
            (b"\x04\x88\xb2\x1e", "BIP32  xpub — extended public key (mainnet)"),
            (b"\x04\x9d\x78\x78", "BIP49  yprv — P2SH-P2WPKH extended priv"),
            (b"\x04\x9d\x7c\xb2", "BIP49  ypub — P2SH-P2WPKH extended pub"),
            (b"\x04\xb2\x43\x0c", "BIP84  zprv — P2WPKH extended priv"),
            (b"\x04\xb2\x47\x46", "BIP84  zpub — P2WPKH extended pub"),
            (b"\x04\x35\x83\x94", "Testnet tprv"),
            (b"\x04\x35\x87\xcf", "Testnet tpub"),
            (b"hdchain",          "HD chain record (Bitcoin Core BIP32)"),
            (b"hdseed",           "HD seed record"),
        ]
        found_bip = False
        for marker, desc in bip32_checks:
            pos = data.find(marker)
            if pos != -1:
                lines.append((f"  ✅ {desc}  @0x{pos:X}\n", "green"))
                found_bip = True
        if not found_bip:
            lines.append(("  No BIP32/HD markers found — likely legacy JBOK wallet\n", "warn"))

        lines.append(("\n  SCRIPT BYTECODE PATTERNS\n", "sub"))
        script_checks = [
            (b"\x76\xa9\x14", "P2PKH  OP_DUP OP_HASH160 <20B>"),
            (b"\xa9\x14",     "P2SH   OP_HASH160 <20B>"),
            (b"\x00\x14",     "P2WPKH OP_0 <20B> — SegWit v0 native"),
            (b"\x00\x20",     "P2WSH  OP_0 <32B> — SegWit v0 script hash"),
            (b"\x51\x20",     "P2TR   OP_1 <32B> — Taproot SegWit v1"),
            (b"\x41\x04",     "Uncompressed pubkey (65 bytes, legacy)"),
            (b"\x21\x02",     "Compressed pubkey even (33 bytes)"),
            (b"\x21\x03",     "Compressed pubkey odd (33 bytes)"),
        ]
        found_sc = False
        for pat, desc in script_checks:
            cnt = data.count(pat)
            if cnt:
                lines.append((f"  ✅ {desc:<45} ×{cnt}\n", "green"))
                found_sc = True
        if not found_sc:
            lines.append(("  No script patterns found\n", "dim"))

        result["report_sections"] = lines
        return result

    def _parse_mkey_record(self, mkey_region):
        parsed = {}
        best_score = -1
        for start in range(4, min(len(mkey_region) - 62, 68)):
            try:
                eklen = mkey_region[start]
                if eklen == 48:
                    spos = start + 1 + 48
                    if spos < len(mkey_region):
                        slen = mkey_region[spos]
                        if slen == 8:
                            ipos = spos + 1 + 8
                            if ipos + 8 <= len(mkey_region):
                                iters  = struct.unpack_from("<I", mkey_region, ipos)[0]
                                method = struct.unpack_from("<I", mkey_region, ipos + 4)[0]
                                score  = 10
                                if 10000 <= iters <= 1000000: score += 20
                                if method in (0, 1, 2):       score += 10
                                if score > best_score:
                                    best_score = score
                                    parsed["encrypted_key"] = bytes(mkey_region[start+1:start+1+48])
                                    parsed["salt"]          = bytes(mkey_region[spos+1:spos+1+8])
                                    parsed["derive_iters"]  = iters
                                    parsed["derive_method"] = method
            except Exception: continue
        if best_score < 0:
            for off in range(4, min(len(mkey_region) - 4, 200)):
                try:
                    val = struct.unpack_from("<I", mkey_region, off)[0]
                    if 10000 <= val <= 500000:
                        parsed["derive_iters"] = val
                        break
                except Exception: break
        return parsed

    def _populate_crypto_tab(self, crypto_info):
        w = self.crypto_text
        w.delete(1.0, tk.END)
        self._wi(w, "═" * 72 + "\n", "header")
        self._wi(w, "  CRYPTOGRAPHIC & KDF ANALYSIS\n", "header")
        self._wi(w, "═" * 72 + "\n\n", "header")
        for text, tag in crypto_info["report_sections"]:
            self._wi(w, text, tag)

    # ── ENTROPY ANALYSIS ──
    def _analyze_entropy(self, data):
        result = {}
        sample = data[:min(1 << 20, len(data))]
        freq   = Counter(sample)
        n      = len(sample)

        # Shannon entropy
        global_ent = -sum((c/n) * math.log2(c/n) for c in freq.values() if c > 0)
        result["global_entropy"] = global_ent

        # Chi-square
        expected = n / 256.0
        chi2 = sum((freq.get(b, 0) - expected) ** 2 / expected for b in range(256))
        result["chi2"] = chi2
        if chi2 < 220:   verdict = "Too uniform (compression artifact possible)"
        elif chi2 < 293: verdict = "Passes (random-looking data) ✅"
        elif chi2 < 500: verdict = "Mild structure detected"
        else:            verdict = "Non-random / structured data ⚠"
        result["chi2_verdict"] = verdict

        # Byte frequency
        sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        result["top_bytes"]    = sorted_freq[:10]
        result["bottom_bytes"] = sorted_freq[-10:]
        result["unique_bytes"] = len(freq)

        # Region entropy
        block_sz = max(512, len(data) // 64)
        regions  = []
        for i in range(0, len(data), block_sz):
            block = data[i:i + block_sz]
            if len(block) < 16: break
            bf  = Counter(block)
            nb  = len(block)
            ent = -sum((c/nb)*math.log2(c/nb) for c in bf.values() if c > 0)
            regions.append((i, i + len(block), ent))
        result["regions"] = regions

        # Runs test (Wald-Wolfowitz)
        bits  = [1 if b > 127 else 0 for b in sample[:2048]]
        runs  = 1 + sum(1 for i in range(1, len(bits)) if bits[i] != bits[i-1])
        nm    = len(bits)
        n1    = sum(bits)
        n0    = nm - n1
        if n0 > 0 and n1 > 0 and nm > 1:
            mu_r  = (2 * n0 * n1) / nm + 1
            sig_r = math.sqrt((2*n0*n1*(2*n0*n1 - nm)) / (nm**2 * (nm - 1)))
            z_r   = (runs - mu_r) / sig_r if sig_r > 0 else 0
        else:
            mu_r = sig_r = z_r = 0
        result["runs"]         = runs
        result["runs_mu"]      = mu_r
        result["runs_z"]       = z_r
        result["runs_verdict"] = "Passes (|z|<1.96) ✅" if abs(z_r) < 1.96 else "Fails ⚠"

        # Histogram
        result["histogram"] = self._byte_histogram(freq, n)
        return result

    def _byte_histogram(self, freq, total):
        lines = []
        lines.append("  Byte frequency histogram (16×16, each cell = 1 byte value):\n")
        lines.append("       " + "".join(f" {j:X}" for j in range(16)) + "\n")
        max_cnt = max(freq.values()) if freq else 1
        for row in range(16):
            hex_row = f"  {row:X}x   "
            for col in range(16):
                bv = row * 16 + col
                r  = freq.get(bv, 0) / max_cnt
                c  = "█" if r > 0.75 else "▓" if r > 0.5 else "▒" if r > 0.25 else "░" if r > 0.05 else "·"
                hex_row += f" {c}"
            lines.append(hex_row + "\n")
        return lines

    def _populate_entropy_tab(self, ent):
        w = self.entropy_text
        w.delete(1.0, tk.END)
        self._wi(w, "═" * 72 + "\n", "header")
        self._wi(w, "  ENTROPY & STATISTICAL ANALYSIS\n", "header")
        self._wi(w, "═" * 72 + "\n\n", "header")

        e = ent["global_entropy"]
        self._wi(w, "  GLOBAL SHANNON ENTROPY\n", "sub")
        bar = int(e / 8.0 * 40)
        ct  = "green" if e > 7.5 else "yellow" if e > 6.5 else "red"
        self._wi(w, f"  Value            : {e:.6f} bits/byte  (max 8.0)\n", ct)
        self._wi(w, f"  [{'█'*bar}{'░'*(40-bar)}]  {e/8*100:.1f}%\n", ct)
        interp = ("Very high — strongly encrypted/compressed" if e > 7.8 else
                  "High — likely encrypted" if e > 7.0 else
                  "Medium — mixed" if e > 5.5 else "Low — structured/plaintext")
        self._wi(w, f"  Interpretation   : {interp}\n\n", ct)

        self._wi(w, "  CHI-SQUARE TEST  (DOF=255)\n", "sub")
        self._wi(w, f"  Chi² statistic   : {ent['chi2']:.2f}\n", None)
        self._wi(w, f"  Verdict          : {ent['chi2_verdict']}\n",
                 "green" if "Passes" in ent["chi2_verdict"] else "warn")
        self._wi(w, f"  Reference        : p<0.05 ↔ χ²>293.2  |  p>0.95 ↔ χ²<220.0\n\n", "dim")

        self._wi(w, "  RUNS TEST  (Wald-Wolfowitz)\n", "sub")
        self._wi(w, f"  Observed runs    : {ent['runs']}\n", None)
        self._wi(w, f"  Expected runs    : {ent['runs_mu']:.1f}\n", None)
        self._wi(w, f"  Z-score          : {ent['runs_z']:.4f}\n", None)
        self._wi(w, f"  Verdict          : {ent['runs_verdict']}\n\n",
                 "green" if "Passes" in ent["runs_verdict"] else "warn")

        self._wi(w, "  BYTE STATISTICS\n", "sub")
        self._wi(w, f"  Unique byte vals : {ent['unique_bytes']} / 256  ({ent['unique_bytes']/256*100:.1f}%)\n", "accent")
        self._wi(w, f"  Top 10           : " + "  ".join(f"0x{b:02X}({c})" for b,c in ent["top_bytes"]) + "\n", "yellow")
        self._wi(w, f"  Rarest 10        : " + "  ".join(f"0x{b:02X}({c})" for b,c in ent["bottom_bytes"]) + "\n\n", "dim")

        self._wi(w, "  BYTE HISTOGRAM\n", "sub")
        for line in ent["histogram"]:
            self._wi(w, line, "dim")

        block_sz = max(512, len(self.current_data) // 64) if self.current_data else 512
        self._wi(w, f"\n  REGION ENTROPY MAP  (block size: {block_sz} bytes)\n", "sub")
        self._wi(w, "  [start offset]      [end offset]  [entropy]  [bar]\n", "dim")
        for start, end, rent in ent["regions"][:64]:
            bar2 = int(rent / 8.0 * 24)
            ct2  = "green" if rent > 7.5 else "yellow" if rent > 6.5 else "red"
            self._wi(w, f"  0x{start:08X} – 0x{end:08X}  {rent:.4f}  [{'█'*bar2}{'░'*(24-bar2)}]\n", ct2)
        if len(ent["regions"]) > 64:
            self._wi(w, f"  … {len(ent['regions'])-64} more regions …\n", "dim")

    # ── OVERVIEW ──
    def _build_overview(self, fp, data, bdb_info, crypto_info, entropy_info):
        w = self.overview_text
        path  = Path(fp)
        fsize = len(data)
        mtime = datetime.datetime.fromtimestamp(path.stat().st_mtime)
        ctime = datetime.datetime.fromtimestamp(path.stat().st_ctime)
        now   = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        def H(title):
            self._wi(w, "═" * 72 + "\n", "header")
            self._wi(w, f"  {title}\n", "header")
            self._wi(w, "═" * 72 + "\n", "header")

        def S(title):
            self._wi(w, f"\n  ── {title} " + "─" * max(0,54-len(title)) + "\n", "sub")

        def R(label, value, tag=None):
            self._wi(w, f"  {label:<30} : ", "dim")
            self._wi(w, f"{value}\n", tag)

        H("BITCOIN WALLET ANALYZER v2.0 — ANALYSIS REPORT")
        self._wi(w, f"  Generated : {now}\n\n", "dim")

        S("FILE INFORMATION")
        R("Full path",       fp)
        R("Filename",        path.name, "accent")
        R("File size",       f"{fsize:,} bytes  ({self._fmt_size(fsize)})", "accent")
        R("Last modified",   mtime.strftime("%Y-%m-%d  %H:%M:%S"))
        R("Created",         ctime.strftime("%Y-%m-%d  %H:%M:%S"))
        R("MD5",             hashlib.md5(data).hexdigest(), "dim")
        R("SHA-1",           hashlib.sha1(data).hexdigest(), "dim")
        R("SHA-256",         hashlib.sha256(data).hexdigest(), "yellow")
        R("SHA-512",         hashlib.sha512(data).hexdigest()[:64]+"…", "dim")

        S("DATABASE FORMAT")
        R("Format",          bdb_info["db_format"], "accent")
        R("Magic bytes",     data[:8].hex().upper())
        R("Is BerkeleyDB",   "YES ✅" if bdb_info["is_bdb"] else "NO", "green" if bdb_info["is_bdb"] else "warn")
        if "page_size"  in bdb_info: R("Page size",  f"{bdb_info['page_size']} bytes")
        if "last_pgno"  in bdb_info: R("Last page",  str(bdb_info["last_pgno"]))
        if "estimated_pages" in bdb_info: R("Est. pages", str(bdb_info["estimated_pages"]))
        if "version_num" in bdb_info: R("BDB version", str(bdb_info["version_num"]), "accent")
        if "byte_order"  in bdb_info: R("Byte order",  bdb_info["byte_order"])

        S("ENCRYPTION SUMMARY")
        enc = crypto_info["encrypted"]
        R("Encrypted",       "YES  ✅" if enc else "NO   ⚠  (CRITICAL — plaintext!)",
          "green" if enc else "crit")
        R("Cipher",          "AES-256-CBC")
        R("KDF",             "SHA-512 iterative (Bitcoin Core)")
        R("Salt size",       "8 bytes")
        R("Enc. key size",   "48 bytes (master key)")
        R("HashCat mode",    "-m 11300  (Bitcoin/Litecoin wallet.dat)", "yellow")
        R("John mode",       "--format=bitcoin-core", "yellow")
        mp = crypto_info.get("mkey_parsed", {})
        if mp.get("derive_iters"):
            iters = mp["derive_iters"]
            R("KDF iterations",  f"{iters:,}", "accent")
            R("Crack est. CPU",  f"~{max(1,1_000_000//iters):,} pw/s")
            R("Crack est. GPU",  f"~{max(1,100_000_000//iters):,} pw/s  (RTX-class)")
        if mp.get("salt"):
            R("Salt (hex)",      mp["salt"].hex().upper(), "yellow")

        S("KEY & RECORD COUNTS")
        for key, (desc, icon, _) in WALLET_MARKERS.items():
            k   = key.decode("latin1")
            cnt = bdb_info["marker_counts"].get(k, 0)
            if cnt:
                R(f"{icon} {desc[:28]}", str(cnt), "yellow")
        R("Total key records", str(crypto_info["key_count"]), "accent")

        S("STATISTICAL SUMMARY")
        e = entropy_info["global_entropy"]
        R("Shannon entropy",  f"{e:.6f} bits/byte", "green" if e > 7.5 else "yellow")
        R("Chi² statistic",   f"{entropy_info['chi2']:.2f} — {entropy_info['chi2_verdict']}")
        R("Runs test Z",      f"{entropy_info['runs_z']:.4f} — {entropy_info['runs_verdict']}")
        R("Unique byte vals", f"{entropy_info['unique_bytes']} / 256")

        S("RECOMMENDED NEXT STEPS")
        if enc:
            self._wi(w, "  1. Hash Extraction tab → click Extract Hash via bitcoin2john.py\n", "green")
            self._wi(w, "  2. hashcat -m 11300 hash.txt rockyou.txt\n", "yellow")
            self._wi(w, "  3. bitcoin-cli walletpassphrase \"<pw>\" 600\n", "yellow")
            self._wi(w, "  4. bitcoin-cli dumpwallet wallet_backup.txt\n", "yellow")
        else:
            self._wi(w, "  1. ⚠ CRITICAL: Transfer funds from this wallet immediately!\n", "crit")
            self._wi(w, "  2. python pywallet.py --dumpwallet --wallet=wallet.dat\n", "yellow")
            self._wi(w, "  3. bitcoin-cli dumpwallet wallet_backup.txt\n", "yellow")

        S("DONATE · Support Development")
        self._wi(w, "  ₿  BTC  : bc1qn6t8hy8memjfzp4y3sh6fvadjdtqj64vfvlx58\n", "accent")
        self._wi(w, "  Ξ  ETH  : 0x512936ca43829C8f71017aE47460820Fe703CAea\n", "blue")
        self._wi(w, "  ◎  SOL  : 6ZZrRmeGWMZSmBnQFWXG2UJauqbEgZnwb4Ly9vLYr7mi\n", "purple")
        self._wi(w, "  PayPal  : syabiz@yandex.com\n", "dim")

    # ── HEX DUMP ──
    def _build_hex(self, data, offset=0, rows=256):
        self.hex_text.delete(1.0, tk.END)
        chunk = data[offset: offset + rows * 16]
        lines = [f"{'Offset':10}  {'00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F':<50}  ASCII\n",
                 "─" * 80 + "\n"]
        for i in range(0, len(chunk), 16):
            row = chunk[i:i+16]
            addr = offset + i
            parts = []
            for j, b in enumerate(row):
                parts.append(f"{b:02X}")
                if j == 7: parts.append(" ")
            hex_str = " ".join(parts).ljust(50)
            asc = "".join(chr(b) if 32 <= b < 127 else "·" for b in row)
            lines.append(f"0x{addr:08X}  {hex_str}  {asc}\n")
        self.hex_text.insert(1.0, "".join(lines))

    def _hex_goto(self):
        if not self.current_data: return
        try:
            offset = int(self._hex_offset_var.get(), 16)
            rows   = int(self._hex_rows_var.get())
            self._build_hex(self.current_data, offset, rows)
        except ValueError: pass

    # ── ADDRESS EXTRACTION ──
    def extract_addresses(self):
        if not self.current_data:
            messagebox.showwarning("No Data", "Analyze a wallet file first!")
            return
        threading.Thread(target=self._do_extract_addresses, daemon=True).start()

    def _do_extract_addresses(self):
        data       = self.current_data
        ascii_data = data.decode("latin1", errors="ignore")
        w          = self.address_text
        w.delete(1.0, tk.END)
        self._wi(w, "═"*72+"\n", "header")
        self._wi(w, "  BITCOIN ADDRESS EXTRACTION & VALIDATION\n", "header")
        self._wi(w, "═"*72+"\n\n", "header")

        legacy_raw  = set(re.findall(r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b', ascii_data))
        bech32_raw  = set(re.findall(r'\bbc1[a-zA-Z0-9]{39,59}\b', ascii_data, re.IGNORECASE))
        testnet_raw = set(re.findall(r'\b[mn2][a-km-zA-HJ-NP-Z1-9]{25,34}\b', ascii_data))

        valid_legacy, invalid_legacy = [], []
        for addr in sorted(legacy_raw):
            ok, atype, _ = validate_base58check(addr)
            (valid_legacy if ok else invalid_legacy).append((addr, atype))

        valid_bech32, invalid_bech32 = [], []
        for addr in sorted(bech32_raw):
            ok, atype = validate_bech32(addr)
            (valid_bech32 if ok else invalid_bech32).append((addr, atype))

        valid_testnet = []
        for addr in sorted(testnet_raw):
            ok, atype, _ = validate_base58check(addr)
            if ok: valid_testnet.append((addr, atype))

        total_valid = len(valid_legacy) + len(valid_bech32) + len(valid_testnet)
        total_raw   = len(legacy_raw)   + len(bech32_raw)   + len(testnet_raw)

        self._wi(w, "  SUMMARY\n", "sub")
        self._wi(w, f"  Total patterns found     : {total_raw}\n", None)
        self._wi(w, f"  Valid (checksum ok)      : {total_valid}\n", "green")
        self._wi(w, f"  Invalid / false positive : {total_raw - total_valid}\n",
                 "warn" if total_raw - total_valid else "dim")
        self._wi(w, f"  Legacy (P2PKH/P2SH)      : {len(valid_legacy)} valid / {len(legacy_raw)} raw\n", "yellow")
        self._wi(w, f"  SegWit/Taproot (bech32)  : {len(valid_bech32)} valid / {len(bech32_raw)} raw\n", "yellow")
        self._wi(w, f"  Testnet                  : {len(valid_testnet)}\n", "blue")

        if valid_legacy:
            self._wi(w, "\n  LEGACY ADDRESSES — Base58Check VALID\n", "sub")
            for i, (addr, atype) in enumerate(valid_legacy, 1):
                self._wi(w, f"  {i:4}. ", "dim")
                self._wi(w, addr, "yellow")
                self._wi(w, f"  [{atype}]  len={len(addr)}\n", "dim")

        if valid_bech32:
            self._wi(w, "\n  BECH32 / TAPROOT ADDRESSES — Format VALID\n", "sub")
            for i, (addr, atype) in enumerate(valid_bech32, 1):
                tag = "purple" if addr.lower().startswith("bc1p") else "green"
                self._wi(w, f"  {i:4}. ", "dim")
                self._wi(w, addr, tag)
                self._wi(w, f"  [{atype}]\n", "dim")

        if valid_testnet:
            self._wi(w, "\n  TESTNET ADDRESSES\n", "sub")
            for i, (addr, atype) in enumerate(valid_testnet, 1):
                self._wi(w, f"  {i:4}. {addr}  [{atype}]\n", "blue")

        if invalid_legacy or invalid_bech32:
            self._wi(w, "\n  FAILED CHECKSUM (false positives)\n", "sub")
            for addr, reason in (invalid_legacy + invalid_bech32)[:20]:
                self._wi(w, f"  ✗  {addr}  ({reason})\n", "muted")

        if total_valid == 0:
            self._wi(w, "\n  No valid addresses found. Wallet may use HD derivation.\n", "warn")
            self._wi(w, "  Use: bitcoin-cli dumpwallet backup.txt\n", "yellow")

        self._set_status(f"[OK] {total_valid} valid addresses / {total_raw} raw patterns")

    # ── HASH EXTRACTION ──
    def use_bitcoin2john(self):
        if not self.filepath.get():
            messagebox.showwarning("No File", "Select a wallet file first!")
            return
        import subprocess
        wallet_path = self.filepath.get()
        possible = ["bitcoin2john.py", "./bitcoin2john.py",
                    os.path.join(os.getcwd(), "bitcoin2john.py"),
                    "/usr/local/bin/bitcoin2john.py", "/usr/bin/bitcoin2john.py"]
        b2j = next((p for p in possible if os.path.exists(p)), None)
        if not b2j:
            if messagebox.askyesno("Download bitcoin2john.py",
                                   "bitcoin2john.py not found.\n\nDownload from John the Ripper repo?"):
                try:
                    import urllib.request
                    url    = "https://raw.githubusercontent.com/openwall/john/bleeding-jumbo/run/bitcoin2john.py"
                    target = os.path.join(os.getcwd(), "bitcoin2john.py")
                    self._set_status("[>>] Downloading bitcoin2john.py…")
                    urllib.request.urlretrieve(url, target)
                    b2j = target
                    messagebox.showinfo("Downloaded", f"Saved:\n{target}")
                except Exception as e:
                    messagebox.showerror("Download Error", str(e))
                    return
            else: return
        try:
            self._set_status("[>>] Running bitcoin2john.py…")
            res = None
            for py in ("python3", "python"):
                try:
                    res = subprocess.run([py, b2j, wallet_path],
                                         capture_output=True, text=True, timeout=30)
                    if res.returncode == 0: break
                except FileNotFoundError: continue
            if res is None: raise RuntimeError("No Python interpreter found")
            output = res.stdout.strip()
            stderr = res.stderr.strip()
            w = self.hash_text
            w.delete(1.0, tk.END)
            self._wi(w, "═"*72+"\n", "header")
            self._wi(w, "  bitcoin2john.py — OFFICIAL HASH OUTPUT\n", "header")
            self._wi(w, "═"*72+"\n\n", "header")
            if output:
                self._wi(w, "  EXTRACTED HASH:\n\n", "sub")
                self._wi(w, "  " + output + "\n\n", "yellow")
                if "$bitcoin$" in output:
                    parts = output.split("$")
                    self._wi(w, "  HASH FIELD BREAKDOWN\n", "sub")
                    try:
                        # Format: name:$bitcoin$<mkLen>$<mkHex>$<saltLen>$<saltHex>$<iters>$<ctLen>$<ctHex>$<hLen>$<hHex>
                        # After split on $: [name:, bitcoin, mkLen, mkHex, saltLen, saltHex, iters, ctLen, ctHex, hLen, hHex]
                        p = parts
                        i0 = 1  # skip name: part
                        mk_len = p[i0+1]; mk_hex = p[i0+2]
                        sl_len = p[i0+3]; sl_hex = p[i0+4]
                        iters  = p[i0+5]; ct_len = p[i0+6]; ct_hex = p[i0+7]
                        hs_len = p[i0+8] if len(p) > i0+8 else "?"
                        hs_hex = p[i0+9] if len(p) > i0+9 else "?"
                        self._wi(w, f"  Format           : $bitcoin$ (HashCat -m 11300)\n", "accent")
                        self._wi(w, f"  mk_hex_len       : {mk_len} chars  ({int(mk_len)//2 if mk_len.isdigit() else '?'} bytes)\n", None)
                        self._wi(w, f"  mk_hex           : {mk_hex[:64]}{'…' if len(mk_hex)>64 else ''}\n", "yellow")
                        self._wi(w, f"  salt_len         : {sl_len} chars  ({int(sl_len)//2 if sl_len.isdigit() else '?'} bytes)\n", None)
                        self._wi(w, f"  salt_hex         : {sl_hex}\n", "yellow")
                        self._wi(w, f"  Iterations       : {iters}\n", "accent")
                        self._wi(w, f"  ct_len           : {ct_len}\n", None)
                        self._wi(w, f"  ct_hex           : {ct_hex[:64]}{'…' if len(ct_hex)>64 else ''}\n", "yellow")
                        self._wi(w, f"  hash_len         : {hs_len}\n", None)
                        self._wi(w, f"  hash_hex         : {hs_hex[:64]}{'…' if len(hs_hex)>64 else ''}\n", "yellow")
                        try:
                            iv = int(iters)
                            self._wi(w, f"\n  KDF iterations   : {iv:,}\n", "accent")
                            self._wi(w, f"  Crack estimate   : {self._crack_speed_est(iv)}\n", "yellow")
                        except Exception: pass
                    except Exception as ex:
                        self._wi(w, f"  [Parse error: {ex}]\n", "red")
                self._wi(w, "\n  ✅  hashcat -m 11300 hash.txt wordlist.txt\n", "green")
            else:
                self._wi(w, f"  No output. stderr:\n  {stderr}\n", "warn")
                if "unencrypted" in stderr.lower():
                    self._wi(w, "\n  ⚠  Wallet appears NOT encrypted.\n", "crit")
            self._set_status("[OK] Hash extracted!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ── JSON EXPORT ──
    def export_json(self):
        if not self.analysis_result:
            messagebox.showwarning("No Analysis", "Run analysis first!")
            return
        fn = filedialog.asksaveasfilename(
            defaultextension=".json", initialfile="wallet_analysis.json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if fn:
            with open(fn, "w", encoding="utf-8") as fh:
                json.dump(self.analysis_result, fh, indent=2, default=str)
            self._set_status(f"[OK] JSON exported: {fn}")

    # ── HELPERS ──
    def _fmt_size(self, n):
        if n < 1024: return f"{n} B"
        elif n < 1024**2: return f"{n/1024:.2f} KB"
        else: return f"{n/1024**2:.2f} MB"

    def _crack_speed_est(self, iters):
        cpu = max(1, 1_000_000 // iters)
        gpu = max(1, 100_000_000 // iters)
        return f"~{cpu:,} pw/s on CPU  /  ~{gpu:,} pw/s on RTX GPU"

    def _extract_strings(self, data, min_len=8):
        result, cur = [], []
        for b in data:
            if 32 <= b < 127: cur.append(chr(b))
            else:
                if len(cur) >= min_len: result.append("".join(cur))
                cur = []
        if len(cur) >= min_len: result.append("".join(cur))
        return result

    def _copy(self, widget):
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(widget.get(1.0, tk.END))
            self._set_status("[OK] Copied to clipboard")
        except Exception as e: messagebox.showerror("Error", str(e))

    def _save(self, widget, default="report.txt"):
        try:
            fn = filedialog.asksaveasfilename(
                defaultextension=".txt", initialfile=default,
                filetypes=[("Text files","*.txt"),("All files","*.*")])
            if fn:
                with open(fn,"w",encoding="utf-8") as fh:
                    fh.write(widget.get(1.0, tk.END))
                self._set_status(f"[OK] Saved: {fn}")
        except Exception as e: messagebox.showerror("Error", str(e))

    def save_hash(self):
        content = self.hash_text.get(1.0, tk.END)
        if "$bitcoin$" not in content:
            messagebox.showwarning("No Hash","Extract a hash first!")
            return
        hash_line = next((l.strip() for l in content.splitlines() if "$bitcoin$" in l), "")
        fn = filedialog.asksaveasfilename(
            defaultextension=".txt", initialfile="bitcoin_hash.txt",
            filetypes=[("Text files","*.txt"),("All files","*.*")])
        if fn:
            with open(fn,"w") as fh: fh.write(hash_line+"\n")
            self._set_status(f"[OK] Hash saved: {fn}")
            messagebox.showinfo("Saved",f"Hash saved:\n{fn}\n\nhashcat -m 11300 {fn} wordlist.txt")

    def save_addresses(self):
        self._save(self.address_text, "bitcoin_addresses.txt")

    # ── STATIC CONTENT ──
    def _show_crack_instructions(self):
        w = self.crack_text
        lines = [
            ("  HASHCAT — GPU ACCELERATED  (recommended)\n", "sub"),
            ("  Mode : -m 11300  (Bitcoin/Litecoin wallet.dat)\n\n", "accent"),
            ("  1. Dictionary attack\n", "yellow"),
            ("     hashcat -m 11300 hash.txt rockyou.txt\n\n", None),
            ("  2. Dictionary + rules\n", "yellow"),
            ("     hashcat -m 11300 hash.txt rockyou.txt -r rules/best64.rule\n\n", None),
            ("  3. Brute-force all printable, up to 8 chars\n", "yellow"),
            ("     hashcat -m 11300 hash.txt -a 3 ?a?a?a?a?a?a?a?a\n\n", None),
            ("  4. Mask: lowercase+digits, 6-9 chars\n", "yellow"),
            ("     hashcat -m 11300 hash.txt -a 3 --increment ?l?l?l?l?d?d?d?d?d\n\n", None),
            ("  5. Combinator: two wordlists\n", "yellow"),
            ("     hashcat -m 11300 hash.txt -a 1 words1.txt words2.txt\n\n", None),
            ("  Resume: hashcat --restore    Status: 's'\n\n", "dim"),
            ("  JOHN THE RIPPER — CPU\n", "sub"),
            ("  john --format=bitcoin-core hash.txt --wordlist=wordlist.txt\n", None),
            ("  john --restore\n", None),
            ("  john --show hash.txt\n\n", None),
            ("  WORDLISTS\n", "sub"),
            ("  rockyou.txt   — 14M passwords\n", "yellow"),
            ("  CrackStation  — 15 GB  https://crackstation.net\n", "yellow"),
            ("  SecLists      — https://github.com/danielmiessler/SecLists\n", "yellow"),
            ("  Custom words  — satoshi bitcoin hodl btc moon 2010..2023\n\n", "green"),
            ("  ⚠  Only crack wallets you own or have explicit written permission.\n", "crit"),
        ]
        for text, tag in lines:
            self._wi(w, text, tag)

    def _show_recovery_guide(self):
        w = self.recovery_text
        sections = [
            ("═"*72+"\n  BITCOIN WALLET RECOVERY GUIDE — v2.0\n"+"═"*72+"\n\n", "header"),
            ("  SCENARIO A: Encrypted wallet (mkey present)\n", "sub"),
            ("  1. Hash Extraction tab → Extract Hash via bitcoin2john.py\n", None),
            ("  2. hashcat -m 11300 hash.txt rockyou.txt\n", "yellow"),
            ("  3. bitcoin-cli walletpassphrase \"<pw>\" 600\n", "yellow"),
            ("  4. bitcoin-cli dumpwallet \"/safe/backup.txt\"\n\n", "yellow"),
            ("  SCENARIO B: Unencrypted wallet (no mkey — CRITICAL)\n", "sub"),
            ("  ⚠  DO NOT connect to internet until keys are secured!\n", "crit"),
            ("  1. python pywallet.py --dumpwallet --wallet=wallet.dat\n", "yellow"),
            ("  2. bitcoin-cli dumpwallet \"/safe/backup.txt\"\n\n", "yellow"),
            ("  SCENARIO C: HD / Descriptor wallet (Core ≥ 0.21)\n", "sub"),
            ("  1. bitcoin-wallet -wallet=wallet.dat info\n", "yellow"),
            ("  2. bitcoin-wallet -wallet=wallet.dat dump\n", "yellow"),
            ("  3. bitcoin-cli listdescriptors\n\n", "yellow"),
            ("  SCENARIO D: Corrupt wallet\n", "sub"),
            ("  1. bitcoin-cli -salvagewallet -wallet=wallet.dat\n", "yellow"),
            ("  2. BTCRecover: https://github.com/gurnec/btcrecover\n\n", "yellow"),
            ("  WALLET RECORD REFERENCE\n", "sub"),
            ("  mkey   — Master key encrypted with passphrase (AES-256-CBC)\n", "yellow"),
            ("  ckey   — Encrypted private key (AES-256-CBC with master key)\n", "yellow"),
            ("  key    — Plaintext private key ⚠  EXTREMELY DANGEROUS\n", "red"),
            ("  wkey   — Watch-only key (public key, no spending power)\n", None),
            ("  pool   — Pre-generated key pool (privacy buffer)\n", None),
            ("  tx     — Raw transaction data\n", None),
            ("  hdchain— BIP32 HD derivation chain metadata\n", None),
            ("  hdseed — BIP32 HD master seed\n", None),
            ("  keymeta— Key metadata: birth time, HD path\n", None),
            ("  version— Wallet version integer\n\n", None),
            ("  TOOLS\n", "sub"),
            ("  PyWallet     : https://github.com/jackjack-jj/pywallet\n",    "blue"),
            ("  BTCRecover   : https://github.com/gurnec/btcrecover\n",       "blue"),
            ("  Bitcoin Core : https://bitcoin.org/en/download\n",            "blue"),
            ("  HashCat      : https://hashcat.net\n",                        "blue"),
            ("  John t.R.    : https://www.openwall.com/john/\n\n",           "blue"),
            ("  DONATE\n", "sub"),
            ("  ₿  BTC  : bc1qn6t8hy8memjfzp4y3sh6fvadjdtqj64vfvlx58\n", "accent"),
            ("  Ξ  ETH  : 0x512936ca43829C8f71017aE47460820Fe703CAea\n",   "blue"),
            ("  ◎  SOL  : 6ZZrRmeGWMZSmBnQFWXG2UJauqbEgZnwb4Ly9vLYr7mi\n","purple"),
            ("  PayPal  : syabiz@yandex.com\n\n",                          "dim"),
            ("═"*72+"\n  Made with ❤  — by Syabiz  |  Use only on wallets you own.\n"+"═"*72+"\n", "header"),
        ]
        for text, tag in sections:
            self._wi(w, text, tag)


def main():
    root = tk.Tk()
    app  = BitcoinWalletAnalyzer(root)
    root.update_idletasks()
    w, h = root.winfo_width(), root.winfo_height()
    x    = (root.winfo_screenwidth()  - w) // 2
    y    = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.mainloop()


if __name__ == "__main__":
    main()
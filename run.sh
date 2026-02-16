#!/bin/bash
# Bitcoin Wallet Analyzer - Quick Launcher
# Script untuk menjalankan aplikasi dengan mudah

echo "=========================================="
echo "  Bitcoin Wallet Analyzer - GUI"
echo "=========================================="
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 tidak ditemukan!"
    echo "   Install Python 3 terlebih dahulu"
    exit 1
fi

echo "✓ Python 3 ditemukan"

# Check tkinter
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ tkinter tidak ditemukan!"
    echo "   Install dengan: sudo apt-get install python3-tk"
    exit 1
fi

echo "✓ tkinter tersedia"

# Check numpy (optional)
python3 -c "import numpy" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ numpy tersedia (analisis advanced aktif)"
else
    echo "⚠️  numpy tidak ditemukan (opsional)"
    echo "   Install dengan: pip3 install numpy"
fi

echo ""
echo "🚀 Menjalankan Bitcoin Wallet Analyzer..."
echo ""

# Run the application
python3 bitcoin_wallet_analyzer_gui.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Error menjalankan aplikasi!"
    echo "   Pastikan file bitcoin_wallet_analyzer_gui.py ada"
    exit 1
fi

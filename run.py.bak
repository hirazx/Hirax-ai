#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Tambahkan path ke sys.path
sys.path.insert(0, str(Path(__file__).parent))

# Import dan jalankan
from backend.main import app
import uvicorn

def check_model():
    """Cek apakah model GGUF tersedia"""
    import glob
    model_files = glob.glob("models/*.gguf")
    
    if not model_files:
        print("""
╔══════════════════════════════════════════════════════════════╗
║  ⚠️  MODEL GGUF TIDAK DITEMUKAN!                           ║
║                                                             ║
║  Tempatkan file model .gguf di folder:                     ║
║  models/                                                   ║
║                                                             ║
║  Aplikasi tetap jalan dengan mode mock (tanpa AI)          ║
╚══════════════════════════════════════════════════════════════╝
        """)
    else:
        model_file = model_files[0]
        size_gb = Path(model_file).stat().st_size / (1024**3)
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║  ✅ MODEL GEMMA DITEMUKAN!                                  ║
║  File: {Path(model_file).name}                           ║
║  Size: {size_gb:.2f} GB                                    ║
║                                                             ║
║  Memuat model... (butuh beberapa detik)                    ║
╚══════════════════════════════════════════════════════════════╝
        """)

if __name__ == "__main__":
    check_model()
    
    print("""
    ╔══════════════════════════════════════════╗
    ║  🤖 HIRAX AI - FULL OFFLINE EDITION     ║
    ║  Model: Gemma-4-E4B                     ║
    ║  Mode: 100% OFFLINE                     ║
    ║  Port: 8080                             ║
    ║  http://localhost:8080                  ║
    ╚══════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8080,
        log_level="info"
    )
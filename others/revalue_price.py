"""
reprice_themes.py — Ganti harga semua tema sekaligus
=====================================================
Cara pakai:
  1. Letakkan file ini di folder yang sama dengan folder 'themes/'
  2. Edit bagian KONFIGURASI HARGA di bawah sesuai keinginan
  3. Jalankan: python reprice_themes.py
"""

import json
import os
import glob
import shutil
from datetime import datetime

# ─────────────────────────────────────────────────
#  KONFIGURASI HARGA — Edit bagian ini
# ─────────────────────────────────────────────────

NEW_PRICE          = 60000          # Harga promo (angka, tanpa titik)
NEW_PRICE_LABEL    = "Rp 60.000"    # Label yang tampil di UI
NEW_PRICE_ORIGINAL = 149000         # Harga coret (angka)
NEW_PRICE_NOTE     = ""             # Catatan harga, kosongkan jika tidak ada

# ─────────────────────────────────────────────────
#  KONFIGURASI FOLDER
# ─────────────────────────────────────────────────

THEMES_DIR = "themes"               # Folder tema relatif dari lokasi script
BACKUP_DIR = "themes_backup"        # Folder backup otomatis sebelum diubah

# ─────────────────────────────────────────────────
#  SCRIPT (tidak perlu diedit)
# ─────────────────────────────────────────────────

def backup_themes():
    """Backup semua file sebelum diubah."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{BACKUP_DIR}_{timestamp}"
    shutil.copytree(THEMES_DIR, backup_path)
    print(f"✅ Backup disimpan di: {backup_path}/")
    return backup_path

def reprice_all():
    json_files = sorted(glob.glob(os.path.join(THEMES_DIR, "*.json")))

    if not json_files:
        print(f"❌ Tidak ada file .json di folder '{THEMES_DIR}/'")
        print(f"   Pastikan script ini dijalankan dari folder yang benar.")
        return

    # Backup dulu sebelum apapun diubah
    backup_path = backup_themes()

    success, failed = [], []

    for filepath in json_files:
        filename = os.path.basename(filepath)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Update harga
            data["price"]          = NEW_PRICE
            data["price_label"]    = NEW_PRICE_LABEL
            data["price_original"] = NEW_PRICE_ORIGINAL
            data["price_note"]     = NEW_PRICE_NOTE

            # Tulis kembali dengan format rapi (indent 2)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")  # newline di akhir file

            success.append(filename)

        except json.JSONDecodeError as e:
            failed.append((filename, f"JSON tidak valid: {e}"))
        except Exception as e:
            failed.append((filename, str(e)))

    # Laporan hasil
    print(f"\n{'='*50}")
    print(f"  HASIL REPRICE — {len(json_files)} tema")
    print(f"{'='*50}")
    print(f"✅ Berhasil  : {len(success)} file")
    if failed:
        print(f"❌ Gagal     : {len(failed)} file")
    print(f"\nHarga baru   : {NEW_PRICE_LABEL}")
    print(f"Harga coret  : Rp {NEW_PRICE_ORIGINAL:,}".replace(",", "."))
    print(f"\nFile yang diubah:")
    for name in success:
        print(f"  • {name}")
    if failed:
        print(f"\nFile yang GAGAL (cek manual):")
        for name, err in failed:
            print(f"  ✗ {name} → {err}")
    print(f"\n💾 Backup tersimpan di: {backup_path}/")
    print("Selesai!")

if __name__ == "__main__":
    reprice_all()

#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  compress.sh — Image Optimizer UndanganKita
#  Aman dijalankan berulang — file yang sudah dicompress di-SKIP
#  Usage: bash compress.sh
# ═══════════════════════════════════════════════════════════════

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
HASH_FILE="$APP_DIR/.compressed_hashes"  # rekam file yang sudah dicompress

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC}   $1"; }
skip()    { echo -e "${YELLOW}[SKIP]${NC} $1"; }

# Cek imagemagick
if ! command -v convert &>/dev/null; then
    echo "imagemagick tidak ditemukan. Install dulu:"
    echo "  sudo apt install -y imagemagick"
    exit 1
fi

# Load hash list yang sudah dicompress
touch "$HASH_FILE"

compressed=0
skipped=0

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}   Image Optimizer — UndanganKita${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo ""

BEFORE_SIZE=$(du -sh "$APP_DIR/static/" 2>/dev/null | cut -f1)
info "Ukuran sebelum: $BEFORE_SIZE"
echo ""

# ── Compress JPG ────────────────────────────────────────────────
find "$APP_DIR/static/themes/" "$APP_DIR/static/demo-photos/" \
    \( -name "*.jpg" -o -name "*.jpeg" \) 2>/dev/null | sort | while read f; do

    # Skip file < 80KB — sudah kecil, tidak perlu compress
    size=$(stat -c%s "$f" 2>/dev/null || echo 0)
    if [ "$size" -lt 81920 ]; then
        skip "$(basename $f) — sudah kecil ($(( size/1024 ))KB), skip"
        continue
    fi

    # Cek hash — kalau sudah pernah dicompress dengan ukuran ini, skip
    hash=$(md5sum "$f" 2>/dev/null | cut -d' ' -f1)
    if grep -q "^$hash$" "$HASH_FILE" 2>/dev/null; then
        skip "$(basename $f) — sudah dicompress sebelumnya, skip"
        continue
    fi

    # Compress
    before=$(stat -c%s "$f")
    convert "$f" -strip -quality 82 -resize "1200x>" "$f" 2>/dev/null
    after=$(stat -c%s "$f")

    # Simpan hash BARU setelah compress
    new_hash=$(md5sum "$f" 2>/dev/null | cut -d' ' -f1)
    echo "$new_hash" >> "$HASH_FILE"

    saved=$(( (before - after) / 1024 ))
    success "$(basename $f) — hemat ${saved}KB ($(( before/1024 ))KB → $(( after/1024 ))KB)"
    echo $((compressed + 1)) > /tmp/compress_count
done

# ── Compress PNG ─────────────────────────────────────────────────
find "$APP_DIR/static/themes/" -name "*.png" 2>/dev/null | sort | while read f; do
    size=$(stat -c%s "$f" 2>/dev/null || echo 0)
    if [ "$size" -lt 81920 ]; then
        skip "$(basename $f) — sudah kecil ($(( size/1024 ))KB), skip"
        continue
    fi

    hash=$(md5sum "$f" 2>/dev/null | cut -d' ' -f1)
    if grep -q "^$hash$" "$HASH_FILE" 2>/dev/null; then
        skip "$(basename $f) — sudah dicompress sebelumnya, skip"
        continue
    fi

    before=$(stat -c%s "$f")
    convert "$f" -strip "$f" 2>/dev/null
    after=$(stat -c%s "$f")

    new_hash=$(md5sum "$f" 2>/dev/null | cut -d' ' -f1)
    echo "$new_hash" >> "$HASH_FILE"

    saved=$(( (before - after) / 1024 ))
    success "$(basename $f) — hemat ${saved}KB"
done

# Bersihkan duplikat di hash file
sort -u "$HASH_FILE" -o "$HASH_FILE"

echo ""
AFTER_SIZE=$(du -sh "$APP_DIR/static/" 2>/dev/null | cut -f1)
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo -e "  Sebelum : $BEFORE_SIZE"
echo -e "  Sesudah : $AFTER_SIZE"
echo -e "${GREEN}  Selesai! Aman dijalankan lagi kapanpun.${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo ""
echo "  File yang sudah dicompress dicatat di: .compressed_hashes"
echo "  Hapus file itu kalau mau force compress ulang semua."
echo ""

#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  compress.sh — Image Optimizer UndanganKita
#  • Semua JPG/JPEG/PNG → diconvert ke WebP in-place
#    (ekstensi tetap .jpg/.png — tidak perlu edit HTML/template)
#  • Recursive — semua subfolder static/themes/ & static/demo-photos/
#  • uploads/ di-SKIP — foto user tidak disentuh
#  • Aman dijalankan berulang — file yang sudah diproses di-skip via hash
#  Usage: bash compress.sh
# ═══════════════════════════════════════════════════════════════

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
HASH_FILE="$APP_DIR/.compressed_hashes"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; RED='\033[0;31m'; NC='\033[0m'
info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC}   $1"; }
skip()    { echo -e "${YELLOW}[SKIP]${NC} $1"; }
warn()    { echo -e "${RED}[WARN]${NC} $1"; }

# ── Cek tools ───────────────────────────────────────────────────
MISSING=0
if ! command -v cwebp &>/dev/null; then
    warn "cwebp tidak ditemukan."
    MISSING=1
fi
if ! command -v convert &>/dev/null; then
    warn "imagemagick tidak ditemukan."
    MISSING=1
fi
if [ "$MISSING" -eq 1 ]; then
    echo ""
    echo "Install dulu:"
    echo "  sudo apt install -y imagemagick webp   # Linux/VPS"
    echo "  pkg install imagemagick libwebp        # Termux"
    exit 1
fi

touch "$HASH_FILE"

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}   Image Optimizer — UndanganKita${NC}"
echo -e "${GREEN}   WebP in-place (ekstensi tetap)${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo ""

BEFORE_SIZE=$(du -sh "$APP_DIR/static/" 2>/dev/null | cut -f1)
info "Ukuran sebelum : $BEFORE_SIZE"
info "Folder uploads : SKIP (foto user tidak disentuh)"
echo ""

# ── Fungsi compress satu file → WebP in-place ───────────────────
compress_file() {
    local f="$1"
    local min_size="$2"  # skip kalau lebih kecil dari ini (bytes)

    # Skip folder uploads — foto user tidak boleh disentuh
    if [[ "$f" == *"/uploads/"* ]]; then
        return
    fi

    # Skip file kecil
    local size
    size=$(stat -c%s "$f" 2>/dev/null || echo 0)
    if [ "$size" -lt "$min_size" ]; then
        skip "$(basename $f) — $(( size/1024 ))KB, skip"
        return
    fi

    # Skip kalau sudah pernah dicompress (hash match)
    local hash
    hash=$(md5sum "$f" 2>/dev/null | cut -d' ' -f1)
    if grep -q "^$hash$" "$HASH_FILE" 2>/dev/null; then
        skip "$(basename $f) — sudah dicompress, skip"
        return
    fi

    local before=$size
    local tmp="${f}.webp.tmp"
    local ext="${f##*.}"
    local ok=0

    # Convert ke WebP, simpan ke tmp dulu
    if [[ "${ext,,}" == "png" ]]; then
        # PNG — preserve transparency, lossless jika transparan
        cwebp -q 85 -mt "$f" -o "$tmp" 2>/dev/null && ok=1
    else
        # JPG/JPEG — lossy WebP, resize max 1200px wide
        convert "$f" -strip -resize "1200x>" /tmp/_ck_mid.jpg 2>/dev/null
        cwebp -q 82 -mt /tmp/_ck_mid.jpg -o "$tmp" 2>/dev/null && ok=1
        rm -f /tmp/_ck_mid.jpg
    fi

    if [ "$ok" -eq 1 ] && [ -f "$tmp" ]; then
        local after
        after=$(stat -c%s "$tmp")

        # Hanya replace kalau hasilnya lebih kecil
        if [ "$after" -lt "$before" ]; then
            mv "$tmp" "$f"
            local saved=$(( (before - after) / 1024 ))
            success "$(basename $f) — ${saved}KB hemat ($(( before/1024 ))KB → $(( after/1024 ))KB)"
        else
            rm -f "$tmp"
            skip "$(basename $f) — WebP tidak lebih kecil, pakai original"
        fi
    else
        rm -f "$tmp"
        warn "$(basename $f) — gagal convert, skip"
    fi

    # Catat hash file hasil (apapun hasilnya) biar tidak diproses lagi
    local new_hash
    new_hash=$(md5sum "$f" 2>/dev/null | cut -d' ' -f1)
    echo "$new_hash" >> "$HASH_FILE"
}

# ── JPG/JPEG — themes + demo-photos ─────────────────────────────
info "Compress JPG → WebP in-place..."
while IFS= read -r -d '' f; do
    compress_file "$f" 81920   # skip < 80KB
done < <(find "$APP_DIR/static/themes/" "$APP_DIR/static/demo-photos/" \
    \( -name "*.jpg" -o -name "*.jpeg" \) -not -path "*/uploads/*" \
    -print0 2>/dev/null)

echo ""

# ── PNG — themes only (assets dekoratif) ────────────────────────
info "Compress PNG → WebP in-place..."
while IFS= read -r -d '' f; do
    compress_file "$f" 40960   # skip < 40KB
done < <(find "$APP_DIR/static/themes/" \
    -name "*.png" -not -path "*/uploads/*" \
    -print0 2>/dev/null)

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
echo "  • File terproses dicatat di : .compressed_hashes"
echo "  • Hapus .compressed_hashes  : force compress ulang semua"
echo "  • Folder uploads            : tidak disentuh sama sekali"
echo ""

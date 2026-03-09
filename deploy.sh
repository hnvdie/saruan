#!/bin/bash
# ═══════════════════════════════════════════════════════════════
#  UndanganKita v3 — One-Click Deploy Script
#  Usage: bash deploy.sh
#  Aman dijalankan ulang (idempotent) — migrasi hosting juga oke
# ═══════════════════════════════════════════════════════════════

set -e  # stop kalau ada error

# ── KONFIGURASI — sesuaikan sebelum pertama kali run ────────────
APP_DIR="$(cd "$(dirname "$0")" && pwd)"   # otomatis path folder ini
APP_USER="$(whoami)"
DOMAIN="habarkita.com"                     # ← ganti domain kamu
DOMAIN_WWW="www.habarkita.com"             # ← atau kosongkan kalau tidak pakai www
PORT="5000"
WORKERS="2"
# ────────────────────────────────────────────────────────────────

# Warna output
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'
info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC}   $1"; }
warn()    { echo -e "${YELLOW}[WARN]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}   UndanganKita v3 — Deploy Script${NC}"
echo -e "${GREEN}   Domain : ${DOMAIN}${NC}"
echo -e "${GREEN}   Dir    : ${APP_DIR}${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo ""

# ── 1. SYSTEM DEPENDENCIES ──────────────────────────────────────
info "Install system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y -qq python3 python3-pip nginx certbot python3-certbot-nginx openssl curl imagemagick
success "System dependencies OK"

# ── 2. PYTHON DEPENDENCIES ──────────────────────────────────────
info "Install Python dependencies..."
pip install --quiet flask werkzeug gunicorn python-dotenv --break-system-packages --ignore-installed
GUNICORN_BIN=$(which gunicorn)
success "Python dependencies OK — gunicorn: $GUNICORN_BIN"

# ── 3. SETUP .env ───────────────────────────────────────────────
info "Cek .env..."
if [ ! -f "$APP_DIR/.env" ]; then
    if [ -f "$APP_DIR/.env.example" ]; then
        cp "$APP_DIR/.env.example" "$APP_DIR/.env"
        warn ".env dibuat dari .env.example — WAJIB isi SECRET_KEY & ADMIN_PW_HASH sebelum lanjut!"
        warn "Edit: nano $APP_DIR/.env"
        warn "Lalu jalankan script ini lagi."
        exit 1
    else
        error ".env dan .env.example tidak ditemukan di $APP_DIR"
    fi
fi

# Cek SECRET_KEY sudah diisi
source "$APP_DIR/.env" 2>/dev/null || true
if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "ganti_ini_dengan_random_hex_panjang_minimal_64_karakter" ]; then
    warn "SECRET_KEY belum di-set di .env!"
    NEW_KEY=$(python3 -c "import secrets; print(secrets.token_hex(64))")
    sed -i "s|SECRET_KEY=.*|SECRET_KEY=$NEW_KEY|" "$APP_DIR/.env"
    success "SECRET_KEY di-generate otomatis dan disimpan ke .env"
fi

chmod 600 "$APP_DIR/.env"
success ".env OK"

# ── 4. INIT DATABASE ─────────────────────────────────────────────
info "Init database..."
mkdir -p "$APP_DIR/data"
cd "$APP_DIR"
python3 -c "from app import init_db; init_db()"
success "Database OK — $(ls -lh $APP_DIR/data/undangan.db | awk '{print $5}')"

# ── 5. BACKUP DATABASE HARIAN ───────────────────────────────────
info "Backup database..."
if [ -f "$APP_DIR/data/undangan.db" ]; then
    cp "$APP_DIR/data/undangan.db" "$APP_DIR/data/undangan.db.backup"
    success "Backup → data/undangan.db.backup (timpa terbaru)"
fi

# Setup cron backup harian — timpa file yang sama tiap hari
CRON_JOB="0 3 * * * cp $APP_DIR/data/undangan.db $APP_DIR/data/undangan.db.backup"
( crontab -l 2>/dev/null | grep -v "undangan.db.backup" ; echo "$CRON_JOB" ) | crontab -
success "Cron backup harian jam 03:00 — data/undangan.db.backup"

# ── 6. FOLDER STRUCTURE ─────────────────────────────────────────
info "Siapkan folder..."
mkdir -p "$APP_DIR/logs"
mkdir -p "$APP_DIR/static/uploads/invitations"
mkdir -p "$APP_DIR/static/demo-photos/individual"
chmod -R 755 "$APP_DIR/static"
# Beri nginx akses ke /root kalau deploy sebagai root
if [ "$APP_USER" = "root" ]; then
    chmod o+x /root
fi
success "Folder OK"

# ── 7. SSL DUMMY CERT (block scanner via IP) ────────────────────
info "Setup SSL dummy cert..."
if [ ! -f /etc/nginx/ssl/dummy.crt ]; then
    sudo mkdir -p /etc/nginx/ssl
    sudo openssl req -x509 -nodes -newkey rsa:2048 -days 3650 \
        -keyout /etc/nginx/ssl/dummy.key \
        -out    /etc/nginx/ssl/dummy.crt \
        -subj   "/CN=dummy" 2>/dev/null
    success "Dummy cert dibuat"
else
    success "Dummy cert sudah ada, skip"
fi

# ── 8. NGINX CONFIG ─────────────────────────────────────────────
info "Setup Nginx..."

# Tambah rate limit zone ke nginx.conf kalau belum ada
if ! grep -q "zone=rsvp" /etc/nginx/nginx.conf; then
    sudo sed -i '/http {/a\\t# Rate limiting — UndanganKita\n\tlimit_req_zone $binary_remote_addr zone=rsvp:10m rate=5r\/m;\n\tlimit_req_zone $binary_remote_addr zone=general:10m rate=30r\/m;' /etc/nginx/nginx.conf
    success "Rate limit zone ditambah ke nginx.conf"
else
    success "Rate limit zone sudah ada, skip"
fi

# Generate nginx site config dari template
STATIC_PATH="$APP_DIR/static"
sudo tee /etc/nginx/sites-available/undangankita > /dev/null << NGINXCONF
# ── Block akses langsung via IP (anti-Shodan/scanner) ──────────
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;
    return 444;
}
server {
    listen 443 ssl default_server;
    listen [::]:443 ssl default_server;
    server_name _;
    ssl_certificate     /etc/nginx/ssl/dummy.crt;
    ssl_certificate_key /etc/nginx/ssl/dummy.key;
    return 444;
}

# ── HTTP → HTTPS redirect ───────────────────────────────────────
server {
    listen 80;
    server_name ${DOMAIN} ${DOMAIN_WWW};
    return 301 https://\$host\$request_uri;
}

# ── Server utama ────────────────────────────────────────────────
server {
    listen 443 ssl http2;
    server_name ${DOMAIN} ${DOMAIN_WWW};

    # SSL — akan di-replace otomatis oleh Certbot
    ssl_certificate     /etc/nginx/ssl/dummy.crt;
    ssl_certificate_key /etc/nginx/ssl/dummy.key;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;
    ssl_session_cache   shared:SSL:10m;

    server_tokens off;

    # Security headers
    add_header X-Frame-Options           "SAMEORIGIN"   always;
    add_header X-Content-Type-Options    "nosniff"      always;
    add_header X-XSS-Protection          "1; mode=block" always;
    add_header Referrer-Policy           "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;

    # Block file sensitif
    location ~ /\\.  { deny all; return 404; }
    location ~ \\.(env|db|sqlite|sqlite3|log|sh|py|cfg|ini|bak|sql)\$ { deny all; return 404; }
    location ^~ /data/  { deny all; return 404; }
    location ^~ /.git/  { deny all; return 404; }

    # Upload limit
    client_max_body_size 20M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/javascript application/json
               image/svg+xml image/jpeg image/png image/webp audio/mpeg;
    gzip_min_length 1024;

    # Static files langsung dari Nginx
    location /static/ {
        alias ${STATIC_PATH}/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # RSVP — rate limit ketat
    location /rsvp/ {
        limit_req zone=rsvp burst=3 nodelay;
        proxy_pass http://127.0.0.1:${PORT};
        include /etc/nginx/proxy_params;
    }

    # Semua route lain
    location / {
        limit_req zone=general burst=20 nodelay;
        proxy_pass         http://127.0.0.1:${PORT};
        proxy_set_header   Host \$host;
        proxy_set_header   X-Real-IP \$remote_addr;
        proxy_set_header   X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto \$scheme;
        proxy_read_timeout 60;
    }
}
NGINXCONF

# Enable site, hapus default
sudo ln -sf /etc/nginx/sites-available/undangankita /etc/nginx/sites-enabled/undangankita
sudo rm -f /etc/nginx/sites-enabled/default

# Test config
sudo nginx -t || error "Nginx config error — cek output di atas"
sudo systemctl restart nginx
success "Nginx OK"

# ── 9. SYSTEMD SERVICE ──────────────────────────────────────────
info "Setup systemd service..."

sudo tee /etc/systemd/system/habarkita.service > /dev/null << SERVICECONF
[Unit]
Description=UndanganKita v3 — Flask Wedding Invitation App
After=network.target

[Service]
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${APP_DIR}

ExecStart=${GUNICORN_BIN} \\
    --workers ${WORKERS} \\
    --bind 127.0.0.1:${PORT} \\
    --timeout 60 \\
    --access-logfile ${APP_DIR}/logs/access.log \\
    --error-logfile  ${APP_DIR}/logs/error.log \\
    app:app

Restart=always
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
SERVICECONF

sudo systemctl daemon-reload
sudo systemctl enable habarkita
sudo systemctl restart habarkita
sleep 2

# Verifikasi Flask jalan
if curl -sf http://127.0.0.1:$PORT > /dev/null; then
    success "Gunicorn jalan di port $PORT"
else
    warn "Gunicorn belum response — cek: journalctl -u habarkita -n 20"
fi
success "Service habarkita OK"

# ── 10. SSL LET'S ENCRYPT ───────────────────────────────────────
echo ""
info "Setup SSL Let's Encrypt..."

# Cek apakah domain sudah pointing ke server ini
SERVER_IP=$(curl -sf https://api.ipify.org 2>/dev/null || echo "unknown")
DOMAIN_IP=$(dig +short $DOMAIN 2>/dev/null | tail -1 || echo "unknown")

if [ "$SERVER_IP" = "$DOMAIN_IP" ] && [ "$SERVER_IP" != "unknown" ]; then
    info "Domain $DOMAIN → $DOMAIN_IP ✓ (match server IP)"
    info "Memulai Certbot..."
    if [ -n "$DOMAIN_WWW" ]; then
        sudo certbot --nginx -d "$DOMAIN" -d "$DOMAIN_WWW" --non-interactive --agree-tos --register-unsafely-without-email --redirect
    else
        sudo certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --register-unsafely-without-email --redirect
    fi
    sudo systemctl restart nginx
    success "SSL Let's Encrypt OK — https://$DOMAIN aktif"
else
    warn "Domain $DOMAIN belum pointing ke server ini (server: $SERVER_IP, domain: $DOMAIN_IP)"
    warn "SSL Let's Encrypt dilewati — jalankan manual setelah domain pointing:"
    warn "  sudo certbot --nginx -d $DOMAIN -d $DOMAIN_WWW"
    warn "Sementara pakai dummy cert (HTTP tetap jalan via Nginx)"
fi

# ── 11. COMPRESS IMAGES ────────────────────────────────────────
info "Compress static images..."
BEFORE=$(du -sh "$APP_DIR/static/themes/" "$APP_DIR/static/demo-photos/" 2>/dev/null | awk '{sum+=$1} END{print sum}')

find "$APP_DIR/static/themes/" "$APP_DIR/static/demo-photos/"     \( -name "*.jpg" -o -name "*.jpeg" \) 2>/dev/null | while read f; do
    # Skip kalau file < 50KB (sudah kecil)
    size=$(stat -c%s "$f" 2>/dev/null || echo 0)
    if [ "$size" -gt 51200 ]; then
        convert "$f" -strip -quality 82 -resize "1200x>" "$f" 2>/dev/null && echo "  ✓ $(basename $f)"
    fi
done

# Compress PNG (assets tema seperti rumahbanjar, gerbangzen)
find "$APP_DIR/static/themes/" -name "*.png" 2>/dev/null | while read f; do
    size=$(stat -c%s "$f" 2>/dev/null || echo 0)
    if [ "$size" -gt 51200 ]; then
        convert "$f" -strip -quality 85 "$f" 2>/dev/null && echo "  ✓ $(basename $f)"
    fi
done

AFTER=$(du -sh "$APP_DIR/static/themes/" "$APP_DIR/static/demo-photos/" 2>/dev/null | awk '{sum+=$1} END{print sum}')
success "Images compressed — sebelum: ~${BEFORE}MB → sesudah: ~${AFTER}MB"

# ── SELESAI ──────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}   ✓ Deploy selesai!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════${NC}"
echo ""
echo -e "  App dir    : ${APP_DIR}"
echo -e "  Domain     : https://${DOMAIN}"
echo -e "  Admin      : https://${DOMAIN}/admin"
echo -e "  Log app    : ${APP_DIR}/logs/error.log"
echo -e "  DB backup  : ${APP_DIR}/data/undangan.db.backup (harian 03:00)"
echo ""
echo -e "  Cek status : ${YELLOW}sudo systemctl status habarkita${NC}"
echo -e "  Cek log    : ${YELLOW}journalctl -u habarkita -f${NC}"
echo ""
echo -e "  Ganti password admin:"
echo -e "  ${YELLOW}python3 -c \"from app import hash_pw; print(hash_pw('passwordbaru'))\"${NC}"
echo -e "  Lalu update ADMIN_PW_HASH di .env dan restart:"
echo -e "  ${YELLOW}sudo systemctl restart habarkita${NC}"
echo ""

# UndanganKita v3

Undangan digital pernikahan berbasis Flask. Semua konfigurasi sensitif via **environment variables**.

---

## Setup Cepat

```bash
pip install flask
python app.py
# Buka: http://localhost:5000
# Admin: http://localhost:5000/admin/login  (admin / admin123)
```

---

## Environment Variables

| Variable | Default | Keterangan |
|---|---|---|
| `SECRET_KEY` | random | Session key — **wajib ganti di production** |
| `ADMIN_USER` | `admin` | Username login admin |
| `ADMIN_PW_HASH` | hash(admin123) | Hash password admin |
| `SITE_NAME` | `UndanganKita` | Nama website (muncul di title, nav, footer, SEO) |
| `WA_NUMBER` | `6281234567890` | Nomor WA tombol "Pesan" (format 62xxx) |
| `RECAPTCHA_SITE_KEY` | kosong | Google reCAPTCHA v2 site key (kosong = off) |
| `RECAPTCHA_SECRET` | kosong | Google reCAPTCHA v2 secret key |

### Contoh .env:
```bash
export SECRET_KEY="random-string-panjang-banget"
export ADMIN_USER="namalo"
export ADMIN_PW_HASH="pbkdf2:sha256:260000$salt$hash"
export SITE_NAME="UndanganKami"
export WA_NUMBER="628123456789"
```

Jalankan: `source .env && python app.py`

---

## Ganti Password Admin

```bash
python -c "from app import hash_pw; print(hash_pw('password_baru'))"
# Copy hasilnya → set ADMIN_PW_HASH=<hasil>
```

---

## reCAPTCHA (opsional)

1. Daftar: https://www.google.com/recaptcha/admin → pilih v2 "I'm not a robot"
2. Set `RECAPTCHA_SITE_KEY` dan `RECAPTCHA_SECRET`

---

## Foto Demo Katalog

- **Global**: taruh foto di `static/demo-photos/` → muncul di semua preview
- **Per tema**: Dashboard admin → klik "📷 Foto" di kartu tema → upload

---

## Tambah Tema

1. Buat `themes/nama.json` (dengan field `id` wajib ada)
2. Buat `templates/themes/nama.html`
3. Upload foto dari dashboard

```json
{
  "id": "nama",
  "name": "Nama Tema",
  "description": "Deskripsi",
  "preview_color": "#warna",
  "accent_color": "#warna",
  "tags": ["elegant", "dark"],
  "price": 299000,
  "price_label": "Rp 299.000"
}
```

---

## Production

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

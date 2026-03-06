# UndanganKita 💍
Undangan digital pernikahan profesional berbasis Flask Python.

## Cara Jalankan

```bash
pip install -r requirements.txt
python app.py
```

Buka: http://localhost:5000
Admin: http://localhost:5000/admin

---

## Struktur Folder

```
undangan/
├── app.py                        # Flask app utama
├── requirements.txt
├── themes/                       # Config JSON tiap tema
│   ├── firefly.json
│   ├── cinematic.json
│   └── sakura.json
├── templates/
│   ├── index.html                # Landing page
│   ├── admin/
│   │   ├── dashboard.html
│   │   └── create.html
│   └── themes/                   # HTML tiap tema (bisa beda total)
│       ├── firefly.html
│       ├── cinematic.html
│       └── sakura.html
├── static/
│   └── themes/                   # Asset per tema (SVG, PNG, dll)
│       ├── firefly/
│       ├── cinematic/
│       └── sakura/
└── data/
    └── undangan.db               # Database SQLite (auto dibuat)
```

---

## 🎨 Cara Tambah Tema Baru

### Step 1 — Buat file JSON di `/themes/`
```json
{
  "id": "nama_tema",
  "name": "Nama Tampil",
  "description": "Deskripsi singkat tema ini",
  "preview_color": "#warna_bg",
  "accent_color": "#warna_aksen",
  "skeleton": "fullpage_scroll",
  "tags": ["dark", "modern"]
}
```

### Step 2 — Buat file HTML di `/templates/themes/nama_tema.html`

Gunakan variabel Jinja2 ini:
- `{{ inv.groom_name }}` — nama pria
- `{{ inv.bride_name }}` — nama wanita
- `{{ inv.groom_full }}` — nama lengkap pria
- `{{ inv.bride_full }}` — nama lengkap wanita
- `{{ inv.groom_parents }}` — orang tua pria
- `{{ inv.bride_parents }}` — orang tua wanita
- `{{ inv.akad_date | format_date }}` — tanggal akad (terformat)
- `{{ inv.akad_time }}` — jam akad
- `{{ inv.akad_venue }}` — nama venue akad
- `{{ inv.akad_address }}` — alamat akad
- `{{ inv.resepsi_date | format_date }}` — tanggal resepsi
- `{{ inv.resepsi_time }}` — jam resepsi
- `{{ inv.resepsi_venue }}` — nama venue resepsi
- `{{ inv.resepsi_address }}` — alamat resepsi
- `{{ inv.maps_url }}` — link Google Maps
- `{{ inv.love_story }}` — kisah cinta
- `{{ inv.music_url }}` — URL musik latar
- `{{ inv.id }}` — ID undangan (untuk RSVP)
- `{{ rsvp_list }}` — list RSVP yang masuk
- `{{ gifts }}` — list rekening hadiah

### Step 3 — Taruh assets di `/static/themes/nama_tema/`
- SVG ilustrasi
- PNG/WebP foto/texture
- File lainnya

Tema langsung muncul di landing page dan bisa dipilih saat buat undangan!

---

## Prompt AI untuk Generate Tema Baru

Salin prompt ini, ganti bagian [CAPS]:

```
Buatkan tema undangan digital pernikahan bernama "[NAMA TEMA]".

Konsep: [DESKRIPSI SINGKAT, misal: malam berbintang, nuansa biru gelap dan silver]
Mood: [MOOD, misal: romantic, mysterious, modern, minimalis]
Warna utama: [WARNA]
Skeleton layout: [fullpage_scroll / storybook / cinematic / parallax]

Buat:
1. File JSON config (id, name, description, preview_color, accent_color, skeleton, tags)
2. File HTML template lengkap dengan:
   - Intro/splash screen yang unik
   - Animasi CSS (tanpa library eksternal)
   - Canvas animation yang relevan dengan tema
   - Semua section: hero, couple, event, countdown, love story, rsvp, gift, closing
   - Mobile-first design, max-width 480px untuk konten
   - Menggunakan variabel Jinja2: inv.groom_name, inv.bride_name, dll (lihat README)
   - RSVP form dengan fetch POST ke /rsvp/{{ inv.id }}
   - Countdown timer JavaScript
   - Scroll reveal animation

Pastikan layout dan struktur HTML BERBEDA dari tema lain.
Gunakan Google Fonts yang unik dan tidak pasaran.
```

---

## Deploy ke VPS / Cloud

### Gunicorn (production):
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Nginx config:
```nginx
server {
    listen 80;
    server_name undangankita.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
    }
    
    location /static {
        alias /path/to/undangan/static;
    }
}
```

### HTTPS: Gunakan Certbot + Let's Encrypt

---

## Fitur yang Sudah Ada
- ✅ 3 tema berbeda total (Firefly Garden, Cinematic Gold, Sakura Dream)
- ✅ Intro animation (envelope, splash, cinematic)
- ✅ Canvas animation (firefly, gold dust, sakura petals)
- ✅ Countdown timer real-time
- ✅ RSVP system dengan database
- ✅ Daftar ucapan dari tamu
- ✅ Wedding gift / rekening
- ✅ Google Maps link
- ✅ Background music
- ✅ Admin dashboard
- ✅ Scroll reveal animation
- ✅ Mobile-first responsive
- ✅ Copy to clipboard
- ✅ Love story section

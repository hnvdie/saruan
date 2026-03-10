# Prompt Master — Buat Tema Wedding Invitation Baru
## UndanganKita v3 · Flask · Jinja2

---

Copy-paste prompt di bawah ini setiap kali mau bikin tema baru.
Ganti semua bagian `[...]` sesuai keinginan sebelum dikirim.

---

## PROMPT

Buatkan tema wedding invitation digital baru untuk app Flask UndanganKita v3.

**Nama tema:** `[namatema]` (huruf kecil, tanpa spasi, contoh: `malambiru`)
**Judul tema:** `"[Judul Tema]"` (nama tampil ke user, contoh: `"Malam Biru"`)
**Konsep / vibe:** `[deskripsikan feel-nya, contoh: dark moody oceanic, langit malam dengan bintang, nuansa biru tua dan silver, cinematic dan dramatis]`

**Output yang dibutuhkan: 2 file**
1. `[namatema].json` — theme definition (ikuti struktur kalajingga.json)
2. `[namatema].html` — template Jinja2 untuk Flask, disimpan di `templates/themes/[namatema].html`

**Aturan teknis wajib:**
- Template Jinja2, variabel dari Flask: `inv`, `theme`, `rsvp_list`, `gifts`, `photos`, `is_preview`, `photo_src()`, `wa_number`, `site_name`
- Sistem scroll: `scroll-snap-type: y mandatory` di html, tiap section `scroll-snap-align: start; scroll-snap-stop: always; height: 100dvh` — efeknya harus terasa seperti swipe bukan scroll biasa
- Animasi: wajib pakai GSAP 3 via CDN (`https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js` + `ScrollTrigger.min.js`), setiap section masuk dengan animasi ScrollTrigger yang berbeda karakternya
- Opening: ada overlay buka undangan full-screen yang latar belakangnya `cover.webp` dari `static/themes/[namatema]/cover.webp`, atau fallback ke `inv.cover_photo`
- Music player floating (mute/unmute), baca dari `inv.music_url`
- Nav dots di kanan layar sebagai section indicator
- Lightbox untuk galeri foto
- Countdown real-time (hari/jam/menit/detik) ke tanggal `inv.resepsi_date` atau `inv.akad_date`
- RSVP submit ke `POST /rsvp/{{ inv.id }}` via fetch JSON, tampilkan sukses/error
- Tombol salin nomor rekening/ewallet
- **JANGAN ada tombol "Kirim ucapan via WhatsApp"** di bagian manapun
- Preview mode: jika `is_preview == True`, langsung buka tanpa klik tombol
- OG tags TIDAK perlu dimasukkan (sudah di-inject otomatis oleh Flask)
- Semua CSS inline dalam 1 file HTML (tidak ada file terpisah), JS juga inline dalam 1 file HTML

**Layout & urutan section (10 section, kreatif urutannya):**
Wajib ada: Hero/cover, Ayat Al-Quran, Profil pasangan (dengan foto portrait groom & bride), Info acara + countdown, Kisah cinta, Galeri foto, Lokasi + peta, RSVP, Hadiah digital, Penutup. Urutannya bebas — sesuaikan mana yang paling dramatis dan natural flow-nya untuk konsep tema ini.
Kasih footer untuk paling bawah Dibuat dengan ❤ oleh habarkita.com, pesan undangan digital sekarang. (atau sesuaikan biar ga ngeganggu undangan user)
Usahakan Setiap Kali Tema Dibuat Tema akan selalu berbeda beda design nya agar tidak menggunakan 1 template / 1 referensi yang selalu sama.


**Design direction:**
- Konsep visual: `[jelaskan lebih detail, misal: dominan warna navy #0A1628 dan silver #C0C0C0, background texture seperti kulit malam, bintang-bintang kecil berkedip sebagai particle, font display Playfair Display, font sans Outfit]`
- Perbedaan dari tema sebelumnya: `[sebutkan apa yang harus beda dari tema yang sudah ada, misal: layout pasangan horizontal bukan portrait, section quran ada parallax teks, galeri pakai horizontal scroll masonry, penutup ada animasi teks typewriter]`
- Tingkat kemewahan: sangat mewah, bukan template biasa — setiap section harus terasa seperti karya desain bukan web generik
- Animasi harus semakin epic dan emosional setiap scroll ke bawah, bukan seragam dari atas ke bawah
- Particle system ambient harus sesuai tema (bintang, debu emas, kelopak, dan sebagainya)

**Spesifikasi `cover.webp`:** sebutkan ukuran ideal dan max KB yang direkomendasikan untuk tema ini.

**Assets tambahan (JS/font/dll):** sebutkan CDN link kalau perlu library tambahan selain GSAP. Jika ada file yang perlu diunduh dan disimpan offline di `static/themes/[namatema]/`, sebutkan URL-nya.
**Jika Assets Lebih Aman diunduh offline langsung maka berikan link + path nya yang akan disimpan nantinya ke /static/themes/namatema/allfile (js,svg, other)

---

## REFERENSI VARIABEL FLASK

Semua variabel ini tersedia di dalam template:

| Variabel | Tipe | Isi |
|---|---|---|
| `inv.id` | string | ID unik undangan |
| `inv.groom_name` | string | Nama panggilan pria |
| `inv.bride_name` | string | Nama panggilan wanita |
| `inv.groom_full` | string | Nama lengkap pria |
| `inv.bride_full` | string | Nama lengkap wanita |
| `inv.groom_parents` | string | Nama orang tua pria |
| `inv.bride_parents` | string | Nama orang tua wanita |
| `inv.show_parents` | int (0/1) | Tampilkan nama orang tua? |
| `inv.groom_photo_url` | string/None | URL foto portrait pria |
| `inv.bride_photo_url` | string/None | URL foto portrait wanita |
| `inv.akad_date` | string `YYYY-MM-DD` | Tanggal akad |
| `inv.akad_time` | string `HH:MM` | Jam akad |
| `inv.akad_venue` | string | Nama venue akad |
| `inv.akad_address` | string | Alamat akad |
| `inv.resepsi_date` | string `YYYY-MM-DD` | Tanggal resepsi |
| `inv.resepsi_time` | string `HH:MM` | Jam resepsi |
| `inv.resepsi_venue` | string | Nama venue resepsi |
| `inv.resepsi_address` | string | Alamat resepsi |
| `inv.maps_url` | string | URL Google Maps |
| `inv.maps_embed` | string | Embed src URL peta |
| `inv.maps_embed_html` | string (HTML) | `<iframe>` siap pakai |
| `inv.love_story` | string | Cerita cinta pasangan |
| `inv.music_url` | string/None | URL file musik |
| `inv.cover_photo` | string/None | Filename foto cover upload |
| `inv.expires_at` | string | Tanggal expired |
| `is_preview` | bool | True = mode preview admin |
| `photos` | list[Row] | Daftar foto galeri |
| `rsvp_list` | list[Row] | Daftar RSVP masuk |
| `gifts` | list[Row] | Data rekening/ewallet |
| `theme` | dict | Data tema dari JSON |
| `photo_src(photo)` | func | Return URL foto |
| `wa_number` | string | Nomor WA admin (jangan dipakai untuk tombol WA tamu) |
| `site_name` | string | Nama website |

**Filter Jinja2 tersedia:**
- `{{ inv.resepsi_date | format_date }}` → `"Sabtu, 20 Desember 2025"`
- `{{ inv.resepsi_date | days_left }}` → angka hari tersisa

**Akses foto:**
```jinja2
{% for photo in photos %}
  <img src="{{ photo_src(photo) }}" alt="Foto {{ loop.index }}">
{% endfor %}
```

**Akses gifts:**
```jinja2
{% for g in gifts %}
  {% if g.bank_name %}  {# Transfer bank #}
  {% endif %}
  {% if g.ewallet_type %}  {# E-wallet #}
  {% endif %}
{% endfor %}
```

---

## IDE KONSEP TEMA (Tinggal Pilih & Kustomisasi)

| Nama Ide | Vibe | Warna Kunci | Particle |
|---|---|---|---|
| **Malam Emas** | Dark luxury, royal, dramatic | `#0D0A06` + `#C9A96E` | Bintang berkedip |
| **Fajar Suci** | Soft, sakral, morning light | `#FFF8F0` + `#E8C99A` | Sinar cahaya |
| **Hutan Hujan** | Organic, earthy, lush | `#1A2E1A` + `#8B7355` | Partikel daun |
| **Langit Merah** | Bold, sunset, cinematic | `#1A0A06` + `#C44B2A` | Bara api |
| **Kertas Lama** | Vintage, sepia, intimate | `#2C2010` + `#D4A96A` | Dust partikel |
| **Samudra Tenang** | Navy, serene, elegant | `#050F1A` + `#8BA8C4` | Bubble melayang |
| **Bunga Kering** | Muted rose, botanical | `#1E1518` + `#C4827A` | Kelopak jatuh |
| **Perak Dingin** | Silver, modern luxury | `#0A0A12` + `#B8C4D4` | Kristal salju |
| **Tanah Merah** | Terracotta, warm earth | `#1C0E08` + `#C46A3A` | Pasir melayang |
| **Kabut Pagi** | Dreamy, misty, soft | `#F0EDE8` + `#9B8E84` | Mist partikel |

---

## TIPS VARIASI LAYOUT BIAR GA MONOTON

Gunakan referensi ini buat bagian "Perbedaan dari tema sebelumnya":

**Layout Pasangan:**
- Portrait vertikal berdampingan (default)
- Full-width horizontal split kiri-kanan
- Overlap center dengan nama besar di tengah
- Satu per satu dengan swipe horizontal antar section
- Circular frame dengan ornamen border animasi

**Layout Galeri:**
- Grid mosaic (besar-kecil, baris 1 double)
- Horizontal scroll carousel
- Polaroid stack dengan efek tilt acak
- Masonry asymmetric
- Filmstrip full-width

**Layout Ayat:**
- Teks Arab besar full-screen, terjemah muncul setelah scroll
- Split: Arab kanan, terjemah kiri
- Teks Arab sebagai background watermark, terjemah overlay
- Typewriter effect per kata

**Efek Opening Overlay:**
- Segel lilin (wax seal) yang harus di-klik
- Amplop membuka dari bawah ke atas
- Tirai yang membuka ke kiri-kanan
- Reveal dari tengah melebar
- Fade langsung dengan particle burst

**Section Countdown:**
- Angka besar saja, minimalis
- Flip clock animation
- Lingkaran progress per unit waktu
- Integrated di dalam section Hero (bukan section sendiri)

---

## CHECKLIST SEBELUM KIRIM PROMPT

- [ ] Nama tema sudah diisi (huruf kecil, tanpa spasi)
- [ ] Konsep/vibe sudah dideskripsikan dengan jelas
- [ ] Warna palette spesifik sudah disebutkan (hex code kalau bisa)
- [ ] Font display & body sudah dipilih (cek tersedia di Google Fonts)
- [ ] Perbedaan layout dari tema sebelumnya sudah disebutkan
- [ ] Particle system sudah disesuaikan dengan tema
- [ ] Tidak ada permintaan tombol WA untuk tamu

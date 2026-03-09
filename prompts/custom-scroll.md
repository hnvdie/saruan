# PROMPT_SCROLL — Wedding Invitation Mode Full Page Scroll
> Gunakan prompt ini untuk tema dengan navigasi scroll vertikal (layout klasik, section per section)

---

Buatkan tema wedding invitation digital baru untuk proyek Flask saya.
Buat BENAR-BENAR UNIK — bukan template. Ini karya, bukan form.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## FLASK VARIABLES — WAJIB SEMUA DIPAKAI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{{ inv.groom_name }}, {{ inv.bride_name }}
{{ inv.groom_full }}, {{ inv.bride_full }}
{{ inv.groom_parents }}, {{ inv.bride_parents }}
{{ inv.show_parents }}
{{ inv.akad_date | format_date }}, {{ inv.akad_time }}
{{ inv.akad_venue }}, {{ inv.akad_address }}
{{ inv.resepsi_date | format_date }}, {{ inv.resepsi_time }}
{{ inv.resepsi_venue }}, {{ inv.resepsi_address }}
{{ inv.maps_url }}, {{ inv.maps_embed_html }}
{{ inv.love_story }}, {{ inv.id }}, {{ inv.music_url }}

Photos:
{% if photos %}{% for p in photos %}{{ photo_src(p) }}{% endfor %}{% endif %}
- photos[0] = foto couple/bersama
- photos[1] = foto mempelai pria
- photos[2] = foto mempelai wanita
- photos[3+] = foto tambahan

Gifts:
{% for gift in gifts %}
  gift.bank_name, gift.account_number, gift.account_name
  gift.ewallet_type, gift.ewallet_number, gift.ewallet_name
{% endfor %}

RSVP list: {% for r in rsvp_list %}{{ r.guest_name }}, {{ r.message }}{% endfor %}
RSVP POST: /rsvp/{{ inv.id }} — Body JSON: { name, attendance, count, message }

Maps embed: gunakan {{ inv.maps_embed_html | safe }} — JANGAN buat <iframe> sendiri

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## TEMA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

> ADA DUA MODE — PILIH SALAH SATU, HAPUS YANG TIDAK DIPAKAI:

---

### MODE A — TEMA DARI SAYA (isi bagian ini kalau lo mau tentukan sendiri)

- Nama tema       : [isi atau kosongkan biar AI tentukan]
- Konsep & mood   : [isi — deskripsikan nuansa, feel, referensi visual yang lo mau]
- Palet warna     : [isi — bisa hex, nama warna, atau deskripsi "warna tanah + biru laut"]
- Referensi visual: [isi — era, budaya, film, tempat, tekstil, dll]
- Cover asset     : [isi — "pakai cover.jpg dari saya" / atau deskripsikan gambarnya]
- Font vibe       : [opsional — "serif klasik", "japanese", "editorial modern", dll]
- Hal lain        : [opsional — hal spesifik yang lo minta, misal "ada animasi api", "dark mode", dll]

> Kalau ada field yang lo kosongin, AI bebas tentukan sendiri sesuai yang lainnya.

---

### MODE B — TEMA DARI AI SEPENUHNYA (hapus blok ini kalau pakai Mode A)

Tentukan sendiri sepenuhnya. Jangan tanya, langsung eksekusi:
- Nama tema orisinal, bukan kata generik
- Konsep relevan emosional dengan pernikahan — kehangatan, keintiman,
  perjalanan bersama. Inspirasi dari: arsitektur vernakular, sinema romantis,
  alam organik, folklore nusantara, era sejarah romantis (Meiji, Belle Époque,
  Majapahit), kota romantis (Jogja, Kyoto, Marrakech, Lisbon), seni kriya lokal.
  HINDARI: luar angkasa, sci-fi, horror, dystopia, konsep dingin emosional
- Palet 4–6 warna kohesif, tidak klise
- Minimal 2 referensi visual dari dunia berbeda, tetap relevan pernikahan

---

ATURAN BERLAKU DI KEDUA MODE:
Jika tema terasa "aman" atau "familiar" — push lebih jauh.
Unik ≠ asing. Berani ≠ tidak relevan.
Setiap keputusan desain harus bisa dijawab: "ini memperkuat rasa cinta dan perayaan."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## LAYOUT SISTEM — FULL PAGE SCROLL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Konsep: halaman scroll vertikal. User scroll kebawah melewati section per section.
Setiap section = 1 scene fullscreen (min-height: 100vh) yang berdiri sendiri.

ATURAN LAYOUT — TIDAK BOLEH DILANGGAR:
- DILARANG: max-width, min-width untuk membatasi lebar container utama
- DILARANG: angka pixel statis seperti width: 480px pada container
- SEMUA section wrapper = width: 100% atau width: 100vw
- Konten dalam section boleh punya max-width untuk readability teks (misal 800px pada paragraf)
  tapi BUKAN pada wrapper section/background

RESPONSIVE (mobile + desktop):
- clamp() untuk font-size dan padding
  Contoh: font-size: clamp(16px, 4vw, 32px)
  Contoh: padding: clamp(24px, 6vw, 80px)
- Di desktop: layout bisa 2 kolom, grid lebih lebar, whitespace lebih luas
- Gunakan CSS Grid / Flexbox untuk layout yang adapt di semua screen
- Foto dan galeri: lebih banyak kolom di desktop

SCROLL BEHAVIOR:
- IntersectionObserver untuk scroll reveal animations
- Setiap section punya entrance yang BERBEDA — tidak boleh semua translateY
- Gunakan: clip-path wipe, scale dari center, blur-to-sharp, letter reveal, stagger

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## FILOSOFI DESAIN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LAYOUT:
- DILARANG urutan section yang predictable (hero→quran→couple→story→events→...)
- BEBAS reorder, gabungkan, ciptakan section baru
- BEBAS: full-bleed, diagonal cut, overlapping, sticky panels, horizontal scroll dalam section

FOTO:
- DILARANG semua foto jadi gallery grid biasa
- Bisa: background parallax, cutout floating, split-screen, masked shape (blob/hex/circle),
  collage bertumpuk, strip film, polaroid, foto yang "bocor" keluar container
- photos[0] tidak harus di hero

SECTION IDENTITY:
- Setiap section WAJIB punya visual DNA sendiri
- Alternasi gelap-terang boleh dibuang kalau ada konsep lebih kuat
- Boleh ada section 1 kalimat besar fullscreen, section hanya foto + nama, section poster

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## FITUR WAJIB — SEMUA HARUS ADA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✦ Envelope/cover intro — cover.jpg sebagai fullscreen background, efek buka DRAMATIS
✦ Nama mempelai + tanggal
✦ Ayat Al-Quran QS. Ar-Rum: 21 (Arabic + terjemahan)
✦ Profil mempelai pria & wanita + orang tua
✦ Love story
✦ Detail akad nikah + resepsi
✦ Google Maps link + embed ({{ inv.maps_embed_html | safe }})
✦ Countdown timer real-time (hari/jam/menit/detik)
✦ Galeri foto kreatif (bukan grid biasa)
✦ RSVP form (nama, kehadiran, jumlah tamu, pesan)
✦ Gift section (bank + e-wallet, copy button)
✦ Guestbook (rsvp_list + append real-time)
✦ Music player floating (autoplay setelah envelope dibuka)
✦ Closing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## ANIMASI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AMBIENT:
- Wajib 1 sistem partikel canvas unik sesuai tema (bukan bintang sci-fi)
  Contoh: kelopak melayang, kunang-kunang, uap teh, butir pasir, gelembung, dll

ENVELOPE:
- Efek buka DRAMATIS — bukan sekadar fade
  Contoh: curtain split, zoom out dramatis, iris, burn, morphing shape, dll

SCROLL ANIMATIONS:
- IntersectionObserver per section
- Variasi entrance: clip-path wipe, scale center, skew straighten, blur-to-sharp,
  letter-by-letter reveal, stagger kiri/kanan/bawah
- Stagger delay berbeda per nth-child

CONTINUOUS:
- Elemen yang terus bergerak: breathing ornamen, shimmer teks, border trace, floating foto

INTERAKTIF:
- Hover premium di semua clickable: ripple, magnetic, glow, fill-from-cursor
- Foto: scale + brightness + shadow
- Card: lift + shadow depth

TEKNIS:
- Pure CSS + Vanilla JS — DILARANG GSAP, AOS, library luar
- GPU-friendly: transform & opacity
- Custom cubic-bezier — bukan ease/linear bawaan
- @keyframes untuk looping, requestAnimationFrame untuk canvas

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## OUTPUT — 3 FILE WAJIB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**[namatema].html**
- Single file, CSS + JS inline, Jinja2 lengkap
- Komentar per section
- FULLY RESPONSIVE: mobile (360px+) dan desktop (1024px+)
- ZERO max-width pada container/section utama

**[namatema].json**
```json
{
  "id": "namatema",
  "name": "Nama Tema",
  "description": "2-3 kalimat mood dan keunikannya",
  "preview_color": "#hex",
  "accent_color": "#hex",
  "skeleton": "namatema",
  "tags": ["tag1", "tag2", "tag3"],
  "demo_photos": [
    "/static/themes/namatema/photos/couple.jpg",
    "/static/themes/namatema/photos/groom.jpg",
    "/static/themes/namatema/photos/bride.jpg"
  ],
  "price": 85000,
  "price_label": "Rp. 85.000",
  "price_original": 120000,
  "price_note": "Harga promo terbatas",
  "palette": {
    "nama_warna": "#hex"
  },
  "fonts": {
    "display": "Nama Font",
    "serif": "Nama Font",
    "sans": "Nama Font"
  },
  "features": [
    "Full page scroll storytelling",
    "Fitur 2",
    "Fitur 3",
    "Fitur 4",
    "Fitur 5"
  ]
}
```

PENTING: demo_photos = foto pasangan sample, BUKAN cover.jpg
cover.jpg = background envelope/hero dekorasi

**ASSETS_GUIDE.md**
- Tabel semua file di /static/themes/[namatema]/
- Nama file, ukuran ideal, format, max size, deskripsi, tips
- Bedain cover.jpg vs folder photos/
- Posisi photos[0–3+] dalam layout
- Checklist deployment
- Palette hex + font lengkap
- Sumber gratis (Unsplash, Freepik, Freesound)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## STANDAR KUALITAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- Terasa dibuat desainer profesional yang obsesif dengan detail
- Elemen dekoratif: CSS murni atau SVG inline — jangan skip
- Typography hierarchy jelas dan intentional
- Setiap section bisa berdiri sendiri sebagai scene yang indah
- Test mental: "Kalau gw terima undangan ini, apakah gw terharu dan excited?"
  Kalau jawabannya tidak — desain ulang.


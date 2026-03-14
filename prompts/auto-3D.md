# AUTO-GENERATE TEMA WEDDING INVITATION — FLASK UNDANGANKITA v3
# ═══════════════════════════════════════════════════════════════
# INSTRUKSI: Copy-paste seluruh dokumen ini tanpa mengubah apapun.
# AI akan langsung generate 1 tema lengkap yang unik secara otomatis.
# Setiap kali dipaste, tema yang dihasilkan HARUS berbeda total.
# ═══════════════════════════════════════════════════════════════

---

## 🎯 MISI UTAMA

Kamu adalah **Senior Creative Director + Lead Frontend Engineer** spesialis wedding invitation digital premium. Tugasmu adalah membuat **1 tema undangan pernikahan digital** untuk Flask app UndanganKita v3 yang:

- **Sekelas karya studio desain profesional** — bukan template web biasa
- **Menggunakan efek 3D spatial parallax** seperti aplikasi Mental Canvas
- **Selalu berbeda 100%** dari tema yang pernah ada — konsep, warna, layout, animasi, semua baru
- **Langsung production-ready** — output adalah 2 file siap pakai

**Output wajib: 2 file**
1. `[namatema].json` — theme definition
2. `[namatema].html` — Jinja2 template Flask

---

## 🎲 STEP 1: AUTO-GENERATE KONSEP UNIK

**Sebelum menulis kode apapun**, kamu WAJIB terlebih dahulu memilih secara kreatif dan acak:

### A. Pilih Satu "Dunia Visual" (Pilih Acak — Jangan Terprediksi)
Pilih dari daftar ini ATAU ciptakan yang belum pernah ada:
- Hutan bambu Jepang saat malam — cahaya lantern, embun, kabut hijau
- Padang lavender Provence sore hari — ungu, emas, angin pelan
- Kabin kayu di pegunungan musim salju — abu hangat, api, frost
- Bawah laut coral reef — teal, turquoise, bioluminescence
- Kebun teh pagi di Jawa — hijau teh, krem, embun pagi
- Langit gurun Sahara bintang jatuh — indigo, pasir, meteor
- Taman keraton tradisional — batik, emas, ukiran kayu jati
- Pantai cliff Santorini senja — putih bersih, biru Aegean, oranye senja
- Hutan mangrove malam — refleksi air, kunang-kunang, biru teal
- Studio foto vintage tahun 1920 — sepia, grain, cahaya jendela
- Atau ciptakan dunia visual BARU yang belum ada di daftar ini

### B. Tentukan Semua Parameter Ini Secara Otomatis:
```
nama_tema    : [generate nama huruf kecil tanpa spasi, 1-2 kata, bahasa Indonesia/Inggris, puitis]
judul_tema   : [nama tampil ke user, 2-3 kata, indah]
vibe         : [3-5 kata sifat yang menggambarkan feel-nya]
bg_utama     : [hex color]
bg_gelap     : [hex color]
accent_1     : [hex color — warna aksen utama]
accent_2     : [hex color — warna aksen pendukung]
teks_utama   : [hex color]
teks_soft    : [hex color]
font_display : [pilih dari Google Fonts — BUKAN Inter/Roboto/Arial — harus indah & unik]
font_body    : [pilih dari Google Fonts — bersih, readable]
font_script  : [pilih dari Google Fonts — kursif/handwriting untuk "dan" / "and"]
font_arabic  : [Amiri atau Noto Naskh Arabic]
particle     : [jenis partikel: kelopak/bintang/kunang2/debu emas/salju/dll — sesuai dunia visual]
opening_style: [pilih: wax-seal / amplop / tirai / clip-path-circle / particle-burst / custom]
parallax_hero: [deskripsikan 4 layer isi hero section]
layout_couple: [pilih variasi: portrait-berdampingan / split-horizontal / overlap-center / circular-frame]
layout_galeri: [pilih variasi: masonry / filmstrip / polaroid-stack / mosaic / carousel-3d]
layout_ayat  : [pilih variasi: fullscreen-arabic-bg / split-arabic-trans / typewriter / watermark-overlay]
countdown_style: [pilih: angka-besar / flip-clock / lingkaran-progress / integrated-hero]
```

### C. Aturan Diferensiasi — WAJIB BERBEDA dari Pola Umum:
- JANGAN selalu pakai warna gelap + emas (terlalu klise untuk undangan mewah)
- JANGAN selalu layout hero nama tengah dengan font serif besar saja
- JANGAN selalu particle berupa bintang atau kelopak — coba sesuatu yang unexpected
- JANGAN selalu opening overlay wax seal atau amplop — variasikan
- Warna bisa light/pastel yang quaint, atau bold/vibrant yang unexpected, atau dark yang moody
- Setiap kali generate, bayangkan kamu seorang art director berbeda dengan selera berbeda

---

## 🏗️ STEP 2: BANGUN TEMA DENGAN STANDAR INI

### ATURAN TEKNIS WAJIB

- Template Jinja2, variabel dari Flask: `inv`, `theme`, `rsvp_list`, `gifts`, `photos`, `is_preview`, `photo_src()`, `wa_number`, `site_name`
- Sistem scroll: `scroll-snap-type: y mandatory` di html, tiap section `scroll-snap-align: start; scroll-snap-stop: always; height: 100dvh`
- Animasi: wajib pakai GSAP 3 via CDN:
  - `https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js`
  - `https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js`
- Opening overlay fullscreen — background dari `static/themes/[namatema]/cover.webp` atau fallback `inv.cover_photo`
- Music player floating (mute/unmute) dari `inv.music_url`
- Nav dots di kanan layar
- Lightbox galeri foto
- Countdown real-time ke `inv.resepsi_date` atau `inv.akad_date`
- RSVP submit ke `POST /rsvp/{{ inv.id }}` via fetch JSON
- **JANGAN ada tombol "Kirim ucapan via WhatsApp"**
- Preview mode: `is_preview == True` → langsung buka tanpa klik
- OG tags tidak perlu (sudah auto-inject Flask)
- Semua CSS + JS inline dalam 1 file HTML

**Gift section — filter None gausah didisplay**

**Galeri foto — wajib GSAP stagger per item:**
```javascript
// Setiap .gallery-item mulai opacity:0, translateY(60px), scale(0.88), rotate sedikit
// Masuk satu per satu dengan delay bertahap — bukan muncul serentak
gsap.fromTo('.gallery-item',
  { opacity: 0, y: 70, scale: 0.88, rotation: (i) => i%2===0 ? -3 : 3 },
  { opacity: 1, y: 0, scale: 1, rotation: 0,
    stagger: 0.12, duration: 0.9, ease: 'power3.out',
    scrollTrigger: { trigger: '#s-gallery', start: 'top 75%' }
  }
);
```

---

## ⭐ STEP 3: MENTAL CANVAS SPATIAL PARALLAX — IMPLEMENTASI WAJIB

Ini yang membedakan tema ini dari web biasa. Setiap section harus punya **kedalaman ruang** yang terasa nyata.

### Konsep: "Gambar 2D di Ruang 3D"
Seperti Mental Canvas — elemen 2D diletakkan di bidang-bidang berbeda dalam ruang tiga dimensi. Ketika viewport bergerak (mouse/scroll), elemen dekat bergerak lebih cepat dari elemen jauh — menciptakan ilusi kedalaman tanpa model 3D.

### CSS Foundation (Wajib di Setiap Section Spatial)
```css
.scene {
  position: relative;
  width: 100%;
  height: 100dvh;
  perspective: 900px;
  perspective-origin: 50% 50%;
  overflow: hidden;
}
.layer {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  will-change: transform;
  transform-style: preserve-3d;
}

/* Z-depth sistem — 4 lapisan kedalaman */
.layer-bg    { transform: translateZ(-180px) scale(1.28); } /* paling jauh */
.layer-mid   { transform: translateZ(-60px)  scale(1.09); } /* tengah belakang */
.layer-fore  { transform: translateZ(0px)    scale(1);    } /* netral / konten utama */
.layer-front { transform: translateZ(80px)   scale(0.91); } /* paling dekat */

/* Depth of Field — blur sesuai jarak */
.layer-bg    { filter: blur(1.2px); }
.layer-mid   { filter: blur(0px);   }
.layer-fore  { filter: blur(0px);   }
.layer-front { filter: blur(0.6px); }

/* Mobile: reduce ke 2 layer */
@media (max-width: 768px) {
  .layer-bg    { filter: blur(0px); transform: translateZ(0) scale(1); }
  .layer-front { filter: blur(0px); transform: translateZ(0) scale(1); }
}
```

### Mouse + Gyro Parallax (Wajib di Hero & Closing)
```javascript
// Deteksi apakah section aktif
let mouseParallaxActive = false;

const heroSection = document.getElementById('s-hero');
const heroObserver = new IntersectionObserver(entries => {
  mouseParallaxActive = entries[0].isIntersecting;
}, { threshold: 0.5 });
heroObserver.observe(heroSection);

// Mouse parallax — intensitas berbeda per layer
document.addEventListener('mousemove', (e) => {
  if (!mouseParallaxActive) return;
  const cx = window.innerWidth  / 2;
  const cy = window.innerHeight / 2;
  const dx = (e.clientX - cx) / cx; // -1 sampai 1
  const dy = (e.clientY - cy) / cy;

  // Semakin dekat ke depan = bergerak makin banyak
  gsap.to('#s-hero .layer-bg',    { x: dx * 6,  y: dy * 4,  duration: 1.2, ease: 'power2.out' });
  gsap.to('#s-hero .layer-mid',   { x: dx * 16, y: dy * 10, duration: 1.0, ease: 'power2.out' });
  gsap.to('#s-hero .layer-fore',  { x: dx * 28, y: dy * 18, duration: 0.9, ease: 'power2.out' });
  gsap.to('#s-hero .layer-front', { x: dx * 42, y: dy * 26, duration: 0.8, ease: 'power2.out' });
});

// Gyroscope untuk mobile
if (window.DeviceOrientationEvent) {
  window.addEventListener('deviceorientation', (e) => {
    const dx = Math.max(-1, Math.min(1, e.gamma / 35));
    const dy = Math.max(-1, Math.min(1, (e.beta - 45) / 35));
    gsap.to('#s-hero .layer-bg',    { x: dx * 5,  y: dy * 3,  duration: 0.8 });
    gsap.to('#s-hero .layer-mid',   { x: dx * 12, y: dy * 8,  duration: 0.7 });
    gsap.to('#s-hero .layer-fore',  { x: dx * 22, y: dy * 14, duration: 0.6 });
    gsap.to('#s-hero .layer-front', { x: dx * 32, y: dy * 20, duration: 0.5 });
  });
}
```

### ScrollTrigger Parallax per Section (Wajib — scrub berbeda per layer)
```javascript
// Terapkan di SETIAP section yang punya spatial layers
// bg bergerak paling lambat, front bergerak paling cepat
function applyParallax(sectionId) {
  const triggers = [
    { selector: `#${sectionId} .layer-bg`,    y: '-15%', scrub: 2.0 },
    { selector: `#${sectionId} .layer-mid`,   y: '-35%', scrub: 1.3 },
    { selector: `#${sectionId} .layer-fore`,  y: '-55%', scrub: 0.9 },
    { selector: `#${sectionId} .layer-front`, y: '-80%', scrub: 0.5 },
  ];
  triggers.forEach(({ selector, y, scrub }) => {
    if (document.querySelector(selector)) {
      gsap.to(selector, {
        scrollTrigger: {
          trigger: `#${sectionId}`,
          start: 'top top',
          end: 'bottom top',
          scrub
        },
        y
      });
    }
  });
}
// Panggil untuk semua section
['s-hero','s-quran','s-couple','s-event','s-story','s-gallery','s-map','s-closing']
  .forEach(applyParallax);
```

### Camera Travel — Transisi Antar Section (Wajib)
```javascript
// Section baru masuk dari kejauhan — scale kecil, zoom ke normal
// Seperti kamera yang bergerak maju menelusuri ruang
const sectionIds = ['s-quran','s-couple','s-event','s-story','s-gallery','s-map','s-rsvp','s-gift','s-closing'];
sectionIds.forEach((id, i) => {
  const el = document.getElementById(id);
  if (!el) return;

  // Content utama section datang dari depth
  const content = el.querySelector('.scene-content, .section-inner, .z2');
  if (content) {
    gsap.fromTo(content,
      { opacity: 0, scale: 0.82, y: 50 },
      {
        scrollTrigger: { trigger: el, start: 'top 85%', toggleActions: 'play none none reverse' },
        opacity: 1, scale: 1, y: 0,
        duration: 1.3, ease: 'power3.out',
        delay: i * 0.03  // sedikit offset antar section
      }
    );
  }
});
```

### Parallax Ayat Al-Quran (Wajib — Signature Effect)
```javascript
// Teks Arab besar di layer-bg bergerak lambat — seperti tembok yang dilewati
gsap.to('#s-quran .arabic-watermark', {
  scrollTrigger: {
    trigger: '#s-quran', start: 'top bottom', end: 'bottom top', scrub: 2.5
  },
  y: '-25%', scale: 1.08, opacity: 0.05, ease: 'none'
});
// Terjemah di layer-fore bergerak lebih cepat
gsap.to('#s-quran .quran-translation', {
  scrollTrigger: {
    trigger: '#s-quran', start: 'top bottom', end: 'bottom top', scrub: 0.8
  },
  y: '-55%', ease: 'none'
});
```

### Panduan Isi Layer per Section

```
HERO (4 layer wajib):
  layer-bg    → background utama: gradien / foto / tekstur sesuai tema
  layer-mid   → ornamen besar: bunga, pohon, arsitektur, atau elemen dekoratif tema
  layer-fore  → nama pengantin + tanggal + tagline
  layer-front → partikel ambient + elemen kecil dekoratif (daun, bintang, dll)

QURAN (3 layer):
  layer-bg    → Arabic text watermark BESAR, blur, opacity rendah
  layer-mid   → ornamen dekoratif (border, motif)
  layer-fore  → translation text + source ayat

COUPLE (3 layer):
  layer-bg    → background / tekstur / warna
  layer-mid   → foto portrait pasangan (lebih lambat dari teks)
  layer-fore  → nama, info orang tua (di depan foto)

EVENT (3 layer):
  layer-bg    → background dekoratif
  layer-mid   → kartu acara / event cards
  layer-fore  → countdown (paling depan, paling cepat)

STORY (3 layer):
  layer-bg    → background + ornamen besar transparan
  layer-mid   → elemen dekoratif (tanda kutip besar, bunga)
  layer-fore  → teks cerita cinta

GALLERY (3 layer):
  layer-bg    → background warna/tekstur
  layer-mid   → judul section
  layer-fore  → grid/scroll foto

CLOSING (4 layer):
  layer-bg    → background dramatis
  layer-mid   → ornamen / ilustrasi besar
  layer-fore  → pesan penutup + nama pengantin
  layer-front → partikel (sama seperti hero tapi lebih dense)
```

---

## 📐 STEP 4: LAYOUT & SECTION

**10 section wajib** (urutan bebas, sesuaikan dramaturgi tema):
Hero/cover · Ayat Al-Quran · Profil Pasangan · Info Acara + Countdown · Kisah Cinta · Galeri Foto · Lokasi + Peta · RSVP · Hadiah Digital · Penutup

Footer terbawah (subtle, tidak mengganggu):
> Dibuat dengan ❤ oleh [habarkita.com](https://habarkita.com) — Pesan undangan digital sekarang

---

## 📦 STEP 5: FORMAT JSON (Ikuti Struktur Ini Persis)

```json
{
  "id": "[namatema]",
  "name": "[Judul Tema]",
  "description": "[Deskripsi 2-3 kalimat tentang vibe dan keunggulan visual tema ini]",
  "preview_color": "[hex warna utama]",
  "accent_color": "[hex warna aksen]",
  "skeleton": "[namatema]",
  "tags": ["[tag1]", "[tag2]", "..."],
  "demo_photos": ["/static/themes/[namatema]/demo_cover.jpg"],
  "price": 25000,
  "price_label": "Rp 25.000",
  "price_original": 50000,
  "price_note": "",
  "palette": {
    "[nama_warna]": "[hex]",
    "...": "..."
  },
  "fonts": {
    "display": "[nama font]",
    "script": "[nama font]",
    "sans": "[nama font]",
    "arabic": "[Amiri atau Noto Naskh Arabic]"
  },
  "features": [
    "[fitur 1]",
    "[fitur 2]",
    "..."
  ]
}
```

---

## 🔧 REFERENSI VARIABEL FLASK

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
| `wa_number` | string | Nomor WA admin |
| `site_name` | string | Nama website |

**Filter Jinja2:**
- `{{ inv.resepsi_date | format_date }}` → `"Sabtu, 20 Desember 2025"`
- `{{ inv.resepsi_date | days_left }}` → angka hari tersisa

---

## 🎨 REFERENSI VARIASI — AI WAJIB MEMILIH SECARA ACAK

### Dunia Visual yang Belum Pernah Dipakai (Rotasi Acak)
Setiap generate pilih 1 yang berbeda. Jika sudah pernah dipakai dalam sesi ini, pilih yang lain:

| # | Dunia Visual | Warna Dominan | Particle | Parallax Signature |
|---|---|---|---|---|
| 1 | Hutan bambu malam Jepang | #0D1A12 + #4A8C6A | Kunang-kunang | Batang bambu 3 kedalaman |
| 2 | Padang lavender Provence | #2A1A3D + #B08CC4 | Serbuk bunga | Bunga lavender berlapis |
| 3 | Bawah laut coral reef | #041824 + #2A8FA0 | Gelembung + ikan kecil | Terumbu karang 4 layer |
| 4 | Kebun teh pagi Jawa | #1A2A18 + #8AAA6A | Embun + cahaya pagi | Daun teh berlapis kabut |
| 5 | Langit gurun bintang jatuh | #06081A + #C4A04A | Meteor + pasir | Galaksi jauh + pasir depan |
| 6 | Keraton Yogya goldenhour | #1A1008 + #C49A3A | Debu emas + daun waringin | Gerbang jauh + ukiran depan |
| 7 | Cliff Santorini senja | #1A2A40 + #E8904A | Cahaya senja + buih laut | Laut + arsitektur + langit |
| 8 | Studio foto 1920s | #1A1208 + #C4A068 | Grain film + dust | Bokeh + ornamen + teks |
| 9 | Hutan mangrove kunang-kunang | #041814 + #3A9A7A | Kunang-kunang + refleksi | Air + akar + cahaya |
| 10 | Taman bunga sakura malam | #0D0814 + #C47AA0 | Kelopak sakura | Pohon + kelopak + bulan |
| 11 | Pegunungan Alpen musim dingin | #080C14 + #8AB0D4 | Salju + frost | Gunung jauh + salju depan |
| 12 | Pantai Raja Ampat fajar | #0A1824 + #6AB4C4 | Percikan laut + cahaya | Pulau + laut + langit |
| 13 | Kota Paris malam hujan | #08101A + #C4A8D4 | Tetes hujan + lampu | Menara jauh + jalan depan |
| 14 | Kebun mawar hitam gothic | #0A0810 + #C43A6A | Kelopak gelap + petir | Mawar berlapis + bayangan |
| 15 | Lembah foggy Skotlandia | #0C1018 + #8A9AB0 | Kabut + partikel heather | Kastil jauh + kabut depan |

### Layout Pasangan (Pilih Acak)
- Portrait vertikal berdampingan, foto di layer-mid teks di layer-fore
- Split horizontal full-width kiri (groom) kanan (bride), boundary di tengah
- Overlap center — foto overlap di layer-mid, nama BESAR di layer-fore
- Satu per satu — groom di section sendiri, bride di section sendiri (swipe horizontal)
- Circular frame dengan border ornamen animasi rotating
- Silhouette + warna flat, detail muncul saat hover/scroll

### Layout Galeri (Pilih Acak)
- Filmstrip horizontal full-width, foto berukuran 80dvh, scroll horizontal
- Polaroid stack acak — tiap foto punya tilt berbeda, layer berbeda, hover meluruskan
- Masonry asymmetric — 3 kolom, ukuran berbeda-beda
- Carousel 3D perspective — foto tengah besar, kiri kanan mengecil dengan rotateY
- Grid mosaic — 1 foto besar kiri, 2 kecil kanan, baris bergantian
- Magazine spread — foto bleeding ke edge, teks overlay italic

### Layout Ayat Al-Quran (Pilih Acak)
- Teks Arab fullscreen layer-bg blur transparan, reveal terjemah dari bawah
- Split: Arab kanan (layer-mid), terjemah kiri (layer-fore), garis di tengah
- Arabic typewriter per kata, terjemah muncul setelah Arabic selesai
- Arabic besar sebagai background watermark, terjemah overlay center
- Parallax zoom-in: scroll maju = Arabic makin besar dan blur makin banyak

### Opening Overlay (Pilih Acak)
- Wax seal klik → clip-path circle expand dari center
- Amplop membuka ke atas (CSS 3D flap fold)
- Tirai dua sisi membuka (GSAP scaleX dari tengah ke tepi)
- Portal cahaya — clip-path ellipse mengecil lalu hilang
- Reveal dari titik jari — simulasi sentuhan melebar
- Halaman buku terbalik — 3D rotateY

### Countdown (Pilih Acak)
- Angka Cormorant/Playfair besar, masing-masing di layer berbeda (hari depan, detik belakang)
- Flip card animation per digit — CSS 3D rotateX
- Ring progress melingkar per unit (hari, jam, menit, detik)
- Integrated di Hero section — floating di bawah nama
- Split layout: hari di kiri besar, jam/menit/detik kecil di kanan

---

## ✅ SELF-CHECK SEBELUM OUTPUT

AI harus memastikan semua ini terpenuhi sebelum menulis kode:

**Konsep:**
- [ ] Dunia visual sudah dipilih (bukan yang generik)
- [ ] Semua hex color sudah ditentukan (min 6 warna)
- [ ] Font display unik, bukan Inter/Roboto/Arial
- [ ] Particle sesuai dunia visual
- [ ] Layout semua section sudah diputuskan (bukan default semua)

**Mental Canvas Parallax:**
- [ ] Hero punya 4 layer dengan konten yang tepat
- [ ] Mouse parallax aktif di Hero (dan Closing)
- [ ] Gyroscope parallax untuk mobile
- [ ] `applyParallax()` dipanggil untuk semua section
- [ ] Camera travel entrance di semua section
- [ ] Ayat Al-Quran parallax khusus (arabic watermark bergerak lambat)
- [ ] CSS depth-of-field blur sesuai layer
- [ ] `will-change: transform` pada layer yang dianimasi
- [ ] Mobile: layer disederhanakan jadi 2

**Teknis:**
- [ ] Gift section filter None/null Jinja2
- [ ] Galeri GSAP stagger per item
- [ ] RSVP fetch JSON ke Flask
- [ ] Countdown real-time berjalan
- [ ] Tidak ada tombol WA untuk tamu
- [ ] Preview mode skip overlay
- [ ] Semua CSS + JS inline 1 file HTML
- [ ] JSON struktur lengkap (id, name, description, preview_color, accent_color, skeleton, tags, demo_photos, price, price_label, price_original, price_note, palette, fonts, features)

---

## 🚀 MULAI SEKARANG

Tidak perlu menunggu instruksi tambahan. Tidak perlu konfirmasi.

1. Jalankan **Step 1** — pilih dunia visual dan tentukan semua parameter secara otomatis
2. Jalankan **Step 2-4** — bangun HTML + JSON lengkap
3. Output **2 file final** langsung

Hasilkan tema yang memukau. Setiap pixel harus terasa disengaja. Setiap animasi harus terasa hidup. Ini bukan template — ini adalah karya.

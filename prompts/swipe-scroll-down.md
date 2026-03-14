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

Foto Profil Mempelai (opsional — bisa None):
{{ inv.groom_photo_url }}  ← URL foto portrait pria (dari upload khusus, bukan gallery)
{{ inv.bride_photo_url }}  ← URL foto portrait wanita (dari upload khusus, bukan gallery)

Cara pakai di template:
{% if inv.groom_photo_url %}
  <img src="{{ inv.groom_photo_url }}" alt="{{ inv.groom_name }}">
{% elif photos and photos|length > 1 %}
  <img src="{{ photo_src(photos[1]) }}" alt="{{ inv.groom_name }}">  {# fallback ke gallery #}
{% endif %}

Photos (gallery umum):
{% if photos %}{% for p in photos %}{{ photo_src(p) }}{% endfor %}{% endif %}
- photos[0] = foto couple/bersama
- photos[1] = foto mempelai pria (jika groom_photo_url kosong, pakai ini sebagai fallback)
- photos[2] = foto mempelai wanita (jika bride_photo_url kosong, pakai ini sebagai fallback)
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
## TEMA — TENTUKAN SENDIRI SEPENUHNYA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Jangan tanya, langsung eksekusi. Tentukan sendiri:

- Nama tema       : orisinal, bukan kata generik
- Konsep & mood   : relevan emosional dengan pernikahan — kehangatan, keintiman,
                    perjalanan bersama. Inspirasi dari: arsitektur vernakular,
                    sinema romantis, alam organik, folklore nusantara, era sejarah
                    romantis (Meiji, Belle Époque, Majapahit), kota romantis
                    (Jogja, Kyoto, Marrakech, Lisbon), seni kriya lokal, dll.
                    HINDARI: luar angkasa, sci-fi, horror, dystopia, konsep dingin
- Palet warna     : 4–6 warna kohesif, tidak klise
- Referensi visual: minimal 2 dunia berbeda, tetap relevan pernikahan
                    Contoh: "Art Nouveau × padang bunga liar Jawa"
- Cover asset     : deskripsikan cover.jpg ideal untuk tema ini

ATURAN: Setiap tema harus terasa dari desainer berbeda. Jika tema terasa "aman" atau
"familiar" — buang dan ulang. Unik ≠ asing. Berani ≠ tidak relevan.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## LAYOUT SISTEM — SCROLL SECTION (WAJIB IKUTI PERSIS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Konsep: User scroll ke bawah antar section. Setiap section = 1 scene fullscreen (100vh)
yang berdiri sendiri secara visual.
Navigasi: scroll touch/mouse + tombol panah atas/bawah + dot indicator (kanan layar) +
keyboard arrow keys (↑↓) / Page Up / Page Down.

ATURAN LAYOUT — TIDAK BOLEH DILANGGAR:
- WAJIB: Setiap .section memiliki width: 100vw; height: 100vh; overflow: hidden
- DILARANG: max-width, min-width, min(), clamp() untuk membatasi lebar container
- DILARANG: angka pixel statis seperti width: 480px pada container
- SEMUA width container = width: 100vw — tanpa pengecualian
- DILARANG: scroll bebas (free scroll) — navigasi harus snap per section

SCROLL SECTION — TEMPLATE INI WAJIB DIPAKAI PERSIS:

```css
html, body {
  margin: 0; padding: 0;
  width: 100vw; height: 100vh;
  overflow: hidden;
}

#app {
  width: 100vw; height: 100vh;
  overflow: hidden;
  position: relative;
}

#track {
  position: fixed;
  top: 0; left: 0;
  width: 100vw;
  will-change: transform;
  transition: transform .65s cubic-bezier(.77,0,.175,1);
}

.section {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  position: relative;
}
```

```js
let current = 0;
const sections = document.querySelectorAll('.section');
const total = sections.length;

function goTo(idx) {
  if (idx < 0 || idx >= total) return;
  current = idx;
  document.getElementById('track').style.transform =
    `translateY(-${current * 100}vh)`;
  updateDots();
}

// Dot indicator
function updateDots() {
  document.querySelectorAll('.dot').forEach((d, i) =>
    d.classList.toggle('active', i === current));
}

// Keyboard
document.addEventListener('keydown', e => {
  if (e.key === 'ArrowDown' || e.key === 'PageDown') goTo(current + 1);
  if (e.key === 'ArrowUp'   || e.key === 'PageUp')   goTo(current - 1);
});

// Touch/swipe vertikal
let startY = 0;
document.addEventListener('touchstart', e => { startY = e.touches[0].clientY; });
document.addEventListener('touchend',   e => {
  const dy = startY - e.changedTouches[0].clientY;
  if (Math.abs(dy) > 40) goTo(dy > 0 ? current + 1 : current - 1);
});

// Wheel / scroll
let wheelLock = false;
document.addEventListener('wheel', e => {
  if (wheelLock) return;
  wheelLock = true;
  goTo(e.deltaY > 0 ? current + 1 : current - 1);
  setTimeout(() => { wheelLock = false; }, 750);
}, { passive: true });
```

DOT INDICATOR — posisi fixed kanan layar:
```css
#dots {
  position: fixed;
  right: clamp(12px, 3vw, 24px);
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 100;
}
.dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: rgba(255,255,255,.4);
  cursor: pointer;
  transition: background .3s, transform .3s;
}
.dot.active {
  background: #fff;
  transform: scale(1.4);
}
```

TOMBOL PANAH — atas & bawah:
```css
.nav-btn {
  position: fixed;
  right: clamp(12px, 3vw, 24px);
  z-index: 100;
  background: rgba(255,255,255,.15);
  border: none; border-radius: 50%;
  width: 40px; height: 40px;
  cursor: pointer;
  backdrop-filter: blur(4px);
  transition: background .2s;
}
.nav-btn:hover { background: rgba(255,255,255,.3); }
#btn-up   { top:    clamp(12px, 5vh, 40px); }
#btn-down { bottom: clamp(12px, 5vh, 40px); }
```

RESPONSIVE (mobile + desktop):
- clamp() boleh HANYA untuk font-size dan padding
- Contoh: font-size: clamp(14px, 4vw, 28px)
- Contoh: padding: clamp(20px, 5vw, 60px)
- Di desktop: elemen lebih besar, whitespace lebih luas
- Foto/grid boleh punya kolom lebih banyak di desktop via CSS Grid/Flex

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## FILOSOFI DESAIN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LAYOUT:
- DILARANG urutan section yang predictable
- BEBAS reorder, gabungkan, ciptakan section baru
- BEBAS: full-bleed split, diagonal cut, overlapping layers

FOTO:
- DILARANG semua foto jadi gallery grid biasa
- Bisa: background parallax, cutout floating, split-screen, masked shape,
  collage bertumpuk, strip film, polaroid acak, texture
- photos[0] tidak harus di hero

SECTION IDENTITY:
- Setiap section WAJIB punya visual DNA sendiri
- Setiap section harus indah jika di-screenshot sendiri

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## FITUR WAJIB — SEMUA HARUS ADA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✦ Envelope/cover intro — fullscreen background, tombol "Buka Undangan"
   Background prioritas: photos[0] (foto user) → inv.groom_photo_url → warna solid fallback
   JANGAN hardcode cover.jpg — pakai Jinja if/elif seperti ini:

   CSS element background: background: var(--deep) center/cover no-repeat;  ← default warna
   HTML envelope bg:
   {% if photos and photos|length > 0 %}
     <div class="env-bg" style="background-image:url('{{ photo_src(photos[0]) }}')"></div>
   {% elif inv.groom_photo_url %}
     <div class="env-bg" style="background-image:url('{{ inv.groom_photo_url }}')"></div>
   {% else %}
     <div class="env-bg"></div>  ← fallback warna solid dari CSS
   {% endif %}
✦ Nama mempelai + tanggal
✦ Profil mempelai pria & wanita + orang tua
✦ Love story
✦ Detail akad nikah + resepsi
✦ Google Maps link + embed ({{ inv.maps_embed_html | safe }})
✦ Countdown timer real-time (hari/jam/menit/detik)
✦ Galeri foto kreatif (bukan grid biasa)
✦ RSVP form (nama, kehadiran, jumlah tamu, pesan)
✦ Gift section (bank + e-wallet, copy button)
✦ Guestbook (rsvp_list + append real-time)
✦ Ayat Al-Quran QS. Ar-Rum: 21 (Arabic + terjemahan)
✦ Music player floating (autoplay setelah envelope dibuka)
✦ Closing

posisi sangat boleh diacak-acak urutannya jika ingin menyesuaikan dengan design.
Kasih footer untuk paling bawah Dibuat dengan ❤ oleh habarkita.com, pesan undangan digital sekarang. (atau sesuaikan biar ga ngeganggu undangan user)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## ANIMASI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AMBIENT:
- Wajib 1 sistem partikel canvas unik sesuai tema (bukan bintang sci-fi)
  Contoh: kelopak melayang, kunang-kunang, uap teh, butir pasir, dll

ENVELOPE — WAJIB IKUTI PERSIS:
- Efek buka: FADE OUT halus saja
- DILARANG: curtain split, iris transition, zoom out, burn effect,
  atau efek terbelah/dramatis apapun bentuknya
- Flow: tombol "Buka Undangan" diklik → envelope fade out → konten muncul

CSS envelope — WAJIB pakai ini persis:
```css
#envelope.opening { opacity: 0; transition: opacity .6s ease; pointer-events: none; }
#envelope.gone    { display: none; }
```

JS envelope — WAJIB pakai ini persis:
```js
function openEnvelope() {
  env.classList.add('opening');
  setTimeout(() => {
    env.classList.add('gone');
    app.classList.add('visible');
    // autoplay musik di sini jika ada
  }, 650);
}
env.addEventListener('click', openEnvelope);
```

TEKNIS:
- Pure CSS + Vanilla JS — DILARANG GSAP, AOS, library luar
- GPU-friendly: gunakan transform & opacity
- Custom cubic-bezier — bukan ease/linear bawaan

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## OUTPUT — 3 FILE WAJIB
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**[namatema].html**
- Single file, CSS + JS inline, Jinja2 lengkap
- Komentar per section
- FULLY RESPONSIVE: mobile (360px+) dan desktop (1024px+)
- ZERO max-width pada container utama

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
  "demo_photos": [],
  "price": 85000,
  "price_label": "Rp 85.000",
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
    "Scroll section navigation fullscreen",
    "Fitur 2",
    "Fitur 3",
    "Fitur 4",
    "Fitur 5"
  ]
}
```

PENTING: demo_photos = kosongkan (array kosong [])
cover.jpg = TIDAK DIPERLUKAN — background envelope otomatis pakai photos[0] dari upload user.
            Kalau mau ada fallback static, boleh sertakan cover.jpg tapi opsional.

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

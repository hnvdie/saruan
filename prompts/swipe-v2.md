> Gunakan prompt ini untuk tema dengan navigasi swipe kiri/kanan (1 layar penuh, tanpa scroll)

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
## LAYOUT SISTEM — SWIPE CARD (WAJIB IKUTI PERSIS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Konsep: 1 layar tanpa scroll. User swipe kiri/kanan antar card.
Navigasi: swipe touch + tombol panah + dot indicator + keyboard arrow keys.
Setiap card = 1 scene fullscreen yang berdiri sendiri.

ATURAN LAYOUT — TIDAK BOLEH DILANGGAR:
- WAJIB: position: fixed; top:0; left:0; width:100vw; height:100vh untuk semua elemen utama
- DILARANG: max-width, min-width, min(), clamp() untuk membatasi lebar container
- DILARANG: angka pixel statis seperti width: 480px pada container
- SEMUA width container = width: 100vw — tanpa pengecualian

CARD SLIDER — TEMPLATE INI WAJIB DIPAKAI PERSIS:

```css
#track {
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  z-index: 10;
}
.card {
  position: absolute;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  overflow: hidden;
  transition: transform .65s cubic-bezier(.77,0,.175,1), opacity .45s ease;
}
.card.cur  { transform: translateX(0);     opacity: 1; z-index: 10; }
.card.prev { transform: translateX(-100%); opacity: 0; z-index: 5;  }
.card.next { transform: translateX(100%);  opacity: 0; z-index: 5;  }
.card.far  { transform: translateX(200%);  opacity: 0; z-index: 1;  }
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
- Setiap card WAJIB punya visual DNA sendiri
- Setiap card harus indah jika di-screenshot sendiri

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## FITUR WAJIB — SEMUA HARUS ADA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✦ Envelope/cover intro — cover.jpg sebagai fullscreen background, tombol "Buka Undangan"
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
    "Swipe card navigation fullscreen",
    "Fitur 2",
    "Fitur 3",
    "Fitur 4",
    "Fitur 5"
  ]
}
```

PENTING: demo_photos = kosongkan (array kosong [])
cover.jpg = background envelope/hero dekorasi, bukan foto pasangan

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
- Setiap card bisa berdiri sendiri sebagai scene yang indah
- Test mental: "Kalau gw terima undangan ini, apakah gw terharu dan excited?"
  Kalau jawabannya tidak — desain ulang.

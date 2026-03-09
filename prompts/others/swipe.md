Buatkan tema wedding invitation digital baru untuk proyek Flask saya.
Buat BENAR-BENAR UNIK — bukan template. Ini karya, bukan form.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KONTEKS PROYEK FLASK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Template variables yang tersedia:
{{ inv.groom_name }}, {{ inv.bride_name }}
{{ inv.groom_full }}, {{ inv.bride_full }}
{{ inv.groom_parents }}, {{ inv.bride_parents }}
{{ inv.show_parents }}
{{ inv.akad_date | format_date }}, {{ inv.akad_time }}
{{ inv.akad_venue }}, {{ inv.akad_address }}
{{ inv.resepsi_date | format_date }}, {{ inv.resepsi_time }}
{{ inv.resepsi_venue }}, {{ inv.resepsi_address }}
{{ inv.maps_url }}, {{ inv.maps_embed }}, {{ inv.maps_embed_html }}
{{ inv.love_story }}, {{ inv.id }}, {{ inv.music_url }}
Photos (list, gunakan BEBAS — tidak harus gallery):
{% if photos %}{% for p in photos %}{{ photo_src(p) }}{% endfor %}{% endif %}
photos[0] = foto couple/bersama
photos[1] = foto mempelai pria
photos[2] = foto mempelai wanita
photos[3+] = foto tambahan
Gifts (dinamis dari database):
{% for gift in gifts %}
gift.bank_name, gift.account_number, gift.account_name
gift.ewallet_type, gift.ewallet_number, gift.ewallet_name
{% endfor %}
RSVP list (ucapan tamu):
{% for r in rsvp_list %}{{ r.guest_name }}, {{ r.message }}{% endfor %}
RSVP POST endpoint: /rsvp/{{ inv.id }}
Body JSON: { name, attendance, count, message }
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INPUT TEMA — KAMU YANG TENTUKAN SEPENUHNYA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Kamu bebas dan WAJIB menciptakan tema yang benar-benar baru setiap kali prompt ini dijalankan.
Jangan tanya, jangan minta konfirmasi — langsung eksekusi dengan keputusan kreatif penuh.
Tentukan sendiri secara acak dan unik:
Nama tema       : ciptakan nama orisinal (bukan kata generik seperti "Elegant" atau "Classic")
Konsep & mood   : pilih sesuatu yang RELEVAN secara emosional dengan pernikahan — kehangatan,
keintiman, perjalanan bersama, alam yang lembut, tradisi budaya, keindahan
arsitektur, momen-momen kecil yang indah. Inspirasi boleh dari:
arsitektur vernakular, sinema romantis, alam organik (hutan, lautan tenang,
bunga, musim hujan, padang savana), folklore & mitos cinta nusantara,
era sejarah yang romantis (Art Deco, Meiji, Belle Époque, Majapahit),
kota-kota dengan aura romantis (Jogja, Kyoto, Marrakech, Lisbon, Havana),
ritual budaya Indonesia, seni kriya & tekstil lokal, suasana waktu
(golden hour, senja, subuh tenang, malam lampion), dll.
HINDARI KERAS: luar angkasa, nebula, galaksi, black hole, astrofisika,
teknologi futuristik/sci-fi, horror, dystopia, konsep yang terlalu abstrak
dan dingin secara emosional.
Palet warna     : tentukan 4–6 warna yang kohesif dan tidak klise.
Referensi visual: gabungkan minimal 2 referensi dari dunia berbeda yang TETAP relevan
dengan konteks pernikahan.
Cover asset     : deskripsikan gambar cover.jpg yang ideal untuk tema ini
Custom assets   : tentukan semua asset pendukung yang dibutuhkan
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ATURAN LAYOUT & TEKNIS — WAJIB DIIKUTI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LAYOUT SISTEM — SWIPE CARD, SATU LAYAR PENUH:
Konsep: 1 layar tanpa scroll, user swipe kiri/kanan untuk berpindah card
Semua navigasi via: swipe touch, tombol panah, dot indicator, keyboard arrow keys
Setiap card = satu "scene" fullscreen yang berdiri sendiri
WAJIB gunakan position: fixed; top:0; left:0; width:100vw; height:100vh untuk semua elemen utama
DILARANG KERAS menggunakan max-width, min-width, min(), clamp() untuk membatasi lebar layout
DILARANG KERAS menggunakan angka pixel statis seperti width: 480px untuk container utama
Semua width container utama HARUS width: 100vw — tidak ada pengecualian
Card individual: position:absolute; top:0; left:0; width:100vw; height:100vh
RESPONSIVE — MOBILE & DESKTOP:
Layout harus terlihat bagus di mobile (360px–430px) DAN desktop (1024px+)
Gunakan CSS clamp() HANYA untuk font-size, padding, gap — BUKAN untuk width container
Contoh font responsive: font-size: clamp(14px, 4vw, 22px)
Contoh padding responsive: padding: clamp(20px, 5vw, 60px)
Di desktop, elemen bisa dibuat lebih besar, lebih lebar, dengan lebih banyak whitespace
Foto split/polaroid/grid boleh punya kolom lebih banyak di desktop via CSS Grid/Flex
CARD SLIDER WAJIB:
/* TEMPLATE WAJIB — jangan dimodifikasi */
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
.card.cur  { transform: translateX(0);    opacity: 1; z-index: 10; }
.card.prev { transform: translateX(-100%); opacity: 0; z-index: 5;  }
.card.next { transform: translateX(100%);  opacity: 0; z-index: 5;  }
.card.far  { transform: translateX(200%);  opacity: 0; z-index: 1;  }
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILOSOFI DESAIN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LAYOUT:
DILARANG urutan section yang selalu sama
BEBAS reorder, gabungkan, pisahkan, atau ciptakan section baru
BEBAS buat layout tidak konvensional: full-bleed split, diagonal cut, overlapping layers, dll
FOTO:
DILARANG memperlakukan semua foto hanya sebagai gallery grid
Foto bisa menjadi: background parallax, cutout floating, split-screen, masked shape, collage, polaroid acak, dll
SECTION IDENTITY:
Setiap section WAJIB punya visual DNA sendiri
Setiap section harus bisa berdiri sendiri sebagai "scene" yang indah jika di-screenshot
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FITUR WAJIB — SEMUA HARUS ADA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✦ Envelope/cover intro (wajib pakai cover.jpg sebagai fullscreen background)
✦ Nama mempelai + tanggal pernikahan
✦ Ayat Al-Quran QS. Ar-Rum: 21 (Arabic + terjemahan)
✦ Profil mempelai pria & wanita (nama lengkap + orang tua)
✦ Love story ({{ inv.love_story }})
✦ Detail acara: akad nikah + resepsi (tanggal, waktu, venue, alamat)
✦ Google Maps link + embed iframe
Untuk link: <a href="{{ inv.maps_url }}">
Untuk embed: gunakan {{ inv.maps_embed_html | safe }} — JANGAN buat iframe sendiri
✦ Countdown timer real-time (hari / jam / menit / detik)
✦ Galeri / penempatan foto kreatif
✦ RSVP form (nama, kehadiran, jumlah tamu, pesan)
✦ Gift section (bank + e-wallet dari gifts loop, dengan copy button)
✦ Guestbook (dari rsvp_list + append real-time saat RSVP berhasil)
✦ Music player floating (autoplay setelah envelope dibuka)
✦ Closing / penutup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ANIMASI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AMBIENT:
Wajib ada 1 sistem partikel/canvas unik yang sesuai tema
HINDARI: partikel yang terasa sci-fi (bintang putih di hitam, dll)
ENVELOPE:
Efek buka undangan harus DRAMATIS dan tidak generik
Bukan sekadar fade out
TEKNIS:
Semua animasi menggunakan transform & opacity (GPU-friendly)
Custom cubic-bezier — tidak boleh pakai ease/linear bawaan saja
Tidak boleh pakai library animasi eksternal (GSAP, AOS, dll) — pure CSS + JS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT YANG DIBUTUHKAN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[namatema].html
Single file, CSS + JS inline
Jinja2 template lengkap
Kode bersih, diberi komentar per section
FULLY RESPONSIVE: mobile (360px+) dan desktop (1024px+)
ZERO max-width/min-width pada container utama
[namatema].json
Struktur WAJIB PERSIS:
{
  "id": "namatema",
  "name": "Nama Tema",
  "description": "2-3 kalimat",
  "preview_color": "#hex",
  "accent_color": "#hex",
  "skeleton": "namatema",
  "tags": ["tag1", "tag2"],
  "demo_photos": [
    "/static/themes/namatema/photos/couple.jpg",
    "/static/themes/namatema/photos/groom.jpg",
    "/static/themes/namatema/photos/bride.jpg"
  ],
  "price": 85000,
  "price_label": "Rp. 85.000",
  "price_original": 120000,
  "price_note": "Harga promo terbatas",
  "palette": { "nama": "#hex" },
  "fonts": { "display": "...", "serif": "...", "sans": "..." },
  "features": ["fitur1", "fitur2", "fitur3", "fitur4", "fitur5"]
}
ASSETS_GUIDE.md
Tabel semua file di /static/themes/[namatema]/
Penjelasan cover.jpg vs demo_photos
Posisi setiap photos[0–3+] dalam layout
Checklist deployment
Warna palette + font lengkap
Sumber asset gratis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STANDAR KUALITAS FINAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Terasa seperti dibuat desainer profesional
Elemen dekoratif dibuat dengan CSS murni atau SVG inline
Typography hierarchy jelas dan intentional
Setiap section bisa berdiri sendiri sebagai scene yang indah
Test mental: "Kalau saya terima undangan nikah ini, apakah saya terharu dan excited?"

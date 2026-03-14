PROMPT MASTER \u2014 Tema Wedding Invitation Flask
UndanganKita v3 | Mental Canvas Spatial Edition
Copy-paste prompt di bawah ini setiap kali mau bikin tema baru.
Ganti semua bagian [...] sesuai keinginan sebelum dikirim.
PROMPT
Buatkan tema wedding invitation digital baru untuk app Flask UndanganKita v3.
Nama tema: [namatema] (huruf kecil, tanpa spasi, contoh: malambiru)
Judul tema: "[Judul Tema]" (nama tampil ke user, contoh: "Malam Biru")
Konsep / vibe: [deskripsikan feel-nya, contoh: dark moody oceanic, langit malam dengan bintang, nuansa biru tua dan silver, cinematic dan dramatis]
Output yang dibutuhkan: 2 file
[namatema].json \u2014 theme definition (ikuti struktur kalajingga.json)
[namatema].html \u2014 template Jinja2 untuk Flask, disimpan di templates/themes/[namatema].html
ATURAN TEKNIS WAJIB
Template Jinja2, variabel dari Flask: inv, theme, rsvp_list, gifts, photos, is_preview, photo_src(), wa_number, site_name
Sistem scroll: scroll-snap-type: y mandatory di html, tiap section scroll-snap-align: start; scroll-snap-stop: always; height: 100dvh \u2014 efeknya harus terasa seperti swipe bukan scroll biasa
Animasi: wajib pakai GSAP 3 via CDN (https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js + ScrollTrigger.min.js), setiap section masuk dengan animasi ScrollTrigger yang berbeda karakternya
Opening: ada overlay buka undangan full-screen yang latar belakangnya cover.webp dari static/themes/[namatema]/cover.webp, atau fallback ke inv.cover_photo
Music player floating (mute/unmute), baca dari inv.music_url
Nav dots di kanan layar sebagai section indicator
Lightbox untuk galeri foto \u2014 tiap foto masuk stagger dengan GSAP (opacity + translateY + scale + rotate per item, delay bertahap)
Countdown real-time (hari/jam/menit/detik) ke tanggal inv.resepsi_date atau inv.akad_date
RSVP submit ke POST /rsvp/{{ inv.id }} via fetch JSON, tampilkan sukses/error
Gift section: filter None/'None' di Jinja2 sebelum render \u2014 jangan display field yang nilainya None. Gunakan {% if g.bank_name and g.bank_name != 'None' %} dan {% if g.ewallet_type and g.ewallet_type != 'None' %}. Field account_name, account_number juga harus dicek. Ikon ewallet dinamis (GoPay \ud83d\udc9a, OVO \ud83d\udc9c, DANA \ud83d\udc99, ShopeePay \ud83e\udde1, dll via lowercase match).
Tombol salin nomor rekening/ewallet
JANGAN ada tombol "Kirim ucapan via WhatsApp" di bagian manapun
Preview mode: jika is_preview == True, langsung buka tanpa klik tombol
OG tags TIDAK perlu dimasukkan (sudah di-inject otomatis oleh Flask)
Semua CSS inline dalam 1 file HTML (tidak ada file terpisah), JS juga inline dalam 1 file HTML
\u2b50 EFEK WAJIB: MENTAL CANVAS SPATIAL PARALLAX (3D Layered Web)
Ini adalah fitur pembeda utama tema ini. Setiap section HARUS menggunakan sistem parallax berlapis seperti aplikasi Mental Canvas \u2014 bukan scroll biasa, tapi seperti kamera yang bergerak menelusuri ruang tiga dimensi.
Konsep Inti: "Spatial Drawing di Web"
Efek 3D bukan dari model 3D, melainkan dari elemen 2D yang ditempatkan di kedalaman berbeda menggunakan CSS transform: translateZ() dan perspective. Ketika kamera (viewport) bergerak, elemen di depan bergerak lebih cepat dari elemen di belakang \u2014 ini disebut parallax depth illusion.
Implementasi Teknis Wajib
1. Scene Container dengan CSS Perspective
Setiap section yang punya efek spatial HARUS pakai struktur ini:
.scene {
  perspective: 800px;
  perspective-origin: 50% 50%;
  transform-style: preserve-3d;
  overflow: hidden;
}
.layer {
  position: absolute;
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;
  will-change: transform;
}
/* Sistem kedalaman layer (Z-axis) */
.layer-bg     { transform: translateZ(-200px) scale(1.35); } /* paling jauh */
.layer-mid    { transform: translateZ(-80px)  scale(1.12); } /* tengah */
.layer-fore   { transform: translateZ(0px)    scale(1);    } /* netral */
.layer-front  { transform: translateZ(60px)   scale(0.92); } /* paling dekat */
2. Mouse/Gyro Parallax (Wajib di Hero & Penutup)
Gunakan JavaScript untuk mendeteksi gerakan mouse/tilt dan menggeser setiap layer dengan intensitas berbeda:
// Parallax mouse \u2014 tiap layer punya speed berbeda
document.addEventListener('mousemove', (e) => {
  const cx = window.innerWidth / 2;
  const cy = window.innerHeight / 2;
  const dx = (e.clientX - cx) / cx; // -1 sampai 1
  const dy = (e.clientY - cy) / cy;

  // Layer paling depan: bergerak paling banyak
  gsap.to('.layer-front', { x: dx * 25, y: dy * 15, duration: 0.8, ease: 'power2.out' });
  // Layer tengah: bergerak sedang
  gsap.to('.layer-mid',   { x: dx * 12, y: dy * 8,  duration: 0.9, ease: 'power2.out' });
  // Layer belakang: bergerak sedikit
  gsap.to('.layer-bg',    { x: dx * 4,  y: dy * 3,  duration: 1.0, ease: 'power2.out' });
});

// Gyroscope untuk mobile
if (window.DeviceOrientationEvent) {
  window.addEventListener('deviceorientation', (e) => {
    const dx = e.gamma / 45; // -1 sampai 1
    const dy = e.beta  / 45;
    gsap.to('.layer-front', { x: dx * 20, y: dy * 12, duration: 0.6, ease: 'power2.out' });
    gsap.to('.layer-mid',   { x: dx * 10, y: dy * 6,  duration: 0.7, ease: 'power2.out' });
    gsap.to('.layer-bg',    { x: dx * 3,  y: dy * 2,  duration: 0.8, ease: 'power2.out' });
  });
}
3. ScrollTrigger Parallax per Section (Wajib)
Saat scroll dari section ke section, tiap layer bergerak dengan kecepatan berbeda menggunakan GSAP ScrollTrigger scrub:
// Di setiap section yang punya layers:
gsap.to('#hero .layer-bg', {
  scrollTrigger: { trigger: '#hero', start: 'top top', end: 'bottom top', scrub: 1.5 },
  y: '-20%',   // bergerak lambat (paling jauh)
});
gsap.to('#hero .layer-mid', {
  scrollTrigger: { trigger: '#hero', start: 'top top', end: 'bottom top', scrub: 1 },
  y: '-45%',   // bergerak sedang
});
gsap.to('#hero .layer-front', {
  scrollTrigger: { trigger: '#hero', start: 'top top', end: 'bottom top', scrub: 0.6 },
  y: '-70%',   // bergerak cepat (paling dekat)
});
4. Transisi Antar Section: "Camera Travel"
Saat pindah dari satu section ke section berikutnya, buat ilusi kamera yang berjalan menembus ruang \u2014 bukan sekadar scroll biasa:
// Setiap section baru masuk dengan efek "zoom from depth"
gsap.fromTo('#s-quran .scene-content',
  { opacity: 0, scale: 0.85, z: -150 },  // datang dari kejauhan
  {
    scrollTrigger: { trigger: '#s-quran', start: 'top 80%' },
    opacity: 1, scale: 1, z: 0,
    duration: 1.4, ease: 'power3.out'
  }
);
5. Susunan Layer per Section (Panduan)
Gunakan panduan ini untuk menentukan apa yang masuk ke layer mana:
Layer
Z-depth
Isi yang cocok
layer-bg
Paling jauh
Background tekstur, foto couple, langit, gradien
layer-mid
Tengah
Bunga, ornamen dekorasi, teks sekunder
layer-fore
Netral
Konten utama (nama, info acara)
layer-front
Paling dekat
Particle, dedaunan, elemen UI
Contoh pada Hero Section (4 layer):
layer-bg: foto cover / gradien background
layer-mid: ilustrasi bunga / ornamen botanical di kiri-kanan
layer-fore: nama pengantin + tanggal (teks utama)
layer-front: partikel (kelopak / debu / bintang), elemen kecil dekoratif
Contoh pada Couple Section (3 layer):
layer-bg: warna/tekstur background
layer-mid: foto portrait mempelai (tengah, sedikit lebih lambat dari teks)
layer-fore: nama, info orang tua (teks di depan foto)
6. Depth of Field Illusion (CSS)
Tambahkan blur yang mengecil sesuai kedalaman layer untuk memperkuat efek 3D:
.layer-bg   { filter: blur(1.5px); }  /* jauh = sedikit blur */
.layer-mid  { filter: blur(0px); }   /* tengah = tajam */
.layer-fore { filter: blur(0px); }   /* depan = tajam */
.layer-front { filter: blur(0.5px); } /* sangat depan = sedikit blur juga */
/* Blur dihapus on hover untuk efek focus */
.scene:hover .layer-bg { filter: blur(2px); transition: filter 0.8s; }
7. Section Khusus: "Parallax Zoom-In Text" (Wajib di Ayat Al-Quran)
Teks Arab tampil sangat besar di layer belakang (blur, transparan) dan terjemah teks ada di layer depan. Saat scroll, teks Arab bergerak ke atas lebih lambat (seperti berpapasan dengan kamera):
gsap.to('#s-quran .arabic-watermark', {
  scrollTrigger: { trigger: '#s-quran', start: 'top bottom', end: 'bottom top', scrub: 2 },
  y: '-30%', scale: 1.1, opacity: 0.08
});
gsap.to('#s-quran .translation-text', {
  scrollTrigger: { trigger: '#s-quran', start: 'top bottom', end: 'bottom top', scrub: 0.8 },
  y: '-60%'
});
8. Performance Wajib
Gunakan will-change: transform hanya pada elemen yang dianimasi
Gunakan transform: translateZ(0) untuk force GPU layer pada elemen statis
Nonaktifkan mouse parallax saat section tidak visible (pakai IntersectionObserver)
Untuk mobile: kurangi jumlah layer menjadi 2 (cukup bg + fore) dan nonaktifkan depth-of-field blur
LAYOUT & URUTAN SECTION (10 section, kreatif urutannya)
Wajib ada: Hero/cover, Ayat Al-Quran, Profil pasangan (dengan foto portrait groom & bride), Info acara + countdown, Kisah cinta, Galeri foto, Lokasi + peta, RSVP, Hadiah digital, Penutup. Urutannya bebas \u2014 sesuaikan mana yang paling dramatis dan natural flow-nya untuk konsep tema ini.
Kasih footer untuk paling bawah: "Dibuat dengan \u2764 oleh habarkita.com, pesan undangan digital sekarang." (atau sesuaikan biar ga ngeganggu undangan user)
Usahakan setiap tema punya design yang BERBEDA-BEDA \u2014 tidak pakai 1 template yang sama terus. Variasikan layout, susunan elemen, dan cara parallax diterapkan per tema.
DESIGN DIRECTION
Konsep visual: [jelaskan lebih detail, misal: dominan warna navy #0A1628 dan silver #C0C0C0, background texture seperti kulit malam, bintang-bintang kecil berkedip sebagai particle, font display Playfair Display, font sans Outfit]
Perbedaan dari tema sebelumnya: [sebutkan apa yang harus beda dari tema yang sudah ada, misal: layout pasangan horizontal bukan portrait, section quran ada parallax teks, galeri pakai horizontal scroll masonry, penutup ada animasi teks typewriter]
Tingkat kemewahan: sangat mewah, bukan template biasa \u2014 setiap section harus terasa seperti karya desain bukan web generik
Animasi harus semakin epic dan emosional setiap scroll ke bawah, bukan seragam dari atas ke bawah
Particle system ambient harus sesuai tema (bintang, debu emas, kelopak, dan sebagainya)
Parallax depth: setiap section minimal punya 3 layer kedalaman yang terasa berbeda ketika mouse digerakkan atau saat scroll
Spesifikasi cover.webp: sebutkan ukuran ideal dan max KB yang direkomendasikan untuk tema ini.
Assets tambahan (JS/font/dll): sebutkan CDN link kalau perlu library tambahan selain GSAP. Jika ada file yang perlu diunduh dan disimpan offline di static/themes/[namatema]/, sebutkan URL-nya.
Jika assets lebih aman diunduh offline, berikan link + path-nya yang akan disimpan ke /static/themes/namatema/allfile.
REFERENSI VARIABEL FLASK
Semua variabel ini tersedia di dalam template:
Variabel
Tipe
Isi
inv.id
string
ID unik undangan
inv.groom_name
string
Nama panggilan pria
inv.bride_name
string
Nama panggilan wanita
inv.groom_full
string
Nama lengkap pria
inv.bride_full
string
Nama lengkap wanita
inv.groom_parents
string
Nama orang tua pria
inv.bride_parents
string
Nama orang tua wanita
inv.show_parents
int (0/1)
Tampilkan nama orang tua?
inv.groom_photo_url
string/None
URL foto portrait pria
inv.bride_photo_url
string/None
URL foto portrait wanita
inv.akad_date
string YYYY-MM-DD
Tanggal akad
inv.akad_time
string HH:MM
Jam akad
inv.akad_venue
string
Nama venue akad
inv.akad_address
string
Alamat akad
inv.resepsi_date
string YYYY-MM-DD
Tanggal resepsi
inv.resepsi_time
string HH:MM
Jam resepsi
inv.resepsi_venue
string
Nama venue resepsi
inv.resepsi_address
string
Alamat resepsi
inv.maps_url
string
URL Google Maps
inv.maps_embed
string
Embed src URL peta
inv.maps_embed_html
string (HTML)
<iframe> siap pakai
inv.love_story
string
Cerita cinta pasangan
inv.music_url
string/None
URL file musik
inv.cover_photo
string/None
Filename foto cover upload
inv.expires_at
string
Tanggal expired
is_preview
bool
True = mode preview admin
photos
list[Row]
Daftar foto galeri
rsvp_list
list[Row]
Daftar RSVP masuk
gifts
list[Row]
Data rekening/ewallet
theme
dict
Data tema dari JSON
photo_src(photo)
func
Return URL foto
wa_number
string
Nomor WA admin (jangan dipakai untuk tombol WA tamu)
site_name
string
Nama website
Filter Jinja2 tersedia:
{{ inv.resepsi_date | format_date }} \u2192 "Sabtu, 20 Desember 2025"
{{ inv.resepsi_date | days_left }} \u2192 angka hari tersisa
Akses foto:
{% for photo in photos %}
  <img src="{{ photo_src(photo) }}" alt="Foto {{ loop.index }}">
{% endfor %}
Akses gifts (wajib filter None):
{% for g in gifts %}
  {% if g.bank_name and g.bank_name != 'None' %}
    {# Transfer bank \u2014 tampilkan card bank #}
  {% endif %}
  {% if g.ewallet_type and g.ewallet_type != 'None' %}
    {# E-wallet \u2014 tampilkan card ewallet #}
  {% endif %}
{% endfor %}
IDE KONSEP TEMA (Tinggal Pilih & Kustomisasi)
Nama Ide
Vibe
Warna Kunci
Particle
Parallax Style
Malam Emas
Dark luxury, royal, dramatic
#0D0A06 + #C9A96E
Bintang berkedip
Langit jauh + dekorasi tengah + teks depan
Fajar Suci
Soft, sakral, morning light
#FFF8F0 + #E8C99A
Sinar cahaya
Cahaya bg + bunga tengah + teks depan
Hutan Hujan
Organic, earthy, lush
#1A2E1A + #8B7355
Partikel daun
Hutan jauh + ranting tengah + kabut depan
Langit Merah
Bold, sunset, cinematic
#1A0A06 + #C44B2A
Bara api
Langit senja + siluet + teks terbakar
Kertas Lama
Vintage, sepia, intimate
#2C2010 + #D4A96A
Dust partikel
Kertas jauh + ornamen tua + teks tinta
Samudra Tenang
Navy, serene, elegant
#050F1A + #8BA8C4
Bubble melayang
Laut dalam + gelombang + buih depan
Bunga Kering
Muted rose, botanical
#1E1518 + #C4827A
Kelopak jatuh
Background muted + bouquet + kelopak depan
Perak Dingin
Silver, modern luxury
#0A0A12 + #B8C4D4
Kristal salju
Salju jauh + kristal tengah + frost depan
Tanah Merah
Terracotta, warm earth
#1C0E08 + #C46A3A
Pasir melayang
Tanah + tekstur + pasir beterbangan
Kabut Pagi
Dreamy, misty, soft
#F0EDE8 + #9B8E84
Mist partikel
Background mist + bunga + embun depan
TIPS VARIASI LAYOUT BIAR GA MONOTON
Layout Pasangan:
Portrait vertikal berdampingan \u2014 foto di layer-mid, teks di layer-fore
Full-width horizontal split kiri-kanan \u2014 foto kiri di layer-bg, foto kanan di layer-mid
Overlap center \u2014 foto overlap di layer-mid, nama besar di layer-fore
Circular frame dengan ornamen border animasi di layer-front
Layout Galeri:
Grid mosaic (besar-kecil, baris 1 double)
Horizontal scroll carousel dengan setiap foto masuk stagger
Polaroid stack dengan efek t

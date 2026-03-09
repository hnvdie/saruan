uatkan tema wedding invitation digital baru untuk proyek Flask saya.
Buat BENAR-BENAR UNIK — bukan template. Ini karya, bukan form.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## KONTEKS PROYEK FLASK
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
- photos[0] = foto couple/bersama
- photos[1] = foto mempelai pria
- photos[2] = foto mempelai wanita
- photos[3+] = foto tambahan

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
## INPUT TEMA — KAMU YANG TENTUKAN SEPENUHNYA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Kamu bebas dan WAJIB menciptakan tema yang benar-benar baru setiap kali prompt ini dijalankan.
Jangan tanya, jangan minta konfirmasi — langsung eksekusi dengan keputusan kreatif penuh.

Tentukan sendiri secara acak dan unik:
- Nama tema       : ciptakan nama orisinal (bukan kata generik seperti "Elegant" atau "Classic")
- Konsep & mood   : pilih sesuatu yang belum pernah ada di wedding invitation digital — bisa dari dunia arsitektur, sinema, alam, sains, folklore, era sejarah, subkultur, dll
- Palet warna     : tentukan 4–6 warna yang kohesif dan tidak klise (hindari kombinasi hitam-emas, putih-pink, krem-coklat yang sudah terlalu umum — kecuali dieksekusi dengan cara yang benar-benar segar)
- Referensi visual: gabungkan minimal 2 referensi dari dunia berbeda (contoh: "Art Nouveau × deep sea bioluminescence" atau "1970s Soviet constructivism × cherry blossom")
- Cover asset     : deskripsikan gambar cover.jpg yang ideal untuk tema ini
- Custom assets   : tentukan semua asset pendukung yang dibutuhkan

ATURAN KREATIVITAS:
- Setiap output HARUS terasa seperti dari desainer berbeda dengan tangan berbeda
- Tidak boleh ada pola visual, layout, atau color story yang mirip dengan tema manapun yang pernah ada
- Jika kamu merasa tema ini "aman" atau "familiar" — buang dan mulai ulang dengan sesuatu yang lebih berani
- Surprise yourself.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## FILOSOFI DESAIN — BACA INI DENGAN SERIUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Setiap tema harus terasa seperti karya baru dari nol.
Berikut adalah LARANGAN KERAS yang tidak boleh diulang antar tema:

LAYOUT:
- DILARANG urutan section yang selalu sama (hero → quran → couple → story → events → countdown → gallery → rsvp → gift → closing)
- BEBAS reorder, gabungkan, pisahkan, atau ciptakan section baru yang tidak ada di tema lain
- BEBAS buat layout yang tidak konvensional: full-bleed split, diagonal cut, overlapping layers, sticky panels, horizontal scroll dalam section, dll

FOTO:
- DILARANG memperlakukan semua foto hanya sebagai gallery grid
- Foto bisa menjadi: background parallax, cutout floating, split-screen dengan teks, masked shape (lingkaran/hexagon/organic blob), foto yang "bocor" keluar dari container, collage bertumpuk, strip film, polaroid acak, dll
- photos[0] tidak harus selalu di hero — bisa muncul di mana saja secara dramatis
- Foto boleh tampil fragmented, dipotong sebagian, atau dijadikan texture

SECTION IDENTITY:
- Setiap section WAJIB punya visual DNA sendiri yang tidak mirip section lain dalam tema yang sama
- Alternasi gelap-terang boleh dibuang jika ada konsep yang lebih kuat
- Boleh ada section yang "tidak biasa": section berupa satu kalimat besar fullscreen, section berupa hanya foto + nama, section yang terasa seperti poster, dll

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## FITUR WAJIB — SEMUA HARUS ADA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Konten (tidak harus urut, tidak harus satu section per item):
✦ Envelope/cover intro (wajib pakai cover.jpg sebagai fullscreen background)
✦ Nama mempelai + tanggal pernikahan
✦ Ayat Al-Quran QS. Ar-Rum: 21 (Arabic + terjemahan)
✦ Profil mempelai pria & wanita (nama lengkap + orang tua)
✦ Love story ({{ inv.love_story }})
✦ Detail acara: akad nikah + resepsi (tanggal, waktu, venue, alamat)
✦ Google Maps link + embed iframe
   - Untuk link: <a href="{{ inv.maps_url }}">
   - Untuk embed: gunakan {{ inv.maps_embed_html | safe }} — JANGAN buat <iframe> sendiri dengan src="{{ inv.maps_embed }}"
✦ Countdown timer real-time (hari / jam / menit / detik)
✦ Galeri / penempatan foto kreatif
✦ RSVP form (nama, kehadiran, jumlah tamu, pesan)
✦ Gift section (bank + e-wallet dari gifts loop, dengan copy button)
✦ Guestbook (dari rsvp_list + append real-time saat RSVP berhasil)
✦ Music player floating (autoplay setelah envelope dibuka)
✦ Closing / penutup

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## ANIMASI — INI YANG MEMBUAT TEMA HIDUP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AMBIENT / BACKGROUND:
- Wajib ada 1 sistem partikel/canvas unik yang sesuai tema (bukan sakura copas)
  Contoh: debu cahaya, percikan api, bintang jatuh, gelembung, daun melayang organic, kristal, dll
- Boleh ada animated gradient, noise texture bergerak, atau SVG path yang berjalan

ENVELOPE INTRO:
- Efek buka undangan harus DRAMATIS dan tidak generik
- Contoh ide: layar split ke kiri-kanan, cover zoom out dramatis, curtain reveal, morphing shape, iris transition, cover yang "terbakar" keluar, dll
- Bukan sekadar fade out

SCROLL ANIMATIONS (IntersectionObserver):
- Setiap section punya entrance yang berbeda — tidak boleh semua translateY
- Gunakan variasi: clip-path wipe, scale dari center, skew straighten, blur-to-sharp, letter-by-letter text reveal, stagger dari kiri/kanan/bawah secara bergantian
- Elemen dalam satu section boleh punya stagger delay yang berbeda

CONTINUOUS / AMBIENT ANIMATIONS:
- Ada elemen yang terus bergerak sepanjang halaman terbuka
- Contoh: ornamen yang breathing (scale pulse), garis yang berjalan, teks yang shimmer, border yang trace, foto yang floating subtle

INTERAKTIF:
- Hover state pada semua elemen yang bisa diklik harus terasa premium
- Tombol: ripple, magnetic, fill-from-cursor, atau glow effect
- Foto: scale + brightness + shadow pada hover
- Card: lift + shadow depth

TEKNIS:
- Semua animasi menggunakan transform & opacity (GPU-friendly, 60fps)
- Custom cubic-bezier — tidak boleh pakai ease/linear/ease-in-out bawaan saja
- CSS @keyframes untuk looping, JS requestAnimationFrame untuk canvas
- Stagger JS: setiap nth-child dapat delay berbeda secara dinamis
- Tidak boleh pakai library animasi eksternal (GSAP, AOS, dll) — pure CSS + JS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## OUTPUT YANG DIBUTUHKAN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. [namatema].html
   - Single file, CSS + JS inline
   - Jinja2 template lengkap
   - Kode bersih, diberi komentar per section
   - Max-width 480px, mobile-first

2. [namatema].json
   Struktur:
   {
     "id": "namatema",
     "name": "Nama Tema",
     "description": "...",
     "preview_color": "#hex",
     "accent_color": "#hex",
     "skeleton": "namatema",
     "tags": [...],
     "demo_photos": ["/static/themes/namatema/hbner.jpg"],
     "price": 85000,
     "price_label": "Rp. 85.000",
     "price_original": 120000,
     "price_note": "...",
     "palette": { "nama": "#hex", ... },
     "fonts": { "display": "...", "serif": "...", "sans": "..." },
     "features": [...]
   }

3. ASSETS_GUIDE.md
   Wajib mencakup:
   - Tabel semua file yang dibutuhkan di /static/themes/[namatema]/
   - Setiap file: nama file, ukuran ideal, format, max size, deskripsi konten, tips
   - Penjelasan cover.jpg: apakah pakai foto dari user atau generated/illustrated
   - Penjelasan posisi setiap photos[0–3+] dalam layout tema ini (karena tidak selalu gallery)
   - Checklist deployment
   - Warna palette lengkap dengan kode hex
   - Sumber asset gratis yang disarankan (Unsplash, Freepik, Freesound, dll)
   - Panduan jika user ingin ganti custom assets sendiri

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## STANDAR KUALITAS FINAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- Tema ini harus terasa seperti dibuat oleh desainer profesional yang terobsesi dengan detail
- Jika ada elemen dekoratif (garis, shape, ornamen), buat dengan CSS murni atau SVG inline — jangan skip
- Typography hierarchy harus jelas dan intentional — pilih Google Fonts yang tepat untuk tema
- Setiap section harus bisa berdiri sendiri sebagai "scene" yang indah jika di-screenshot
- Jangan ada section yang terasa "belum selesai" atau "placeholder feel"
- Tema ini harus bisa langsung dipakai tanpa modifikasi CSS tambahan

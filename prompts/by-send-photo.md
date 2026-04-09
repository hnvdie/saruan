TUGAS: Buat template undangan digital berbasis Flask + Jinja2. Design harus mengikuti 100% referensi gambar yang diberikan user.

Gunakan semua data berikut di dalam template:

{{ inv.groom_name }}, {{ inv.bride_name }} {{ inv.groom_full }}, {{ inv.bride_full }} {{ inv.groom_parents }}, {{ inv.bride_parents }} {{ inv.show_parents }} {{ inv.akad_date | format_date }}, {{ inv.akad_time }} {{ inv.akad_venue }}, {{ inv.akad_address }} {{ inv.resepsi_date | format_date }}, {{ inv.resepsi_time }} {{ inv.resepsi_venue }}, {{ inv.resepsi_address }} {{ inv.maps_url }}, {{ inv.maps_embed_html }} {{ inv.love_story }} {{ inv.id }} {{ inv.music_url }}


Tambahkan cover pembuka sebelum seluruh isi undangan.
Cover ini bersifat sebagai gerbang awal (tidak boleh langsung menampilkan isi undangan).
Struktur cover:
Fullscreen
Background menggunakan photos[0] jika ada, jika tidak gunakan photos lain atau fallback warna
Menampilkan nama mempelai
Menampilkan nama tamu jika tersedia
Tambahkan tombol: "Buka Undangan"
Perilaku:
Saat pertama dibuka, hanya cover yang terlihat
Konten undangan disembunyikan
Setelah tombol "Buka Undangan" diklik, baru konten utama muncul
Tidak boleh auto masuk tanpa klik
Transisi:
Gunakan efek animasi berbeda beda tergantung bagusnya bagaimana
Tujuan:
Memberikan pengalaman seperti membuka amplop undangan

tidak ada highlight berwarna biru ditemplate ini.

Gunakan foto dengan pembagian fungsi yang jelas:

{{ inv.groom_photo_url }} {{ inv.bride_photo_url }}

Foto ini adalah portrait resmi mempelai, digunakan khusus untuk section profil. Jangan digunakan sebagai elemen dekoratif atau background. Jika tidak tersedia, baru boleh fallback ke photos.

Gallery:
{% if photos %}{% for p in photos %}{{ photo_src(p) }}{% endfor %}{% endif %}

Gunakan photos sebagai elemen desain, bukan sebagai list atau grid biasa.

Aturan penggunaan photos:

- photos[0] sebagai visual utama jika dibutuhkan (hero / cover)
- photos[1+] sebagai elemen pendukung

Penempatan harus manual mengikuti kebutuhan design, contoh:

- background section
- image di love story
- elemen collage / layering
- bentuk custom (arch, circle, dll)

Jika foto sedikit:

- boleh reuse dengan variasi (crop, zoom, opacity, blur)

Jika foto banyak:

- pilih yang paling relevan
- tidak semua wajib ditampilkan

Jangan membuat gallery grid standar. Loop hanya boleh digunakan jika benar-benar diperlukan (misalnya slider kecil), bukan sebagai tampilan utama.

Gift: {% for gift in gifts %}gift.bank_name gift.account_number gift.account_name gift.ewallet_type gift.ewallet_number gift.ewallet_name{% endfor %}

RSVP: {% for r in rsvp_list %}{{ r.guest_name }}, {{ r.message }}{% endfor %} POST ke /rsvp/{{ inv.id }}

Gunakan maps embed berikut: {{ inv.maps_embed_html | safe }}

Tambahkan cover nama tamu jika ada: {% if nama_tamu %}
Kepada Yth:

{{ nama_tamu }}

{% endif %}

terus diakhir dikasih "Dibuat dengan (love icon) oleh habarkita.com"

Selain HTML, hasilkan juga file JSON dengan struktur berikut:

{
"id": "",
"name": "",
"description": "",
"preview_color": "",
"accent_color": "",
"skeleton": "",
"tags": [],
"demo_photos": [],
"price": "",
"price_label": "",
"price_original": "",
"price_note": "",
"palette": {},
"fonts": {},
"features": []
}

Output yang dihasilkan harus berupa HTML (Jinja), JSON, dan ASSETS_GUIDE.md. kirim dalam format namatema.html dan namatema.json.


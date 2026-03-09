# Celestial Bloom - Assets Guide

## 📋 Overview

Tema **Celestial Bloom** adalah tema undangan pernikahan dengan konsep "Dreamy Night Garden" — perpaduan antara langit malam berbintang dengan kelembutan bunga-bunga yang melayang. Panduan ini menjelaskan semua asset yang dibutuhkan dan cara penggunaannya.

---

## 🎨 Color Palette

| Nama | Hex | Usage |
|------|-----|-------|
| Midnight | `#0F172A` | Background utama |
| Midnight Light | `#1E293B` | Card backgrounds, overlays |
| Blush | `#F8E1E7` | Teks sekunder, accents |
| Blush Deep | `#F5D0D9` | Labels, meta text |
| Champagne | `#D4AF37` | Primary accent, headings, icons |
| Champagne Light | `#E8D5A3` | Hover states, highlights |
| Ivory | `#FFFBF5` | Primary text |
| Ivory Dark | `#F5F0E8` | Secondary text |

---

## 📁 Required Assets

### Struktur Folder

```
/static/themes/celestialbloom/
├── cover.jpg              (WAJIB - Background envelope)
├── couple.jpg             (WAJIB - Hero background)
├── groom.jpg              (WAJIB - Profile groom)
├── bride.jpg              (WAJIB - Profile bride)
├── gallery1.jpg           (WAJIB - Gallery utama)
├── gallery2.jpg           (WAJIB - Gallery)
├── gallery3.jpg           (WAJIB - Gallery)
├── gallery4.jpg           (WAJIB - Gallery)
├── music.mp3              (Opsional - Background music)
├── placeholder-groom.jpg  (Fallback)
└── placeholder-bride.jpg  (Fallback)
```

---

## 📸 Detailed Asset Specifications

### 1. cover.jpg

| Property | Specification |
|----------|---------------|
| **Usage** | Background fullscreen envelope intro |
| **Dimensions** | 1080 x 1920 px (9:16 portrait) |
| **Format** | JPG |
| **Max Size** | 500 KB |
| **Quality** | 80-85% |
| **Content** | Foto couple bersama, romantic pose |
| **Style** | Soft lighting, bisa outdoor sunset/golden hour atau indoor elegant |
| **Treatment** | Akan diberi overlay gelap otomatis oleh CSS |

**Tips:**
- Pilih foto yang memiliki ruang kosong di tengah untuk teks
- Hindari foto yang terlalu busy/ramai
- Warna foto akan di-adjust oleh overlay, jadi tidak masalah jika tidak match palette

---

### 2. couple.jpg

| Property | Specification |
|----------|---------------|
| **Usage** | Hero section background (fullscreen) |
| **Dimensions** | 1080 x 1920 px (9:16 portrait) |
| **Format** | JPG |
| **Max Size** | 600 KB |
| **Quality** | 80-85% |
| **Content** | Foto couple bersama, full body atau 3/4 |
| **Style** | Elegant, romantic, bisa pre-wedding atau engagement |
| **Position** | Subjek sebaiknya di bagian atas 60% gambar |

**Tips:**
- Foto ini akan memiliki parallax effect saat scroll
- Gradient overlay akan muncul dari bawah, jadi pastikan subjek tidak terlalu di bawah

---

### 3. groom.jpg

| Property | Specification |
|----------|---------------|
| **Usage** | Profile card groom (split screen) |
| **Dimensions** | 600 x 800 px (3:4 portrait) |
| **Format** | JPG |
| **Max Size** | 300 KB |
| **Quality** | 80% |
| **Content** | Foto mempelai pria, solo portrait |
| **Style** | Formal atau semi-formal, elegant |
| **Background** | Bersih, bisa solid atau blur |

**Tips:**
- Foto akan diberi efek grayscale 30% secara default
- Pada hover, grayscale akan hilang
- Frame berwarna gold akan muncul di sekitar foto

---

### 4. bride.jpg

| Property | Specification |
|----------|---------------|
| **Usage** | Profile card bride (split screen) |
| **Dimensions** | 600 x 800 px (3:4 portrait) |
| **Format** | JPG |
| **Max Size** | 300 KB |
| **Quality** | 80% |
| **Content** | Foto mempelai wanita, solo portrait |
| **Style** | Formal atau semi-formal, elegant |
| **Background** | Bersih, bisa solid atau blur |

**Tips:**
- Sama dengan groom.jpg
- Posisi frame akan sedikit berbeda (rotasi mirror)

---

### 5. gallery1.jpg - gallery4.jpg

| Property | Specification |
|----------|---------------|
| **Usage** | Gallery collage (creative layout) |
| **Dimensions** | 800 x 600 px (4:3) atau 800 x 800 px (1:1) |
| **Format** | JPG |
| **Max Size** | 250 KB each |
| **Quality** | 75-80% |
| **Content** | Foto couple, candid, detail, atau moments |
| **Style** | Variasi: wide shot, close up, detail, candid |

**Layout Gallery:**
```
+------------------+
|    gallery1      |  ← Full width, landscape (16:10)
|   (16:10 ratio)  |
+--------+--------+
|gallery2|gallery3|  ← 2 square photos side by side
| (1:1)  |  (1:1) |
+------------------+
|    gallery4      |  ← Full width, landscape (16:9)
|   (16:9 ratio)   |
+------------------+
```

**Tips:**
- gallery1: Pilih foto landscape yang impactful
- gallery2 & 3: Pilih foto square yang complement each other
- gallery4: Pilih foto landscape dengan komposisi berbeda dari gallery1

---

### 6. music.mp3 (Opsional)

| Property | Specification |
|----------|---------------|
| **Usage** | Background music (autoplay setelah envelope dibuka) |
| **Format** | MP3 |
| **Max Size** | 5 MB |
| **Duration** | 2-5 minutes (looping) |
| **Style** | Romantic instrumental, acoustic, atau piano |
| **Volume** | Normalize to -14 LUFS |

**Rekomendasi Genre:**
- Acoustic guitar instrumental
- Piano romantic
- String quartet
- Jazz soft

**Sumber Gratis (Royalty Free):**
- YouTube Audio Library
- Free Music Archive
- Incompetech
- Bensound

---

## 🖼️ Placeholder Images

Jika foto tidak tersedia, tema akan menggunakan placeholder. Anda bisa membuat:

- `placeholder-groom.jpg` - Siluet atau gambar default untuk groom
- `placeholder-bride.jpg` - Siluet atau gambar default untuk bride

**Ukuran:** Sama dengan foto asli (600 x 800 px)

---

## 🎨 Cover Image Guidelines

### Opsi 1: Menggunakan Foto dari User (REKOMENDASI)

Foto couple dengan kriteria:
- **Lighting**: Soft, golden hour preferred
- **Pose**: Romantic, bisa berdampingan atau berpelukan
- **Background**: Tidak terlalu ramai, bisa nature atau elegant indoor
- **Composition**: Portrait orientation, subjek di tengah

### Opsi 2: Generated/Illustrated Cover

Jika tidak ada foto couple yang sesuai, bisa menggunakan:
- Illustrasi floral dengan background night sky
- Watercolor painting style
- Digital art dengan tema celestial + floral

**Spesifikasi Illustrasi:**
- Background: Deep midnight blue dengan stars
- Foreground: Soft blush pink flowers (peonies/roses)
- Accent: Gold/champagne sparkles atau light rays
- Style: Dreamy, ethereal, romantic

---

## ✅ Deployment Checklist

Sebelum deploy, pastikan:

- [ ] `cover.jpg` ada dan ukuran < 500 KB
- [ ] `couple.jpg` ada dan ukuran < 600 KB
- [ ] `groom.jpg` ada dan ukuran < 300 KB
- [ ] `bride.jpg` ada dan ukuran < 300 KB
- [ ] `gallery1.jpg` - `gallery4.jpg` ada dan ukuran < 250 KB each
- [ ] Semua foto sudah di-compress (gunakan TinyPNG atau Squoosh)
- [ ] `music.mp3` ada (opsional) dan ukuran < 5 MB
- [ ] Semua file di folder `/static/themes/celestialbloom/`
- [ ] Test di mobile device (iOS Safari & Android Chrome)
- [ ] Test autoplay music (catat: beberapa browser block autoplay)

---

## 🛠️ Custom Asset Instructions

### Mengganti Asset Sendiri

1. **Siapkan foto** sesuai spesifikasi di atas
2. **Compress foto** menggunakan:
   - [TinyPNG](https://tinypng.com/) untuk JPG/PNG
   - [Squoosh](https://squoosh.app/) untuk advanced compression
3. **Rename file** sesuai nama yang diperlukan
4. **Upload ke folder** `/static/themes/celestialbloom/`
5. **Clear browser cache** dan test

### Menggunakan Photo Upload dari Database

Tema ini support foto dinamis dari database Flask:

```jinja2
{# Foto couple dari database #}
{{ photo_src(photos[0]) }}

{# Foto groom dari database #}
{{ photo_src(photos[1]) }}

{# Foto bride dari database #}
{{ photo_src(photos[2]) }}

{# Gallery foto dari database #}
{% for photo in photos %}
    {{ photo_src(photo) }}
{% endfor %}
```

Jika foto dari database tidak tersedia, tema akan otomatis fallback ke file di folder static.

---

## 📚 Free Asset Resources

### Stock Photos (Free for Commercial Use)

| Resource | URL | Notes |
|----------|-----|-------|
| Unsplash | https://unsplash.com | High quality, CC0 |
| Pexels | https://pexels.com | Free, no attribution |
| Pixabay | https://pixabay.com | Large collection |
| Stocksnap | https://stocksnap.io | CC0 license |

**Keywords untuk search:**
- "couple romantic night"
- "wedding couple elegant"
- "bride portrait"
- "groom portrait"
- "pre wedding photography"
- "engagement photoshoot"

### Music (Royalty Free)

| Resource | URL | Notes |
|----------|-----|-------|
| YouTube Audio Library | https://youtube.com/audiolibrary | Free, various genres |
| Free Music Archive | https://freemusicarchive.org | CC licenses |
| Incompetech | https://incompetech.com | Kevin MacLeod's music |
| Bensound | https://bensound.com | Free with attribution |

---

## 🔧 Image Optimization Commands

### Using ImageMagick (Command Line)

```bash
# Resize and compress cover.jpg
convert cover.jpg -resize 1080x1920^ -gravity center -extent 1080x1920 -quality 85 cover.jpg

# Resize and compress couple.jpg
convert couple.jpg -resize 1080x1920^ -gravity center -extent 1080x1920 -quality 85 couple.jpg

# Resize and compress profile photos
convert groom.jpg -resize 600x800^ -gravity center -extent 600x800 -quality 80 groom.jpg
convert bride.jpg -resize 600x800^ -gravity center -extent 600x800 -quality 80 bride.jpg

# Resize and compress gallery
convert gallery1.jpg -resize 800x600 -quality 75 gallery1.jpg
```

### Using cjpeg (MozJPEG)

```bash
# High quality compression
cjpeg -quality 85 -outfile cover.jpg cover-original.jpg
```

---

## 📱 Testing Checklist

Test tema dengan asset Anda:

- [ ] Envelope terbuka dengan smooth animation
- [ ] Cover image muncul dengan baik
- [ ] Tidak ada layout shift saat load
- [ ] Gallery images load dengan benar
- [ ] Profile photos muncul di posisi yang benar
- [ ] Tidak ada broken image
- [ ] Music autoplay (jika diizinkan browser)
- [ ] Countdown timer berjalan
- [ ] Copy button di gift section berfungsi
- [ ] RSVP form berfungsi

---

## 🐛 Troubleshooting

### Issue: Foto tidak muncul
**Solution:** 
- Cek path file
- Cek nama file (case sensitive)
- Cek format file (harus .jpg)

### Issue: Load time lambat
**Solution:**
- Compress foto lebih agresif
- Kurangi ukuran foto
- Gunakan lazy loading (sudah built-in)

### Issue: Music tidak autoplay
**Solution:**
- Normal — browser modern block autoplay
- User harus klik tombol play manual
- Atau gunakan muted autoplay (tapi tidak ada suara)

---

## 📞 Support

Jika ada pertanyaan atau issue dengan asset:
1. Cek spesifikasi di atas
2. Pastikan semua file di folder yang benar
3. Test dengan browser dev tools (Network tab)
4. Clear cache dan hard refresh (Ctrl+Shift+R)

---

**Versi Guide:** 1.0.0  
**Last Updated:** 2025-01-08  
**Tema:** Celestial Bloom

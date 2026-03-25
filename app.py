"""
UndanganKita v3 — Flask Wedding Invitation App
Config via environment variables (see README).
"""

from flask import (Flask, render_template, request, redirect, url_for,
                   jsonify, abort, session, flash, send_from_directory, make_response)
import json, os, uuid, hashlib, hmac, secrets, sqlite3, re, time, threading, sys, threading, sys
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from flask import send_from_directory

from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# ─── CONFIG ──────────────────────────────────────────────────────────────────
BASE_DIR        = Path(__file__).parent
DB_PATH         = BASE_DIR / 'data' / 'undangan.db'
UPLOAD_DIR           = BASE_DIR / 'static' / 'uploads' / 'invitations'
MUSIC_UPLOAD_DIR     = BASE_DIR / 'static' / 'uploads' / 'music'
THEMES_DIR           = BASE_DIR / 'themes'
DEMO_PHOTOS_DIR      = BASE_DIR / 'static' / 'demo-photos'
DEMO_PORTRAIT_DIR    = BASE_DIR / 'static' / 'demo-photos' / 'individual'  # groom.*/bride.* khusus preview

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MUSIC_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DEMO_PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
DEMO_PORTRAIT_DIR.mkdir(parents=True, exist_ok=True)

MAX_UPLOAD_MB        = 5
ALLOWED_EXT          = {'jpg','jpeg','png','webp'}
MAX_MUSIC_MB         = 15
ALLOWED_MUSIC_EXT    = {'mp3','ogg','wav','m4a','aac'}
MAX_PHOTOS      = 10
SESSION_HOURS   = 8

CLEANUP_GRACE_DAYS   = 7
CLEANUP_INTERVAL_SEC = 86400

# Simple rate limit — no owner IP concept, just use reCAPTCHA for protection
RATE_WINDOW_SEC   = 60 * 10   # 10 menit window
RATE_MAX_ATTEMPTS = 30        # 30 percobaan per window
RATE_STORE: dict  = {}

# RSVP-specific rate limit (anti-spam bot)
RSVP_WINDOW_SEC      = 60 * 60   # 1 jam window per IP per undangan
RSVP_MAX_PER_IP      = 3         # maks 3 RSVP per IP per undangan per jam
RSVP_MAX_PER_INV     = 2000      # maks total RSVP per undangan (hard cap)
RSVP_RATE_STORE: dict = {}       # key: (ip, inv_id)

# Admin credentials — set via env vars
ADMIN_USERNAME  = os.environ.get('ADMIN_USER', 'admin')
_SALT           = 'undangankita_v3'
_DEFAULT_HASH   = 'pbkdf2:sha256:260000$' + _SALT + '$' + \
    hashlib.pbkdf2_hmac('sha256', b'admin123', _SALT.encode(), 260000).hex()
ADMIN_PW_HASH   = os.environ.get('ADMIN_PW_HASH', _DEFAULT_HASH)

# All config via env — no web UI for sensitive settings
WA_NUMBER        = os.environ.get('WA_NUMBER', '6281234567890')
SITE_NAME        = os.environ.get('SITE_NAME', 'habarkita.com')
RECAPTCHA_KEY    = os.environ.get('RECAPTCHA_SITE_KEY', '')   # empty = disabled
RECAPTCHA_SECRET = os.environ.get('RECAPTCHA_SECRET', '')

# Demo photos — loaded from static/demo-photos/
DEMO_PHOTOS_EXTS = {'.jpg','.jpeg','.png','.webp'}

# ─── PASSWORD ────────────────────────────────────────────────────────────────
# ─── INPUT SANITIZATION ──────────────────────────────────────────────────────
_TAG_RE = re.compile(r'<[^>]+>')
_CTRL_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')  # control chars except \t\n\r

def sanitize_text(value: str, maxlen: int = 500) -> str:
    """Strip semua HTML tags dan control chars dari input teks bebas.
    Dipakai untuk nama, alamat, venue, love_story, dll."""
    if not value:
        return ''
    v = _TAG_RE.sub('', value)       # buang semua <tag>
    v = _CTRL_RE.sub('', v)          # buang control chars
    return v.strip()[:maxlen]

def sanitize_name(value: str, maxlen: int = 100) -> str:
    """Nama orang/tempat — boleh huruf, angka, spasi, tanda baca umum."""
    v = sanitize_text(value, maxlen)
    # Buang karakter yang tidak lazim di nama tapi bisa dipakai untuk injeksi
    v = re.sub(r'[<>"\'`]', '', v)
    return v.strip()[:maxlen]

def sanitize_url(value: str, maxlen: int = 500) -> str:
    """URL — hanya izinkan http/https, buang apapun yang lain."""
    v = (value or '').strip()[:maxlen]
    if v and not re.match(r'^https?://', v):
        return ''
    return v

def html_escape(value: str) -> str:
    """Escape untuk inject ke HTML string (bukan Jinja2 context)."""
    return (str(value or '')
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
        .replace("'", '&#x27;'))

def _clean_inv_form(f) -> dict:
    """Sanitize semua field teks dari form invitation — return dict siap pakai."""
    return {
        'groom_name':      sanitize_name(f.get('groom_name',''), 100),
        'bride_name':      sanitize_name(f.get('bride_name',''), 100),
        'groom_full':      sanitize_name(f.get('groom_full',''), 200),
        'bride_full':      sanitize_name(f.get('bride_full',''), 200),
        'groom_parents':   sanitize_text(f.get('groom_parents',''), 300),
        'bride_parents':   sanitize_text(f.get('bride_parents',''), 300),
        'akad_venue':      sanitize_name(f.get('akad_venue',''), 200),
        'akad_address':    sanitize_text(f.get('akad_address',''), 500),
        'resepsi_venue':   sanitize_name(f.get('resepsi_venue',''), 200),
        'resepsi_address': sanitize_text(f.get('resepsi_address',''), 500),
        'maps_url':        sanitize_url(f.get('maps_url',''), 500),
        'love_story':      sanitize_text(f.get('love_story',''), 2000),
        'music_url':       sanitize_url(f.get('music_url',''), 500),
        'akad_date':       re.sub(r'[^0-9-]','', f.get('akad_date',''))[:10],
        'akad_time':       re.sub(r'[^0-9:]','', f.get('akad_time',''))[:5],
        'resepsi_date':    re.sub(r'[^0-9-]','', f.get('resepsi_date',''))[:10],
        'resepsi_time':    re.sub(r'[^0-9:]','', f.get('resepsi_time',''))[:5],
    }

def hash_pw(password: str, salt: str = _SALT) -> str:
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 260000)
    return f'pbkdf2:sha256:260000${salt}${dk.hex()}'

def check_pw(password: str, stored: str) -> bool:
    try:
        _, _, rest = stored.split(':', 2)
        salt = rest.split('$')[1]
        return hmac.compare_digest(hash_pw(password, salt), stored)
    except Exception:
        return False

# ─── RATE LIMITING ───────────────────────────────────────────────────────────
def _clean_rate(ip: str):
    now = time.time()
    RATE_STORE[ip] = [t for t in RATE_STORE.get(ip, [])
                      if now - t < RATE_WINDOW_SEC]

def is_rate_limited(ip: str) -> bool:
    _clean_rate(ip)
    return len(RATE_STORE.get(ip, [])) >= RATE_MAX_ATTEMPTS

def record_attempt(ip: str):
    _clean_rate(ip)
    RATE_STORE.setdefault(ip, []).append(time.time())

def attempts_left(ip: str) -> int:
    _clean_rate(ip)
    return max(0, RATE_MAX_ATTEMPTS - len(RATE_STORE.get(ip, [])))

# ─── RSVP RATE LIMITING ──────────────────────────────────────────────────────
def _clean_rsvp_rate(key: tuple):
    now = time.time()
    RSVP_RATE_STORE[key] = [t for t in RSVP_RATE_STORE.get(key, [])
                             if now - t < RSVP_WINDOW_SEC]

def is_rsvp_rate_limited(ip: str, inv_id: str) -> bool:
    key = (ip, inv_id)
    _clean_rsvp_rate(key)
    return len(RSVP_RATE_STORE.get(key, [])) >= RSVP_MAX_PER_IP

def record_rsvp_attempt(ip: str, inv_id: str):
    key = (ip, inv_id)
    _clean_rsvp_rate(key)
    RSVP_RATE_STORE.setdefault(key, []).append(time.time())

# ─── AUTH ────────────────────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        if (datetime.now().timestamp() - session.get('last_active', 0)) > SESSION_HOURS * 3600:
            session.clear()
            flash('Sesi berakhir. Silakan login kembali.', 'warning')
            return redirect(url_for('admin_login'))
        session['last_active'] = datetime.now().timestamp()
        return f(*a, **kw)
    return dec

# ─── DATABASE ────────────────────────────────────────────────────────────────
def get_db():
    c = sqlite3.connect(str(DB_PATH))
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA journal_mode=WAL')
    return c

def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    c = get_db()
    c.executescript('''
        CREATE TABLE IF NOT EXISTS invitations (
            id TEXT PRIMARY KEY, slug TEXT UNIQUE NOT NULL,
            theme_id TEXT NOT NULL, groom_name TEXT NOT NULL, bride_name TEXT NOT NULL,
            groom_full TEXT, bride_full TEXT,
            groom_parents TEXT, bride_parents TEXT,
            show_parents INTEGER DEFAULT 1,
            akad_date TEXT, akad_time TEXT, akad_venue TEXT, akad_address TEXT,
            resepsi_date TEXT, resepsi_time TEXT, resepsi_venue TEXT, resepsi_address TEXT,
            maps_url TEXT, maps_embed TEXT,
            love_story TEXT, music_url TEXT, cover_photo TEXT,
            is_active INTEGER DEFAULT 1, expires_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS invitation_photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invitation_id TEXT NOT NULL, filename TEXT NOT NULL,
            is_url INTEGER DEFAULT 0, caption TEXT, sort_order INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (invitation_id) REFERENCES invitations(id)
        );
        CREATE TABLE IF NOT EXISTS rsvp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invitation_id TEXT NOT NULL, guest_name TEXT NOT NULL,
            attendance TEXT NOT NULL, guest_count INTEGER DEFAULT 1,
            message TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (invitation_id) REFERENCES invitations(id)
        );
        CREATE TABLE IF NOT EXISTS gifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invitation_id TEXT NOT NULL,
            bank_name TEXT, account_number TEXT, account_name TEXT,
            ewallet_type TEXT, ewallet_number TEXT, ewallet_name TEXT,
            FOREIGN KEY (invitation_id) REFERENCES invitations(id)
        );
    ''')
    # Safe migrations
    migrations = [
        ('invitations', 'show_parents INTEGER DEFAULT 1'),
        ('invitations', 'maps_embed TEXT'),
        ('invitations', 'cover_photo TEXT'),
        ('invitations', 'expires_at TEXT'),
        ('invitations', 'updated_at TEXT'),
        ('invitation_photos', 'is_url INTEGER DEFAULT 0'),
        ('invitations', 'groom_photo TEXT'),   # filename di UPLOAD_DIR
        ('invitations', 'bride_photo TEXT'),   # filename di UPLOAD_DIR
        ('invitations', 'music_file TEXT'),    # filename di MUSIC_UPLOAD_DIR
    ]
    for table, coldef in migrations:
        try: c.execute(f'ALTER TABLE {table} ADD COLUMN {coldef}')
        except: pass
    c.commit(); c.close()

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def allowed_file(fn): return '.' in fn and fn.rsplit('.',1)[1].lower() in ALLOWED_EXT
def secure_name(fn):
    ext = fn.rsplit('.',1)[1].lower() if '.' in fn else 'jpg'
    return f'{uuid.uuid4().hex}.{ext}'

def allowed_music(fn): return '.' in fn and fn.rsplit('.',1)[1].lower() in ALLOWED_MUSIC_EXT
def secure_music_name(fn):
    ext = fn.rsplit('.',1)[1].lower() if '.' in fn else 'mp3'
    return f'music_{uuid.uuid4().hex}.{ext}'

_THEME_DEFAULTS = {
    'name': '', 'description': '',
    'preview_color': '#cccccc', 'accent_color': '#999999',
    'tags': [], 'demo_photos': [], 'features': [],
    'price': 0, 'price_label': '', 'price_original': 0, 'price_note': '',
    'palette': {}, 'fonts': {},
}

def _normalize_theme(data: dict) -> dict:
    """Pastikan semua field yang diakses template selalu ada — cegah Jinja Undefined / tojson error."""
    result = {**_THEME_DEFAULTS, **data}
    if not isinstance(result['tags'], list):        result['tags'] = []
    if not isinstance(result['demo_photos'], list): result['demo_photos'] = []
    if not isinstance(result['features'], list):    result['features'] = []
    return result

def get_all_themes():
    themes = []
    if THEMES_DIR.exists():
        for f in sorted(THEMES_DIR.glob('*.json')):
            if f.name.startswith('_'):  # skip _settings.json etc
                continue
            try:
                data = json.load(open(f))
                if 'id' in data:
                    themes.append(_normalize_theme(data))
            except: pass
    return themes

def get_theme(tid):
    p = THEMES_DIR / f'{tid}.json'
    if not p.exists(): return None
    try:
        return _normalize_theme(json.load(open(p)))
    except:
        return None

def get_inv_photos(conn, inv_id):
    return conn.execute(
        'SELECT * FROM invitation_photos WHERE invitation_id=? ORDER BY sort_order,id',
        (inv_id,)).fetchall()

def photo_src(row):
    if row['is_url']: return row['filename']
    return f'/uploads/{row["filename"]}'

def is_expired(inv):
    exp = inv['expires_at'] if isinstance(inv, dict) else inv['expires_at']
    if not exp: return False
    try: return datetime.strptime(exp, '%Y-%m-%d') < datetime.now()
    except: return False

def delete_photo_file(row):
    if not row['is_url']:
        try: (UPLOAD_DIR / row['filename']).unlink(missing_ok=True)
        except: pass

def get_demo_photos():
    """Return list of /static/demo-photos/* URLs sorted — EXCLUDE subfolder individual/"""
    photos = []
    if DEMO_PHOTOS_DIR.exists():
        for f in sorted(DEMO_PHOTOS_DIR.iterdir()):
            # skip subfolder (termasuk individual/)
            if f.is_dir():
                continue
            if f.suffix.lower() in DEMO_PHOTOS_EXTS:
                photos.append(f'/static/demo-photos/{f.name}')
    return photos

def extract_maps_embed_src(url: str) -> str:
    """Convert Google Maps URL to embed src URL only (not full iframe), or return empty"""
    if not url: return ''
    import urllib.parse

    # Already a full iframe tag — extract the src URL from it
    if url.strip().startswith('<iframe'):
        m = re.search(r'src=["\']([^"\']+)["\']', url)
        return m.group(1) if m else ''
    # Already embed src URL
    if 'maps/embed' in url: return url
    # Standard Google Maps share/search URL
    try:
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        q = params.get('q', [''])[0]
        if q:
            return f'https://maps.google.com/maps?q={urllib.parse.quote(q)}&output=embed&z=15'
        # /place/Name/@lat,lng or /place/Name/
        if '/place/' in url:
            place = url.split('/place/')[1].split('/')[0]
            return f'https://maps.google.com/maps?q={place}&output=embed&z=15'
        # any other google maps URL — append output=embed
        if 'google.com/maps' in url or 'goo.gl/maps' in url:
            sep = '&' if '?' in url else '?'
            return url + sep + 'output=embed'
    except: pass
    return ''

def make_maps_iframe(src: str) -> str:
    """Wrap embed src URL into full iframe HTML"""
    if not src: return ''
    return (f'<iframe src="{src}" width="100%" height="260" style="border:0;display:block;" '
            f'allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>')

@app.template_filter('format_date')
def format_date(v):
    if not v: return ''
    try:
        dt = datetime.strptime(v, '%Y-%m-%d')
        days   = ['Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu']
        months = ['Januari','Februari','Maret','April','Mei','Juni','Juli',
                  'Agustus','September','Oktober','November','Desember']
        return f"{days[dt.weekday()]}, {dt.day} {months[dt.month-1]} {dt.year}"
    except: return v

@app.template_filter('days_left')
def days_left(v):
    if not v: return None
    try: return max((datetime.strptime(v,'%Y-%m-%d')-datetime.now()).days, 0)
    except: return None

@app.context_processor
def inject_globals():
    return {
        'now': datetime.now(),
        'wa_number': WA_NUMBER,
        'site_name': SITE_NAME,
        'photo_src': photo_src,
        'recaptcha_key': RECAPTCHA_KEY,
    }

# ─── ERROR HANDLERS ──────────────────────────────────────────────────────────
@app.errorhandler(404)
def e404(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def e403(e):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def e500(e):
    return render_template('errors/500.html'), 500

@app.errorhandler(429)
def e429(e):
    return render_template('errors/429.html'), 429

# ─── PUBLIC ROUTES ───────────────────────────────────────────────────────────
@app.route('/')
def index():
    themes = get_all_themes()
    return render_template('index.html', themes=themes)

@app.route('/themes')
def themes_page():
    themes = get_all_themes()
    return render_template('themes_catalog.html', themes=themes)

def get_demo_portrait(name: str) -> str | None:
    """Cari static/demo-photos/individual/groom.* atau bride.*
    Folder individual/ terpisah supaya TIDAK ikut masuk gallery demo."""
    for ext in ('jpg', 'jpeg', 'png', 'webp'):
        p = DEMO_PORTRAIT_DIR / f'{name}.{ext}'
        if p.exists():
            return f'/static/demo-photos/individual/{name}.{ext}'
    # fallback: root demo-photos (kompatibilitas setup lama yg belum pindah)
    for ext in ('jpg', 'jpeg', 'png', 'webp'):
        p = DEMO_PHOTOS_DIR / f'{name}.{ext}'
        if p.exists():
            return f'/static/demo-photos/{name}.{ext}'
    return None


def preview_theme(theme_id):
    theme = get_theme(theme_id)
    if not theme: abort(404)
    demo_photos = get_demo_photos()
    # get_demo_photos() sudah exclude folder individual/, jadi langsung pakai semua
    photos = [{'filename': p, 'is_url': 1, 'id': i} for i, p in enumerate(demo_photos)]
    dummy = dict(
        id='preview', slug='preview', theme_id=theme_id,
        groom_name='Zaid', bride_name='Zainab',
        groom_full='Zaid bin Haritsah', bride_full='Zainab binti Jahsy',
        groom_parents='Haritsah bin Syurahbil & Su’da binti Tsa’labah',
        bride_parents='Jahsy bin Ri’ab & Umamah binti Abdul Muththalib',
        show_parents=1,
        akad_date='2029-12-20', akad_time='08:00',
        akad_venue='Masjid Al-Ikhlas',
        akad_address='Jl. Mawar No. 12, Jakarta Selatan',
        resepsi_date='2029-12-20', resepsi_time='11:00',
        resepsi_venue='Grand Ballroom Hotel Bintang Lima',
        resepsi_address='Jl. Jend. Sudirman No. 88, Jakarta',
        maps_url='https://maps.google.com/?q=Hotel+Indonesia+Kempinski',
        maps_embed=extract_maps_embed_src('https://maps.google.com/?q=Hotel+Indonesia+Kempinski'),
        maps_embed_html=make_maps_iframe(extract_maps_embed_src('https://maps.google.com/?q=Hotel+Indonesia+Kempinski')),
        love_story='Kami pertama bertemu di kampus pada tahun 2019. Berawal dari teman sekelas yang sering belajar bersama, lalu menjadi sahabat yang saling menguatkan. Kini dengan penuh rasa syukur, kami memutuskan untuk melangkah bersama menuju jenjang pernikahan yang penuh berkah dan cinta.',
        cover_photo=None, music_url='/static/assets/moon.mp3', expires_at=None, is_preview=True,
        groom_photo_url=get_demo_portrait('groom'),
        bride_photo_url=get_demo_portrait('bride'),
    )
    dummy_gifts = [
        {
            'id': 1, 'invitation_id': 'preview',
            'bank_name': 'BCA', 'account_number': '1234567890', 'account_name': 'Zaid bin Haritsah',
            'ewallet_type': None, 'ewallet_number': None, 'ewallet_name': None,
        },
        {
            'id': 2, 'invitation_id': 'preview',
            'bank_name': None, 'account_number': None, 'account_name': None,
            'ewallet_type': 'GoPay', 'ewallet_number': '081234567890', 'ewallet_name': 'Zainab binti Jahsy',
        },
    ]
    return render_template(f'themes/{theme_id}.html',
                           inv=dummy, theme=theme, rsvp_list=[], gifts=dummy_gifts,
                           photos=photos, is_preview=True)

@app.route('/preview/<theme_id>')
def theme_preview(theme_id):
    return preview_theme(theme_id)

# ─── OG TAGS INJECTOR ───────────────────────────────────────────────────────
def _build_og_tags(inv: dict, theme: dict, photos: list, site_name: str) -> str:
    """Build OG/Twitter meta tags dinamis dari data undangan — disuntik ke <head> tiap tema."""
    groom = html_escape(inv.get('groom_name', ''))
    bride = html_escape(inv.get('bride_name', ''))
    slug  = re.sub(r'[^a-z0-9-]', '', inv.get('slug', ''))
    url   = f'https://{html_escape(site_name)}/i/{slug}'

    # ── Title natural — tanpa nama tema ──────────────────────────
    # Format: "Undangan Pernikahan Rizky & Alya — 12 April 2026"
    resepsi_date = inv.get('resepsi_date', '')
    akad_date    = inv.get('akad_date', '')
    venue        = html_escape(inv.get('resepsi_venue', '') or inv.get('akad_venue', ''))
    tgl = ''
    tgl_pendek = ''
    try:
        from datetime import datetime as _dt
        d = _dt.strptime(resepsi_date or akad_date, '%Y-%m-%d')
        days   = ['Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu']
        months = ['Januari','Februari','Maret','April','Mei','Juni','Juli',
                  'Agustus','September','Oktober','November','Desember']
        tgl        = f"{days[d.weekday()]}, {d.day} {months[d.month-1]} {d.year}"
        tgl_pendek = f"{d.day} {months[d.month-1]} {d.year}"
    except:
        tgl = resepsi_date or akad_date

    # Title: "Undangan Pernikahan Rizky & Alya — 12 April 2026"
    title = f"Undangan Pernikahan {groom} & {bride}"
    if tgl_pendek:
        title += f" — {tgl_pendek}"

    # ── Deskripsi kaya, layaknya preview undangan asli ───────────
    desc_parts = []
    desc_parts.append(f"💌 {groom} & {bride} mengundang kehadiran Bapak/Ibu/Saudara/i")
    if tgl:
        desc_parts.append(f"📅 {tgl}")
    if venue:
        desc_parts.append(f"📍 {venue}")
    desc_parts.append(f"Buka undangan & konfirmasi kehadiran di: {url}")
    description = " · ".join(desc_parts)

    # ── Gambar OG — prioritas: foto gallery > groom_photo > cover > banner ──
    # Gallery foto prewed lebih menarik untuk preview sosmed
    image_url = None
    if photos:
        for p in photos:
            try:
                fn     = p['filename']
                is_url = p['is_url']
            except (KeyError, TypeError):
                fn = is_url = None
            if fn:
                image_url = fn if is_url else f'https://{site_name}/uploads/{fn}'
                break
    if not image_url and inv.get('groom_photo'):
        image_url = f'https://{site_name}/uploads/{inv["groom_photo"]}'
    if not image_url and inv.get('cover_photo'):
        image_url = f'https://{site_name}/uploads/{inv["cover_photo"]}'
    if not image_url:
        image_url = f'https://{site_name}/static/themes/banner.jpg'

    tags = f"""
  <!-- OG Tags — auto-inject UndanganKita -->
  <meta property="og:type"        content="website">
  <meta property="og:url"         content="{url}">
  <meta property="og:site_name"   content="{site_name}">
  <meta property="og:title"       content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:image"       content="{image_url}">
  <meta property="og:image:width"  content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt"   content="Undangan Pernikahan {groom} &amp; {bride}">
  <meta property="og:locale"      content="id_ID">
  <meta name="twitter:card"        content="summary_large_image">
  <meta name="twitter:title"       content="{title}">
  <meta name="twitter:description" content="{description}">
  <meta name="twitter:image"       content="{image_url}">
  <meta name="description"         content="{description}">
  <title>{title}</title>"""
    return tags

def _inject_og(html: str, og_tags: str) -> str:
    """Sisipkan OG tags tepat setelah tag <head> — replace <title> bawaan tema juga."""
    import re
    # Hapus <title> bawaan tema supaya tidak duplikat
    html = re.sub(r'<title>[^<]*</title>', '', html, count=1)
    # Sisipkan setelah <head> atau <head ...>
    html = re.sub(r'(<head[^>]*>)', r'\1' + og_tags, html, count=1)
    return html

@app.route('/i/<slug>')
def view_invitation(slug):
    conn = get_db()
    inv  = conn.execute('SELECT * FROM invitations WHERE slug=? AND is_active=1',(slug,)).fetchone()
    if not inv: conn.close(); abort(404)
    inv = dict(inv)
    if is_expired(inv): conn.close(); return render_template('expired.html', inv=inv)
    theme   = get_theme(inv['theme_id'])
    rsvps   = conn.execute('SELECT * FROM rsvp WHERE invitation_id=? ORDER BY created_at DESC LIMIT 50',(inv['id'],)).fetchall()
    gifts   = conn.execute('SELECT * FROM gifts WHERE invitation_id=?',(inv['id'],)).fetchall()
    photos  = get_inv_photos(conn, inv['id'])
    # Auto-generate embed URL jika belum ada
    if inv.get('maps_url') and not inv.get('maps_embed'):
        inv['maps_embed'] = extract_maps_embed_src(inv['maps_url'])
    # Normalize data lama di DB yang tersimpan sebagai full iframe tag
    elif inv.get('maps_embed') and inv['maps_embed'].strip().startswith('<iframe'):
        inv['maps_embed'] = extract_maps_embed_src(inv['maps_embed'])
    # Inject maps_embed_html = full iframe HTML (untuk tema yang pakai | safe)
    inv['maps_embed_html'] = make_maps_iframe(inv.get('maps_embed', ''))
    # Inject portrait photo URLs dari kolom groom_photo / bride_photo
    inv['groom_photo_url'] = f'/uploads/{inv["groom_photo"]}' if inv.get('groom_photo') else None
    inv['bride_photo_url'] = f'/uploads/{inv["bride_photo"]}' if inv.get('bride_photo') else None

     # --- TAMBAHAN DI SINI ---
    # Ambil nama tamu dari URL: ?to=Nama+Tamu
    nama_tamu = request.args.get('to') 

    conn.close()
    html = render_template(f'themes/{inv["theme_id"]}.html',
                           inv=inv, theme=theme, rsvp_list=rsvps,
                           gifts=gifts, photos=photos, is_preview=False,nama_tamu=nama_tamu)
    # Inject OG tags dinamis — tanpa perlu ubah tiap file tema
    og  = _build_og_tags(inv, theme, list(photos), SITE_NAME)
    html = _inject_og(html, og)
    resp = make_response(html)
    resp.headers['Content-Type'] = 'text/html; charset=utf-8'
    return resp

@app.route('/rsvp/<inv_id>', methods=['POST'])
def submit_rsvp(inv_id):
    ip   = request.remote_addr
    if is_rate_limited(ip):
        return jsonify({'error': 'Too many requests'}), 429
    record_attempt(ip)

    # RSVP-specific rate limit: maks 3x per IP per undangan per jam
    if is_rsvp_rate_limited(ip, inv_id):
        return jsonify({'error': 'Terlalu banyak RSVP dari alamat ini. Coba lagi nanti.'}), 429
    record_rsvp_attempt(ip, inv_id)

    data = request.get_json()
    if not data or not data.get('name','').strip():
        return jsonify({'error':'Nama wajib diisi'}), 400
    conn = get_db()
    inv  = conn.execute('SELECT * FROM invitations WHERE id=? AND is_active=1',(inv_id,)).fetchone()
    if not inv or is_expired(dict(inv)):
        conn.close(); return jsonify({'error':'Undangan tidak tersedia'}), 404

    # Hard cap: cegah spam database
    total_existing = conn.execute('SELECT COUNT(*) as c FROM rsvp WHERE invitation_id=?',(inv_id,)).fetchone()['c']
    if total_existing >= RSVP_MAX_PER_INV:
        conn.close(); return jsonify({'error': 'Batas maksimal RSVP untuk undangan ini telah tercapai.'}), 429

    conn.execute(
        'INSERT INTO rsvp(invitation_id,guest_name,attendance,guest_count,message) VALUES(?,?,?,?,?)',
        (inv_id, data['name'].strip()[:100], data.get('attendance','hadir'),
         min(int(data.get('count',1)),20), data.get('message','')[:500]))
    conn.commit()
    total = conn.execute('SELECT COUNT(*) as c FROM rsvp WHERE invitation_id=?',(inv_id,)).fetchone()['c']
    conn.close()
    return jsonify({'success':True,'total':total})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(str(UPLOAD_DIR), filename)

# ─── ADMIN LOGIN ─────────────────────────────────────────────────────────────
@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    if session.get('admin_logged_in'): return redirect(url_for('admin_dashboard'))
    ip    = request.remote_addr
    error = None

    if request.method == 'POST':
        if is_rate_limited(ip):
            remaining_sec = RATE_WINDOW_SEC
            error = f'Terlalu banyak percobaan. Coba lagi dalam beberapa menit.'
        else:
            record_attempt(ip)
            u = request.form.get('username','').strip()
            p = request.form.get('password','')
            # reCAPTCHA verify (if enabled)
            if RECAPTCHA_SECRET and RECAPTCHA_KEY:
                token = request.form.get('g-recaptcha-response','')
                if not _verify_recaptcha(token):
                    error = 'Verifikasi reCAPTCHA gagal.'
                    return render_template('admin/login.html', error=error, recaptcha_key=RECAPTCHA_KEY)
            if u == ADMIN_USERNAME and check_pw(p, ADMIN_PW_HASH):
                session.clear()
                session['admin_logged_in'] = True
                session['last_active']     = datetime.now().timestamp()
                return redirect(url_for('admin_dashboard'))
            else:
                left = attempts_left(ip)
                error = f'Username atau password salah.' + (f' ({left} percobaan tersisa dalam window ini)' if left < RATE_MAX_ATTEMPTS else '')

    return render_template('admin/login.html', error=error, recaptcha_key=RECAPTCHA_KEY)

def _verify_recaptcha(token: str) -> bool:
    import urllib.request, urllib.parse
    try:
        data = urllib.parse.urlencode({'secret': RECAPTCHA_SECRET, 'response': token}).encode()
        req  = urllib.request.Request('https://www.google.com/recaptcha/api/siteverify', data=data)
        resp = json.loads(urllib.request.urlopen(req, timeout=5).read())
        return resp.get('success', False)
    except: return False

@app.route('/admin/logout')
def admin_logout():
    session.clear(); return redirect(url_for('admin_login'))

# ─── ADMIN DASHBOARD ─────────────────────────────────────────────────────────
@app.route('/admin')
@login_required
def admin_dashboard():
    conn     = get_db()
    q        = request.args.get('q','').strip()
    qt       = request.args.get('qt','').strip()
    _filter  = request.args.get('_filter','inv')

    # Unified search — radio filter menentukan target pencarian
    if q and _filter == 'theme':
        qt = q; q = ''
    elif q and _filter == 'inv':
        qt = ''

    if q:
        rows = conn.execute(
            "SELECT * FROM invitations WHERE is_active=1 AND "
            "(groom_name LIKE ? OR bride_name LIKE ? OR slug LIKE ? OR theme_id LIKE ?) "
            "ORDER BY created_at DESC",
            (f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%')
        ).fetchall()
    else:
        rows = conn.execute('SELECT * FROM invitations WHERE is_active=1 ORDER BY created_at DESC').fetchall()
    invs = []
    for r in rows:
        d = dict(r)
        d['rsvp_count'] = conn.execute('SELECT COUNT(*) as c FROM rsvp WHERE invitation_id=?',(d['id'],)).fetchone()['c']
        d['is_expired'] = is_expired(d)
        invs.append(d)
    total_rsvp  = conn.execute('SELECT COUNT(*) as c FROM rsvp').fetchone()['c']
    promo_codes = conn.execute('SELECT * FROM promo_codes ORDER BY created_at DESC').fetchall()

    # ── Statistik ─────────────────────────────────────────────────────────────
    _rev = conn.execute("SELECT COALESCE(SUM(amount),0) as s FROM orders WHERE status='paid'").fetchone()
    total_revenue = int(_rev['s'] or 0)

    _month = datetime.now().strftime('%Y-%m')
    _om = conn.execute(
        "SELECT COUNT(*) as c FROM orders WHERE status='paid' AND created_at LIKE ?",
        (f'{_month}%',)
    ).fetchone()
    orders_this_month = int(_om['c'] or 0)

    _top = conn.execute(
        "SELECT theme_id, COUNT(*) as c FROM orders WHERE status='paid' GROUP BY theme_id ORDER BY c DESC LIMIT 1"
    ).fetchone()
    top_theme_id   = _top['theme_id'] if _top else ''
    top_theme_obj  = get_theme(top_theme_id) if top_theme_id else None
    top_theme_name = (top_theme_obj.get('name') if top_theme_obj else top_theme_id) or '—'

    all_inv = conn.execute('SELECT expires_at FROM invitations WHERE is_active=1').fetchall()
    active_count  = sum(1 for i in all_inv if not is_expired(i))
    expired_count = sum(1 for i in all_inv if is_expired(i))

    stats = dict(
        total_revenue=total_revenue,
        orders_this_month=orders_this_month,
        top_theme_id=top_theme_id,
        top_theme_name=top_theme_name,
        active_count=active_count,
        expired_count=expired_count,
    )
    # ──────────────────────────────────────────────────────────────────────────

    conn.close()
    all_themes = get_all_themes()
    filtered_themes = [t for t in all_themes if qt.lower() in t.get('name','').lower() or qt.lower() in t.get('id','').lower()] if qt else all_themes
    return render_template('admin/dashboard.html',
                           invitations=invs, themes=all_themes,
                           filtered_themes=filtered_themes,
                           total_rsvp=total_rsvp, search_q=q, search_qt=qt,
                           promo_codes=promo_codes, stats=stats)

# ─── ADMIN PROMO ROUTES ───────────────────────────────────────────────────────
@app.route('/admin/promo/create', methods=['POST'])
@login_required
def admin_promo_create():
    f = request.form
    code = re.sub(r'[^A-Z0-9]', '', (f.get('code','') or '').strip().upper())[:30]
    discount_type  = f.get('discount_type','percent')
    if discount_type not in ('percent', 'fixed'): discount_type = 'percent'
    discount_value = int(re.sub(r'[^0-9]','', f.get('discount_value','0') or '0') or 0)
    max_uses_raw   = (f.get('max_uses','') or '').strip()
    max_uses       = int(max_uses_raw) if max_uses_raw.isdigit() else None
    expires_at     = re.sub(r'[^0-9-]','', f.get('expires_at','') or '')[:10] or None
    if not code or discount_value <= 0:
        flash('Kode dan nilai diskon wajib diisi.', 'warning')
        return redirect(url_for('admin_dashboard'))
    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO promo_codes (code,discount_type,discount_value,max_uses,expires_at) VALUES (?,?,?,?,?)',
            (code, discount_type, discount_value, max_uses, expires_at))
        conn.commit()
        flash(f'Promo "{code}" berhasil dibuat! 🎉', 'success')
    except Exception:
        flash(f'Kode "{code}" sudah ada atau terjadi kesalahan.', 'warning')
    finally:
        conn.close()
    return redirect(url_for('admin_dashboard') + '#promo-section')

@app.route('/admin/promo/toggle/<code>', methods=['POST'])
@login_required
def admin_promo_toggle(code):
    conn = get_db()
    promo = conn.execute('SELECT is_active FROM promo_codes WHERE code=?', (code,)).fetchone()
    if promo:
        new_status = 0 if promo['is_active'] else 1
        conn.execute('UPDATE promo_codes SET is_active=? WHERE code=?', (new_status, code))
        conn.commit()
        label = 'diaktifkan' if new_status else 'dinonaktifkan'
        flash(f'Promo "{code}" {label}.', 'success')
    conn.close()
    return redirect(url_for('admin_dashboard') + '#promo-section')

@app.route('/admin/promo/delete/<code>', methods=['POST'])
@login_required
def admin_promo_delete(code):
    conn = get_db()
    conn.execute('DELETE FROM promo_codes WHERE code=?', (code,))
    conn.commit()
    conn.close()
    flash(f'Promo "{code}" dihapus.', 'info')
    return redirect(url_for('admin_dashboard') + '#promo-section')

# ─── ADMIN CREATE ────────────────────────────────────────────────────────────
@app.route('/admin/create', methods=['GET','POST'])
@login_required
def admin_create():
    themes = get_all_themes()
    if request.method == 'POST':
        f   = request.form
        iid = uuid.uuid4().hex[:10]
        slug = re.sub(r'[^a-z0-9-]','', f.get('slug','').lower().replace(' ','-'))
        if not slug:
            return render_template('admin/create.html', themes=themes, error='Slug tidak valid.', form=f)
        try:
            rd  = datetime.strptime(f.get('resepsi_date',''), '%Y-%m-%d')
            exp = (rd + timedelta(days=365)).strftime('%Y-%m-%d')
        except:
            exp = f.get('expires_at') or (datetime.now()+timedelta(days=365)).strftime('%Y-%m-%d')
        maps_embed = extract_maps_embed_src(sanitize_url(f.get('maps_url','')))
        c = _clean_inv_form(f)
        conn = get_db()
        try:
            conn.execute('''INSERT INTO invitations
                (id,slug,theme_id,groom_name,bride_name,groom_full,bride_full,
                 groom_parents,bride_parents,show_parents,
                 akad_date,akad_time,akad_venue,akad_address,
                 resepsi_date,resepsi_time,resepsi_venue,resepsi_address,
                 maps_url,maps_embed,love_story,music_url,expires_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (iid, slug, re.sub(r'[^a-z0-9_-]','',f.get('theme_id','').lower())[:50],
                 c['groom_name'], c['bride_name'],
                 c['groom_full'], c['bride_full'],
                 c['groom_parents'], c['bride_parents'],
                 1 if f.get('show_parents') else 0,
                 c['akad_date'], c['akad_time'], c['akad_venue'], c['akad_address'],
                 c['resepsi_date'], c['resepsi_time'], c['resepsi_venue'], c['resepsi_address'],
                 c['maps_url'], maps_embed, c['love_story'], c['music_url'], exp))
            conn.commit()
            _save_photos(conn, iid, request.files, f)
            _save_gifts(conn, iid, f)
            conn.commit(); conn.close()
            flash('Undangan berhasil dibuat! 🎉','success')
            return redirect(url_for('admin_dashboard'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('admin/create.html', themes=themes, error=f'Slug "{slug}" sudah dipakai.', form=f)
        except Exception as e:
            conn.close()
            return render_template('admin/create.html', themes=themes, error=str(e), form=f)
    return render_template('admin/create.html', themes=themes, form={})

# ─── ADMIN EDIT ──────────────────────────────────────────────────────────────
@app.route('/admin/edit/<inv_id>', methods=['GET','POST'])
@login_required
def admin_edit(inv_id):
    conn = get_db()
    inv  = conn.execute('SELECT * FROM invitations WHERE id=?',(inv_id,)).fetchone()
    if not inv: conn.close(); abort(404)
    inv    = dict(inv)
    themes = get_all_themes()
    gifts  = conn.execute('SELECT * FROM gifts WHERE invitation_id=?',(inv_id,)).fetchall()
    photos = get_inv_photos(conn, inv_id)
    if request.method == 'POST':
        f = request.form
        c = _clean_inv_form(f)
        maps_embed = extract_maps_embed_src(c['maps_url'])
        try:
            conn.execute('''UPDATE invitations SET
                theme_id=?,groom_name=?,bride_name=?,groom_full=?,bride_full=?,
                groom_parents=?,bride_parents=?,show_parents=?,
                akad_date=?,akad_time=?,akad_venue=?,akad_address=?,
                resepsi_date=?,resepsi_time=?,resepsi_venue=?,resepsi_address=?,
                maps_url=?,maps_embed=?,love_story=?,music_url=?,expires_at=?,
                updated_at=CURRENT_TIMESTAMP WHERE id=?''',
                (re.sub(r'[^a-z0-9_-]','',f.get('theme_id','').lower())[:50],
                 c['groom_name'], c['bride_name'],
                 c['groom_full'], c['bride_full'],
                 c['groom_parents'], c['bride_parents'],
                 1 if f.get('show_parents') else 0,
                 c['akad_date'], c['akad_time'], c['akad_venue'], c['akad_address'],
                 c['resepsi_date'], c['resepsi_time'], c['resepsi_venue'], c['resepsi_address'],
                 c['maps_url'], maps_embed, c['love_story'], c['music_url'],
                 re.sub(r'[^0-9-]','',f.get('expires_at',''))[:10], inv_id))
            conn.execute('DELETE FROM gifts WHERE invitation_id=?',(inv_id,))
            _save_gifts(conn, inv_id, f)
            conn.commit()
            # Handle clear portrait checkboxes
            for key, col in (('clear_groom_photo','groom_photo'), ('clear_bride_photo','bride_photo')):
                if f.get(key):
                    row = conn.execute(f'SELECT {col} FROM invitations WHERE id=?',(inv_id,)).fetchone()
                    if row and row[col]:
                        try: (UPLOAD_DIR / row[col]).unlink(missing_ok=True)
                        except: pass
                    conn.execute(f'UPDATE invitations SET {col}=NULL WHERE id=?',(inv_id,))
            conn.commit()
            _save_photos(conn, inv_id, request.files, f)
            conn.commit(); conn.close()
            flash('Undangan berhasil diperbarui! ✓','success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            conn.close()
            return render_template('admin/edit.html', inv=inv, themes=themes,
                                   gifts=list(gifts), photos=list(photos), error=str(e))
    conn.close()
    return render_template('admin/edit.html', inv=inv, themes=themes,
                           gifts=list(gifts), photos=list(photos))

@app.route('/admin/photo/delete/<int:pid>', methods=['POST'])
@login_required
def admin_delete_photo(pid):
    conn = get_db()
    row  = conn.execute('SELECT * FROM invitation_photos WHERE id=?',(pid,)).fetchone()
    if row:
        delete_photo_file(dict(row))
        conn.execute('DELETE FROM invitation_photos WHERE id=?',(pid,))
        conn.commit()
    conn.close()
    return jsonify({'success':True})

@app.route('/admin/extend/<inv_id>', methods=['POST'])
@login_required
def admin_extend(inv_id):
    conn = get_db()
    inv  = conn.execute('SELECT expires_at FROM invitations WHERE id=?',(inv_id,)).fetchone()
    if not inv: conn.close(); abort(404)
    try: cur = datetime.strptime(inv['expires_at'],'%Y-%m-%d')
    except: cur = datetime.now()
    new_exp = (max(cur, datetime.now())+timedelta(days=365)).strftime('%Y-%m-%d')
    conn.execute('UPDATE invitations SET expires_at=? WHERE id=?',(new_exp,inv_id))
    conn.commit(); conn.close()
    flash(f'Masa aktif diperpanjang hingga {format_date(new_exp)} ✓','success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete/<inv_id>', methods=['POST'])
@login_required
def admin_delete(inv_id):
    conn = get_db()
    # Hapus file gallery
    for p in conn.execute('SELECT * FROM invitation_photos WHERE invitation_id=?',(inv_id,)).fetchall():
        delete_photo_file(dict(p))
    # Hapus file portrait + musik
    inv_row = conn.execute('SELECT groom_photo, bride_photo, music_file FROM invitations WHERE id=?',(inv_id,)).fetchone()
    if inv_row:
        for col in ('groom_photo', 'bride_photo'):
            if inv_row[col]:
                try: (UPLOAD_DIR / inv_row[col]).unlink(missing_ok=True)
                except: pass
        if inv_row['music_file']:
            try: (MUSIC_UPLOAD_DIR / inv_row['music_file']).unlink(missing_ok=True)
            except: pass
    # Cascade delete semua data + row undangan (hard delete supaya storage bersih)
    conn.execute('DELETE FROM rsvp WHERE invitation_id=?',(inv_id,))
    conn.execute('DELETE FROM gifts WHERE invitation_id=?',(inv_id,))
    conn.execute('DELETE FROM invitation_photos WHERE invitation_id=?',(inv_id,))
    conn.execute('DELETE FROM invitations WHERE id=?',(inv_id,))
    conn.commit(); conn.close()
    flash('Undangan dihapus.','info')
    return redirect(url_for('admin_dashboard'))

# ─── AUTO CLEANUP ─────────────────────────────────────────────────────────────
def _do_cleanup():
    cutoff = (datetime.now() - timedelta(days=CLEANUP_GRACE_DAYS)).strftime('%Y-%m-%d')
    try:
        conn = get_db()
        rows = conn.execute(
            'SELECT id, groom_name, bride_name, expires_at, groom_photo, bride_photo, music_file '
            'FROM invitations WHERE expires_at IS NOT NULL AND expires_at < ?', (cutoff,)
        ).fetchall()
        deleted = 0
        for inv in rows:
            inv_id = inv['id']
            try:
                for p in conn.execute('SELECT * FROM invitation_photos WHERE invitation_id=?',(inv_id,)).fetchall():
                    try: delete_photo_file(dict(p))
                    except: pass
                for col in ('groom_photo','bride_photo'):
                    if inv[col]:
                        try: (UPLOAD_DIR / inv[col]).unlink(missing_ok=True)
                        except: pass
                if inv['music_file']:
                    try: (MUSIC_UPLOAD_DIR / inv['music_file']).unlink(missing_ok=True)
                    except: pass
                conn.execute('DELETE FROM rsvp              WHERE invitation_id=?',(inv_id,))
                conn.execute('DELETE FROM gifts             WHERE invitation_id=?',(inv_id,))
                conn.execute('DELETE FROM invitation_photos WHERE invitation_id=?',(inv_id,))
                conn.execute('DELETE FROM orders            WHERE invitation_id=?',(inv_id,))
                conn.execute('DELETE FROM invitations       WHERE id=?',(inv_id,))
                conn.commit()
                deleted += 1
                print(f'[CLEANUP] Dihapus: {inv["groom_name"]} & {inv["bride_name"]} (expired: {inv["expires_at"]})')
            except Exception as e:
                conn.rollback(); print(f'[CLEANUP][ERROR] {inv_id}: {e}')
        conn.close()
        if deleted > 0:
            try: c2 = get_db(); c2.execute('VACUUM'); c2.close()
            except: pass
            print(f'[CLEANUP] Selesai — {deleted} dihapus.')
    except Exception as e:
        print(f'[CLEANUP][FATAL] {e}')

def _cleanup_loop():
    time.sleep(60)
    while True:
        try: _do_cleanup()
        except Exception as e: print(f'[CLEANUP][THREAD] {e}')
        time.sleep(CLEANUP_INTERVAL_SEC)

# Theme demo photo management
@app.route('/admin/theme-demo/<theme_id>', methods=['POST'])
@login_required
def upload_theme_demo(theme_id):
    theme = get_theme(theme_id)
    if not theme: abort(404)
    results = []
    dest = BASE_DIR / 'static' / 'themes' / theme_id
    dest.mkdir(parents=True, exist_ok=True)
    for key in request.files:
        f = request.files[key]
        if not f or not f.filename or not allowed_file(f.filename): continue
        f.stream.seek(0,2); size=f.stream.tell(); f.stream.seek(0)
        if size > MAX_UPLOAD_MB*1024*1024: continue
        ext  = f.filename.rsplit('.',1)[1].lower()
        name = f'demo_{uuid.uuid4().hex[:8]}.{ext}'
        f.save(str(dest/name))
        url = f'/static/themes/{theme_id}/{name}'
        theme.setdefault('demo_photos',[]).append(url)
        results.append(url)
    if results:
        with open(THEMES_DIR/f'{theme_id}.json','w') as fp:
            json.dump(theme,fp,indent=2,ensure_ascii=False)
    return jsonify({'success':True,'urls':results})

@app.route('/admin/theme-demo/<theme_id>/delete', methods=['POST'])
@login_required
def delete_theme_demo(theme_id):
    data  = request.get_json()
    photo = data.get('photo','')
    theme = get_theme(theme_id)
    if theme and photo in theme.get('demo_photos',[]):
        theme['demo_photos'].remove(photo)
        with open(THEMES_DIR/f'{theme_id}.json','w') as fp:
            json.dump(theme,fp,indent=2,ensure_ascii=False)
        fn = photo.split('/')[-1]
        (BASE_DIR/'static'/'themes'/theme_id/fn).unlink(missing_ok=True)
    return jsonify({'success':True})

# Theme pricing
@app.route('/admin/theme-price/<theme_id>', methods=['POST'])
@login_required
def update_theme_price(theme_id):
    theme = get_theme(theme_id)
    if not theme: abort(404)
    data  = request.get_json()
    theme['price']          = data.get('price', 0)
    theme['price_label']    = data.get('price_label', '')
    theme['price_original'] = data.get('price_original', 0)
    theme['price_note']     = data.get('price_note', '')
    with open(THEMES_DIR/f'{theme_id}.json','w') as fp:
        json.dump(theme,fp,indent=2,ensure_ascii=False)
    return jsonify({'success':True})

# NOTE: Admin settings (password, recaptcha, site name, WA number)
# are configured via environment variables only — no web UI for security.
# See README.md for full config reference.

# ─── PHOTO SAVE HELPER ───────────────────────────────────────────────────────
# Keys reserved for portrait uploads — disimpan ke kolom invitations, BUKAN gallery table
_PORTRAIT_KEYS = {'groom_photo', 'bride_photo'}

def _save_portrait(conn, inv_id, key: str, f) -> bool:
    """Simpan satu file portrait ke UPLOAD_DIR dan update kolom DB.
    Return True jika berhasil."""
    if not f or not f.filename or not allowed_file(f.filename):
        return False
    f.stream.seek(0, 2); size = f.stream.tell(); f.stream.seek(0)
    if size > MAX_UPLOAD_MB * 1024 * 1024:
        return False
    # Hapus file lama jika ada
    col = 'groom_photo' if key == 'groom_photo' else 'bride_photo'
    row = conn.execute(f'SELECT {col} FROM invitations WHERE id=?', (inv_id,)).fetchone()
    if row and row[col]:
        try: (UPLOAD_DIR / row[col]).unlink(missing_ok=True)
        except: pass
    fname = secure_name(f.filename)
    f.save(str(UPLOAD_DIR / fname))
    conn.execute(f'UPDATE invitations SET {col}=? WHERE id=?', (fname, inv_id))
    return True

def _save_gifts(conn, inv_id: str, form):
    """Baca gift_0_* … gift_3_* dari form, insert ke tabel gifts.
    Dipanggil setelah DELETE gifts WHERE invitation_id sudah dilakukan di caller."""
    MAX_GIFTS = 4
    for i in range(MAX_GIFTS):
        gtype = form.get(f'gift_{i}_type', 'bank')
        if gtype == 'ewallet':
            ewallet_type   = sanitize_name(form.get(f'gift_{i}_ewallet_type') or '', 30)
            ewallet_number = re.sub(r'[^0-9+\-]', '', form.get(f'gift_{i}_ewallet_number') or '')[:30]
            ewallet_name   = sanitize_name(form.get(f'gift_{i}_ewallet_name') or '', 100)
            if ewallet_type and ewallet_number:
                conn.execute(
                    'INSERT INTO gifts(invitation_id,ewallet_type,ewallet_number,ewallet_name) VALUES(?,?,?,?)',
                    (inv_id, ewallet_type, ewallet_number, ewallet_name))
        else:
            bank_name      = sanitize_name(form.get(f'gift_{i}_bank_name') or '', 50)
            account_number = re.sub(r'[^0-9\-]', '', form.get(f'gift_{i}_account_number') or '')[:30]
            account_name   = sanitize_name(form.get(f'gift_{i}_account_name') or '', 100)
            if bank_name and account_number:
                conn.execute(
                    'INSERT INTO gifts(invitation_id,bank_name,account_number,account_name) VALUES(?,?,?,?)',
                    (inv_id, bank_name, account_number, account_name))

def _save_photos(conn, inv_id, files, form):
    existing = conn.execute('SELECT COUNT(*) as c FROM invitation_photos WHERE invitation_id=?',(inv_id,)).fetchone()['c']
    saved = 0
    for key in files:
        if key in _PORTRAIT_KEYS:
            # Portrait → simpan ke kolom groom_photo/bride_photo, bukan gallery
            _save_portrait(conn, inv_id, key, files.get(key))
            continue
        file_list = files.getlist(key)
        for f in file_list:
            if saved + existing >= MAX_PHOTOS: break
            if not f or not f.filename or not allowed_file(f.filename): continue
            f.stream.seek(0, 2); size = f.stream.tell(); f.stream.seek(0)
            if size > MAX_UPLOAD_MB * 1024 * 1024: continue
            fname = secure_name(f.filename)
            f.save(str(UPLOAD_DIR / fname))
            conn.execute('INSERT INTO invitation_photos(invitation_id,filename,is_url,sort_order) VALUES(?,?,0,?)',
                         (inv_id, fname, existing + saved))
            saved += 1
    for i in range(10):
        if saved + existing >= MAX_PHOTOS: break
        url = form.get(f'photo_url_{i}', '').strip() if form else ''
        if not url or not url.startswith(('http://', 'https://')): continue
        conn.execute('INSERT INTO invitation_photos(invitation_id,filename,is_url,sort_order) VALUES(?,?,1,?)',
                     (inv_id, url, existing + saved))
        saved += 1

#other

# ─── USER SELF-SERVICE ROUTES (v4 addition) ──────────────────────────────────
EXPIRY_DAYS_AFTER_EVENT = 3
MAX_EVENT_YEARS_AHEAD   = 1

def _ensure_user_columns():
    """Add user-facing columns to invitations table if not exist."""
    conn = get_db()
    new_cols = [
        'user_username TEXT',
        'user_pw_hash TEXT',
        'payment_status TEXT DEFAULT paid',
        'payment_order_id TEXT',
        'payment_amount INTEGER DEFAULT 0',
        'event_date_locked INTEGER DEFAULT 0',
    ]
    for col in new_cols:
        try: conn.execute(f'ALTER TABLE invitations ADD COLUMN {col}')
        except: pass
    # orders table
    conn.execute('''CREATE TABLE IF NOT EXISTS orders (
        id TEXT PRIMARY KEY,
        invitation_id TEXT,
        theme_id TEXT,
        groom_name TEXT, bride_name TEXT, resepsi_date TEXT,
        amount INTEGER DEFAULT 0,
        status TEXT DEFAULT pending,
        snap_token TEXT,
        customer_name TEXT, customer_email TEXT, customer_phone TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        paid_at TEXT,
        FOREIGN KEY (invitation_id) REFERENCES invitations(id)
    )''')
    # promo codes table
    conn.execute('''CREATE TABLE IF NOT EXISTS promo_codes (
        code TEXT PRIMARY KEY,
        discount_type TEXT NOT NULL DEFAULT 'percent',
        discount_value INTEGER NOT NULL DEFAULT 0,
        max_uses INTEGER DEFAULT NULL,
        used_count INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        expires_at TEXT DEFAULT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit(); conn.close()

_ensure_user_columns()

def hash_user_pw(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 260000)
    return f'pbkdf2:sha256:260000${salt}${dk.hex()}'

def check_user_pw(password: str, stored: str) -> bool:
    try:
        _, _, rest = stored.split(':', 2)
        salt = rest.split('$')[1]
        dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 260000)
        candidate = f'pbkdf2:sha256:260000${salt}${dk.hex()}'
        return hmac.compare_digest(candidate, stored)
    except: return False

def calc_expiry(event_date_str: str) -> str:
    try:
        ed = datetime.strptime(event_date_str, '%Y-%m-%d')
        exp = ed + timedelta(days=EXPIRY_DAYS_AFTER_EVENT)
        max_exp = datetime.now() + timedelta(days=MAX_EVENT_YEARS_AHEAD * 365 + EXPIRY_DAYS_AFTER_EVENT)
        if exp > max_exp: exp = max_exp
        if exp < datetime.now() + timedelta(days=1): exp = datetime.now() + timedelta(days=1)
        return exp.strftime('%Y-%m-%d')
    except:
        return (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

def _calc_expiry_capped(event_date_str: str, created_at_str: str) -> str:
    """Sama seperti calc_expiry tapi dibatasi max 1 tahun dari created_at.
    Mencegah user spam ganti tanggal acara untuk memperpanjang masa aktif terus-menerus."""
    new_exp = calc_expiry(event_date_str)
    try:
        created = datetime.strptime(created_at_str[:10], '%Y-%m-%d')
        hard_cap = (created + timedelta(days=MAX_EVENT_YEARS_AHEAD * 365 + EXPIRY_DAYS_AFTER_EVENT)).strftime('%Y-%m-%d')
        return min(new_exp, hard_cap)
    except:
        return new_exp

def user_login_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if not session.get('user_inv_id'):
            return redirect(url_for('user_login'))
        return f(*a, **kw)
    return dec

# ── /promo/check ─────────────────────────────────────────────────────────────
@app.route('/promo/check', methods=['POST'])
def check_promo():
    data        = request.get_json() or {}
    code        = data.get('code', '').strip().upper()
    theme_price = int(data.get('price', 0))
    if not code:
        return jsonify({'valid': False, 'message': 'Kode promo tidak boleh kosong.'})
    conn  = get_db()
    promo = conn.execute('SELECT * FROM promo_codes WHERE code=?', (code,)).fetchone()
    conn.close()
    if not promo:
        return jsonify({'valid': False, 'message': 'Kode promo tidak ditemukan.'})
    if not promo['is_active']:
        return jsonify({'valid': False, 'message': 'Kode promo sudah tidak aktif.'})
    if promo['max_uses'] and promo['used_count'] >= promo['max_uses']:
        return jsonify({'valid': False, 'message': 'Kode promo sudah habis digunakan.'})
    if promo['expires_at']:
        try:
            if datetime.strptime(promo['expires_at'], '%Y-%m-%d') < datetime.now():
                return jsonify({'valid': False, 'message': 'Kode promo sudah kadaluarsa.'})
        except: pass
    if promo['discount_type'] == 'percent':
        disc = int(theme_price * promo['discount_value'] / 100)
    else:
        disc = min(int(promo['discount_value']), theme_price)
    final = max(0, theme_price - disc)
    return jsonify({
        'valid': True,
        'discount_type':   promo['discount_type'],
        'discount_value':  promo['discount_value'],
        'discount_amount': disc,
        'final_price':     final,
        'message': 'Promo "{}" berhasil! Hemat Rp {}'.format(
            code, '{:,}'.format(disc).replace(',', '.'))
    })

# ── /order ────────────────────────────────────────────────────────────────────
@app.route('/order', methods=['GET', 'POST'])
def create_order():
    themes = get_all_themes()
    theme_id = request.args.get('theme', '') or ''
    selected_theme = get_theme(theme_id) if theme_id else None

    if request.method == 'GET':
        return render_template('order.html',
            themes=themes, selected_theme=selected_theme,
            theme_id=theme_id, form=None, errors=None)

    # POST — validate
    f = request.form
    ip = request.remote_addr
    if is_rate_limited(ip):
        return render_template('order.html', themes=themes, selected_theme=selected_theme,
            theme_id=theme_id, form=f, errors=['Terlalu banyak percobaan. Tunggu beberapa menit.'])
    record_attempt(ip)

    cust_name  = (f.get('customer_name','') or '').strip()[:100]
    cust_email = (f.get('customer_email','') or '').strip()[:200]
    cust_phone = re.sub(r'[^0-9+]', '', f.get('customer_phone','') or '')[:20]
    groom_name = sanitize_name(f.get('groom_name',''), 100)
    bride_name = sanitize_name(f.get('bride_name',''), 100)
    tid        = re.sub(r'[^a-z0-9_-]', '', (f.get('theme_id','') or '').lower())[:50]
    resepsi_date = f.get('resepsi_date','').strip()
    username   = re.sub(r'[^a-z0-9]', '', (f.get('username','') or '').lower())[:30]
    password   = f.get('password','') or ''
    password2  = f.get('password2','') or ''

    errors = []
    if not groom_name:  errors.append('Nama mempelai pria wajib diisi.')
    if not bride_name:  errors.append('Nama mempelai wanita wajib diisi.')
    if not tid:         errors.append('Pilih tema terlebih dahulu.')
    if not resepsi_date: errors.append('Tanggal acara wajib diisi.')
    if not username or len(username) < 3: errors.append('Username minimal 3 karakter (huruf kecil & angka).')
    if len(password) < 8: errors.append('Password minimal 8 karakter.')
    if password != password2: errors.append('Konfirmasi password tidak cocok.')

    # Cek username sudah dipakai
    if not errors and username:
        conn = get_db()
        existing = conn.execute('SELECT id FROM invitations WHERE user_username=?', (username,)).fetchone()
        conn.close()
        if existing:
            errors.append(f'Username "{username}" sudah dipakai. Pilih username lain.')

    # Validasi tanggal
    if not errors and resepsi_date:
        try:
            rd = datetime.strptime(resepsi_date, '%Y-%m-%d')
            max_d = datetime.now() + timedelta(days=MAX_EVENT_YEARS_AHEAD * 365)
            if rd < datetime.now():
                errors.append('Tanggal acara tidak boleh di masa lalu.')
            elif rd > max_d:
                errors.append(f'Tanggal acara maksimal 1 tahun ke depan ({max_d.strftime("%d/%m/%Y")}).')
        except:
            errors.append('Format tanggal acara tidak valid.')

    if errors:
        tid2 = tid or ''
        return render_template('order.html', themes=themes,
            selected_theme=get_theme(tid2) if tid2 else None,
            theme_id=tid2, errors=errors, form=f)

    theme = get_theme(tid)
    if not theme:
        return render_template('order.html', themes=themes, selected_theme=None,
            theme_id=tid, errors=['Tema tidak ditemukan.'], form=f)

    amount = int(theme.get('price', 0) or 0)

    # ── Promo kode ────────────────────────────────────────────────────────────
    promo_code = (f.get('promo_code', '') or '').strip().upper()
    if promo_code and amount > 0:
        _pc = get_db()
        _promo = _pc.execute(
            'SELECT * FROM promo_codes WHERE code=? AND is_active=1', (promo_code,)
        ).fetchone()
        _valid = bool(_promo)
        if _valid and _promo['max_uses'] and _promo['used_count'] >= _promo['max_uses']:
            _valid = False
        if _valid and _promo['expires_at']:
            try:
                if datetime.strptime(_promo['expires_at'], '%Y-%m-%d') < datetime.now():
                    _valid = False
            except: pass
        if _valid:
            if _promo['discount_type'] == 'percent':
                _disc = int(amount * _promo['discount_value'] / 100)
            else:
                _disc = min(int(_promo['discount_value']), amount)
            amount = max(0, amount - _disc)
            _pc.execute('UPDATE promo_codes SET used_count = used_count + 1 WHERE code=?', (promo_code,))
            _pc.commit()
        _pc.close()
    # ─────────────────────────────────────────────────────────────────────────

    inv_id   = uuid.uuid4().hex[:10]
    order_id = f'INV-{inv_id.upper()}-{int(time.time())}'
    raw_slug = f'{groom_name.lower()}-{bride_name.lower()}-{uuid.uuid4().hex[:4]}'
    slug = re.sub(r'[^a-z0-9-]', '-', raw_slug.replace(' ','-'))[:80].strip('-')
    expires = calc_expiry(resepsi_date)
    pw_hash = hash_user_pw(password)

    conn = get_db()
    try:
        # Untuk order berbayar: simpan di orders dulu, invitations BELUM dibuat.
        # Invitations baru dibuat setelah payment confirmed (di /order/setup atau webhook).
        # Untuk gratis: langsung buat invitations + orders sekaligus.
        if amount > 0:
            # Pastikan kolom ada (safe migration, jalankan sekali)
            for col in ('user_username TEXT', 'user_pw_hash TEXT', 'slug TEXT'):
                try: conn.execute(f'ALTER TABLE orders ADD COLUMN {col}')
                except: pass
            conn.execute('''INSERT INTO orders
                (id, invitation_id, theme_id, groom_name, bride_name, resepsi_date,
                 amount, status, customer_name, customer_email, customer_phone,
                 snap_token, user_username, user_pw_hash, slug)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (order_id, None, tid, groom_name, bride_name, resepsi_date,
                 amount, 'pending',
                 '', '', cust_phone, '',
                 username, pw_hash, slug))
        else:
            # Gratis — langsung buat invitation + order
            conn.execute('''INSERT INTO invitations
                (id, slug, theme_id, groom_name, bride_name, resepsi_date, expires_at,
                 is_active, payment_status, payment_order_id, payment_amount,
                 user_username, user_pw_hash)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (inv_id, slug, tid, groom_name, bride_name, resepsi_date, expires,
                 1, 'paid', order_id, 0, username, pw_hash))
            conn.execute('''INSERT INTO orders
                (id, invitation_id, theme_id, groom_name, bride_name, resepsi_date,
                 amount, status, customer_name, customer_email, customer_phone)
                VALUES (?,?,?,?,?,?,?,?,?,?,?)''',
                (order_id, inv_id, tid, groom_name, bride_name, resepsi_date,
                 0, 'paid', '', '', cust_phone))
        conn.commit()
    except Exception as e:
        conn.close()
        return render_template('order.html', themes=themes, selected_theme=theme,
            theme_id=tid, errors=[f'Terjadi kesalahan: {e}'], form=f)
    conn.close()

    # Jika gratis — langsung aktif, redirect ke dashboard
    if amount == 0:
        session['user_inv_id'] = inv_id
        return redirect(url_for('user_dashboard'))

    # Midtrans
    MIDTRANS_SERVER_KEY = os.environ.get('MIDTRANS_SERVER_KEY', '')
    if not MIDTRANS_SERVER_KEY:
        # Dev mode — auto-activate tanpa payment
        conn = get_db()
        real_inv_id = _create_invitation_from_order(conn, order_id)
        conn.commit(); conn.close()
        if real_inv_id:
            session['user_inv_id'] = real_inv_id
            return redirect(url_for('order_setup', order_id=order_id))
        return redirect(url_for('user_login'))

    # Buat Snap token
    import urllib.request as _ureq
    import json as _json
    import base64 as _b64
    MIDTRANS_IS_PROD = os.environ.get('MIDTRANS_IS_PROD','false').lower() == 'true'
    base_url = 'https://app.midtrans.com' if MIDTRANS_IS_PROD else 'https://app.sandbox.midtrans.com'
    auth = _b64.b64encode(f'{MIDTRANS_SERVER_KEY}:'.encode()).decode()
    payload = {
        'transaction_details': {'order_id': order_id, 'gross_amount': amount},
        'item_details': [{'id': tid, 'price': amount, 'quantity': 1, 'name': f'Undangan {theme["name"]}'[:50]}],
        'customer_details': {'first_name': f'{groom_name} & {bride_name}'[:50], 'phone': cust_phone or ''},
        'enabled_payments': ['gopay','shopeepay','qris','other_qris','bank_transfer','bca_va','bni_va','bri_va','permata_va','cimb_va'],
        'callbacks': {
            'finish': f'https://{SITE_NAME}/order/setup/{order_id}'
        },
    }
    try:
        req = _ureq.Request(f'{base_url}/snap/v1/transactions',
            data=_json.dumps(payload).encode(),
            headers={'Content-Type':'application/json','Authorization':f'Basic {auth}'},
            method='POST')
        resp = _ureq.urlopen(req, timeout=15)
        snap_data = _json.loads(resp.read())
        snap_token = snap_data.get('token','')
        conn = get_db()
        conn.execute('UPDATE orders SET snap_token=? WHERE id=?', (snap_token, order_id))
        conn.commit(); conn.close()
    except Exception as e:
        snap_token = ''

    MIDTRANS_CLIENT_KEY = os.environ.get('MIDTRANS_CLIENT_KEY','')
    return render_template('payment.html',
        order_id=order_id, inv_id=inv_id, snap_token=snap_token,
        amount=amount, theme=theme,
        groom_name=groom_name, bride_name=bride_name,
        midtrans_client_key=MIDTRANS_CLIENT_KEY,
        midtrans_is_prod=MIDTRANS_IS_PROD)

# ── Helper: create invitation setelah payment confirmed ───────────────────────
def _create_invitation_from_order(conn, order_id: str):
    """Buat invitation dari data order — dipanggil saat payment sukses. Idempotent."""
    order = conn.execute('SELECT * FROM orders WHERE id=?', (order_id,)).fetchone()
    if not order: return None
    order = dict(order)

    # Idempotent: kalau invitation_id sudah ada dan invitation sudah ada di DB, skip
    existing_inv_id = order.get('invitation_id')
    if existing_inv_id:
        already = conn.execute('SELECT id FROM invitations WHERE id=?', (existing_inv_id,)).fetchone()
        if already: return existing_inv_id

    inv_id   = existing_inv_id or uuid.uuid4().hex[:10]
    slug     = order.get('slug') or re.sub(r'[^a-z0-9-]', '-',
        f'{(order["groom_name"] or "").lower()}-{(order["bride_name"] or "").lower()}-{uuid.uuid4().hex[:4]}'.replace(' ','-'))[:80].strip('-')
    expires  = calc_expiry(order.get('resepsi_date',''))

    conn.execute('''INSERT OR IGNORE INTO invitations
        (id, slug, theme_id, groom_name, bride_name, resepsi_date, expires_at,
         is_active, payment_status, payment_order_id, payment_amount,
         user_username, user_pw_hash)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
        (inv_id, slug, order['theme_id'],
         order['groom_name'], order['bride_name'], order.get('resepsi_date',''), expires,
         1, 'paid', order_id, order['amount'],
         order.get('user_username'), order.get('user_pw_hash')))
    conn.execute('UPDATE orders SET invitation_id=?, status="paid", paid_at=COALESCE(paid_at, CURRENT_TIMESTAMP) WHERE id=?',
        (inv_id, order_id))
    return inv_id

# ── /payment/notification ─────────────────────────────────────────────────────
@app.route('/payment/notification', methods=['POST'])
def payment_notification():
    import json as _json, hashlib as _hash
    data = request.get_json(silent=True) or {}
    order_id = data.get('order_id','')
    status   = data.get('transaction_status','')
    fraud    = data.get('fraud_status','')
    MIDTRANS_SERVER_KEY = os.environ.get('MIDTRANS_SERVER_KEY','')
    # Signature check
    sig_input = data.get('order_id','') + data.get('status_code','') + data.get('gross_amount','') + MIDTRANS_SERVER_KEY
    expected = _hash.sha512(sig_input.encode()).hexdigest()
    if not hmac.compare_digest(expected, data.get('signature_key','')):
        return jsonify({'error':'invalid signature'}), 403
    if status in ('capture','settlement') and fraud in ('accept',''):
        conn = get_db()
        _create_invitation_from_order(conn, order_id)
        conn.commit()
        conn.close()
    return jsonify({'status':'ok'})

# ── /payment/<order_id> (GET — recovery setelah balik dari GoPay app) ─────────
@app.route('/payment/<order_id>')
def payment_page(order_id):
    conn = get_db()
    order = conn.execute('SELECT * FROM orders WHERE id=?', (order_id,)).fetchone()
    conn.close()
    if not order:
        return redirect(url_for('create_order'))
    order = dict(order)

    # Kalau sudah paid, langsung ke setup
    if order['status'] == 'paid':
        return redirect(url_for('order_setup', order_id=order_id))

    theme = get_theme(order['theme_id']) or {'name': order['theme_id']}
    MIDTRANS_CLIENT_KEY = os.environ.get('MIDTRANS_CLIENT_KEY', '')
    MIDTRANS_IS_PROD = os.environ.get('MIDTRANS_IS_PROD', 'false').lower() == 'true'
    snap_token = order.get('snap_token', '')

    return render_template('payment.html',
        order_id=order_id,
        inv_id=order.get('invitation_id', ''),
        snap_token=snap_token,
        amount=order['amount'],
        theme=theme,
        groom_name=order['groom_name'],
        bride_name=order['bride_name'],
        midtrans_client_key=MIDTRANS_CLIENT_KEY,
        midtrans_is_prod=MIDTRANS_IS_PROD)

# ── /payment/check ────────────────────────────────────────────────────────────
@app.route('/payment/check/<order_id>')
def payment_check(order_id):
    conn = get_db()
    order = conn.execute('SELECT status, invitation_id FROM orders WHERE id=?', (order_id,)).fetchone()
    conn.close()
    if not order: return jsonify({'status':'not_found'})
    return jsonify({'status': order['status'], 'inv_id': order['invitation_id']})

# ── /payment/activate (setelah Snap callback) ─────────────────────────────────
@app.route('/payment/activate/<order_id>')
def payment_activate(order_id):
    conn = get_db()
    order = conn.execute('SELECT * FROM orders WHERE id=?', (order_id,)).fetchone()
    if order and order['status'] == 'paid':
        inv_id = order['invitation_id']
        conn.close()
        session['user_inv_id'] = inv_id
        return redirect(url_for('order_setup', order_id=order_id))
    conn.close()
    return redirect(url_for('user_login'))

# ── /order/setup (setelah payment berhasil) ───────────────────────────────────
@app.route('/order/setup/<order_id>')
def order_setup(order_id):
    conn = get_db()
    order = conn.execute('SELECT * FROM orders WHERE id=?', (order_id,)).fetchone()
    if not order:
        conn.close()
        return redirect(url_for('user_login'))
    order = dict(order)

    # Kalau status belum paid, coba buat invitation dulu (mungkin webhook sudah masuk
    # tapi order_setup dibuka sebelum status di-update — atau Snap onSuccess lebih cepat)
    if order['status'] != 'paid':
        # Cek sekali lagi langsung ke Midtrans jika ada server key (sandbox delay)
        MIDTRANS_SERVER_KEY = os.environ.get('MIDTRANS_SERVER_KEY', '')
        paid_via_midtrans = False
        if MIDTRANS_SERVER_KEY:
            try:
                import urllib.request as _ureq, base64 as _b64, json as _json
                MIDTRANS_IS_PROD = os.environ.get('MIDTRANS_IS_PROD','false').lower()=='true'
                base_url = 'https://api.midtrans.com' if MIDTRANS_IS_PROD else 'https://api.sandbox.midtrans.com'
                auth = _b64.b64encode(f'{MIDTRANS_SERVER_KEY}:'.encode()).decode()
                req = _ureq.Request(f'{base_url}/v2/{order_id}/status',
                    headers={'Authorization': f'Basic {auth}'})
                resp = _json.loads(_ureq.urlopen(req, timeout=8).read())
                tx_status = resp.get('transaction_status','')
                fraud = resp.get('fraud_status','')
                if tx_status in ('capture','settlement') and fraud in ('accept',''):
                    paid_via_midtrans = True
            except:
                pass

        if not paid_via_midtrans:
            conn.close()
            # Tampilkan halaman tunggu dengan auto-poll
            return render_template('order_setup.html', order=order, status='pending')

    # Buat invitation (idempotent)
    inv_id = _create_invitation_from_order(conn, order_id)
    conn.commit()
    conn.close()

    if inv_id:
        session['user_inv_id'] = inv_id
        return redirect(url_for('user_dashboard'))

    return redirect(url_for('user_login'))

# ── /login (user) ─────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if session.get('user_inv_id'):
        return redirect(url_for('user_dashboard'))
    error = None
    if request.method == 'POST':
        ip = request.remote_addr
        if is_rate_limited(ip):
            error = 'Terlalu banyak percobaan. Coba lagi dalam beberapa menit.'
            return render_template('user_login.html', error=error, recaptcha_key=RECAPTCHA_KEY)
        record_attempt(ip)

        # reCAPTCHA verify (if enabled)
        if RECAPTCHA_SECRET and RECAPTCHA_KEY:
            token = request.form.get('g-recaptcha-response', '')
            if not _verify_recaptcha(token):
                error = 'Verifikasi reCAPTCHA gagal.'
                return render_template('user_login.html', error=error, recaptcha_key=RECAPTCHA_KEY)

        uname = re.sub(r'[^a-z0-9]', '', (request.form.get('username','') or '').lower())
        pw    = request.form.get('password','') or ''
        conn  = get_db()
        row   = conn.execute('SELECT id, user_pw_hash, payment_status FROM invitations WHERE user_username=?', (uname,)).fetchone()
        conn.close()
        if row and row['user_pw_hash'] and check_user_pw(pw, row['user_pw_hash']):
            if row['payment_status'] != 'paid':
                error = 'Pembayaran belum dikonfirmasi. Hubungi admin jika sudah bayar.'
            else:
                session['user_inv_id'] = row['id']
                return redirect(url_for('user_dashboard'))
        else:
            error = 'Username atau password salah.'
    return render_template('user_login.html', error=error, recaptcha_key=RECAPTCHA_KEY)

@app.route('/logout')
def user_logout():
    session.pop('user_inv_id', None)
    return redirect(url_for('user_login'))

# ── /dashboard ────────────────────────────────────────────────────────────────
@app.route('/dashboard')
@user_login_required
def user_dashboard():
    inv_id = session['user_inv_id']
    conn = get_db()
    inv = conn.execute('SELECT * FROM invitations WHERE id=?', (inv_id,)).fetchone()
    rsvp_count = conn.execute('SELECT COUNT(*) as c FROM rsvp WHERE invitation_id=?', (inv_id,)).fetchone()['c']
    conn.close()
    if not inv: session.pop('user_inv_id',None); return redirect(url_for('user_login'))
    theme = get_theme(inv['theme_id']) or {'name': inv['theme_id']}
    expired = is_expired(inv)
    return render_template('user_dashboard.html', inv=inv, theme=theme,
                           rsvp_count=rsvp_count, expired=expired)

# ── /dashboard/edit ───────────────────────────────────────────────────────────
@app.route('/dashboard/edit', methods=['GET', 'POST'])
@user_login_required
def user_edit():
    inv_id = session['user_inv_id']
    conn = get_db()
    inv  = conn.execute('SELECT * FROM invitations WHERE id=?', (inv_id,)).fetchone()
    photos = get_inv_photos(conn, inv_id)
    gifts  = conn.execute('SELECT * FROM gifts WHERE invitation_id=?', (inv_id,)).fetchall()
    conn.close()
    if not inv: return redirect(url_for('user_login'))
    themes  = get_all_themes()
    expired = is_expired(inv)
    errors  = []

    if request.method == 'POST':
        f = request.form
        c = _clean_inv_form(f)
        tid = inv['theme_id']  # tema dikunci
        groom_name = c['groom_name']
        bride_name = c['bride_name']
        if not groom_name: errors.append('Nama mempelai pria wajib diisi.')
        if not bride_name: errors.append('Nama mempelai wanita wajib diisi.')

        resepsi_date = inv['resepsi_date']
        if not expired:
            rd = c['resepsi_date']
            if rd:
                try:
                    rdt = datetime.strptime(rd, '%Y-%m-%d')
                    max_d = datetime.now() + timedelta(days=MAX_EVENT_YEARS_AHEAD * 365)
                    if rdt < datetime.now():
                        errors.append('Tanggal acara tidak boleh di masa lalu.')
                    elif rdt > max_d:
                        errors.append('Tanggal acara maksimal 1 tahun ke depan.')
                    else:
                        resepsi_date = rd
                except:
                    errors.append('Format tanggal tidak valid.')

        if not errors:
            # Handle music: file upload takes priority over URL
            music_url_final = c['music_url']
            music_file_final = dict(inv).get('music_file') or None  # keep existing by default

            music_mode = request.form.get('music_mode', 'url')
            if music_mode == 'upload':
                music_file = request.files.get('music_file')
                if music_file and music_file.filename:
                    if not allowed_music(music_file.filename):
                        errors.append('Format musik tidak didukung. Gunakan MP3, OGG, WAV, M4A, atau AAC.')
                    elif music_file.content_length and music_file.content_length > MAX_MUSIC_MB * 1024 * 1024:
                        errors.append(f'File musik maks. {MAX_MUSIC_MB}MB.')
                    else:
                        if music_file_final:
                            try: (MUSIC_UPLOAD_DIR / music_file_final).unlink(missing_ok=True)
                            except: pass
                        fname = secure_music_name(music_file.filename)
                        music_file.save(str(MUSIC_UPLOAD_DIR / fname))
                        music_file_final = fname
                        music_url_final = f'/static/uploads/music/{fname}'
                elif request.form.get('clear_music_file'):
                    if music_file_final:
                        try: (MUSIC_UPLOAD_DIR / music_file_final).unlink(missing_ok=True)
                        except: pass
                    music_file_final = None
                    music_url_final = ''
            else:
                # URL mode — if user had an uploaded file and now switches to URL, clear the file
                if music_file_final and c['music_url'] and not c['music_url'].startswith('/static/uploads/music/'):
                    try: (MUSIC_UPLOAD_DIR / music_file_final).unlink(missing_ok=True)
                    except: pass
                    music_file_final = None

        if not errors:
            conn = get_db()
            conn.execute('''UPDATE invitations SET
                theme_id=?, groom_name=?, bride_name=?,
                groom_full=?, bride_full=?, groom_parents=?, bride_parents=?,
                show_parents=?,
                akad_date=?, akad_time=?, akad_venue=?, akad_address=?,
                resepsi_date=?, resepsi_time=?, resepsi_venue=?, resepsi_address=?,
                maps_url=?, maps_embed=?, love_story=?, music_url=?, music_file=?,
                expires_at=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?''', (
                tid,
                groom_name, bride_name,
                c['groom_full'], c['bride_full'],
                c['groom_parents'], c['bride_parents'],
                1 if f.get('show_parents') else 0,
                c['akad_date'], c['akad_time'],
                c['akad_venue'], c['akad_address'],
                resepsi_date, c['resepsi_time'],
                c['resepsi_venue'], c['resepsi_address'],
                c['maps_url'],
                extract_maps_embed_src(c['maps_url']),
                c['love_story'],
                music_url_final,
                music_file_final,
                _calc_expiry_capped(resepsi_date, inv['created_at']),
                inv_id))
            # Gifts
            conn.execute('DELETE FROM gifts WHERE invitation_id=?', (inv_id,))
            for i in range(4):
                gtype = f.get(f'gift_{i}_type','bank')
                if gtype == 'ewallet':
                    ew_type = f.get(f'gift_{i}_ewallet_type','')
                    ew_num  = f.get(f'gift_{i}_ewallet_number','')[:50]
                    ew_name = f.get(f'gift_{i}_ewallet_name','')[:100]
                    if ew_num:
                        conn.execute('INSERT INTO gifts(invitation_id,ewallet_type,ewallet_number,ewallet_name) VALUES(?,?,?,?)',
                            (inv_id, ew_type, ew_num, ew_name))
                else:
                    bank = f.get(f'gift_{i}_bank_name','')[:50]
                    acc  = f.get(f'gift_{i}_account_number','')[:50]
                    name = f.get(f'gift_{i}_account_name','')[:100]
                    if acc:
                        conn.execute('INSERT INTO gifts(invitation_id,bank_name,account_number,account_name) VALUES(?,?,?,?)',
                            (inv_id, bank, acc, name))
            _save_photos(conn, inv_id, request.files, f)
            # Portrait
            for key in ('groom_photo','bride_photo'):
                ff = request.files.get(key)
                if ff and ff.filename:
                    _save_portrait(conn, inv_id, key, ff)
                elif f.get(f'clear_{key}'):
                    conn.execute(f'UPDATE invitations SET {key}=NULL WHERE id=?', (inv_id,))
            conn.commit(); conn.close()
            return redirect(url_for('user_dashboard') + '?saved=1')

    # Inject portrait URLs agar template bisa tampilkan foto yang sudah tersimpan
    inv = dict(inv)
    inv['groom_photo_url'] = f'/uploads/{inv["groom_photo"]}' if inv.get('groom_photo') else None
    inv['bride_photo_url']  = f'/uploads/{inv["bride_photo"]}'  if inv.get('bride_photo')  else None
    return render_template('user_edit.html', inv=inv, photos=photos, gifts=gifts,
                           themes=themes, expired=expired, errors=errors, form=request.form if errors else {})

# ── /dashboard/photo/delete ───────────────────────────────────────────────────
@app.route('/dashboard/photo/delete/<int:pid>', methods=['POST'])
@user_login_required
def user_delete_photo(pid):
    inv_id = session['user_inv_id']
    conn = get_db()
    photo = conn.execute('SELECT * FROM invitation_photos WHERE id=? AND invitation_id=?', (pid, inv_id)).fetchone()
    if photo:
        delete_photo_file(photo)
        conn.execute('DELETE FROM invitation_photos WHERE id=?', (pid,))
        conn.commit()
    conn.close()
    return jsonify({'success': True})

# ── /dashboard/music/delete ───────────────────────────────────────────────────
@app.route('/dashboard/music/delete', methods=['POST'])
@user_login_required
def user_delete_music():
    inv_id = session['user_inv_id']
    conn = get_db()
    inv = conn.execute('SELECT music_file FROM invitations WHERE id=?', (inv_id,)).fetchone()
    if inv and inv['music_file']:
        try: (MUSIC_UPLOAD_DIR / inv['music_file']).unlink(missing_ok=True)
        except: pass
        conn.execute('UPDATE invitations SET music_file=NULL, music_url=NULL WHERE id=?', (inv_id,))
        conn.commit()
    conn.close()
    return jsonify({'success': True})

# ── /dashboard/change-password ────────────────────────────────────────────────
@app.route('/dashboard/change-password', methods=['POST'])
@user_login_required
def user_change_password():
    inv_id = session['user_inv_id']
    old_pw = request.form.get('old_password','')
    new_pw = request.form.get('new_password','')
    new_pw2= request.form.get('new_password2','')
    conn = get_db()
    inv = conn.execute('SELECT user_pw_hash FROM invitations WHERE id=?', (inv_id,)).fetchone()
    error = None
    if not inv or not inv['user_pw_hash']:
        error = 'Data tidak ditemukan.'
    elif not check_user_pw(old_pw, inv['user_pw_hash']):
        error = 'Password lama salah.'
    elif len(new_pw) < 6:
        error = 'Password baru minimal 6 karakter.'
    elif new_pw != new_pw2:
        error = 'Konfirmasi password tidak cocok.'
    if error:
        conn.close()
        return redirect(url_for('user_dashboard') + '?pw_error=' + error)
    conn.execute('UPDATE invitations SET user_pw_hash=? WHERE id=?', (hash_user_pw(new_pw), inv_id))
    conn.commit(); conn.close()
    return redirect(url_for('user_dashboard') + '?pw_ok=1')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')

@app.route('/legal')
def legal():
    return render_template('legal.html', 
        site_name=SITE_NAME, 
        wa_number=WA_NUMBER,
        now=datetime.now()
    )


# ─── MAIN ────────────────────────────────────────────────────────────────────
def _cli_list_users():
    conn = get_db()
    rows = conn.execute(
        'SELECT user_username, groom_name, bride_name, slug, payment_status, expires_at '
        'FROM invitations WHERE user_username IS NOT NULL ORDER BY created_at DESC'
    ).fetchall()
    conn.close()
    if not rows: print('Tidak ada user.'); return
    print(f'{"USERNAME":<20} {"MEMPELAI":<35} {"SLUG":<30} {"STATUS":<10} EXPIRES')
    print('-' * 108)
    for r in rows:
        print(f'{r["user_username"]:<20} {r["groom_name"]+" & "+r["bride_name"]:<35} {r["slug"] or "-":<30} {r["payment_status"] or "-":<10} {r["expires_at"] or "-"}')

def _cli_reset_password(username):
    import getpass
    conn = get_db()
    row = conn.execute('SELECT id FROM invitations WHERE user_username=?', (username,)).fetchone()
    if not row: print(f'[ERROR] User "{username}" tidak ditemukan.'); conn.close(); return
    print(f'Reset password untuk: {username}')
    while True:
        pw  = getpass.getpass('Password baru (min 8 karakter): ')
        pw2 = getpass.getpass('Konfirmasi: ')
        if len(pw) < 8: print('[ERROR] Min 8 karakter.'); continue
        if pw != pw2:   print('[ERROR] Tidak cocok.'); continue
        break
    conn.execute('UPDATE invitations SET user_pw_hash=? WHERE user_username=?', (hash_user_pw(pw), username))
    conn.commit(); conn.close()
    print(f'[OK] Password "{username}" berhasil direset.')

def _cli_edit_slug(username, new_slug):
    clean = re.sub(r'[^a-z0-9-]', '-', new_slug.lower().replace(' ', '-')).strip('-')
    if len(clean) < 3: print('[ERROR] Slug tidak valid (min 3 karakter, huruf kecil/angka/strip).'); return
    conn = get_db()
    row = conn.execute('SELECT slug FROM invitations WHERE user_username=?', (username,)).fetchone()
    if not row: print(f'[ERROR] User "{username}" tidak ditemukan.'); conn.close(); return
    conflict = conn.execute('SELECT user_username FROM invitations WHERE slug=? AND user_username!=?', (clean, username)).fetchone()
    if conflict: print(f'[ERROR] Slug "{clean}" sudah dipakai oleh "{conflict["user_username"]}".'); conn.close(); return
    old = row['slug']
    conn.execute('UPDATE invitations SET slug=? WHERE user_username=?', (clean, username))
    conn.commit(); conn.close()
    print(f'[OK] Slug "{username}": "{old}" -> "{clean}"  |  URL: /i/{clean}')

if __name__ == '__main__':
    init_db()
    _ensure_user_columns()

    _CLI = {'list-users', 'reset-password', 'edit-slug'}
    if len(sys.argv) > 1 and sys.argv[1] in _CLI:
        cmd = sys.argv[1]
        if cmd == 'list-users':
            _cli_list_users()
        elif cmd == 'reset-password':
            if len(sys.argv) < 3: print('Usage: python app.py reset-password <username>')
            else: _cli_reset_password(sys.argv[2])
        elif cmd == 'edit-slug':
            if len(sys.argv) < 4: print('Usage: python app.py edit-slug <username> <slug_baru>')
            else: _cli_edit_slug(sys.argv[2], sys.argv[3])
        sys.exit(0)

    # Server mode
    threading.Thread(target=_cleanup_loop, daemon=True, name='auto-cleanup').start()
    print('─' * 50)
    print(f'  UndanganKita — Admin: {ADMIN_USERNAME} / admin123')
    print(f'  Site: {SITE_NAME}  |  WA: {WA_NUMBER}')
    print(f'  reCAPTCHA: {"AKTIF" if RECAPTCHA_KEY else "nonaktif (set RECAPTCHA_SITE_KEY)"}')
    print(f'  Auto-cleanup: aktif (grace {CLEANUP_GRACE_DAYS} hari, tiap 24 jam)')
    print('─' * 50)
    print('  Admin pw : python -c "from app import hash_pw; print(hash_pw(\'pw\'))"')
    print('  CLI      : python app.py list-users')
    print('             python app.py reset-password <username>')
    print('             python app.py edit-slug <username> <slug_baru>')
    print('─' * 50)
    app.run(debug=False, port=5000)



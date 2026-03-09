"""
UndanganKita v3 — Flask Wedding Invitation App
Config via environment variables (see README).
"""

from flask import (Flask, render_template, request, redirect, url_for, make_response,
                   jsonify, abort, session, flash, send_from_directory)
import json, os, uuid, hashlib, hmac, secrets, sqlite3, re, time
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from flask import send_from_directory

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# ─── CONFIG ──────────────────────────────────────────────────────────────────
BASE_DIR        = Path(__file__).parent
DB_PATH         = BASE_DIR / 'data' / 'undangan.db'
UPLOAD_DIR           = BASE_DIR / 'static' / 'uploads' / 'invitations'
THEMES_DIR           = BASE_DIR / 'themes'
DEMO_PHOTOS_DIR      = BASE_DIR / 'static' / 'demo-photos'
DEMO_PORTRAIT_DIR    = BASE_DIR / 'static' / 'demo-photos' / 'individual'  # groom.*/bride.* khusus preview

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DEMO_PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
DEMO_PORTRAIT_DIR.mkdir(parents=True, exist_ok=True)

MAX_UPLOAD_MB   = 5
ALLOWED_EXT     = {'jpg','jpeg','png','webp'}
MAX_PHOTOS      = 10
SESSION_HOURS   = 8

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
    groom   = inv.get('groom_name', '')
    bride   = inv.get('bride_name', '')
    slug    = inv.get('slug', '')
    url     = f'https://{site_name}/i/{slug}'

    # Judul & deskripsi
    title   = f"Undangan Pernikahan {groom} & {bride}"
    resepsi_date = inv.get('resepsi_date', '')
    venue        = inv.get('resepsi_venue', '') or inv.get('akad_venue', '')
    try:
        from datetime import datetime as _dt
        d = _dt.strptime(resepsi_date, '%Y-%m-%d')
        days   = ['Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu']
        months = ['Januari','Februari','Maret','April','Mei','Juni','Juli',
                  'Agustus','September','Oktober','November','Desember']
        tgl = f"{days[d.weekday()]}, {d.day} {months[d.month-1]} {d.year}"
    except:
        tgl = resepsi_date

    desc_parts = [f"Kami mengundang kehadiran Bapak/Ibu/Saudara/i pada pernikahan {groom} & {bride}."]
    if tgl:   desc_parts.append(f"📅 {tgl}")
    if venue: desc_parts.append(f"📍 {venue}")
    desc_parts.append(f"Buka undangan digital di: {url}")
    description = " · ".join(desc_parts)

    # Gambar OG — prioritas: cover_photo > groom_photo > foto gallery pertama > banner
    image_url = None
    if inv.get('cover_photo'):
        image_url = f'https://{site_name}/uploads/{inv["cover_photo"]}'
    elif inv.get('groom_photo'):
        image_url = f'https://{site_name}/uploads/{inv["groom_photo"]}'
    elif photos:
        first = photos[0]
        fn = first['filename'] if isinstance(first, dict) else first.filename
        is_url = first['is_url'] if isinstance(first, dict) else first.is_url
        if is_url:
            image_url = fn
        else:
            image_url = f'https://{site_name}/uploads/{fn}'
    if not image_url:
        image_url = f'https://{site_name}/static/themes/banner.jpg'

    theme_name = theme.get('name', '') if theme else ''

    tags = f"""
  <!-- OG Tags — auto-inject by UndanganKita, no tema edit needed -->
  <meta property="og:type"        content="website">
  <meta property="og:url"         content="{url}">
  <meta property="og:site_name"   content="{site_name}">
  <meta property="og:title"       content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:image"       content="{image_url}">
  <meta property="og:image:alt"   content="Undangan Pernikahan {groom} &amp; {bride}">
  <meta property="og:locale"      content="id_ID">
  <meta name="twitter:card"        content="summary_large_image">
  <meta name="twitter:title"       content="{title}">
  <meta name="twitter:description" content="{description}">
  <meta name="twitter:image"       content="{image_url}">
  <meta name="description"         content="{description}">
  <title>{title}{(' — ' + theme_name) if theme_name else ''}</title>"""
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
    conn.close()
    html = render_template(f'themes/{inv["theme_id"]}.html',
                           inv=inv, theme=theme, rsvp_list=rsvps,
                           gifts=gifts, photos=photos, is_preview=False)
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
    conn   = get_db()
    q      = request.args.get('q','').strip()
    qt     = request.args.get('qt','').strip()  # query for themes
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
    total_rsvp = conn.execute('SELECT COUNT(*) as c FROM rsvp').fetchone()['c']
    conn.close()
    all_themes = get_all_themes()
    if qt:
        filtered_themes = [t for t in all_themes if qt.lower() in t.get('name','').lower() or qt.lower() in t.get('id','').lower()]
    else:
        filtered_themes = all_themes
    return render_template('admin/dashboard.html',
                           invitations=invs, themes=all_themes,
                           filtered_themes=filtered_themes,
                           total_rsvp=total_rsvp, search_q=q, search_qt=qt)

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
        maps_embed = f.get('maps_embed','').strip() or extract_maps_embed_src(f.get('maps_url',''))
        conn = get_db()
        try:
            conn.execute('''INSERT INTO invitations
                (id,slug,theme_id,groom_name,bride_name,groom_full,bride_full,
                 groom_parents,bride_parents,show_parents,
                 akad_date,akad_time,akad_venue,akad_address,
                 resepsi_date,resepsi_time,resepsi_venue,resepsi_address,
                 maps_url,maps_embed,love_story,music_url,expires_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (iid,slug,f['theme_id'],f['groom_name'],f['bride_name'],
                 f.get('groom_full'),f.get('bride_full'),
                 f.get('groom_parents'),f.get('bride_parents'),
                 1 if f.get('show_parents') else 0,
                 f.get('akad_date'),f.get('akad_time'),f.get('akad_venue'),f.get('akad_address'),
                 f.get('resepsi_date'),f.get('resepsi_time'),f.get('resepsi_venue'),f.get('resepsi_address'),
                 f.get('maps_url'),maps_embed,f.get('love_story'),f.get('music_url'),exp))
            if f.get('bank_name'):
                conn.execute('INSERT INTO gifts(invitation_id,bank_name,account_number,account_name) VALUES(?,?,?,?)',
                             (iid,f['bank_name'],f.get('account_number'),f.get('account_name')))
            conn.commit()
            _save_photos(conn, iid, request.files, f)
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
        maps_embed = f.get('maps_embed','').strip() or extract_maps_embed_src(f.get('maps_url',''))
        try:
            conn.execute('''UPDATE invitations SET
                theme_id=?,groom_name=?,bride_name=?,groom_full=?,bride_full=?,
                groom_parents=?,bride_parents=?,show_parents=?,
                akad_date=?,akad_time=?,akad_venue=?,akad_address=?,
                resepsi_date=?,resepsi_time=?,resepsi_venue=?,resepsi_address=?,
                maps_url=?,maps_embed=?,love_story=?,music_url=?,expires_at=?,
                updated_at=CURRENT_TIMESTAMP WHERE id=?''',
                (f['theme_id'],f['groom_name'],f['bride_name'],
                 f.get('groom_full'),f.get('bride_full'),
                 f.get('groom_parents'),f.get('bride_parents'),
                 1 if f.get('show_parents') else 0,
                 f.get('akad_date'),f.get('akad_time'),f.get('akad_venue'),f.get('akad_address'),
                 f.get('resepsi_date'),f.get('resepsi_time'),f.get('resepsi_venue'),f.get('resepsi_address'),
                 f.get('maps_url'),maps_embed,f.get('love_story'),f.get('music_url'),
                 f.get('expires_at'),inv_id))
            conn.execute('DELETE FROM gifts WHERE invitation_id=?',(inv_id,))
            if f.get('bank_name'):
                conn.execute('INSERT INTO gifts(invitation_id,bank_name,account_number,account_name) VALUES(?,?,?,?)',
                             (inv_id,f['bank_name'],f.get('account_number'),f.get('account_name')))
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
                                   gift=dict(gifts[0]) if gifts else {}, photos=list(photos), error=str(e))
    gift = dict(gifts[0]) if gifts else {}
    conn.close()
    return render_template('admin/edit.html', inv=inv, themes=themes,
                           gift=gift, photos=list(photos))

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
    # Hapus file portrait (groom_photo & bride_photo)
    inv_row = conn.execute('SELECT groom_photo, bride_photo FROM invitations WHERE id=?',(inv_id,)).fetchone()
    if inv_row:
        for col in ('groom_photo', 'bride_photo'):
            if inv_row[col]:
                try: (UPLOAD_DIR / inv_row[col]).unlink(missing_ok=True)
                except: pass
    # Cascade delete semua data + row undangan (hard delete supaya storage bersih)
    conn.execute('DELETE FROM rsvp WHERE invitation_id=?',(inv_id,))
    conn.execute('DELETE FROM gifts WHERE invitation_id=?',(inv_id,))
    conn.execute('DELETE FROM invitation_photos WHERE invitation_id=?',(inv_id,))
    conn.execute('DELETE FROM invitations WHERE id=?',(inv_id,))
    conn.commit(); conn.close()
    flash('Undangan dihapus.','info')
    return redirect(url_for('admin_dashboard'))

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
@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')


# ─── MAIN ────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    print('─' * 50)
    print(f'  UndanganKita — Admin: {ADMIN_USERNAME} / admin123')
    print(f'  Site: {SITE_NAME}  |  WA: {WA_NUMBER}')
    print(f'  reCAPTCHA: {"AKTIF" if RECAPTCHA_KEY else "nonaktif (set RECAPTCHA_SITE_KEY)"}')
    print('─' * 50)
    print('  Ganti password:')
    print('  python -c "from app import hash_pw; print(hash_pw(\'newpass\'))"')
    print('  lalu set env: ADMIN_PW_HASH=<hash>')
    print('─' * 50)
    app.run(debug=False, port=5000)


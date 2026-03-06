"""
UndanganKita — Flask App
Features: Admin auth (secure), expired logic, edit invitations,
          photo upload (file + URL), theme catalog, WA order
"""

from flask import (Flask, render_template, request, redirect, url_for,
                   jsonify, abort, session, flash, send_from_directory)
import json, os, uuid, hashlib, hmac, secrets, sqlite3, re
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# ─── CONFIG ──────────────────────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent
DB_PATH     = BASE_DIR / 'data' / 'undangan.db'
UPLOAD_DIR  = BASE_DIR / 'static' / 'uploads' / 'invitations'
THEMES_DIR  = BASE_DIR / 'themes'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_UPLOAD_MB   = 5
ALLOWED_EXT     = {'jpg','jpeg','png','webp'}
MAX_PHOTOS      = 10
SESSION_HOURS   = 8
LOGIN_ATTEMPTS  = {}   # {ip: [datetime, ...]}
MAX_ATTEMPTS    = 5
LOCKOUT_MINUTES = 15

ADMIN_USERNAME = os.environ.get('ADMIN_USER', 'admin')
_DEFAULT_PW_HASH = 'pbkdf2:sha256:260000$undangankita$' + \
    hashlib.pbkdf2_hmac('sha256', b'admin123', b'undangankita', 260000).hex()
ADMIN_PW_HASH  = os.environ.get('ADMIN_PW_HASH', _DEFAULT_PW_HASH)
WA_NUMBER      = os.environ.get('WA_NUMBER', '6281234567890')

# ─── AUTH UTILS ──────────────────────────────────────────────────────────────
def hash_pw(password, salt='undangankita'):
    dk = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 260000)
    return f'pbkdf2:sha256:260000${salt}${dk.hex()}'

def check_pw(password, stored):
    try:
        _, _, rest = stored.split(':', 2)
        parts = rest.split('$')
        salt = parts[1]   # format: 260000$salt$hash
        return hmac.compare_digest(hash_pw(password, salt), stored)
    except Exception:
        return False

def login_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        if (datetime.now().timestamp() - session.get('last_active', 0)) > SESSION_HOURS*3600:
            session.clear()
            flash('Sesi berakhir. Silakan login kembali.', 'warning')
            return redirect(url_for('admin_login'))
        session['last_active'] = datetime.now().timestamp()
        return f(*a, **kw)
    return dec

def is_locked(ip):
    now = datetime.now()
    att = [t for t in LOGIN_ATTEMPTS.get(ip, []) if (now-t).total_seconds() < LOCKOUT_MINUTES*60]
    LOGIN_ATTEMPTS[ip] = att
    return len(att) >= MAX_ATTEMPTS

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
            groom_full TEXT, bride_full TEXT, groom_parents TEXT, bride_parents TEXT,
            akad_date TEXT, akad_time TEXT, akad_venue TEXT, akad_address TEXT,
            resepsi_date TEXT, resepsi_time TEXT, resepsi_venue TEXT, resepsi_address TEXT,
            maps_url TEXT, love_story TEXT, music_url TEXT, cover_photo TEXT,
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
    for col in ['cover_photo TEXT','expires_at TEXT','updated_at TEXT','is_url INTEGER DEFAULT 0']:
        try:
            tbl, coldef = ('invitations', col) if 'TEXT' in col or 'INTEGER' in col and 'is_url' not in col else ('invitation_photos', col)
            # crude but safe
            if 'is_url' in col:
                c.execute('ALTER TABLE invitation_photos ADD COLUMN is_url INTEGER DEFAULT 0')
            else:
                c.execute(f'ALTER TABLE invitations ADD COLUMN {col}')
        except Exception:
            pass
    c.commit(); c.close()

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def allowed_file(fn): return '.' in fn and fn.rsplit('.',1)[1].lower() in ALLOWED_EXT
def secure_name(fn):
    ext = fn.rsplit('.',1)[1].lower() if '.' in fn else 'jpg'
    return f'{uuid.uuid4().hex}.{ext}'

def get_all_themes():
    themes = []
    if THEMES_DIR.exists():
        for f in sorted(THEMES_DIR.glob('*.json')):
            with open(f) as fp: themes.append(json.load(fp))
    return themes

def get_theme(tid):
    p = THEMES_DIR / f'{tid}.json'
    return json.load(open(p)) if p.exists() else None

def get_inv_photos(conn, inv_id):
    return conn.execute(
        'SELECT * FROM invitation_photos WHERE invitation_id=? ORDER BY sort_order,id',
        (inv_id,)
    ).fetchall()

def photo_src(row):
    """Return display URL for a photo row"""
    if row['is_url']:
        return row['filename']   # stored as URL string
    return f'/uploads/{row["filename"]}'

def is_expired(inv):
    exp = inv['expires_at'] if isinstance(inv, dict) else (inv['expires_at'] if inv else None)
    if not exp: return False
    try: return datetime.strptime(exp, '%Y-%m-%d') < datetime.now()
    except: return False

def delete_photo_file(row):
    if not row['is_url']:
        try: (UPLOAD_DIR / row['filename']).unlink(missing_ok=True)
        except: pass

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
    return {'now': datetime.now(), 'wa_number': WA_NUMBER, 'photo_src': photo_src}

# ─── PUBLIC ──────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html', themes=get_all_themes())

@app.route('/themes')
def themes_page():
    return render_template('themes_catalog.html', themes=get_all_themes())

@app.route('/preview/<theme_id>')
def preview_theme(theme_id):
    theme = get_theme(theme_id)
    if not theme: abort(404)
    dummy = dict(
        id='preview', slug='preview', theme_id=theme_id,
        groom_name='Rizky', bride_name='Amara',
        groom_full='Muhammad Rizky Pratama, S.T.',
        bride_full='Amara Putri Sanjaya, S.Kom.',
        groom_parents='Bapak Hendra & Ibu Dewi',
        bride_parents='Bapak Santoso & Ibu Lestari',
        akad_date='2025-12-20', akad_time='08:00',
        akad_venue='Masjid Al-Ikhlas',
        akad_address='Jl. Mawar No. 12, Jakarta Selatan',
        resepsi_date='2025-12-20', resepsi_time='11:00',
        resepsi_venue='Grand Ballroom Hotel Bintang',
        resepsi_address='Jl. Sudirman No. 88, Jakarta',
        maps_url='https://maps.google.com',
        love_story='Kami pertama bertemu di kampus pada tahun 2019. Berawal dari teman sekelas, lalu sahabat, dan kini kami memutuskan untuk melangkah bersama menuju jenjang pernikahan yang penuh berkah.',
        cover_photo=None, music_url=None, expires_at=None, is_preview=True
    )
    return render_template(f'themes/{theme_id}.html',
                           inv=dummy, theme=theme, rsvp_list=[], gifts=[],
                           photos=[], is_preview=True)

@app.route('/i/<slug>')
def view_invitation(slug):
    conn = get_db()
    inv  = conn.execute('SELECT * FROM invitations WHERE slug=? AND is_active=1',(slug,)).fetchone()
    if not inv: conn.close(); abort(404)
    inv = dict(inv)
    if is_expired(inv): conn.close(); return render_template('expired.html', inv=inv)
    theme  = get_theme(inv['theme_id'])
    rsvps  = conn.execute('SELECT * FROM rsvp WHERE invitation_id=? ORDER BY created_at DESC LIMIT 30',(inv['id'],)).fetchall()
    gifts  = conn.execute('SELECT * FROM gifts WHERE invitation_id=?',(inv['id'],)).fetchall()
    photos = get_inv_photos(conn, inv['id'])
    conn.close()
    return render_template(f'themes/{inv["theme_id"]}.html',
                           inv=inv, theme=theme, rsvp_list=rsvps,
                           gifts=gifts, photos=photos, is_preview=False)

@app.route('/rsvp/<inv_id>', methods=['POST'])
def submit_rsvp(inv_id):
    data = request.get_json()
    if not data or not data.get('name','').strip():
        return jsonify({'error':'Nama wajib diisi'}), 400
    conn = get_db()
    inv  = conn.execute('SELECT * FROM invitations WHERE id=? AND is_active=1',(inv_id,)).fetchone()
    if not inv or is_expired(dict(inv)):
        conn.close(); return jsonify({'error':'Undangan tidak tersedia'}), 404
    conn.execute(
        'INSERT INTO rsvp (invitation_id,guest_name,attendance,guest_count,message) VALUES(?,?,?,?,?)',
        (inv_id, data['name'].strip()[:100], data.get('attendance','hadir'),
         min(int(data.get('count',1)),20), data.get('message','')[:500])
    )
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
    error = None
    ip    = request.remote_addr
    if request.method == 'POST':
        if is_locked(ip):
            error = f'Terlalu banyak percobaan. Coba lagi dalam {LOCKOUT_MINUTES} menit.'
        else:
            u = request.form.get('username','').strip()
            p = request.form.get('password','')
            if u == ADMIN_USERNAME and check_pw(p, ADMIN_PW_HASH):
                LOGIN_ATTEMPTS.pop(ip, None)
                session.clear()
                session['admin_logged_in'] = True
                session['last_active']     = datetime.now().timestamp()
                return redirect(url_for('admin_dashboard'))
            else:
                LOGIN_ATTEMPTS.setdefault(ip,[]).append(datetime.now())
                rem = MAX_ATTEMPTS - len(LOGIN_ATTEMPTS.get(ip,[]))
                error = f'Username atau password salah. Sisa percobaan: {max(rem,0)}'
    return render_template('admin/login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    session.clear(); return redirect(url_for('admin_login'))

# ─── ADMIN DASHBOARD ─────────────────────────────────────────────────────────
@app.route('/admin')
@login_required
def admin_dashboard():
    conn = get_db()
    rows = conn.execute('SELECT * FROM invitations WHERE is_active=1 ORDER BY created_at DESC').fetchall()
    invs = []
    for r in rows:
        d = dict(r)
        d['rsvp_count'] = conn.execute('SELECT COUNT(*) as c FROM rsvp WHERE invitation_id=?',(d['id'],)).fetchone()['c']
        d['is_expired'] = is_expired(d)
        invs.append(d)
    conn.close()
    return render_template('admin/dashboard.html',
                           invitations=invs, themes=get_all_themes(),
                           total_rsvp=sum(i['rsvp_count'] for i in invs))

# ─── ADMIN CREATE ────────────────────────────────────────────────────────────
@app.route('/admin/create', methods=['GET','POST'])
@login_required
def admin_create():
    themes = get_all_themes()
    if request.method == 'POST':
        f   = request.form
        iid = uuid.uuid4().hex[:10]
        slug = re.sub(r'[^a-z0-9-]','', f['slug'].lower().replace(' ','-'))
        if not slug:
            return render_template('admin/create.html', themes=themes, error='Slug tidak valid.', form=f)
        try:
            rd  = datetime.strptime(f.get('resepsi_date',''), '%Y-%m-%d')
            exp = (rd + timedelta(days=365)).strftime('%Y-%m-%d')
        except:
            exp = (datetime.now()+timedelta(days=365)).strftime('%Y-%m-%d')
        conn = get_db()
        try:
            conn.execute('''INSERT INTO invitations
                (id,slug,theme_id,groom_name,bride_name,groom_full,bride_full,
                 groom_parents,bride_parents,akad_date,akad_time,akad_venue,akad_address,
                 resepsi_date,resepsi_time,resepsi_venue,resepsi_address,
                 maps_url,love_story,music_url,expires_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (iid,slug,f['theme_id'],f['groom_name'],f['bride_name'],
                 f.get('groom_full'),f.get('bride_full'),
                 f.get('groom_parents'),f.get('bride_parents'),
                 f.get('akad_date'),f.get('akad_time'),f.get('akad_venue'),f.get('akad_address'),
                 f.get('resepsi_date'),f.get('resepsi_time'),f.get('resepsi_venue'),f.get('resepsi_address'),
                 f.get('maps_url'),f.get('love_story'),f.get('music_url'),exp))
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
            return render_template('admin/create.html',themes=themes,error=f'Slug "{slug}" sudah dipakai.',form=f)
        except Exception as e:
            conn.close()
            return render_template('admin/create.html',themes=themes,error=str(e),form=f)
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
        try:
            conn.execute('''UPDATE invitations SET
                theme_id=?,groom_name=?,bride_name=?,groom_full=?,bride_full=?,
                groom_parents=?,bride_parents=?,akad_date=?,akad_time=?,
                akad_venue=?,akad_address=?,resepsi_date=?,resepsi_time=?,
                resepsi_venue=?,resepsi_address=?,maps_url=?,love_story=?,
                music_url=?,expires_at=?,updated_at=CURRENT_TIMESTAMP WHERE id=?''',
                (f['theme_id'],f['groom_name'],f['bride_name'],
                 f.get('groom_full'),f.get('bride_full'),
                 f.get('groom_parents'),f.get('bride_parents'),
                 f.get('akad_date'),f.get('akad_time'),
                 f.get('akad_venue'),f.get('akad_address'),
                 f.get('resepsi_date'),f.get('resepsi_time'),
                 f.get('resepsi_venue'),f.get('resepsi_address'),
                 f.get('maps_url'),f.get('love_story'),f.get('music_url'),
                 f.get('expires_at'),inv_id))
            conn.execute('DELETE FROM gifts WHERE invitation_id=?',(inv_id,))
            if f.get('bank_name'):
                conn.execute('INSERT INTO gifts(invitation_id,bank_name,account_number,account_name) VALUES(?,?,?,?)',
                             (inv_id,f['bank_name'],f.get('account_number'),f.get('account_name')))
            conn.commit()
            _save_photos(conn, inv_id, request.files, f)
            conn.commit(); conn.close()
            flash('Undangan berhasil diperbarui! ✓','success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            conn.close()
            return render_template('admin/edit.html',inv=inv,themes=themes,
                                   gift=dict(gifts[0]) if gifts else {},
                                   photos=photos,error=str(e))
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
    for p in conn.execute('SELECT * FROM invitation_photos WHERE invitation_id=?',(inv_id,)).fetchall():
        delete_photo_file(dict(p))
    conn.execute('UPDATE invitations SET is_active=0 WHERE id=?',(inv_id,))
    conn.commit(); conn.close()
    flash('Undangan dihapus.','info')
    return redirect(url_for('admin_dashboard'))

# Theme demo photos (untuk katalog)
@app.route('/admin/theme-demo/<theme_id>', methods=['POST'])
@login_required
def upload_theme_demo(theme_id):
    theme = get_theme(theme_id)
    if not theme: abort(404)
    results = []
    for key in request.files:
        f = request.files[key]
        if f and f.filename and allowed_file(f.filename):
            f.stream.seek(0,2); size=f.stream.tell(); f.stream.seek(0)
            if size > MAX_UPLOAD_MB*1024*1024: continue
            ext  = f.filename.rsplit('.',1)[1].lower()
            name = f'demo_{uuid.uuid4().hex[:8]}.{ext}'
            dest = BASE_DIR / 'static' / 'themes' / theme_id
            dest.mkdir(parents=True, exist_ok=True)
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

# ─── PHOTO SAVE HELPER ───────────────────────────────────────────────────────
def _save_photos(conn, inv_id, files, form):
    existing = conn.execute(
        'SELECT COUNT(*) as c FROM invitation_photos WHERE invitation_id=?',(inv_id,)
    ).fetchone()['c']
    saved = 0
    # 1. Upload file
    for key in files:
        if saved+existing >= MAX_PHOTOS: break
        f = files[key]
        if not f or not f.filename or not allowed_file(f.filename): continue
        f.stream.seek(0,2); size=f.stream.tell(); f.stream.seek(0)
        if size > MAX_UPLOAD_MB*1024*1024: continue
        fname = secure_name(f.filename)
        f.save(str(UPLOAD_DIR/fname))
        conn.execute(
            'INSERT INTO invitation_photos(invitation_id,filename,is_url,sort_order) VALUES(?,?,0,?)',
            (inv_id, fname, existing+saved))
        saved += 1
    # 2. URL tambahan
    for i in range(10):
        if saved+existing >= MAX_PHOTOS: break
        url = form.get(f'photo_url_{i}','').strip() if form else ''
        if not url: continue
        if not url.startswith(('http://','https://')): continue
        conn.execute(
            'INSERT INTO invitation_photos(invitation_id,filename,is_url,sort_order) VALUES(?,?,1,?)',
            (inv_id, url, existing+saved))
        saved += 1

# ─── MAIN ────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    print('=== UndanganKita ===')
    print(f'Admin: {ADMIN_USERNAME} / admin123')
    print(f'WA   : {WA_NUMBER}')
    print('Ganti password: python -c "from app import hash_pw; print(hash_pw(\'pwbaru\'))"')
    print('Set env: ADMIN_PW_HASH=<hash>')
    print('====================')
    app.run(debug=True, port=5000)

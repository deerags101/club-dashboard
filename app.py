from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3, os, hashlib
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret")

# 🔐 helpers
def hash_password(p): return hashlib.sha256(p.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if not session.get("admin"): return redirect(url_for("login"))
        return f(*a, **kw)
    return wrapper

# 🗄️ DB init (auto on start)
def init_db():
    conn = sqlite3.connect("database.db")
    conn.execute("CREATE TABLE IF NOT EXISTS admins (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS teams (id INTEGER PRIMARY KEY, name TEXT, leader TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS members (id INTEGER PRIMARY KEY, name TEXT, team_id INTEGER)")
    conn.execute("CREATE TABLE IF NOT EXISTS scores (id INTEGER PRIMARY KEY, team_id INTEGER, score INTEGER)")
    # default admin: admin / 1234
    conn.execute("INSERT OR IGNORE INTO admins (username, password) VALUES (?,?)",
                 ("admin", hash_password("1234")))
    conn.commit(); conn.close()

init_db()

def get_db(): return sqlite3.connect("database.db")

# 🌐 PUBLIC DASHBOARD
@app.route('/')
def index():
    conn = get_db()
    teams = conn.execute("""
        SELECT t.id, t.name, t.leader, IFNULL(SUM(s.score),0) AS total
        FROM teams t
        LEFT JOIN scores s ON t.id = s.team_id
        GROUP BY t.id
        ORDER BY total DESC
    """).fetchall()

    data = []
    for t in teams:
        members = conn.execute("SELECT name FROM members WHERE team_id=?", (t[0],)).fetchall()
        data.append({
            "name": t[1],
            "leader": t[2],
            "score": t[3],
            "members": [m[0] for m in members]
        })
    conn.close()
    return render_template("index.html", teams=data)

# 🔐 LOGIN
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = hash_password(request.form['password'])
        conn = get_db()
        row = conn.execute("SELECT 1 FROM admins WHERE username=? AND password=?", (u,p)).fetchone()
        conn.close()
        if row:
            session['admin'] = u
            return redirect('/admin')
    return render_template("login.html")

# 🔓 LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# 🛠️ ADMIN PANEL
@app.route('/admin')
@login_required
def admin():
    conn = get_db()
    teams = conn.execute("SELECT id, name FROM teams").fetchall()
    conn.close()
    return render_template("admin.html", teams=teams)

# ➕ ACTIONS (ADMIN ONLY)
@app.route('/add_team', methods=['POST'])
@login_required
def add_team():
    conn = get_db()
    conn.execute("INSERT INTO teams (name, leader) VALUES (?,?)",
                 (request.form['name'], request.form['leader']))
    conn.commit(); conn.close()
    return redirect('/admin')

@app.route('/add_member', methods=['POST'])
@login_required
def add_member():
    conn = get_db()
    conn.execute("INSERT INTO members (name, team_id) VALUES (?,?)",
                 (request.form['name'], request.form['team_id']))
    conn.commit(); conn.close()
    return redirect('/admin')

@app.route('/add_score', methods=['POST'])
@login_required
def add_score():
    conn = get_db()
    conn.execute("INSERT INTO scores (team_id, score) VALUES (?,?)",
                 (request.form['team_id'], request.form['score']))
    conn.commit(); conn.close()
    return redirect('/admin')

# 🚀 RUN (Render compatible)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

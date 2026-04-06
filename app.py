from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"  # 🔐 session ke liye

# 🔥 AUTO DB
def init_db_auto():
    conn = sqlite3.connect("database.db")

    conn.execute("CREATE TABLE IF NOT EXISTS teams (id INTEGER PRIMARY KEY, name TEXT, leader TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS members (id INTEGER PRIMARY KEY, name TEXT, team_id INTEGER)")
    conn.execute("CREATE TABLE IF NOT EXISTS scores (id INTEGER PRIMARY KEY, team_id INTEGER, score INTEGER)")

    conn.commit()
    conn.close()

init_db_auto()

def get_db():
    return sqlite3.connect("database.db")

# 🌐 PUBLIC VIEW
@app.route('/')
def index():
    conn = get_db()

    teams = conn.execute("""
    SELECT teams.id, teams.name, teams.leader,
    IFNULL(SUM(scores.score),0)
    FROM teams
    LEFT JOIN scores ON teams.id = scores.team_id
    GROUP BY teams.id
    ORDER BY SUM(scores.score) DESC
    """).fetchall()

    data = []
    for t in teams:
        members = conn.execute("SELECT name FROM members WHERE team_id=?", (t[0],)).fetchall()
        data.append({
            "name": t[1],
            "leader": t[2],
            "score": t[3] or 0,
            "members": [m[0] for m in members]
        })

    conn.close()
    return render_template("index.html", teams=data)


# 🔐 LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        if user == "admin" and pwd == "1234":
            session['admin'] = True
            return redirect('/admin')

    return render_template("login.html")


# 🔓 LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# 🛠️ ADMIN PANEL
@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/login')

    conn = get_db()
    teams = conn.execute("SELECT id, name FROM teams").fetchall()
    conn.close()

    return render_template("admin.html", teams=teams)


# ➕ ADD TEAM
@app.route('/add_team', methods=['POST'])
def add_team():
    if not session.get('admin'):
        return redirect('/login')

    conn = get_db()
    conn.execute("INSERT INTO teams (name, leader) VALUES (?,?)",
                 (request.form['name'], request.form['leader']))
    conn.commit()
    conn.close()
    return redirect('/admin')


# ➕ ADD MEMBER
@app.route('/add_member', methods=['POST'])
def add_member():
    if not session.get('admin'):
        return redirect('/login')

    conn = get_db()
    conn.execute("INSERT INTO members (name, team_id) VALUES (?,?)",
                 (request.form['name'], request.form['team_id']))
    conn.commit()
    conn.close()
    return redirect('/admin')


# ➕ ADD SCORE
@app.route('/add_score', methods=['POST'])
def add_score():
    if not session.get('admin'):
        return redirect('/login')

    conn = get_db()
    conn.execute("INSERT INTO scores (team_id, score) VALUES (?,?)",
                 (request.form['team_id'], request.form['score']))
    conn.commit()
    conn.close()
    return redirect('/admin')


# 🚀 RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

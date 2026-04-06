from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db():
    return sqlite3.connect("database.db")

@app.route('/')
def index():
    conn = get_db()

    teams = conn.execute("""
    SELECT teams.id, teams.name, teams.leader,
    IFNULL(SUM(scores.score),0) as total_score
    FROM teams
    LEFT JOIN scores ON teams.id = scores.team_id
    GROUP BY teams.id
    ORDER BY total_score DESC
    """).fetchall()

    team_data = []

    for team in teams:
        members = conn.execute(
            "SELECT name FROM members WHERE team_id=?",
            (team[0],)
        ).fetchall()

        member_list = [m[0] for m in members]

        team_data.append({
            "name": team[1],
            "leader": team[2],
            "score": team[3],
            "members": member_list
        })

    # ✅ IMPORTANT FIX
    all_teams = conn.execute("SELECT id, name FROM teams").fetchall()

    conn.close()

    return render_template("index.html", teams=team_data, all_teams=all_teams)


@app.route('/add_team', methods=['POST'])
def add_team():
    name = request.form['name']
    leader = request.form['leader']

    conn = get_db()
    conn.execute("INSERT INTO teams (name, leader) VALUES (?,?)", (name, leader))
    conn.commit()
    conn.close()

    return redirect('/')


@app.route('/add_member', methods=['POST'])
def add_member():
    name = request.form['name']
    team_id = request.form['team_id']

    conn = get_db()
    conn.execute("INSERT INTO members (name, team_id) VALUES (?,?)", (name, team_id))
    conn.commit()
    conn.close()

    return redirect('/')


@app.route('/add_score', methods=['POST'])
def add_score():
    team_id = request.form['team_id']
    score = request.form['score']

    conn = get_db()
    conn.execute("INSERT INTO scores (team_id, score) VALUES (?,?)", (team_id, score))
    conn.commit()
    conn.close()

    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
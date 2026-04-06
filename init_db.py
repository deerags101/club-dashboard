import sqlite3

conn = sqlite3.connect("database.db")

conn.execute("""
CREATE TABLE teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    leader TEXT
)
""")

conn.execute("""
CREATE TABLE members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    team_id INTEGER
)
""")

conn.execute("""
CREATE TABLE scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER,
    score INTEGER
)
""")

conn.commit()
conn.close()

print("Database Ready ✅")
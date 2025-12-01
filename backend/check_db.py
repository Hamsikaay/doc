import sqlite3

conn = sqlite3.connect("app.db")
cursor = conn.cursor()

rows = cursor.execute("SELECT id, name, email, hashed_password FROM users").fetchall()

print(rows)

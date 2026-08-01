import sqlite3
conn = sqlite3.connect("attendance.db")
print(conn.execute("SELECT * FROM sessions").fetchall())
conn.close()

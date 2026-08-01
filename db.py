import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path(__file__).parent / "attendance.db"

def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with open(Path(__file__).parent / "schema.sql") as f:
            conn.executescript(f.read())
        conn.commit()

def upsert_session(mac: str, method: str, timestamp: float):
    mac = mac.lower()
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO sessions (mac, method, first_seen, last_seen)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(mac, method)
            DO UPDATE SET last_seen=excluded.last_seen
        """, (mac, method, timestamp, timestamp))
        conn.commit()

def get_all_sessions():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT mac, method, first_seen, last_seen FROM sessions")
        return cur.fetchall()

def register_device(mac: str, roll_no: str, name: str):
    mac = mac.lower()
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO devices (mac, roll_no, name)
            VALUES (?, ?, ?)
            ON CONFLICT(mac) DO UPDATE SET
                roll_no=excluded.roll_no,
                name=excluded.name
        """, (mac, roll_no, name))
        conn.commit()

def get_device(mac: str):
    mac = mac.lower()
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT roll_no, name FROM devices WHERE mac=?", (mac,))
        return cur.fetchone()

def get_all_devices():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        cur = conn.cursor()
        cur.execute("SELECT mac, roll_no, name FROM devices")
        return cur.fetchall()
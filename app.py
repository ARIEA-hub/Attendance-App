import subprocess, re, time, sqlite3, csv
from io import StringIO
from flask import Flask, render_template, Response, request, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from pathlib import Path

# ------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------
DB_PATH = Path(__file__).parent / "attendance.db"
ARP_REGEX = re.compile(r"((?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2})")
IGNORE_MACS = {
    "ff-ff-ff-ff-ff-ff",
    "01-00-5e-00-00-16",
    "01-00-5e-00-00-fb",
    "01-00-5e-00-00-fc",
}

# ------------------------------------------------------------
# DATABASE SETUP
# ------------------------------------------------------------
def init_db():
    """Initialize or reset the database on start."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            mac TEXT PRIMARY KEY,
            first_seen REAL,
            last_seen REAL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            mac TEXT PRIMARY KEY,
            roll_no TEXT,
            name TEXT
        )
    """)
    # ✅ clear previous session each app run
    conn.execute("DELETE FROM sessions")
    conn.commit()
    conn.close()
    print("[DB] Initialized and cleared previous session data.")

def upsert_session(mac, timestamp):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO sessions (mac, first_seen, last_seen)
        VALUES (?, ?, ?)
        ON CONFLICT(mac) DO UPDATE SET last_seen=excluded.last_seen
    """, (mac, timestamp, timestamp))
    conn.commit()
    conn.close()

def get_all_sessions():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT mac, first_seen, last_seen FROM sessions ORDER BY last_seen DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_all_devices():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT mac, roll_no, name FROM devices")
    rows = cur.fetchall()
    conn.close()
    return rows

def register_device(mac, roll_no, name):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO devices (mac, roll_no, name)
        VALUES (?, ?, ?)
        ON CONFLICT(mac) DO UPDATE SET
            roll_no=excluded.roll_no,
            name=excluded.name
    """, (mac, roll_no, name))
    conn.commit()
    conn.close()

# ------------------------------------------------------------
# ARP SCAN FUNCTION
# ------------------------------------------------------------
def scan_wifi():
    now = time.time()
    print(f"[SCAN] Running ARP scan at {time.ctime(now)}")

    try:
        result = subprocess.run(
            ["arp", "-a"],
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout or result.stderr
    except Exception as e:
        print(f"[ERROR] ARP failed: {e}")
        return

    macs = set(re.findall(ARP_REGEX, output))
    macs = {m.lower().replace(":", "-") for m in macs if m.lower() not in IGNORE_MACS}
    if not macs:
        print("[SCAN] No MACs found (check ARP cache).")
        return

    print(f"[SCAN] Found {len(macs)} devices: {', '.join(macs)}")
    for mac in macs:
        upsert_session(mac, now)

# ------------------------------------------------------------
# FLASK APP
# ------------------------------------------------------------
app = Flask(__name__)
init_db()

@app.template_filter('datetimeformat')
def datetimeformat(value):
    import datetime
    return datetime.datetime.fromtimestamp(float(value)).strftime('%Y-%m-%d %H:%M:%S')

@app.route("/")
def dashboard():
    sessions = get_all_sessions()
    devices = {mac: {"roll_no": roll_no, "name": name} for mac, roll_no, name in get_all_devices()}

    merged = []
    for mac, first_seen, last_seen in sessions:
        info = devices.get(mac, {"roll_no": "", "name": ""})
        merged.append((mac, info["roll_no"], info["name"], first_seen, last_seen))

    return render_template("dashboard.html", rows=merged)

@app.route("/assign", methods=["POST"])
def assign_roll():
    mac = request.form.get("mac", "").strip().lower()
    roll_no = request.form.get("roll_no", "").strip()
    name = request.form.get("name", "").strip()
    if mac and (roll_no or name):
        register_device(mac, roll_no, name)
    return redirect(url_for("dashboard"))

@app.route("/export")
def export_csv():
    sessions = get_all_sessions()
    devices = {mac: {"roll_no": roll_no, "name": name} for mac, roll_no, name in get_all_devices()}

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(["MAC", "Roll No", "Name", "First Seen", "Last Seen"])
    for mac, first_seen, last_seen in sessions:
        info = devices.get(mac, {"roll_no": "", "name": ""})
        cw.writerow([mac, info["roll_no"], info["name"],
                     time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(first_seen)),
                     time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_seen))])
    return Response(
        si.getvalue().encode("utf-8"),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=attendance.csv"}
    )

# ------------------------------------------------------------
# MAIN ENTRY
# ------------------------------------------------------------
if __name__ == "__main__":
    print("Starting Wi-Fi Attendance (ARP only)...")
    scheduler = BackgroundScheduler()
    scheduler.add_job(scan_wifi, "interval", seconds=30)
    scheduler.start()
    print("Scheduler started — scanning every 30 seconds.")
    app.run(host="0.0.0.0", port=5050, debug=False)
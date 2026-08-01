import subprocess
import re
import time
from db import upsert_session

# Matches both Windows (AA-BB-CC-DD-EE-FF) and Linux/Mac (AA:BB:CC:DD:EE:FF)
ARP_REGEX = re.compile(r"((?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2})")

# Broadcast / multicast MACs to ignore
IGNORE_MACS = {
    "ff-ff-ff-ff-ff-ff",
    "01-00-5e-00-00-16",
    "01-00-5e-00-00-fb",
    "01-00-5e-00-00-fc"
}

def scan_wifi():
    """Scan ARP table for connected devices (Windows-compatible)."""
    now = time.time()
    print(f"[SCAN] Starting ARP scan at {time.ctime(now)}")

    try:
        result = subprocess.run(
            ["arp", "-a"],
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        output = result.stdout or result.stderr
        if not output.strip():
            print("[SCAN] No ARP output captured.")
            return
    except Exception as e:
        print(f"[ERROR] ARP command failed: {e}")
        return

    macs = set(re.findall(ARP_REGEX, output))
    # Normalize to lower-case with '-'
    macs = {m.lower().replace(":", "-") for m in macs}
    macs = {m for m in macs if m not in IGNORE_MACS}

    if not macs:
        print("[SCAN] No valid connected devices found.")
        return

    print(f"[SCAN] Found {len(macs)} MAC(s): {', '.join(macs)}")

    for mac in macs:
        try:
            upsert_session(mac, "wifi_arp", now)
        except Exception as e:
            print(f"[ERROR] DB upsert failed for {mac}: {e}")

    print(f"[SCAN] Completed at {time.ctime(now)}")
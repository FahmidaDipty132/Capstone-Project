# receiver.py

import socket
import mysql.connector
from datetime import datetime

# ── CONFIG ────────────────────────────────────────────────
UDP_IP   = "0.0.0.0"
UDP_PORT = 4210

DB_HOST  = "localhost"
DB_USER  = "root"
DB_PASS  = ""
DB_NAME  = "quakesense"
# ─────────────────────────────────────────────────────────

def connect_db():
    return mysql.connector.connect(
        host     = DB_HOST,
        user     = DB_USER,
        password = DB_PASS,
        database = DB_NAME
    )

def parse_packet(raw: str):
    try:
        parts      = raw.strip().split("|")
        status     = parts[0].strip()
        diff_str   = parts[1].strip()
        diff_value = float(diff_str.split(":")[1])
        return status, diff_value
    except Exception as e:
        print(f"[PARSE ERROR] {e} | raw='{raw}'")
        return None

def save_to_db(cursor, status, diff_value):
    sql = """
        INSERT INTO seismic_data (status, diff_value, recorded_at)
        VALUES (%s, %s, %s)
    """
    cursor.execute(sql, (status, diff_value, datetime.now()))

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"[*] Listening for UDP packets on port {UDP_PORT}...")

    db     = connect_db()
    cursor = db.cursor()
    print(f"[*] Connected to MySQL database '{DB_NAME}'")
    print(f"[*] Saving WARNING and EARTHQUAKE! events only")
    print("-" * 50)

    try:
        while True:
            data, addr = sock.recvfrom(1024)
            raw        = data.decode("utf-8")
            timestamp  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print(f"[{timestamp}] From {addr[0]} → {raw}")

            result = parse_packet(raw)
            if result:
                status, diff_value = result

                # ✅ Only save WARNING and EARTHQUAKE!
                if status in ("WARNING", "EARTHQUAKE!"):
                    save_to_db(cursor, status, diff_value)
                    db.commit()
                    print(f"  ✔ Saved → Status: {status}  |  Diff: {diff_value:.4f}")
                else:
                    print(f"  ⏭ Skipped (NORMAL — not saved)")
            else:
                print("  ✘ Skipped (parse failed)")

    except KeyboardInterrupt:
        print("\n[!] Stopped by user.")

    finally:
        cursor.close()
        db.close()
        sock.close()
        print("[*] Connections closed.")

if __name__ == "__main__":
    main()
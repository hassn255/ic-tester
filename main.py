from flask import Flask, request, jsonify, send_from_directory
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__, static_folder="static")

# -------------------- Database Connection --------------------
def get_db_conn():
    """Return a psycopg2 connection or None if DATABASE_URL missing/invalid"""
    try:
        DATABASE_URL = os.environ.get("DATABASE_URL")
        if not DATABASE_URL:
            print("DATABASE_URL not found")
            return None
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print("DB connection error:", e)
        return None

# -------------------- Routes --------------------
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/static/<path:path>")
def send_static(path):
    return send_from_directory("static", path)

@app.route("/measure", methods=["POST"])
def measure():
    data = request.get_json()
    ic = data.get("ic")
    ground = data.get("ground")

    if not ic or ground is None:
        return jsonify({"status": "error", "msg": "IC name or ground missing"}), 400

    try:
        ground = int(ground)
    except:
        return jsonify({"status": "error", "msg": "Ground must be an integer"}), 400

    # Dummy measurement values
    values = [round(3.3 * i / 7, 2) for i in range(8)]

    # Save to DB safely
    conn = get_db_conn()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO measurements (ic, ground, values) VALUES (%s, %s, %s)",
                (ic, ground, values)
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print("DB insert error:", e)

    return jsonify({"status": "ok", "values": values})

@app.route("/data")
def data():
    conn = get_db_conn()
    if not conn:
        return "Database not connected", 500

    try:
        cur = conn.cursor()
        cur.execute("SELECT ic, ground, values, created_at FROM measurements ORDER BY id DESC")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        print("DB query error:", e)
        return "Query failed", 500

# -------------------- Run app --------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)

from flask import Flask, render_template, request, jsonify
import psycopg2
import os
import random

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    return psycopg2.connect(DATABASE_URL)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/measure", methods=["POST"])
def measure():
    data = request.json
    ic = data.get("ic")
    ground = data.get("ground")

    if not ic or ground is None:
        return jsonify({"status": "error", "msg": "Missing input"})

    # 🔌 Simulated ADC voltages (0–5V)
    values = [round(random.uniform(0, 5), 2) for _ in range(8)]

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO measurements (ic_name, ground_pin, voltages)
        VALUES (%s, %s, %s)
        """,
        (ic, int(ground), values)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "status": "ok",
        "values": values
    })

@app.route("/data")
def data():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT ic_name, ground_pin, voltages, created_at
        FROM measurements
        ORDER BY created_at DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(rows)

if __name__ == "__main__":
    app.run(debug=True)

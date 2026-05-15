from flask import Flask, request, jsonify
import psycopg2 # type: ignore
import os
import time

app = Flask(__name__)

# CONEXION A BASE DE DATOS
while True:
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

        cur = conn.cursor()

        print("Conectado a notifications_db")
        break

    except:
        print("Esperando base de datos...")
        time.sleep(3)

# CREAR TABLA
cur.execute("""
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    identificacion VARCHAR(50),
    turno VARCHAR(20),
    mensaje TEXT
)
""")
conn.commit()

# HOME
@app.route("/")
def home():
    return jsonify({
        "mensaje": "Notifications Service activo"
    })

# LISTAR NOTIFICACIONES
@app.route("/notifications", methods=["GET"])
def get_notifications():

    cur.execute("""
        SELECT id, identificacion, turno, mensaje
        FROM notifications
        ORDER BY id ASC
    """)

    rows = cur.fetchall()

    lista = []

    for r in rows:
        lista.append({
            "id": r[0],
            "identificacion": r[1],
            "turno": r[2],
            "mensaje": r[3]
        })

    return jsonify({
        "mensaje": "Listado de notificaciones",
        "notificaciones": lista
    })

# CREAR NOTIFICACION
@app.route("/notify", methods=["POST"])
def create_notification():

    data = request.json

    if not data:
        return jsonify({
            "error": "Debe enviar datos"
        }), 400

    if "identificacion" not in data:
        return jsonify({
            "error": "Falta identificacion"
        }), 400

    if "turno" not in data:
        return jsonify({
            "error": "Falta turno"
        }), 400

    identificacion = str(data["identificacion"])
    turno = str(data["turno"])

    mensaje = "Turno asignado: " + turno

    cur.execute("""
        INSERT INTO notifications
        (identificacion, turno, mensaje)
        VALUES (%s, %s, %s)
    """, (identificacion, turno, mensaje))

    conn.commit()

    print("Notificacion enviada a:", identificacion)

    return jsonify({
        "mensaje": "Notificacion registrada correctamente",
        "identificacion": identificacion,
        "turno": turno
    })

# INICIAR APP
app.run(host="0.0.0.0", port=5000)
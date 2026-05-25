from flask import Flask, request, jsonify
import requests
import psycopg2 # type: ignore
import os
import time
import logging
from datetime import datetime

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s REPORTS: %(message)s"
)

# CONEXION BASE DE DATOS
while True:
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

        cur = conn.cursor()

        logging.info("Conectado a reports_db")
        break

    except:
        logging.error("Esperando base de datos...")
        time.sleep(3)

# CREAR TABLA
cur.execute("""
CREATE TABLE IF NOT EXISTS reports_history (
    id SERIAL PRIMARY KEY,
    fecha TIMESTAMP,
    usuarios INTEGER,
    turnos INTEGER,
    notificaciones INTEGER,
    estado_circuito VARCHAR(20)
)
""")

conn.commit()

# VARIABLES CIRCUIT BREAKER
fallos = 0
MAX_FALLOS = 3

estado_circuito = "CLOSED"

ultimo_fallo = None

TIEMPO_RECUPERACION = 15

# HOME
@app.route("/")
def home():

    return jsonify({
        "mensaje": "Reports Service activo"
    })

# HEALTH CHECK
@app.route("/health")
def health():

    return jsonify({
        "estado": "ok",
        "servicio": "reports-service"
    })

# CONSULTAR REPORTES
@app.route("/reports", methods=["GET"])
def reports():

    global fallos
    global estado_circuito
    global ultimo_fallo

    # CIRCUITO ABIERTO
    if estado_circuito == "OPEN":

        tiempo_actual = time.time()

        if tiempo_actual - ultimo_fallo > TIEMPO_RECUPERACION:

            estado_circuito = "HALF-OPEN"

            logging.warning(
                "Circuito HALF-OPEN"
            )

        else:

            return jsonify({
                "error": "Circuito abierto",
                "estado_circuito": estado_circuito
            }), 503

    try:

        # USERS
        users_response = requests.get(
            "http://users-service:5000/users",
            timeout=3
        )

        usuarios = users_response.json()[
            "usuarios_registrados"
        ]

        # TURNS
        turns_response = requests.get(
            "http://turns-service:5000/turns",
            timeout=3
        )

        turnos = turns_response.json()[
            "turnos"
        ]

        # NOTIFICATIONS
        notifications_response = requests.get(
            "http://notifications-service:5000/notifications",
            timeout=3
        )

        notificaciones = notifications_response.json()[
            "notificaciones"
        ]

        # CERRAR CIRCUITO
        fallos = 0

        estado_circuito = "CLOSED"

        # GUARDAR HISTORIAL
        cur.execute("""
            INSERT INTO reports_history
            (
                fecha,
                usuarios,
                turnos,
                notificaciones,
                estado_circuito
            )
            VALUES (%s,%s,%s,%s,%s)
        """, (
            datetime.now(),
            len(usuarios),
            len(turnos),
            len(notificaciones),
            estado_circuito
        ))

        conn.commit()

        logging.info(
            "Reporte generado correctamente"
        )

        return jsonify({
            "estado_circuito": estado_circuito,
            "usuarios": usuarios,
            "turnos": turnos,
            "notificaciones": notificaciones
        })

    except:

        fallos += 1

        logging.error(
            "Error consultando servicios"
        )

        if fallos >= MAX_FALLOS:

            estado_circuito = "OPEN"

            ultimo_fallo = time.time()

            logging.error(
                "Circuito OPEN"
            )

        return jsonify({
            "error": "Servicios no disponibles",
            "estado_circuito": estado_circuito
        }), 500

# HISTORIAL REPORTES
@app.route("/reports/history", methods=["GET"])
def reports_history():

    cur.execute("""
        SELECT
        id,
        fecha,
        usuarios,
        turnos,
        notificaciones,
        estado_circuito
        FROM reports_history
        ORDER BY id DESC
    """)

    rows = cur.fetchall()

    lista = []

    for r in rows:

        lista.append({
            "id": r[0],
            "fecha": str(r[1]),
            "usuarios": r[2],
            "turnos": r[3],
            "notificaciones": r[4],
            "estado_circuito": r[5]
        })

    return jsonify({
        "historial": lista
    })

# CREAR REPORTE MANUAL
@app.route("/reports", methods=["POST"])
def create_report():

    data = request.json

    usuarios = data.get("usuarios", 0)
    turnos = data.get("turnos", 0)
    notificaciones = data.get(
        "notificaciones", 0
    )

    estado = data.get(
        "estado_circuito",
        "CLOSED"
    )

    cur.execute("""
        INSERT INTO reports_history
        (
            fecha,
            usuarios,
            turnos,
            notificaciones,
            estado_circuito
        )
        VALUES (%s,%s,%s,%s,%s)
    """, (
        datetime.now(),
        usuarios,
        turnos,
        notificaciones,
        estado
    ))

    conn.commit()

    logging.info(
        "Reporte manual creado"
    )

    return jsonify({
        "mensaje": "Reporte creado"
    })

# INICIAR APP
app.run(host="0.0.0.0", port=5000)


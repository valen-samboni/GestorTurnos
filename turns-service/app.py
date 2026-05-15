from flask import Flask, request, jsonify
import psycopg2 # type: ignore
import os
import time
import requests
import logging

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s TURNS: %(message)s"
)

# CONEXION CON REINTENTO
while True:
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )
        cur = conn.cursor()
        logging.info("Conectado a turns_db")
        break
    except:
        logging.error("Esperando base de datos...")
        time.sleep(3)

# CREAR TABLA
cur.execute("""
CREATE TABLE IF NOT EXISTS turns (
    id SERIAL PRIMARY KEY,
    identificacion VARCHAR(50),
    turno VARCHAR(20)
)
""")
conn.commit()


# GENERAR TURNO DESDE BD
def generar_turno():

    cur.execute(
        "SELECT turno FROM turns ORDER BY id DESC LIMIT 1"
    )

    ultimo = cur.fetchone()

    if ultimo is None:
        return "T1"

    numero = int(
        ultimo[0].replace("T", "")
    ) + 1

    return "T" + str(numero)

# LISTAR TURNOS
@app.route("/turns", methods=["GET"])
def get_turns():

    cur.execute("""
        SELECT id, identificacion, turno
        FROM turns
        ORDER BY id
    """)

    rows = cur.fetchall()

    lista = []

    for r in rows:
        lista.append({
            "id": r[0],
            "identificacion": r[1],
            "turno": r[2]
        })

    return jsonify({
        "turnos": lista
    })


# CREAR TURNO

@app.route("/turn", methods=["POST"])
def create_turn():

    data = request.json

    identificacion = data.get(
        "identificacion", ""
    ).strip()

    # VALIDAR VACIO
    if identificacion == "":
        return jsonify({
            "error": "Identificacion requerida"
        }), 400

    # VALIDAR NUMERICO
    if not identificacion.isdigit():
        return jsonify({
            "error": "La identificacion debe ser numerica"
        }), 400

    # VALIDAR USUARIO
    try:
        response = requests.get(
            "http://users-service:5000/users",
            timeout=3
        )

        users = response.json()[
            "usuarios_registrados"
        ]

        existe = False

        for u in users:
            if u["identificacion"] == identificacion:
                existe = True
                break

        if not existe:
            return jsonify({
                "error": "Usuario no existe"
            }), 400

    except:
        logging.error(
            "users-service no responde"
        )

        return jsonify({
            "error": "users-service no disponible"
        }), 500

    # VALIDAR SI YA TIENE TURNO
    cur.execute(
        """
        SELECT * FROM turns
        WHERE identificacion=%s
        """,
        (identificacion,)
    )

    ya_tiene = cur.fetchone()

    if ya_tiene:
        return jsonify({
            "error":
            "El usuario ya tiene un turno asignado"
        }), 400

    # NUEVO TURNO
    nuevo_turno = generar_turno()

    cur.execute(
        """
        INSERT INTO turns
        (identificacion, turno)
        VALUES (%s,%s)
        """,
        (identificacion, nuevo_turno)
    )

    conn.commit()

    logging.info(
        "Turno creado %s para %s",
        nuevo_turno,
        identificacion
    )

    # ENVIAR NOTIFICACION
    try:
        requests.post(
            "http://notifications-service:5000/notify",
            json={
                "identificacion":
                identificacion,
                "turno":
                nuevo_turno
            },
            timeout=3
        )

        logging.info(
            "Notificacion enviada"
        )

    except:
        logging.error(
            "notifications-service no responde"
        )

    return jsonify({
        "mensaje":
        "Turno creado correctamente",
        "identificacion":
        identificacion,
        "turno":
        nuevo_turno
    })


app.run(host="0.0.0.0", port=5000)
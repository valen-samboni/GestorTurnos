from flask import Flask, request, jsonify
import psycopg2 # type: ignore
import os
import time
import logging

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s USERS: %(message)s"
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
        logging.info("Conectado a users_db")
        break
    except:
        logging.error("Esperando base de datos...")
        time.sleep(3)

# CREAR TABLA
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    identificacion VARCHAR(50) UNIQUE,
    telefono VARCHAR(50)
)
""")
conn.commit()


# LISTAR USUARIOS
@app.route("/users", methods=["GET"])
def get_users():

    cur.execute("""
        SELECT id, identificacion, telefono
        FROM users
        ORDER BY id
    """)

    rows = cur.fetchall()

    lista = []

    for r in rows:
        lista.append({
            "id": r[0],
            "identificacion": r[1],
            "telefono": r[2]
        })

    return jsonify({
        "usuarios_registrados": lista
    })


# CREAR USUARIO
@app.route("/users", methods=["POST"])
def create_user():

    data = request.json

    identificacion = data.get(
        "identificacion", ""
    ).strip()

    telefono = data.get(
        "telefono", ""
    ).strip()

    # VALIDAR VACIOS
    if identificacion == "" or telefono == "":
        return jsonify({
            "error": "Todos los campos son obligatorios"
        }), 400

    # VALIDAR NUMERICOS
    if not identificacion.isdigit():
        return jsonify({
            "error": "La identificacion debe ser numerica"
        }), 400

    if not telefono.isdigit():
        return jsonify({
            "error": "El telefono debe ser numerico"
        }), 400

    # VALIDAR DUPLICADO
    cur.execute(
        "SELECT * FROM users WHERE identificacion=%s",
        (identificacion,)
    )

    existe = cur.fetchone()

    if existe:
        return jsonify({
            "error": "Usuario ya registrado"
        }), 400

    # INSERTAR
    cur.execute(
        """
        INSERT INTO users
        (identificacion, telefono)
        VALUES (%s,%s)
        """,
        (identificacion, telefono)
    )

    conn.commit()

    logging.info(
        "Usuario creado %s",
        identificacion
    )

    return jsonify({
        "mensaje": "Usuario creado correctamente"
    })


app.run(host="0.0.0.0", port=5000)
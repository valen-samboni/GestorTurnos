from flask import Flask, jsonify
import requests
import logging
import time

app = Flask(__name__)

# LOGS DEL SERVICIO
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s REPORTS: %(message)s"
)

# VARIABLES CIRCUIT BREAKER
fallos = 0
MAX_FALLOS = 3
circuito_abierto = False
ultimo_fallo = 0
TIEMPO_RECUPERACION = 10

TIMEOUT = 3

# FUNCION CIRCUIT BREAKER
def validar_circuito():

    global circuito_abierto
    global ultimo_fallo

    if circuito_abierto:

        tiempo_actual = time.time()

        diferencia = tiempo_actual - ultimo_fallo

        # HALF OPEN
        if diferencia > TIEMPO_RECUPERACION:

            logging.warning(
                "Circuito en HALF-OPEN"
            )

            circuito_abierto = False

            return True

        return False

    return True


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
        "status": "Reports activo"
    })


# REPORTE GENERAL
@app.route("/reports", methods=["GET"])
def reports():

    global fallos
    global circuito_abierto
    global ultimo_fallo

    # VALIDAR CIRCUITO
    if not validar_circuito():

        logging.error(
            "Circuito ABIERTO"
        )

        return jsonify({
            "error":
            "Servicio temporalmente bloqueado",
            "circuito":
            "OPEN"
        }), 503

    try:

        logging.info(
            "Consultando users-service"
        )

        users = requests.get(
            "http://users-service:5000/users",
            timeout=TIMEOUT
        ).json()

        logging.info(
            "Consultando turns-service"
        )

        turns = requests.get(
            "http://turns-service:5000/turns",
            timeout=TIMEOUT
        ).json()

        logging.info(
            "Consultando notifications-service"
        )

        notifications = requests.get(
            "http://notifications-service:5000/notifications",
            timeout=TIMEOUT
        ).json()

        # RESET FALLOS
        fallos = 0

        logging.info(
            "Circuito CLOSED"
        )

        return jsonify({
            "usuarios":
            users.get(
                "usuarios_registrados",
                []
            ),

            "turnos":
            turns.get(
                "turnos",
                []
            ),

            "notificaciones":
            notifications.get(
                "notificaciones",
                []
            ),

            "estado_circuito":
            "CLOSED"
        })

    except Exception as e:

        fallos += 1

        logging.error(
            "Fallo detectado: %s",
            str(e)
        )

        logging.error(
            "Numero de fallos: %s",
            fallos
        )

        # ABRIR CIRCUITO
        if fallos >= MAX_FALLOS:

            circuito_abierto = True

            ultimo_fallo = time.time()

            logging.error(
                "Circuito OPEN"
            )

        return jsonify({
            "error":
            "Error consultando servicios",
            "fallos":
            fallos,
            "estado_circuito":
            "OPEN" if circuito_abierto
            else "CLOSED"
        }), 500


app.run(
    host="0.0.0.0",
    port=5000
)


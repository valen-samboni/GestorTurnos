from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TIMEOUT = 3

# HOME
@app.route("/")
def home():
    return jsonify({
        "mensaje": "API Gateway funcionando",
        "servicios": [
            "users-service",
            "turns-service",
            "notifications-service"
        ]
    })

# USERS - GET
@app.route("/users", methods=["GET"])
def get_users():

    try:
        response = requests.get(
            "http://users-service:5000/users",
            timeout=TIMEOUT
        )

        return jsonify(response.json())

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Timeout en users-service"
        }), 504

    except:
        return jsonify({
            "error": "users-service no disponible"
        }), 500


# USERS - POST
@app.route("/users", methods=["POST"])
def create_user():

    try:
        data = request.json

        response = requests.post(
            "http://users-service:5000/users",
            json=data,
            timeout=TIMEOUT
        )

        return jsonify(response.json())

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Timeout en users-service"
        }), 504

    except:
        return jsonify({
            "error": "users-service no disponible"
        }), 500


# TURNS - GET
@app.route("/turns", methods=["GET"])
def get_turns():

    try:
        response = requests.get(
            "http://turns-service:5000/turns",
            timeout=TIMEOUT
        )

        return jsonify(response.json())

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Timeout en turns-service"
        }), 504

    except:
        return jsonify({
            "error": "turns-service no disponible"
        }), 500


# TURNS - POST
@app.route("/turn", methods=["POST"])
def create_turn():

    try:
        data = request.json

        response = requests.post(
            "http://turns-service:5000/turn",
            json=data,
            timeout=TIMEOUT
        )

        return jsonify(response.json())

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Timeout en turns-service"
        }), 504

    except:
        return jsonify({
            "error": "turns-service no disponible"
        }), 500


# NOTIFICATIONS - GET
@app.route("/notifications", methods=["GET"])
def get_notifications():

    try:
        response = requests.get(
            "http://notifications-service:5000/notifications",
            timeout=TIMEOUT
        )

        return jsonify(response.json())

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Timeout en notifications-service"
        }), 504

    except:
        return jsonify({
            "error": "notifications-service no disponible"
        }), 500


# NOTIFICATIONS - POST
@app.route("/notify", methods=["POST"])
def send_notification():

    try:
        data = request.json

        response = requests.post(
            "http://notifications-service:5000/notify",
            json=data,
            timeout=TIMEOUT
        )

        return jsonify(response.json())

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Timeout en notifications-service"
        }), 504

    except:
        return jsonify({
            "error": "notifications-service no disponible"
        }), 500


# INICIAR APP
app.run(host="0.0.0.0", port=5000)
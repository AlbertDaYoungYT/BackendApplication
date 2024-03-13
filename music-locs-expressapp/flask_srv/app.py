import mysql.connector
import redis

from verify import *
from flask import *
from db import *
import os



app = Flask(__name__)


@app.before_request
def AuthenticateRequest():
    if not request.headers.get("Authorization"):
        return jsonify({"reason": "No authentication provided"}), 401

    if verifyApiToken(request.headers.get("Authorization")):
        pass
    else:
        return jsonify({"reason": "Authentication not verified"}), 403


@app.route("/api/hello", methods=["GET"])
def Hello():
    return {"message": "Hello, World!"}

@app.route("/api/query", methods=["GET"])
def Query():
    query = request.args.get("query")
    _type = request.args.get("_type")

    if _type == "user": return 0


# Pins API
@app.route("/api/pins/create", methods=["POST"])
def CreatePin():
    json_data = request.get_json()
    time_limit_ended = float(redisdb.get("user_create_pin_cooldown:" + json_data["uid"]))

    if not time_limit_ended => time.time(): return jsonify({"reason": "Please wait until cooldown has ended"}), 429

    redisdb.set(f"pin:{json_data['country']}:{json_data['pin_id']}", json.dumps(json_data))
    res = SQLCreatePin(json_data)
    if res: return 200
    return 500

@app.route("/api/pins/<pin_id>", methods=["GET"])
def GetSinglePinData(pin_id):
    

@app.route("/api/pins/<pin_id>/delete", methods=["DELETE"])
def DeletePin(pin_id)


app.run(port=8090, debug=True)

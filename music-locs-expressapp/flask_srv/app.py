from verify import *
from flask import *
from db import *

import urllib.parse
import requests
import hashlib
import uuid
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

    if not time_limit_ended >= time.time(): return jsonify({"reason": "Please wait until cooldown has ended"}), 429

    redisdb.set(f"pin:{json_data['country']}:{json_data['pin_id']}", json.dumps(json_data))
    res = SQLCreatePin(json_data)
    if res == 1: return jsonify({"status":"success"}), 200
    return jsonify(res), 500

@app.route("/api/pins/<pin_id>", methods=["GET"])
def GetSinglePinData(pin_id):
    # Checks if the pin exists in Redis first before checking MySQL
    data = json.loads(redisdb.get(f"pin:*:{pin_id}")) or SQLGetPinData(pin_id)
    

@app.route("/api/pins/<pin_id>/delete", methods=["DELETE"])
def DeletePin(pin_id): return None




# Spotify API
@app.route("/api/spotify/login", methods=["GET"])
def LoginToSpotify():
    state = hashlib.md5(str(time.time()).encode('utf-8')).hexdigest()
    scope = "user-read-private user-read-email user-read-playback-state user-modify-playback-state user-read-currently-playing app-remote-control playlist-read-private user-follow-read user-top-read user-read-recently-played user-library-read"
    
    
    if redisdb.set("spotify_state:" + state, request.args.get("uid")):
        return redirect("https://accounts.spotify.com/authorize?" + urllib.parse.urlencode({
            "response_type":"code",
            "client_id": os.environ["CLIENT_ID"],
            "scope": scope,
            "redirect_uri": "http://62.107.184.114/api/spotify/callback",
            "state": state
        }))
    else:
        return jsonify({"error": "Internal Server Error"}), 500

@app.route("/api/spotify/callback", methods=["GET"])
def CallbackFromSpotify():
    # Check the state parameter to prevent CSR
    state = request.args.get("state") or None
    code  = request.args.get("code") or None
    
    res = SQLAddCode(state, code)
    if res != 1: return jsonify(res), 500
    
    if state == None:
        return jsonify({"error": "State mismatch"}), 400
    else:
        res = requests.post("https://accounts.spotify.com/api/token", data={
            "code": code,
            "redirect_uri": "http://62.107.184.114/api/spotify/callback",
            "grant_type": 'authorization_code'
        })
        if res.status_code != 200:
            return jsonify({"error": "invalid_token"}), 500
        
        access_token = res.json().get("access_token")
        token_type   = res.json().get("token_type")
        
        with redisdb.get("spotify_state:" + state) as r: 
            if r != None: uid = r
            else: return {"error": "Invalid State"}
        
        redisdb.set("spotify_token:" + uid, json.dumps({"access_token": access_token, "token_type": token_type}))

        res = SQLAddToken(state, access_token, token_type)
        if res != 1: return jsonify(res), 500
    
    redisdb.delete(f"spotify_state:{state}")
    
    return jsonify({"access_token": access_token, "token_type": token_type}), 201






app.run(port=8090, debug=True)

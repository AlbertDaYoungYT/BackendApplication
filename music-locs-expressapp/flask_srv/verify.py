from datetime import datetime
from db import *
import hashlib
import time
import json



def verifyApiToken(token):
    if redisdb.get("request-auth:" + token) == None:
        sqlc = sqldb.cursor()
        sqlc.execute("SELECT (uid, expiration_date) FROM api_tokens WHERE token = '%s'", token)
        res = sqlc.fetchone()

        if not res and datetime.timestamp(datetime.strptime(res[1], '%Y-%m-%d %H:%M:%S')) >= time.time():
            return False

        redisdb.set("request-auth:" + token, json.dumps({"uid": res[0], "expiration_date": res[1]}))
    
    return True

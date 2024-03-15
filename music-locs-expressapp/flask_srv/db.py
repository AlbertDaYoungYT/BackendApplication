import mysql.connector
import redis

from datetime import *
import hashlib
import random
import time
import os

global sqldb
global redisdb

redisdb = redis.Redis(host=os.environ["REDIS_HOSTNAME"], port=6379, decode_responses=True)
sqldb = mysql.connector.connect(
    host=os.environ["MYSQL_HOSTNAME"],
    user="root",
    password=os.environ["MYSQL_ROOT_PASSWORD"],
    database="musiclocs"
)


def SQLAddCode(state, code):
    with redisdb.get("spotify_state:" + state) as r: 
        if r != None: uid = r
        else: return {"error": "Invalid State"}
        
    cursor = sqldb.cursor()
    query = ("INSERT INTO spotify_codes (uid, code) VALUES(%s,%s)")
    try:
        cursor.execute(query, (uid, code))
        sqldb.commit()
    except Exception:
        return {"error": "Database Error"}
    
    return 1

def SQLAddToken(state, access_token, token_type):
    with redisdb.get("spotify_state:" + state) as r: 
        if r != None: uid = r
        else: return {"error": "Invalid State"}
        
    cursor = sqldb.cursor()
    query = ("INSERT INTO spotify_tokens (uid, access_token, token_type) VALUES(%s,%s,%s)")
    try:
        cursor.execute(query, (uid, access_token, token_type))
        sqldb.commit()
    except Exception:
        return {"error": "Database Error"}
    
    return 1

def SQLCreatePin(json_data):
    pin_id = hashlib.sha256((str(time.time())+str(random.randint(0,999999999))).encode()).hexdigest()
    uid = json_data["uid"]
    title =  json_data["title"]
    message =  json_data["message"]
    pin_color =  json_data["pin_color"]
    pin_imgurl =  json_data["pin_imgurl"]
    create_date = datetime.now()
    expiration_date = datetime.now() + timedelta(days=os.environ["PIN_EXPIRATION_DELAY_DAYS"]) # Default to one week from creation date
    spotify_id =  json_data["spotify_id"]
    whitelist =  json_data["whitelist"]
    blacklist =  json_data["blacklist"]
    latitude =  json_data["latitude"]
    longitude =  json_data["longitude"]
    country =  json_data["country"]
    location_json =  json_data["location_json"]
    
    cursor = sqldb.cursor()
    query = ("INSERT INTO global_pins (pin_id, uid, title, messagepin_color, pin_imgurl, create_date, expiration_date, song_id, whitelist, blacklist, latitude, longitude, country, location_json) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
    try:
        cursor.execute(query, (pin_id, uid, title, message, pin_color, pin_imgurl, create_date, expiration_date, spotify_id, whitelist, blacklist, latitude, longitude, country, location_json))
        sqldb.commit()
    except Exception:
        return {"error": "Database Error"}
    
    return 1
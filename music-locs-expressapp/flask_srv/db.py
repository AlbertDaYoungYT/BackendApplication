import mysql.connector
import redis
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

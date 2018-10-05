from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import connection, json, datetime
import base64, binascii
from Crypto.Cipher import AES
import globalVariable
from pprint import pprint

app = Flask(__name__)
api = Api(app)

# Connection to km api and cursor km api
connectKmApi = connection.conn_km_master_api
cursorKmApi = connectKmApi.cursor()


def decrypt(enc, key, IV):
    # IV is initialization vector or it's same like public key sent on json
    # IV = '367de05b7558db2ed6fffed6d53d6ef4'
    # convert hexa to bytes binary
    result = binascii.unhexlify(IV)
    decobj = AES.new(globalVariable.key, AES.MODE_CBC, result)
    data = decobj.decrypt(base64.b64decode(enc))
    # return data.encode('utf-8')
    return data

def getPrefixDomain(self, domain):
    checkEmailSql = 'SELECT * FROM tbl_user_domain WHERE name_domain = %s;'
    cursorKmApi.execute(checkEmailSql, ([domain]))
    res = cursorKmApi.fetchall()
    now =  datetime.datetime.now()
    items = []
    for row in res:
        items.append({'prefix_domain': row[0], 'alias': row[2]})
    return items[0]

def checkDomain(self, domain):
    checkEmailSql = 'SELECT COUNT(*) FROM tbl_user_domain WHERE name_domain = %s;'
    cursorKmApi.execute(checkEmailSql, ([domain]))
    res = cursorKmApi.fetchall()
    res = list(sum(res, ()))
    if res[0] == 1:
        return True
    elif res[0] == 0:
        return False
    else:
        return False
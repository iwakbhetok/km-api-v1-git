from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
import connection, json, datetime, time, hashlib, random, string
import globalVariable

app = Flask(__name__)
api = Api(app)

# Connection to kmpay and cursor kmpay
connectKmPay = connection.conn_kmpay
cursorKmPay = connectKmPay.cursor()

# Connection to km api and cursor km api
connectKmApi = connection.conn_km_master_api
cursorKmApi = connectKmApi.cursor()

secret_key = ''.join(random.choice(string.hexdigits)
    for x in xrange(32))

app.config['SECRET_KEY'] = 'thisissecretkey'

def generateToken(self, arg1, arg2):
    m = hashlib.md5()
    timeRandom = int(time.time())
    m.update(arg1 + arg2 + secret_key)
    token = m.hexdigest()
    return token

def checkValidToken(self, token):
    now = datetime.datetime.now()
    conn = connection.conn_km_master_api
    a = conn.cursor()
    checkTokenSql = 'SELECT * FROM tbl_session WHERE session_key = %s;'
    a.execute(checkTokenSql, (token))
    res = a.fetchall()
    items = []
    if res:
        for row in res:
            if now > row[4]:
                items.append({'status':'error', 'code': 401,'result':'Please Request New Token'})
            else:
                items.append({'status':'success', 'code': 204, 'result':'Still alive'})
    else:
        items.append({'status':'error', 'code': 401, 'result':'Invalid Token'})
    return items

def checkWithdrawPin(self, pin):
    pinLength = len(pin)
    if int(pinLength) == globalVariable.length_pin:
        checkPinSql = 'SELECT COUNT(*) FROM tbl_pin WHERE pin = %s AND is_active = 1;'
        cursorKmPay.execute(checkPinSql, ([pin]))
        res = cursorKmPay.fetchall()
        num = list(sum(res, ()))
        if num[0] == 1:
            return {"status":"valid", "code":200,"result":"OK"}
    else:
        return {"status":"invalid","code":400,"result":"Invalid PIN"}

class Auth(Resource):
    def post(self):
        param = request.get_json()

        if 'API_KEY' in param and param['API_KEY'] != '':
            # connect to db master api
            conn = connection.conn_km_master_api
            a = conn.cursor()
            countAccSql = "SELECT COUNT(*) FROM tbl_api_key ak JOIN tbl_user_domain ud ON ak.prefix_id = ud.prefix_id WHERE ak.api_key_id = %s AND ud.name_domain = %s AND ak.is_active = 1"
            a.execute(countAccSql, (param['API_KEY'], param['DOMAIN']))
            res = a.fetchall()
            num = list(sum(res, ()))

            if num[0] == 1:
                # if new session: no token available
                token = generateToken(self, param['API_KEY'], app.config['SECRET_KEY'])
                expired_date = datetime.datetime.now() + datetime.timedelta(minutes=360)
                # new session is save to session table
                saveSessionSql = 'INSERT INTO tbl_session (session_key, created_date, created_by, expired_date) VALUES (%s, %s, %s, %s);'
                a.execute(saveSessionSql, (token, datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%I:%S'), '1', expired_date))
                conn.commit()

                return jsonify({'status':'success', 'code': 200,"result":{"token":token}})

            else:
                # if API key is not in registered tbl_api_key table, then register new account to its service ex: register to member kmpay
                return jsonify({'status':"error",'code': 204, "result":""})
            
        return jsonify({'status':"error",'code': 204,"result":"Empty Api Key"})

class CheckAuth(Resource):
    def post(self):
        param = request.get_json()
        res = checkValidToken(self, param['token'])
        return jsonify({'result':res[0]})

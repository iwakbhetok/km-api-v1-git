from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api

import connection
import pymysql
import random, string
import json
import jwt
import datetime
import hashlib

conn_kmv3 = pymysql.connect(
    host= connection.host,
    user= connection.user,
    password= connection.password,
    unix_socket = connection.unix_socket,
    db= connection.db_kmv3,
)

conn_kmpay = pymysql.connect(
    host= connection.host,
    user= connection.user,
    password= connection.password,
    unix_socket = connection.unix_socket,
    db = connection.db_km_pay,
)

conn_km_crm = pymysql.connect(
    host= connection.host,
    user= connection.user,
    password= connection.password,
    unix_socket = connection.unix_socket,
    db = connection.db_km_crm,
)

conn_km_master_api = pymysql.connect(
    host= connection.host,
    user= connection.user,
    password= connection.password,
    unix_socket = connection.unix_socket,
    db = connection.db_km_master_api,
)

secret_key = ''.join(random.choice(string.hexdigits)
    for x in xrange(32))

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'thisissecretkey'

def generateToken(self, arg1, arg2):
    m = hashlib.md5()
    m.update(arg1 + arg2)
    token = m.hexdigest()
    return token

def authenticate(arg1, arg2):
    result = jsonify({'status ':"response status","data":"","message":"Response message"})
    return result

class Authenticate(Resource):
    # Request format: curl -u username:password http://127.0.0.1:5050/auth
    def get(self):
        auth = request.authorization

        if auth.username != '' and auth.password != '':
            # connect to db master api
            a = conn_km_master_api.cursor()
            sql = "SELECT COUNT(*) FROM `user`AS u INNER JOIN `keys` AS k ON u.`user_id` = k.`user_id` WHERE u.name_user = %s AND k.api_key = %s;"
            a.execute(sql, ([auth.username],[auth.password]))
            res = a.fetchall()
            num = list(sum(res, ()))

            if num[0] == 1:
                token = generateToken(self, auth.username, app.config['SECRET_KEY'])

                # token = jwt.encode({'user': auth.username, 'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=5)}, app.config['SECRET_KEY'])
                return jsonify({'status ':"success","message":"Authentication Success","token":token})

            else:
                return jsonify({'status ':"error","message":"Authentication Failed"})
            conn_km_master_api.close()
            
        return make_response('Could not verify!', 401, {'WWW-Authenticate' : 'Basic-realm="Login Required"'})

class KuisMilioner(Resource):
    def get(self):
        a = conn_kmv3.cursor()
        sql = 'SELECT member_email, nama_lengkap, alamat, tempat_lahir, DATE_FORMAT(member_created_date,"%Y-%m-%d %h:%i:%s") FROM tbl_member limit 100 ;'
        a.execute(sql)
        data = a.fetchall()
        # num = list(sum(data, ()))
        return {'status':'success','data ': data}

    def post(self):
        some_json = request.get_json()
        return {'you sent ': some_json}, 201

class checkSaldo(Resource):
    def post(self):
        data_json = request.get_json()
        no_rekening = data_json['no_rekening']
        now = datetime.datetime.now()
        month = now.month
        year = now.year
        a = conn_kmpay.cursor()
        sql = 'SELECT no_rekening, SUM(IF(transaction_type="K", balance, 0))  as K, SUM(IF(transaction_type="D", balance, 0)) as D, (SUM(IF(transaction_type="K", balance, 0))-SUM(IF(transaction_type="D", balance, 0))) as saldo, created_date FROM db_kmpay.tbl_transaksi WHERE MONTH(created_date)= %s and YEAR(created_date)=%s AND no_rekening = %s AND status_transaksi = "SUCCESS" GROUP BY no_rekening, MONTH(created_date), YEAR(created_date);'
        a.execute(sql,([month], [year],[no_rekening]))
        result = a.fetchall()
        items = []
        for row in result:
            items.append({'no_rekening': row[0], 'sum_kredit': row[1], 'sum_debit': row[2], 'saldo': row[3]})
        if not items:
            return jsonify({'status ':"error","data":items,"message":"Error"})
        else:
            return jsonify({'status ':"success","data":items[0],"message":"Success"})

class registerAccount(Resource):
    def post(self, num):
        return {'result ': num*10}

class topupSaldo(Resource):
    def get(self, num):
        return {'result ': num*10}

class withdrawSaldo(Resource):
    def post(self, num):
        return {'result ': num*10}

class withdrawTypeSaldo(Resource):
    def post(self, num):
        return {'result ': num*10}

# all routes API KM
api.add_resource(KuisMilioner, '/')

# all routes API KM
api.add_resource(Authenticate, '/auth')

# route to check Saldo GOLDMILL
api.add_resource(checkSaldo, '/checkSaldo')

# route to REGISTER ACCOUNT KMPAY
api.add_resource(registerAccount, '/registerAccount/')

# route to TOPUP KMPAY
api.add_resource(topupSaldo, '/topupSaldo/<num>', endpoint="foo")

# route to WITHDRAW KMPAY
api.add_resource(withdrawSaldo, '/withdrawSaldo/')

# route to WITHDRAW BUY WITH TYPE
api.add_resource(withdrawTypeSaldo, '/withdrawTypeSaldo/')

class Transaction():
    __tablename__ = 'tbl_transaksi'
    def generate_auth_token(self, expiration=600):
        s = Serializer(secret_key, expires_in = expiration)
        return s.dumps({'id':self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            # Valid Token but expired
            return None
        except BadSignature:
            #Invalid Token
            return None
        user_id = data['id']
        return user_id

if __name__ == '__main__':
    app.run(debug = True, port=5050)
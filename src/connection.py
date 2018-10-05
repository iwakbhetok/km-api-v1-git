import pymysql

host = 'localhost:3306'
host_production= 'dbnew.kuismilioner.com'
user= 'root'
password= 'root'
user_production= 'kmnetuser2'
password_production= 'B1nt@ngK3j0R4'
db_kmv3 = 'db_kmv3'
db_km_pay = 'db_kmpay'
db_km_crm = 'db_crm'
db_kmstore = 'db_kmstore'
db_km_master_api= 'db_master_api'
unix_socket = '/Applications/MAMP/tmp/mysql/mysql.sock'
version = '/api/v1'

conn_km_main = pymysql.connect(
    host= host,
    user= user,
    password= password,
    unix_socket = unix_socket,
    db= db_kmv3,
)

conn_kmpay = pymysql.connect(
    host= host,
    user= user,
    password= password,
    unix_socket = unix_socket,
    db = db_km_pay,
)

conn_km_crm = pymysql.connect(
    host= host,
    user= user,
    password= password,
    unix_socket = unix_socket,
    db = db_km_crm,
)

conn_km_master_api = pymysql.connect(
    host= host,
    user= user,
    password= password,
    unix_socket = unix_socket,
    db = db_km_master_api,
)

conn_km_store = pymysql.connect(
    host= host,
    user= user,
    password= password,
    unix_socket = unix_socket,
    db = db_kmstore
)
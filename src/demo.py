import base64
from Crypto.Cipher import AES
import binascii 
import pymysql

conn = pymysql.connect(
    host= 'dbnew.kuismilioner.com',
    user= 'kmnetuser2',
    password= 'B1nt@ngK3j0R4',
    db= 'db_kmv3',
)

a = conn.cursor()
sql = 'SELECT * FROM tbl_member limit 1000 ;'
a.execute(sql)

countrow = a.execute(sql)
data = a.fetchall()
print(data)
print("Number of rows :", countrow)

# IV is initialization vector it's same like public key sent on json
IV = '1ceca8552d6f7f48ba7f6323f8709911'
# convert hexa to bytes binary
result = binascii.unhexlify(IV)
# private key on 2 sides
key = "0123456789abcdefghijklmnopqrstuv"

def decrypt(enc, key):
    decobj = AES.new(key, AES.MODE_CBC, result)
    data = decobj.decrypt(base64.b64decode(enc))
    print(str(data.decode()))

decrypt("mhT8Ai2tkVzM+PIjomo/h/nyX0/gv6UilAXMZaDz9qxRzABV9rG7H9Goly1/cRqI", key)
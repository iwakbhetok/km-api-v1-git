from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
import connection, datetime
import Authentication, generalNotification, helper, globalVariable
from flask_caching import Cache
import re
import json
from pprint import pprint
from decimal import Decimal

app = Flask(__name__)
api = Api(app)

# Check Configuring Flask-Cache section for more details
cache = Cache(app,config={'CACHE_TYPE': globalVariable.CACHE_TYPE})

# Connection to kmpay and cursor kmpay
connectKmStore = connection.conn_km_store
cursorKmStore = connectKmStore.cursor()

now = datetime.datetime.now()

def checkEmailAccount(self, email):
    checkEmailSql = 'SELECT COUNT(*) FROM tbl_member WHERE member_email = %s;'
    cursorKmStore.execute(checkEmailSql, ([email]))
    res = cursorKmStore.fetchall()
    num = list(sum(res, ()))
    return num[0]

def calculatePriceProductByQty(self, product_detail_id, qty):
    getProductPriceSql = 'SELECT product_price FROM tbl_product_detail WHERE product_detail_id = %s;'
    cursorKmStore.execute(getProductPriceSql, ([product_detail_id]))
    res = cursorKmStore.fetchall()
    price = list(sum(res, ()))
    if price:
        subTotal = int(qty) * float(price[0])
        return subTotal
    else:
        return 0

def registerAccount(self, param):
    if len(param) != 0:
        if "TOKEN" in param:
            wrapData = param['DATA']
            splitData = wrapData.split(".")
            data = decrypt(splitData[0], key, splitData[1])
            newStr = re.match("(.*?)}", data).group()
            newStr= json.loads(newStr)
            email = newStr.get("email")
            full_name = newStr.get("full_name")
            address = newStr.get("address")
            token = newStr.get("token")
            tokenStatus = Authentication.checkValidToken(self, param['TOKEN'])

            if tokenStatus[0]["status"] == "valid":
                emailStatus = checkEmailAccount(self, email)
                prefix_domain = getPrefixDomain(self, newStr.get("domain"))
                no_rekening = str(prefix_domain['prefix_domain']) + generateAccountBank(self)
                if emailStatus != 1:
                    now = str(datetime.datetime.now())
                    createAccountSql = "INSERT INTO tbl_member (member_no_rekening, member_email, full_name, address, member_created_date, member_created_by) VALUES (%s, %s, %s, %s, %s, %s);"
                    cursorKmPay.execute(createAccountSql,([no_rekening], [email], [full_name], [address], [now], [globalVariable.create_by] ))
                    connectKmStore.commit()
                    return jsonify({'status ':"success", 'code': 200, "message":"Create Account Success"})
                else:
                    return jsonify({'status ':"error", 'code': 204, "message":"Email has been register before"})
            else:
                return tokenStatus
        else:
            return generalNotification.TokenNotAvailable(self)
    else:
        return generalNotification.DataNotAvailable(self)


def getListProduct(self, param):
    getListProductSql = 'SELECT product_id, category_id, product_name, product_number, brand_id, product_desc, create_date, product_slug FROM tbl_product'
    cursorKmStore.execute(getListProductSql)
    res = cursorKmStore.fetchall()
    items = []
    for row in res:
        items.append({'id': row[0], 'category_id': row[1], 'product_name': row[2], 'product_number': row[3], 'brand_id': row[4], 'product_desc':row[5], 'create_date': row[6], 'product_slug': row[7]})
    return jsonify({'status':'success','code': 200, 'result ': items})

def getProduct(self, param):
    getProductSql = 'SELECT product_id, category_id, product_name, product_number, brand_id, product_desc, create_date, product_slug FROM tbl_product WHERE product_id = %s'
    cursorKmStore.execute(getProductSql, (['6']))
    res = cursorKmStore.fetchall()
    items = []
    for row in res:
        items.append({'id': row[0], 'category_id': row[1], 'product_name': row[2], 'product_number': row[3], 'brand_id': row[4], 'product_desc':row[5], 'create_date': row[6], 'product_slug': row[7]})
    return jsonify({'status':'success','code': 200, 'result ': items})

def searchProductByName(self, param):
    searchProductSql = 'SELECT product_id, category_id, product_name, product_number, brand_id, product_desc, create_date, product_slug FROM tbl_product WHERE product_name LIKE %s'
    cursorKmStore.execute(searchProductSql, (["%" + "XL" + "%"]))
    res = cursorKmStore.fetchall()
    items = []
    for row in res:
        items.append({'id': row[0], 'category_id': row[1], 'product_name': row[2], 'product_number': row[3], 'brand_id': row[4], 'product_desc':row[5], 'create_date': row[6], 'product_slug': row[7]})
    return jsonify({'status':'success','code': 200, 'result ': items})

def createCart(self, param):
    if len(param) != 0:
        if "TOKEN" in param:
            wrapData = param['DATA']
            splitData = wrapData.split(".")
            data = helper.decrypt(splitData[0], globalVariable.key, splitData[1])
            data = data.replace("\x08", "")
            newStr= json.loads(data)
            member_id = newStr["member_id"]
            cart_items =  newStr["cart_items"]
            for item in cart_items:
                qty = item["quantity"]
                product_detail_id = item["product_detail_id"]
                subTotal = calculatePriceProductByQty(self, product_detail_id, qty)
                createCartSql = 'INSERT INTO tbl_cart (member_id, product_detail_id, quantity, price, created_date, created_by) VALUES (%s, %s, %s, %s, %s, %s);'
                cursorKmStore.execute(createCartSql,([member_id], [product_detail_id], [qty], [subTotal], [now], [globalVariable.create_by] ))
                connectKmStore.commit()
        else:
            return generalNotification.TokenNotAvailable(self)
    else:
        return generalNotification.DataNotAvailable(self)

def updateCart(self, param):
    if len(param) != 0:
        if "TOKEN" in param:
            pass
        else:
            return generalNotification.TokenNotAvailable(self)
    else:
        return generalNotification.DataNotAvailable(self)

def removeCart(self, param):
    if len(param) != 0:
        if "TOKEN" in param:
            pass
        else:
            return generalNotification.TokenNotAvailable(self)
    else:
        return generalNotification.DataNotAvailable(self)

def viewCart(self, param):
    if len(param) != 0:
        if "TOKEN" in param:
            pass
        else:
            return generalNotification.TokenNotAvailable(self)
    else:
        return generalNotification.DataNotAvailable(self)

def createOrder(self, param):
    if len(param) != 0:
        if "TOKEN" in param:
            pass
        else:
            return generalNotification.TokenNotAvailable(self)
    else:
        return generalNotification.DataNotAvailable(self)

def setMainAddress(self, param):
    if len(param) != 0:
        if "TOKEN" in param:
            pass
        else:
            return generalNotification.TokenNotAvailable(self)
    else:
        return generalNotification.DataNotAvailable(self)

def createNewAddress(self, param):
    if len(param) != 0:
        if "TOKEN" in param:
            pass
        else:
            return generalNotification.TokenNotAvailable(self)
    else:
        return generalNotification.DataNotAvailable(self)

def createPayment(self, param):
    if len(param) != 0:
        if "TOKEN" in param:
            pass
        else:
            return generalNotification.TokenNotAvailable(self)
    else:
        return generalNotification.DataNotAvailable(self)
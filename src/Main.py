from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_caching import Cache

import datetime
import connection, kmPay, kmStore, kmCrm, kmMain
from Authentication import *
import globalVariable, helper, generalNotification

app = Flask(__name__)
# api = Api(app)
api = Api(app, catch_all_404s=True)

# Check Configuring Flask-Cache section for more details
cache = Cache(app,config={'CACHE_TYPE': globalVariable.CACHE_TYPE})

class KmPayRequest(Resource):
    @cache.cached(timeout=globalVariable.timeout_min)
    def post(self):
        param = request.get_json()
        if param["CMD"]:
            if param['CMD'] == "CB":
                return kmPay.checkBalance(self, param)
            elif param['CMD'] == "RA":
                return kmPay.registerAccount(self, param)
            elif param['CMD'] == "TS":
                return kmPay.topupSaldo(self, param)
            elif param['CMD'] == 'WS':
                return kmPay.withdrawSaldo(self, param)
            elif param['CMD'] == 'WTS':
                return kmPay.withdrawTypeSaldo(self, param)
            elif param['CMD'] == 'CT':
                return kmPay.checkTransaction(self, param)
            elif param['CMD'] == 'CTP':
                return kmPay.checkTransactionByPeriod(self, param)
            elif param['CMD'] == 'PIN':
                return kmPay.generatePIN(self, param)
            elif param == None:
                return jsonify({'status':"error",'response_code':401,"result":{}})
            else:
                return jsonify({'status':"error",'response_code':400,"result":{}})
        else:
            return generalNotification.DataNotAvailable(self)


class KmStoreRequest(Resource):
    @cache.cached(timeout=globalVariable.timeout_max)
    def post(self):
        param = request.get_json()
        if param["CMD"]:
            #  Store Register Account
            if param["CMD"] == "SRA":
                return kmStore.registerAccount(self, param)
            #  List Product
            elif param["CMD"] == "SLP":
                return kmStore.getListProduct(self, param)
            # Get Product
            elif param['CMD'] == "SGP":
                return kmStore.getProduct(self, param)
            # Search Product by Name
            elif param['CMD'] == "SSP":
                return kmStore.searchProductByName(self, param)
            # Create Cart
            elif param['CMD'] == "SCC":
                return kmStore.createCart(self,param)
            # Update Cart
            elif param['CMD'] == "SUC":
                return kmStore.updateCart(self,param)
            # Delete Cart
            elif param['CMD'] == "SDC":
                return kmStore.removeCart(self,param)
            # View Detail Cart
            elif param['CMD'] == "SVC":
                return kmStore.viewCart(self,param)
            # Create Order
            elif param['CMD'] == "SCO":
                return kmStore.createOrder(self,param)
            # Set Main Address
            elif param['CMD'] == "SMA":
                return kmStore.setMainAddress(self,param)
            # Create New Address
            elif param['CMD'] == "SCA":
                return kmStore.createNewAddress(self,param)
            # Create Payment
            elif param['CMD'] == "SCP":
                return kmStore.createPayment(self,param)
            else:
                pass
        else:
            return generalNotification.DataNotAvailable(self)

class KmCrmRequest(Resource):
    @cache.cached(timeout=globalVariable.timeout_max)
    def post(self):
        param = request.get_json()
        if param["CMD"]:
            # CRM Register Account
            if param["CMD"] == "CRA":
                return kmCrm.registerAccount(self, param)
            #  Setting Quiz
            elif param["CMD"] == "CSQ":
                pass
            elif param["CMD"] == "CBQ":
                pass
            elif param["CMD"] == "CCQ":
                pass
            elif param == None:
                pass
            else:
                pass
        else:
            return generalNotification.DataNotAvailable(self)

class KmMainRequest(Resource):
    @cache.cached(timeout=globalVariable.timeout_max)
    def post(self):
        param = request.get_json()
        if param["CMD"]:
            #  KM Register Account
            if param["CMD"] == "KRA":
                return kmMain.registerAccount(self, param)
            #  Setting Quiz
            if param["CMD"] == "KSQ":
                pass
            elif param["CMD"] == "KBQ":
                pass
            elif param["CMD"] == "KCQ":
                pass
            else:
                pass
        else:
            return generalNotification.DataNotAvailable(self)


class TestRequest(Resource):
    @cache.cached(timeout=5)
    def get(self):
        return str(datetime.datetime.now())
    
    @cache.cached(timeout=globalVariable.timeout_min)
    def post(self):
        return str(datetime.datetime.now())

# @app.route('/testCache')
# @cache.cached(timeout=5)
# def testCache():
#     return str(datetime.datetime.now())


# auth api handshake
api.add_resource(Auth, connection.version + '/auth')

# api KM PAY request
api.add_resource(KmPayRequest, connection.version + '/kmpay/req')

# api KM STORE request
api.add_resource(KmStoreRequest, connection.version + '/kmstore/req')

# api KM CRM request
api.add_resource(KmCrmRequest, connection.version + '/kmcrm/req')

# api KM MAIN request
api.add_resource(KmMainRequest, connection.version + '/kmmain/req')


# api test
api.add_resource(TestRequest, connection.version + '/test')

if __name__ == '__main__':
    app.run(debug = True, host= '0.0.0.0', port=globalVariable.port, threaded=True)
    # app.run(host="127.0.0.2", port='8080', threaded=True)
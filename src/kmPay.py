from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
import connection, datetime
from random import randint
import re
import json
import Authentication, generalNotification, helper, globalVariable
from flask_caching import Cache

app = Flask(__name__)
api = Api(app)

# Check Configuring Flask-Cache section for more details
cache = Cache(app,config={'CACHE_TYPE': globalVariable.CACHE_TYPE})

# Connection to kmpay and cursor kmpay
connectKmPay = connection.conn_kmpay
cursorKmPay = connectKmPay.cursor()

# Connection to km api and cursor km api
connectKmApi = connection.conn_km_master_api
cursorKmApi = connectKmApi.cursor()

now = datetime.datetime.now()

def checkGoldmilStock(self, member_id, goldmil):
    pass

def checkEmailAccount(self, email):
    checkEmailSql = 'SELECT COUNT(*) FROM tbl_member WHERE member_email = %s;'
    cursorKmPay.execute(checkEmailSql, ([email]))
    res = cursorKmPay.fetchall()
    num = list(sum(res, ()))
    return num[0]

def getMemberIdbyBankAcc(self, no_rekening):
    sql = 'SELECT member_id FROM tbl_member WHERE member_no_rekening = %s'
    cursorKmPay.execute(sql, ([no_rekening]))
    res = cursorKmPay.fetchall()
    member_id = list(sum(res, ()))
    return member_id[0]

def generateAccountBank(self):
    now =  datetime.datetime.now()
    year = str(now.year)
    dateIdentify = '%02d' % now.day + '%02d' % now.month + year[2:4]
    sqlGetLatestAcc = 'SELECT member_no_rekening FROM `tbl_member` WHERE member_no_rekening = (SELECT MAX(member_no_rekening) FROM `tbl_member`);'
    cursorKmPay.execute(sqlGetLatestAcc)
    res = cursorKmPay.fetchall()
    accBankLatest = list(sum(res, ()))
    accBankLatest = accBankLatest[0]
    latestDigit = int(accBankLatest[7:13])
    newCounter = latestDigit + 1
    return dateIdentify + "%06d" % (newCounter,)

def generateOrderNumber(self, alias):
    now =  datetime.datetime.now()
    year = str(now.year)
    dateIdentify = '%02d' % now.day + '%02d' % now.month + year[2:4]
    sqlGetLatestOrd = 'SELECT order_number FROM `tbl_topup` WHERE order_number LIKE %s AND order_number = (SELECT MAX(order_number) FROM `tbl_topup`);'
    cursorKmPay.execute(sqlGetLatestOrd, ([alias + "%"]))
    res = cursorKmPay.fetchall()
    ordNumLatestArr = list(sum(res, ()))
    ordNumLatest = ordNumLatestArr[0]
    latestDigit = int(ordNumLatest[-4:])
    newCounter = latestDigit + 1
    return alias + "-"+ globalVariable.prefix_code_order_number +"-"+ dateIdentify + "-" + "%05d" % (newCounter,)

def generateWithdrawNumber(self, prefix):
    now =  datetime.datetime.now()
    year = str(now.year)
    dateIdentify = '%02d' % now.day + '%02d' % now.month + year[2:4]
    sqlGetLatestWith = 'SELECT withdraw_number FROM `tbl_withdraw` WHERE withdraw_number LIKE %s AND withdraw_number = (SELECT MAX(withdraw_number) FROM `tbl_withdraw`);'
    cursorKmPay.execute(sqlGetLatestWith, ([ globalVariable.prefix_code_withdraw_number + "-" + "%"]))
    res = cursorKmPay.fetchall()
    withNumLatestArr = list(sum(res, ()))
    if withNumLatestArr:
        # Continue counter of number
        withNumLatest = withNumLatestArr[0]
        latestDigit = int(withNumLatest[-4:])
        newCounter = latestDigit + 1
        newCounter = "%05d" % (newCounter,)
        return globalVariable.prefix_code_withdraw_number + "-" + str(prefix) + str(dateIdentify) + str(newCounter)
    else:
        # Create new initiate number
        return globalVariable.prefix_code_withdraw_number + "-" + prefix + dateIdentify + "000001"

def generatePIN(self):
    pin = (randint(000000, 999999))
    # CHECK PIN
    checkPinSql = 'SELECT COUNT(*) FROM tbl_withdraw WHERE withdraw_pin = %s;'
    cursorKmPay.execute(checkPinSql, ([pin]))
    res = cursorKmPay.fetchall()
    num = list(sum(res, ()))
    # IF PIN DOES EXIST
    if num[0] == 0:
        return pin
    else:
        newPin = (randint(000000, 999999))
        return newPin

def registerAccount(self, param):
    if len(param) != 0:
        if "TOKEN" in param:
            now = datetime.datetime.now()
            wrapData = param['DATA']
            splitData = wrapData.split(".")
            data = helper.decrypt(splitData[0], globalVariable.key, splitData[1])
            newStr = re.match("(.*?)}", data).group()
            newStr= json.loads(newStr)
            email = newStr.get("email")
            full_name = newStr.get("full_name")
            address = newStr.get("address")
            member_created_by = '1'
            token = newStr.get("token")
            tokenStatus = Authentication.checkValidToken(self, param['TOKEN'])
            
            if tokenStatus[0]["status"] == "success":
                emailStatus = checkEmailAccount(self, email)
                prefix_domain = helper.getPrefixDomain(self, newStr.get("domain"))
                no_rekening = str(prefix_domain['prefix_domain']) + generateAccountBank(self)
                if emailStatus != 1:
                    now = str(datetime.datetime.now())
                    createMemberAccountSql = "INSERT INTO tbl_member (member_no_rekening, member_email, full_name, address, member_created_date, member_created_by) VALUES (%s, %s, %s, %s, %s, %s);"
                    cursorKmPay.execute(createMemberAccountSql,([no_rekening], [email], [full_name], [address], [now], [member_created_by] ))
                    connectKmPay.commit()
                    # insert into rekening table
                    createAccountSql = 'INSERT INTO tbl_rekening (no_rekening, is_active, activate_date, created_date, created_by) VALUES (%s, %s, %s, %s, %s);'
                    cursorKmPay.execute(createAccountSql, ([no_rekening], [1], [now], [now], [globalVariable.create_by]))
                    connectKmPay.commit()
                    return jsonify({'status ':"success", 'code': 200, "message":"Create Account Success"})
                else:
                    return jsonify({'status ':"error", 'code': 204, "message":"Email has been register before"})
            else:
                return tokenStatus
        else:
            return generalNotification.TokenNotAvailable(self)
    else:
        return generalNotification.DataNotAvailable(self)


def checkBalance(self, params):
    if len(params) != 0:
        if "TOKEN" in params:
            wrapData = params['DATA']
            splitData = wrapData.split(".")
            data = helper.decrypt(splitData[0], globalVariable.key, splitData[1])
            newStr = re.match("(.*?)}", data).group()
            newStr= json.loads(newStr)
            no_rekening = newStr.get("no_rekening")
            token = newStr.get("token")
            tokenStatus = Authentication.checkValidToken(self, params['TOKEN'])
            if tokenStatus[0]["status"] == "success":
                now = datetime.datetime.now()
                month = now.month
                year = now.year
                sql = 'SELECT no_rekening, SUM(IF(transaction_type="K", balance, 0))  as K, SUM(IF(transaction_type="D", balance, 0)) as D, (SUM(IF(transaction_type="K", balance, 0))-SUM(IF(transaction_type="D", balance, 0))) as saldo, created_date FROM db_kmpay.tbl_transaksi WHERE MONTH(created_date)= %s and YEAR(created_date)=%s AND no_rekening = %s AND status_transaksi = "SUCCESS" GROUP BY no_rekening, MONTH(created_date), YEAR(created_date);'
                cursorKmPay.execute(sql,([month], [year],[no_rekening]))
                result = cursorKmPay.fetchall()
                items = []
                for row in result:
                    items.append({'sum_kredit': row[1], 'sum_debit': row[2], 'saldo': row[3]})
                
                if not items:
                    return {'status ':"success",'code': 204, "result":items}
                else:
                    return {'status ':"success",'code': 200, "result":items[0]}
            else:
                return tokenStatus[0]
        else:
            return generalNotification.TokenNotAvailable(self)
    else:
        return generalNotification.DataNotAvailable(self)


def topupSaldo(self, param):
    # insertTblLog = 'INSERT INTO tbl_log_topup topup_id, no_rekening, bank_from, bank_to, balance, status, created_date VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
    if len(param) != 0:
        if "TOKEN" in param:
            now = datetime.datetime.now()
            wrapData = param['DATA']
            splitData = wrapData.split(".")
            data = helper.decrypt(splitData[0], globalVariable.key, splitData[1])
            newStr = re.match("(.*?)}", data).group()
            newStr = json.loads(newStr)
            no_rekening = newStr.get("no_rekening")
            tokenStatus = Authentication.checkValidToken(self, param['TOKEN'])
            if tokenStatus[0]["status"] == "success":
                member_id = getMemberIdbyBankAcc(self, no_rekening)
                domain = helper.getPrefixDomain(self, newStr.get("domain"))
                order_number = generateOrderNumber(self, domain['alias'])
                insertTblTopup = 'INSERT INTO tbl_topup (member_id, order_number, payment_type, total_payment, transaction_time, transaction_status, status_message, created_date, created_by) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
                cursorKmPay.execute(insertTblTopup, ([member_id], [order_number], [globalVariable.payment_type], [newStr.get("amount")], [now], [globalVariable.transaction_status], [globalVariable.topup_status_message], [now], [globalVariable.create_by]))
                connectKmPay.commit()
                # INSERT transaksi tabel
                # insertTblTransaksi = 'INSERT INTO tbl_transaksi (no_rekening, transaction_type, point_type, description, balance, transaksi_date, status_transaksi, created_date, created_by) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
                # a.execute(insertTblTopup, ([no_rekening], ["K"], ['TOPUP'], ["description"], [newStr.get("balance")], [now], ['SUCCESS'], [now], ['1']))
                # conn.commit()
            else:
                return tokenStatus
        else:
            return generalNotification.TokenNotAvailable(self)
    else:
        return generalNotification.DataNotAvailable(self)

def withdrawSaldo(self, param):
    if len(param) != 0:
        if "TOKEN" in param:
            wrapData = param['DATA']
            splitData = wrapData.split(".")
            data = helper.decrypt(splitData[0], globalVariable.key, splitData[1])
            newStr = re.match("(.*?)}", data).group()
            newStr= json.loads(newStr)
            no_rekening = newStr.get("no_rekening")
            type = newStr.get("type")
            domain = newStr.get("domain")
            amount = newStr.get("amount")
            tokenStatus = Authentication.checkValidToken(self, param['TOKEN'])
            prefix = helper.getPrefixDomain(self, domain)
            prefix = prefix['prefix_domain']
            withdrawNumber = generateWithdrawNumber(self, prefix)
            withdraw_pin = generatePIN(self)

            if tokenStatus[0]["status"] == "success" and pinStatus["code"] == 200 :
                balance = checkBalance(self, param)
                
                if balance["result"] != []:
                    lastCredit = balance["result"]["saldo"]
                    saldo = int(lastCredit) - int(amount)
                    if saldo >= 0:
                        withdrawSql = 'INSERT INTO tbl_withdraw (no_rekening, withdraw_number, withdraw_pin, balance, type, status, created_date, created_by) VALUES (%s, %s, %s, %s, %s, %s, %s);'
                        cursorKmPay.execute(withdrawSql, ([no_rekening], [withdrawNumber], [withdraw_pin], [amount], [type], ["PENDING"], [now], [globalVariable.create_by]))
                        connectKmPay.commit()
                        # withdrawSql = 'INSERT INTO tbl_transaksi (no_rekening, transaction_type, description, balance, transaksi_date, status_transaksi, created_date, created_by) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);'
                        # cursorKmPay.execute(withdrawSql, ([no_rekening], ["D"], ["WITHDRAW"], [amount], [now], ["SUCCESS"], [now], [globalVariable.create_by]))
                        # connectKmPay.commit()
                        # Insert to LOG
                        withdrawLogSql = 'INSERT INTO tbl_log_withdraw (no_rekening, withdraw_pin, balance, type, status, created_date, created_by) VALUES (%s, %s, %s, %s, %s, %s, %s);'
                        cursorKmPay.execute(withdrawLogSql, ([no_rekening], [withdraw_pin], [amount], [type], ["NOT RECEIVE"], [now], [globalVariable.create_by]))
                        connectKmPay.commit()
                        return {'status ':"success",'code': 200, "result":"Success Withdraw"}
                    else:
                        return {'status ':"success",'code': 204, "result":"Saldo anda tidak mencukupi"}
                else:
                    return generalNotification.DataNotAvailable(self)
            else:
                return tokenStatus
        else:
            return generalNotification.TokenNotAvailable(self)
    else:
        return generalNotification.DataNotAvailable(self)

def checkTransaction(self, param):
    if len(param) != 0:
        if "TOKEN" in param:
            wrapData = param['DATA']
            splitData = wrapData.split(".")
            data = helper.decrypt(splitData[0], globalVariable.key, splitData[1])
            newStr = re.match("(.*?)}", data).group()
            newStr= json.loads(newStr)
            no_rekening = newStr.get("no_rekening")
            tokenStatus = Authentication.checkValidToken(self, param['TOKEN'])
            if tokenStatus[0]["status"] == "success":
                sql = 'SELECT transaksi_id, transaction_type, description, balance, created_date, status_transaksi FROM tbl_transaksi WHERE no_rekening = %s;'
                cursorKmPay.execute(sql,([no_rekening]))
                result = cursorKmPay.fetchall()
                items = []
                for row in result:
                    transaction_date = row[4].strftime('%d-%m-%Y')
                    items.append({'id': row[0], 'transaction_type': row[1], 'description': row[2], 'balance': row[3], 'transaction_date': transaction_date, 'transaction_status':row[5]})
                return jsonify({'status':'success','code': 200, 'result ': items})
            else:
                return tokenStatus
        else:
            return generalNotification.TokenNotAvailable(self)
    else:
        return generalNotification.DataNotAvailable(self)


def checkTransactionByPeriod(self, param):
    if len(param) != 0:
        if "TOKEN" in param:
            wrapData = param['DATA']
            splitData = wrapData.split(".")
            data = helper.decrypt(splitData[0], globalVariable.key, splitData[1])
            newStr = re.match("(.*?)}", data).group()
            newStr= json.loads(newStr)
            no_rekening = newStr.get("no_rekening")
            start_period = newStr.get("start_period")
            end_period = newStr.get("end_period")
            tokenStatus = Authentication.checkValidToken(self, param['TOKEN'])
            if tokenStatus[0]["status"] == "success":            
                sql = 'SELECT transaksi_id, transaction_type, description, balance, created_date, status_transaksi FROM tbl_transaksi WHERE no_rekening = %s AND created_date BETWEEN %s AND %s;'
                cursorKmPay.execute(sql,([no_rekening], [start_period], [end_period]))
                result = cursorKmPay.fetchall()
                items = []
                for row in result:
                    transaction_date = row[4].strftime('%d-%m-%Y')
                    items.append({'id': row[0], 'transaction_type': row[1], 'description': row[2], 'balance': row[3], 'transaction_date': transaction_date, 'transaction_status':row[5]})
                return {'status':'success','code': 200, 'result ': items}
            else:
                return tokenStatus
        else:
            return generalNotification.TokenNotAvailable(self)
    else:
        return generalNotification.DataNotAvailable(self)

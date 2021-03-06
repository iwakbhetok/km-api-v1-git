from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
import connection, pymysql, random, string, json, jwt, datetime, hashlib
import Authentication, generalNotification, helper, globalVariable
from flask_caching import Cache

app = Flask(__name__)
api = Api(app)

# Check Configuring Flask-Cache section for more details
cache = Cache(app,config={'CACHE_TYPE': globalVariable.CACHE_TYPE})

# Connection to kmcrm and cursor kmcrm
connectKmCrm = connection.conn_km_crm
cursorKmCrm = connectKmCrm.cursor()

now = datetime.datetime.now()

def checkEmailAccount(self, email):
    checkEmailSql = 'SELECT COUNT(*) FROM tbl_member WHERE member_email = %s;'
    cursorKmCrm.execute(checkEmailSql, ([email]))
    res = cursorKmCrm.fetchall()
    num = list(sum(res, ()))
    return num[0]

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
            token = newStr.get("token")
            tokenStatus = Authentication.checkValidToken(self, param['TOKEN'])
            
            if tokenStatus[0]["status"] == "success":
                emailStatus = checkEmailAccount(self, email)
                prefix_domain = helper.getPrefixDomain(self, newStr.get("domain"))
                no_rekening = str(prefix_domain['prefix_domain']) + generateAccountBank(self)
                if emailStatus != 1:
                    now = str(datetime.datetime.now())
                    createMemberAccountSql = "INSERT INTO tbl_member (member_no_rekening, member_email, full_name, address, member_created_date, member_created_by) VALUES (%s, %s, %s, %s, %s, %s);"
                    cursorKmCrm.execute(createMemberAccountSql,([no_rekening], [email], [full_name], [address], [now], [globalVariable.create_by] ))
                    connectKmCrm.commit()
                    # insert into rekening table
                    createAccountSql = 'INSERT INTO tbl_rekening (no_rekening, is_active, activate_date, created_date, created_by) VALUES (%s, %s, %s, %s, %s);'
                    cursorKmCrm.execute(createAccountSql, ([no_rekening], [1], [now], [now], [globalVariable.create_by]))
                    connectKmCrm.commit()
                    return jsonify({'status ':"success", 'code': 200, "message":"Create Account Success"})
                else:
                    return jsonify({'status ':"error", 'code': 204, "message":"Email has been register before"})
            else:
                return tokenStatus
        else:
            return generalNotification.TokenNotAvailable(self)
    else:
        return generalNotification.DataNotAvailable(self)

def settingQuiz(self, param):
    if len(param) != 0:
        if "TOKEN" in param:
            pass
        else:
            return generalNotification.TokenNotAvailable(self)
    else:
        return generalNotification.DataNotAvailable(self)

def buyQuiz(self, param):
    if len(param) != 0:
        if "TOKEN" in param:
            pass
        else:
            return generalNotification.TokenNotAvailable(self)
    else:
        return generalNotification.DataNotAvailable(self)

def createQuiz(self, param):
    if len(param) != 0:
        if "TOKEN" in param:
            pass
        else:
            return generalNotification.TokenNotAvailable(self)
    else:
        return generalNotification.DataNotAvailable(self)

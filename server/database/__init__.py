#encoding: utf-8

import os, json
import logger


"""for example
"User" : {
    "PWD" : xxxxxxxx,
    "UID" : 10000,
    "Name" : "Name10001",
    "Data" : {
        # save data
    }
}
"""

g_Account = {}

# 数据固化到硬盘
def Dumps():
    if not g_Account:
        return
    jsondata = json.dumps(g_Account)
    f = open(os.path.join(os.getcwd(), "account.data"), "wb")
    f.write(jsondata.encode("utf-8"))
    f.close()
    logger.Info("data write success.")

def Loads():
    try:
        global g_Account
        f = open(os.path.join(os.getcwd(), "account.data"), "rb")
        jsondata = f.read()
        f.close()
        g_Account = json.loads(jsondata)
        logger.Info("data read success.")
    except:
        logger.Info("init database")
        Dumps()

def CheckAccountPassword(sUser, sPassword):
    if not sUser in g_Account:
        return 1
    if g_Account[sUser]["PWD"] != sPassword:
        return 2
    return 0

def CheckAccountExist(sUser):
    if sUser in g_Account:
        return True
    return False

def RegisterAccount(sUser, sPassword):
    global g_Account

    if CheckAccountExist(sUser):
        return g_Account[sUser]["UID"]
    
    iCnt = len(g_Account)

    iUid = 10000 + iCnt + 1
    g_Account[sUser] = {
        "UID" : iUid,
        "PWD" : sPassword,
        "Name" : "Name%s"%(iUid),
        "Data" : {
            # save data
        }
    }
    Dumps()

    return iUid

def Init():
    Loads()
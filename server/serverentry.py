#encoding:utf-8
import global_defines

import struct
import protocol
import logger
import database
import service

def OnAnswer(oLink, oProtocol):
    # 判断回复的数据是否正确，不正确的话就断掉
    # 正确的话，就继续等待账密
    if oProtocol.m_Answer != 1234567890:
        return
    oLink.Disconnect("answer error")

def OnLoginAccount(oLink, oAccountProtocol):
    if not database.CheckAccountExist(oAccountProtocol.m_User):
        uid = database.RegisterAccount(oAccountProtocol.m_User, oAccountProtocol.m_Password)
    else:
        ret = database.CheckAccountPassword(oAccountProtocol.m_User, oAccountProtocol.m_Password)
        if ret:
            oLink.Disconnect("check account fail %s"%str(ret))
            return
        uid = database.RegisterAccount(oAccountProtocol.m_User, oAccountProtocol.m_Password)
    oPlayerMgr = service.GetService("PlayerManager")
    oPlayer = oPlayerMgr.CreatePlayer(oLink, uid)
    oPlayer.Login()
    oLink.ConnectedFinish()

def OnRequestTime(oLink, oRequestTime):
    p = protocol.p_login.P_SyncTime()
    p.m_ClientTime = oRequestTime.m_ClientTime
    p.m_ServerTime = global_defines.GetMillisecond()
    oLink.SendProtocol(p)

g_Func = {
    protocol.P_AnswerHello_Idx : OnAnswer,
    protocol.P_Login_Idx : OnLoginAccount,
    protocol.P_RequestSyncTime_Idx : OnRequestTime,
}

def OnEntry(oLink, pkgdata, oOtherEntryFunc):
    iProtocolNumber = struct.unpack("H", pkgdata[2:4])[0]
    cls = protocol.GetProtocol(iProtocolNumber)
    logger.Info("有数据包进来可以解析了")
    if not cls:
        logger.Warning("没找到合适的解析协议")
        return
    oProtocol = cls()
    oProtocol.UnpackData(pkgdata)

    oFunc = g_Func.get(oProtocol.m_ProtocolNumber, oOtherEntryFunc)
    if not oFunc:
        return
    oFunc(oLink, oProtocol)
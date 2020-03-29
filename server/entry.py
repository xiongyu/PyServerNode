#encoding: utf-8

import protocol
import struct
import logger
import player
import service
import database

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

def OnEcho(oLink, oEcho):
    logger.Info(oEcho.m_Text)

    p = protocol.P_Echo()
    p.m_Text = bytes("Copy that!", encoding="utf-8")
    oLink.SendProtocol(p)

g_Func = {
    protocol.P_AnswerHello_Idx : OnAnswer,
    protocol.P_Login_Idx : OnLoginAccount,
    protocol.P_Echo_Idx : OnEcho,
}

def OnEntry(oLink, data):
    iProtocolNumber = struct.unpack("H", data[2:4])[0]
    cls = protocol.GetProtocol(iProtocolNumber)
    logger.Info("有数据包进来可以解析了")
    if not cls:
        logger.Warning("没找到合适的解析协议")
        return
    oProtocol = cls()
    oProtocol.UnpackData(data)
    oFunc = g_Func.get(oProtocol.m_ProtocolNumber, None)
    if oFunc:
        oFunc(oLink, oProtocol)
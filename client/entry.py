#encoding: utf-8

import protocol
import struct
import logger

def OnHello(sock, oProtocol):
    print("Hello", oProtocol.m_Seed)
    a = protocol.p_login.P_AnswerHello()
    a.m_Answer = oProtocol.m_Seed
    data = a.PacketData()
    sock.send(data)

    # 账密
    l = protocol.p_login.P_Login()
    l.m_User = "Test0001"
    l.m_Password = "88888888"
    data = l.PacketData()
    sock.send(data)

def OnEcho(sock, oEchoProtocol):
    print(oEchoProtocol.m_Text)

    p = protocol.P_Echo()
    p.m_Text = bytes("Copy that again?", encoding="utf-8")
    data = p.PacketData()
    sock.send(data)

g_Func = {
    protocol.P_Hello_Idx : OnHello,
    protocol.P_Echo_Idx : OnEcho,
}

def OnEntry(sock, data):
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
        oFunc(sock, oProtocol)
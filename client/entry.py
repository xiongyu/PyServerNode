#encoding: utf-8

from bindfunc import CFunction
import protocol
import customprotocol.p_player
import struct
import logger
import timer

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

def OnPlayerInfo(sock, oInfo):
    print(oInfo.m_Uid)
    print(oInfo.m_Name)

    p = protocol.p_login.P_RequestSyncTime()
    p.m_ClientTime = timer.GetSecond()

    data = p.PacketData()
    sock.send(data)

def OnSyncTime(sock, oSyncTime):
    def TimerSyncTime(sock):
        p = protocol.p_login.P_RequestSyncTime()
        p.m_ClientTime = timer.GetSecond()

        data = p.PacketData()
        sock.send(data)
        
    print("SyncTime:", oSyncTime.m_ClientTime, oSyncTime.m_ServerTimeS, oSyncTime.m_ServerTimeMS)
    iClientMS = timer.GetMillisecond() 
    iServerMS = oSyncTime.m_ServerTimeS * 1000 + oSyncTime.m_ServerTimeMS
    print("Time:", iClientMS, iServerMS)
    timer.SetTimeDifference(iClientMS - iServerMS)
    timer.Schedule(CFunction(TimerSyncTime, sock), 5000, "TimerSyncTime")

g_Func = {
    protocol.P_Hello_Idx : OnHello,
    protocol.P_Echo_Idx : OnEcho,
    protocol.P_BaseInfo_Idx: OnPlayerInfo,
    protocol.P_SyncTime_Idx: OnSyncTime,
}

def OnEntry(sock, data):
    iProtocolNumber = struct.unpack("H", data[2:4])[0]
    cls = protocol.GetProtocol(iProtocolNumber)
    if not cls:
        logger.Warning("没找到合适的解析协议 %s"%(iProtocolNumber))
        return
    oProtocol = cls()
    oProtocol.UnpackData(data)
    oFunc = g_Func.get(oProtocol.m_ProtocolNumber, None)
    if oFunc:
        oFunc(sock, oProtocol)
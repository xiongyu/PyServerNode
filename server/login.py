#encoding: utf-8

from bindfunc import CFunction
import protocol
import tcpserver
import timer, logger
import service

class CLinkObject:

    def __init__(self, iSocketID):
        self.m_ID = g_LinkManager.UpdateID()
        self.m_SocketID = iSocketID
        self.m_RecvData = bytes()

    def SendProtocol(self, oProtocol):
        oMgrServer = service.GetService("ServerManager")
        oTcpServer = oMgrServer.Get("client")

        data = oProtocol.PacketData()
        oTcpServer.SendData(self.m_SocketID, data)

    def ConnectedFinish(self):
        logger.Info("%s Connected finish"%(self.m_SocketID))
        timer.Unschedule("Connected_%s"%(self.m_SocketID))

    def Disconnect(self, sReason):
        timer.Unschedule("Connected_%s"%(self.m_SocketID))
        logger.Info("%s disconnect r=%s"%(self.m_SocketID, sReason))
        oMgrServer = service.GetService("ServerManager")
        oTcpServer = oMgrServer.Get("client")
        oTcpServer.Disconnect(self.m_SocketID)

class CLinkManager:
    
    m_LinkID = 0xffffffff
    m_Links = {}

    def UpdateID(self):
        self.m_LinkID -= 1
        return self.m_LinkID

    def AddLink(self, oLinkObject):
        self.m_Links[oLinkObject.m_SocketID] = oLinkObject

    def GetLink(self, iSocketID):
        if not iSocketID in self.m_Links:
            return None
        return self.m_Links[iSocketID]

if not "g_LinkManager" in globals():
    g_LinkManager = CLinkManager()

def ConnectTimeout(iSocketID):
    timer.Unschedule("Connected_%s"%(iSocketID))
    logger.Info("connect timeout %s"%(iSocketID))
    oLinkObject = g_LinkManager.GetLink(iSocketID)
    oLinkObject.Disconnect("timeout")

def OnConnected(iSocketID):
    oLinkObject = CLinkObject(iSocketID)
    g_LinkManager.AddLink(oLinkObject)
    # 定时5秒，这个链接如果不能在5秒内完成认证回复以及账密登陆，就拒绝连接
    timer.Unschedule("Connected_%s"%(iSocketID))
    timer.Schedule(CFunction(ConnectTimeout, iSocketID), 5000, "Connected_%s"%(iSocketID))

    oProtocol = protocol.p_login.P_Hello()
    oProtocol.m_Seed = 123456789
    oLinkObject.SendProtocol(oProtocol)
    
def GetLinkObject(iSocketID):
    return g_LinkManager.GetLink(iSocketID)
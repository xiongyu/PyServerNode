#encoding: utf-8

from bindfunc import CFunction
import protocol
import tcpserver
import timer, logger
import service

class CLinkObject:

    def __init__(self, iSocketID):
        oLinkMgr = service.GetService("LinkManager")
        self.m_ID = oLinkMgr.UpdateID()
        self.m_SocketID = iSocketID
        self.m_RecvData = bytes()

    def SendProtocol(self, oProtocol):
        oMgrServer = service.GetService("ServerManager")
        oTcpServer = oMgrServer.Get("client")

        data = oProtocol.PacketData()
        oTcpServer.SendData(self.m_SocketID, data)

    def VerifyLink(self):
        # 定时5秒，这个链接如果不能在5秒内完成认证回复以及账密登陆，就拒绝连接
        timer.Unschedule("Connected_%s"%(self.m_ID))
        timer.Schedule(CFunction(ConnectTimeout, self.m_ID), 5000, "Connected_%s"%(self.m_ID))

        oProtocol = protocol.p_login.P_Hello()
        oProtocol.m_Seed = 123456789
        self.SendProtocol(oProtocol)

    def ConnectedFinish(self):
        logger.Info("%s Connected finish"%(self.m_ID))
        timer.Unschedule("Connected_%s"%(self.m_ID))

    def Disconnect(self, sReason):
        timer.Unschedule("Connected_%s"%(self.m_ID))
        logger.Info("%s disconnect r=%s"%(self.m_ID, sReason))
        oMgrServer = service.GetService("ServerManager")
        oTcpServer = oMgrServer.Get("client")
        oTcpServer.Disconnect(self.m_SocketID)

        oLinkMgr = service.GetService("LinkManager")
        oLinkMgr.DelLink(self.m_ID)

class CLinkManager(service.CServiceBase):
    
    m_Name = "LinkManager"
    m_LinkID = 0xffffffff
    m_Links = {}
    m_LinkSockets = {}

    def UpdateID(self):
        self.m_LinkID -= 1
        return self.m_LinkID

    def AddLink(self, oLinkObject):
        self.m_Links[oLinkObject.m_ID] = oLinkObject
        self.m_LinkSockets[oLinkObject.m_SocketID] = oLinkObject

    def DelLink(self, iLinkID):
        if not iLinkID in self.m_Links:
            return
        oLink = self.m_Links[iLinkID]
        iSocketID =oLink.m_SocketID
        del self.m_Links[iLinkID]
        del self.m_LinkSockets[iSocketID]

    def GetLink(self, iLinkID):
        if not iLinkID in self.m_Links:
            return None
        return self.m_Links[iLinkID]

    def GetLinkBySocketID(self, iSocketID):
        if not iSocketID in self.m_LinkSockets:
            return None
        return self.m_LinkSockets[iSocketID]

def ConnectTimeout(iLinkID):
    timer.Unschedule("Connected_%s"%(iLinkID))
    logger.Info("connect timeout %s"%(iLinkID))
    oLinkMgr = service.GetService("LinkManager")
    oLinkObject = oLinkMgr.GetLink(iLinkID)
    oLinkObject.Disconnect("timeout")

def OnConnected(iSocketID):
    oLinkObject = CLinkObject(iSocketID)
    oLinkMgr = service.GetService("LinkManager")
    oLinkMgr.AddLink(oLinkObject)
    oLinkObject.VerifyLink()

def GetLinkObject(iLinkID):
    oLinkMgr = service.GetService("LinkManager")
    return oLinkMgr.GetLink(iLinkID)

def GetLinkObjectBySocketID(iSocketID):
    oLinkMgr = service.GetService("LinkManager")
    return oLinkMgr.GetLinkBySocketID(iSocketID)
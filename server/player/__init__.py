#encoding: utf-8

from bindfunc import CFunction
import service
import timer
import time
import logger

# 5分钟都没连回来，就真正离线吧
def CheckOffline(iUid):
    oPlayerMgr = service.GetService("PlayerManager")
    oPlayer = oPlayerMgr.GetPlayer(iUid)
    if not oPlayer:
        return
    oPlayer.Disconnected("wait reconnect failed.", True)

class CPlayerManager(service.CServiceBase):
    
    m_Name = "PlayerManager"
    m_Players = {}
    m_PlayerClass = None

    def SetCustomPlayerClass(self, cls):
        self.m_PlayerClass= cls

    def CreatePlayer(self, oLink, uid):
        if uid in self.m_Players:
            # 玩家对象还存在，证明断线重连而已，修正socket指向即可
            oPlayer = self.m_Players[uid]
        else:
            if self.m_PlayerClass:
                oPlayer = self.m_PlayerClass(uid)
            else:
                oPlayer = CPlayer(uid)
            self.m_Players[uid] = oPlayer

        oLink.m_ProxyID = uid
        oPlayer.SetLinkID( oLink.m_ID )

        return oPlayer

    def DelPlayer(self, uid, sReason):
        logger.Info("del player %s, r=%s"%(uid, sReason))
        if not uid in self.m_Players:
            return
        del self.m_Players[uid]

    def GetPlayer(self, uid):
        return self.m_Players.get(uid, None)

    def Disconnected(self, uid, sReason):
        oPlayer = self.GetPlayer(uid)
        if not oPlayer:
            return
        oPlayer.m_LinkID = 0
        oPlayer.Disconnected(sReason)


class CPlayer:

    # 记录着连接层的ID，发包就靠这个ID了，这个ID为0
    # 就表示连接断了。会出现一定的延时，不能实时表示为断开
    m_LinkID = 0

    def __init__(self, uid):
        self.m_ID = uid
        self.m_WaitConnectFlag = "WaitConnect_%s"%(uid)
        self.m_OfflineTime = 0

    def GetName(self):
        return "Player%s"%(self.m_ID)

    def SetLinkID(self, iLinkID):
        self.m_LinkID = iLinkID

    def Login(self):
        timer.Unschedule(self.m_WaitConnectFlag)
        if self.m_OfflineTime:
            bRelink = True
            self.m_OfflineTime = 0
        else:
            bRelink = False
        self.OnLogin(bRelink)

    def OnLogin(self, bRelink):
        pass

    def WaitReconnect(self):
        if self.m_OfflineTime:
            return
        logger.Info("wait disconnect %s"%(self.m_ID))
        timer.Unschedule(self.m_WaitConnectFlag)
        timer.Schedule(CFunction(CheckOffline, self.m_ID), 30000, self.m_WaitConnectFlag)
        self.m_OfflineTime = int(time.time())

    def Disconnected(self, sReason, bForceQuit = False):
        if not bForceQuit:
            self.WaitReconnect()
        else:
            logger.Info("real disconnect %s, r=%s, force=%s"%(self.m_ID, sReason, bForceQuit))
            self.OnDisconnected()
            service.GetService('PlayerManager').DelPlayer(self.m_ID, sReason)

    def OnDisconnected(self):
        pass

    def SendProtocol(self, oProtocol):
        oLinkMgr = service.GetService("LinkManager")
        oLink = oLinkMgr.GetLink(self.m_LinkID)
        if not oLink:
            return
        oLink.SendProtocol(oProtocol)
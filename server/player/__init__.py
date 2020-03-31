#encoding: utf-8

import service

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

        oLink.m_Uid = uid
        oPlayer.SetLinkID( oLink.m_ID )

        return oPlayer

    def GetPlayer(self, uid):
        return self.m_Players.get(uid, None)

    def Disconnected(self, uid):
        oPlayer = self.GetPlayer(uid)
        if not oPlayer:
            return
        oPlayer.m_LinkID = 0
        oPlayer.Disconnected()


class CPlayer:

    # 记录着连接层的ID，发包就靠这个ID了，这个ID为0
    # 就表示连接断了。会出现一定的延时，不能实时表示为断开
    m_LinkID = 0

    def __init__(self, uid):
        self.m_ID = uid

    def GetName(self):
        return "Player%s"%(self.m_ID)

    def SetLinkID(self, iLinkID):
        self.m_LinkID = iLinkID

    def Login(self):
        self.OnLogin()

    def OnLogin(self):
        pass

    def Disconnected(self):
        self.OnDisconnected()

    def OnDisconnected(seslf):
        pass

    def SendProtocol(self, oProtocol):
        oLinkMgr = service.GetService("LinkManager")
        oLink = oLinkMgr.GetLink(self.m_LinkID)
        if not oLink:
            return
        oLink.SendProtocol(oProtocol)
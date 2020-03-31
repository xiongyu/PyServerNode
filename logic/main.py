#encoding: utf-8

import sys,os
sys.path.append("../server")
sys.path.append("../common")

import serverapp
import sys
import entry
import service
import player

class CCustomPlayer(player.CPlayer):
    
    def OnLogin(self):
        import customprotocol.p_player
        oBaseInfo = customprotocol.p_player.P_BaseInfo()
        oBaseInfo.m_Uid = self.m_ID
        oBaseInfo.m_Name = self.GetName()
        print(oBaseInfo)
        self.SendProtocol(oBaseInfo)

    def OnDisconnected(self):
        pass

app = serverapp.CServerApplication(sys.argv)
app.SetEntry(entry.OnEntry)

service.GetService("PlayerManager").SetCustomPlayerClass(CCustomPlayer)

app.Listen(12349, "0.0.0.0")
app.Exec()
print("Bye!~")

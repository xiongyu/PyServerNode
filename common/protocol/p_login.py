#encoding: utf-8

from .protocolbase import CProtocol, VarType, g_Protocol

# 握手协议
class P_Hello(CProtocol):

    m_ProtocolNumber = 0x1
    m_Define = (
        ("m_Seed", VarType.uInt32),
    )

class P_AnswerHello(CProtocol):
    
    m_ProtocolNumber = 0x2
    m_Define = (
        ("m_Answer", VarType.uInt32),
    )

# 账密登陆
class P_Login(CProtocol):
    m_ProtocolNumber = 0x3
    m_Define = (
        ("m_User", VarType.String)
        , ("m_Password", VarType.String)
    )

# 对时协议

class P_RequestSyncTime(CProtocol):
    m_ProtocolNumber = 0x4
    m_Define = (
        ("m_ClientTime", VarType.uInt32),
    )

class P_SyncTime(CProtocol):
    m_ProtocolNumber = 0x5
    m_Define = (
        ("m_ClientTime", VarType.uInt32),
        ("m_ServerTimeS", VarType.uInt32),
        ("m_ServerTimeMS", VarType.uInt16),
    )

class P_Echo(CProtocol):
    m_ProtocolNumber = 0xC350
    m_Define = (
        ("m_Text", VarType.String),
    )

"""
p = CLoginProtocol()
p.m_User = "TestMan".encode("utf-8")
p.m_Password = "asdasdasd".encode("utf-8")
data = p.PacketData()
print(data)

p2 = CLoginProtocol()
p2.UnpackData(data)
print(p2.m_ProtocolNumber)
print(p2.m_User)
print(p2.m_Password)
"""
#encoding: utf-8

from protocol.protocolbase import CProtocol, VarType, g_Protocol

# 玩家基础信息
class P_BaseInfo(CProtocol):

    m_ProtocolNumber = 0x20
    m_Define = (
        ("m_Uid", VarType.uInt32),
        ("m_Name", VarType.String),
        ("m_Cash", VarType.uInt32),
    )

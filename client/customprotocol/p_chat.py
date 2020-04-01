#encoding: utf-8

from protocol.protocolbase import CProtocol, VarType, g_Protocol

# 玩家基础信息
class P_Say(CProtocol):

    m_ProtocolNumber = 0x100
    m_Define = (
        ("m_Channel", VarType.uInt32),
        ("m_Text", VarType.String),
    )

class P_RecvSay(CProtocol):

    m_ProtocolNumber = 0x101
    m_Define = (
        ("m_ID", VarType.uInt32),
        ("m_Name", VarType.String),
        ("m_Text", VarType.String),
    )

class P_BrocastSay(CProtocol):

    m_ProtocolNumber = 0x102
    m_Define = (
        ("m_ID", VarType.uInt32),
        ("m_Name", VarType.String),
        ("m_Text", VarType.String),
    )
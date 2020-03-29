#encoding: utf-8

class CTcpSocket:

    def __init__(self, iSocketID, sock, sAddress):
        self.m_ID = iSocketID
        self.m_Socket = sock
        self.m_Address = sAddress

#encoding: utf-8

import protocol
import tcpserver
import timer
import traceback, struct, signal
import logger
import login
import service
import database
import player

import serverentry

S_NOTRUN = 0
S_LISTEN = 1
S_EXIT = 2

class CServerApplication:
    
    def __init__(self, argv):
        logger.Init()
        database.Init()
        service.Init()

        self.m_Status = S_NOTRUN
        self.m_Server = None
        self.m_EntryFunc = None

        logger.Info("Server Application Init")

        # 处理下退出的消息
        signal.signal(signal.SIGINT, self.OnSignal) # 2
        signal.signal(signal.SIGQUIT, self.OnSignal) # 3

    def Listen(self, iPort, sAddress = "127.0.0.1"):
        logger.Info("Server listen port %s"%(iPort))
        self.m_Status = S_LISTEN
        self.m_Server = tcpserver.CTcpServer(sAddress, iPort, "client")

        # 注册两个回调函数，一个是有新链接进来时回调
        # 另外一个是已经连上的有数据可读
        self.m_Server.On("OnConnected", self.OnConnected)
        self.m_Server.On("OnDisconnected", self.OnDisconnected)
        self.m_Server.On("OnReadyRead", self.OnReadyRead)

    def Exit(self):
        self.m_Status = S_EXIT

    # 有新链接进来，do some sth.
    def OnConnected(self, oMsg):
        logger.Info("OnConnected")
        login.OnConnected(oMsg.m_SocketID)

    def OnDisconnected(self, oMsg):
        oLink = login.GetLinkObjectBySocketID(oMsg.m_SocketID)
        oLink.Disconnect("client close")

    def OnReadyRead(self, oMsg):
        oLink = login.GetLinkObjectBySocketID(oMsg.m_SocketID)
        oLink.m_RecvData += oMsg.m_Data["Data"]

        newdata, pkglist = protocol.GetRecvPackage(oLink.m_RecvData)
        if not pkglist:
            return

        oLink.m_RecvData = newdata
        for pkgdata in pkglist:
            serverentry.OnEntry(oLink, pkgdata, self.m_EntryFunc)

    def Exec(self):
        self.m_Server.Listen()
        
        while S_LISTEN == self.m_Status:
            # 处理定时器超时
            try:
                timer.Frame()
            except Exception as e:
                traceback.print_exc()
            # 处理网络部分
            try:
                self.m_Server.Frame()
            except Exception as e:
                traceback.print_exc()

        logger.Info("进程退出")
        self.m_Server.Exit()

    def OnSignal(self, signum, frame):
        signal.signal(signal.SIGINT, self.OnSignal) # 2
        signal.signal(signal.SIGQUIT, self.OnSignal) # 3

        if signum in (signal.SIGINT, signal.SIGQUIT):
            self.Exit()

    def SetEntry(self, oEntryFunc):
        self.m_EntryFunc = oEntryFunc
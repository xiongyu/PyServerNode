#encoding: utf-8

from queue import Queue
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import threading, traceback, ctypes, inspect
import tcpsocket
import select
import service
import logger
from bindfunc import CFuncBinder

MSG_UNKONW = 0
MSG_NEW = 1
MSG_READ = 2
MSG_CLOSE = 3

class CNetWorkMessage:

    def __init__(self, msg, iSocketID, **data):
        self.m_Type = msg
        self.m_SocketID = iSocketID #not fd, is id
        self.m_Data = data


def StopThread(tid):
    """raises the exception, performs cleanup if needed"""
    exctype = SystemExit
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def NetworkThread(oTcpServer):
    epoll = oTcpServer.m_Epoll
    oSocket = oTcpServer.m_ServerSocket
    container = oTcpServer.m_Sockets

    while oTcpServer.IsRunning():
        try:
            # 处理需要退出的socket
            while not oTcpServer.m_QuitQueue.empty():
                iSocketID = oTcpServer.m_QuitQueue.get()
                if not iSocketID in oTcpServer.m_SocketID2FD:
                    continue
                fd = oTcpServer.m_SocketID2FD[iSocketID]
                if fd in container:
                    oTcpSocket = container[fd]
                    epoll.unregister(fd)
                    oTcpSocket.m_Socket.close()
                    del container[fd]
                    del oTcpServer.m_SocketID2FD[oTcpSocket.m_ID]

            epoll_list = epoll.poll(0.1)
            # epoll 进行 fd 扫描的地方 扫描出能满足条件的套接字，添加进列表中
            for fd, events in epoll_list:
                #对epoll列表中的文件描述符、事件进行扫描
                if fd == oSocket.fileno():
                    oTcpServer.m_SocketID += 1
                    #表示有客户端连接了服务器套接字
                    conn, addr = oSocket.accept()
                    oTcpSocket = tcpsocket.CTcpSocket(oTcpServer.m_SocketID, conn, addr)

                    logger.Info('there has been a new cilent form [%s] %s %s %s'%(str(addr), oTcpSocket.m_ID, fd, conn.fileno()))

                    container[conn.fileno()] = oTcpSocket
                    oTcpServer.m_SocketID2FD[oTcpSocket.m_ID] = conn.fileno()
                    epoll.register(conn.fileno(), select.EPOLLIN|select.EPOLLET)

                    oMsg = CNetWorkMessage(MSG_NEW, oTcpSocket.m_ID)
                    oTcpServer.PushMessage(oMsg)

                elif events == select.EPOLLIN:
                    #表示可以收取信息 
                    oTcpSocket = container[fd]
                    oClientSocket = oTcpSocket.m_Socket
                    recvData = oClientSocket.recv(1024)

                    if len(recvData) > 0:
                        #logger.Info('massage from [%s] is %s'%(str(addr), str(recvData)))
                        oMsg = CNetWorkMessage(MSG_READ, oTcpSocket.m_ID, Data = recvData)
                        oTcpServer.PushMessage(oMsg)
                    else:
                        logger.Info('client[%s] was closed'%str(addr))
                        epoll.unregister(fd)
                        oTcpSocket = container[fd]
                        oTcpSocket.m_Socket.close()
                        del container[fd]
                        del oTcpServer.m_SocketID2FD[oTcpSocket.m_ID]
                        
                        oMsg = CNetWorkMessage(MSG_CLOSE, oTcpSocket.m_ID)
                        oTcpServer.PushMessage(oMsg)
        except Exception as e:
            traceback.print_exc()

class CTcpServer(CFuncBinder):

    def __init__(self, sAddress, iPort, sFlag):
        self.m_Address = sAddress
        self.m_Port = iPort
        self.m_Queue = Queue()
        self.m_SendQueue = Queue()
        self.m_QuitQueue = Queue()
        self.m_Epoll = None
        self.m_Sockets = {}
        self.m_SocketID2FD = {}
        self.m_SocketID = 0
        self.m_ServerSocket = socket(AF_INET, SOCK_STREAM)
        self.m_NetThread = threading.Thread(target = NetworkThread,args = (self,))
        self.m_CBFunc = {}
        self.m_Running = False

        self.m_Flag = sFlag

        oSMgr = service.GetService("ServerManager")
        oSMgr.Add(sFlag, self)

    def Listen(self):
        if self.m_Running:
            return
        self.m_Running = True
        self.m_ServerSocket.bind((self.m_Address,self.m_Port))
        self.m_ServerSocket.listen(65535)     #最大连接数
        self.m_Epoll = select.epoll()
        self.m_Epoll.register(self.m_ServerSocket.fileno(), select.EPOLLIN|select.EPOLLET)
        self.m_NetThread.start()

    def Close(self):
        self.m_Running = False

        #立即释放端口
        StopThread(self.m_NetThread.ident)
        self.m_ServerSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.m_ServerSocket.close()

    def PushMessage(self, oMsg: CNetWorkMessage):
        self.m_Queue.put(oMsg)

    def Disconnect(self, iSocketID):
        self.m_QuitQueue.put(iSocketID)

    def SendData(self, iSocketID, data):
        self.m_SendQueue.put((iSocketID, data))

    def WriteData(self, iSocketID, data):
        if not iSocketID in self.m_SocketID2FD:
            return False
        iFD = self.m_SocketID2FD[iSocketID]
        if not iFD in self.m_Sockets:
            return False
        oTcpSocket = self.m_Sockets[iFD]
        oTcpSocket.m_Socket.send(data)

    def Frame(self):
        # 处理消息队列
        while not self.m_Queue.empty():
            oMsg = self.m_Queue.get()
            dCBFunc = {
                1: "OnConnected",
                2: "OnReadyRead",
                3: "OnDisconnected",
            }
            sFunc = dCBFunc.get(oMsg.m_Type, None)
            if not sFunc:
                return
            self.Call(sFunc, oMsg)
        
        # 处理发包队列
        while not self.m_SendQueue.empty():
            iSocketID, data = self.m_SendQueue.get()
            self.WriteData(iSocketID, data)            

    def Exit(self):
        self.Close()
        logger.Info("关闭网络服务")

    def IsRunning(self):
        return self.m_Running

class CServerManager(service.CServiceBase):

    m_Name = "ServerManager"

    def __init__(self):
        self.m_Objs = {}

    def Add(self, sFlag, oObj):
        if sFlag in self.m_Objs:
            raise Exception("'%s' Server is already exist!"%(sFlag))
        self.m_Objs[sFlag] = oObj

    def Get(self, sFlag):
        if not sFlag in self.m_Objs:
            return None
        return self.m_Objs[sFlag]

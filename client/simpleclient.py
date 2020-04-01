#encoding:utf-8

import sys
sys.path.append("../common")

# 把协议文件拷过来用
import shutil
try:
    shutil.rmtree("customprotocol/")
except:
    pass

try:
    shutil.copytree("../logic/customprotocol", "customprotocol/")
except:
    pass

#客户端与上一个没有任何改变
import protocol
from socket import socket, AF_INET, SOCK_STREAM
from protocol import GetRecvPackage
import entry, logger

logger.Init()

address='127.0.0.1'   #服务器的ip地址
port=12349           #服务器的端口号
s=socket(AF_INET, SOCK_STREAM)
s.connect((address,port))

g_Data = bytes()

while True:
    recvdata=s.recv(1024)
    if not recvdata:
        break
    g_Data += recvdata
    print(type(recvdata), recvdata)
    data, pkglist = GetRecvPackage(g_Data)
    if not pkglist:
        continue
    g_Data = data
    print(pkglist)
    for pkgdata in pkglist:
        entry.OnEntry(s, pkgdata)

s.close()
logger.Info("Exit! Bye!~")
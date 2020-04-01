#encoding: utf-8

from .protocolbase import *
import struct

def GetProtocol(iProtocolNumber):
    return g_Protocol.get(iProtocolNumber, None)

def GetRecvPackage(data):
    pkglist = []
    iPoint = 0

    while len(data[iPoint:]) > 2:
        iLen = struct.unpack("H", data[iPoint: iPoint + 2])[0]
        # 数据还不够，等足够了再说
        if iLen > len(data[iPoint:]):
            break

        pkgdata = data[iPoint : iPoint + iLen]
        iPoint += iLen
        pkglist.append(pkgdata)

    if 0 != iPoint:
        data = data[iPoint:]

    return data, pkglist

import protocol.p_login
#encoding: utf-8

import sys, struct, enum

"""
协议格式：
[协议包长度][协议数据内容]
"""

if not "g_Protocol" in globals():
    g_Protocol = {}

class Meta(type):
    # cls 代表动态修改的类
    # name 代表动态修改的类名
    # bases 代表被动态修改的类的所有父类
    # attrs 代表被动态修改的类的所有属性、方法组成的字典
 
    def __new__(metacls, name, bases, attrs):
        if name != "CProtocol":
            #动态为该类添加一个cal_price方法
            #attrs['TestFunc'] = TestFunc
            cls = type.__new__(metacls, name, bases, attrs)
            g_Protocol[attrs["m_ProtocolNumber"]] = cls
            mod = __import__("protocol")
            setattr(mod, "%s_Idx"%(name), attrs["m_ProtocolNumber"])
            return cls
        return type.__new__(metacls, name, bases, attrs)

class VarType(enum.Enum):

    uInt8 = 0
    uInt16 = 1
    uInt32 = 2
    uInt64 = 3
    String = 4

class CProtocol(metaclass = Meta):

    m_ProtocolNumber = 0x0
    m_Define = (
        """
        ("m_TestVal", VarType.uInt8)
        , ("m_TestVal2", VarType.uInt32)
        , ("m_TestString", VarType.String)
        """
    )

    def __init__(self):
        for tInfo in self.m_Define:
            sAttr, attrtype = tInfo
            if VarType.String == attrtype:
                defaultval = ""
            else:
                defaultval = 0
            setattr(self, sAttr, defaultval)

    def PacketData(self):
        sFmt = "=HH"
        args = [self.m_ProtocolNumber,]
        iDataLen = 4
        for sAttr, attrtype in self.m_Define:
            val = getattr(self, sAttr)
            if VarType.String == attrtype:
                iLen = len(val)
                sFmt += "H%ss"%(iLen)
                args.append(iLen)
                args.append(val.encode("utf-8"))
                iDataLen += 2
                iDataLen += iLen
            else:
                if VarType.uInt8 == attrtype:
                    sFmt += "B"
                    iDataLen += 1
                elif VarType.uInt16 == attrtype:
                    sFmt += "H"
                    iDataLen += 2
                elif VarType.uInt32 == attrtype:
                    sFmt += "I"
                    iDataLen += 4
                elif VarType.uInt64 == attrtype:
                    sFmt += "Q"  # only support 64bit platform
                    iDataLen += 8
                args.append(val)
        args.insert(0, iDataLen)
        # 内容数据
        data = struct.pack(sFmt, *args)
        # 包个长度进去
        return data

    def UnpackData(self, data):
        point = 2
        self.m_ProtocolNumber = struct.unpack("H", data[point : point + 2])[0]
        point = 4
        for sAttr, attrtype in self.m_Define:
            if VarType.String == attrtype:
                iLen = struct.unpack("H", data[point : point + 2])[0]
                point += 2
                strval = struct.unpack("%ss"%(iLen), data[point: point + iLen])[0]
                point += iLen
                setattr(self, sAttr, strval.decode('utf-8'))
            else:
                if attrtype == VarType.uInt8:
                    sType, iSize = "B", 1
                elif attrtype == VarType.uInt16:
                    sType, iSize = "H", 2
                elif attrtype == VarType.uInt32:
                    sType, iSize = "I", 4
                elif attrtype == VarType.uInt64:
                    sType, iSize = "Q", 8
                else:
                    raise Exception("Unsupport var type %s"%(attrtype))
                
                iVal = struct.unpack(sType, data[point : point + iSize])[0]
                point += iSize
                setattr(self, sAttr, iVal)

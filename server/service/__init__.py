#encoding: utf-8

if not "g_ServiceCls" in globals():
    g_ServiceCls = {}
    g_ServiceInstance = {}

class ServiceMeta(type):
    # cls 代表动态修改的类
    # name 代表动态修改的类名
    # bases 代表被动态修改的类的所有父类
    # attrs 代表被动态修改的类的所有属性、方法组成的字典
 
    def __new__(metacls, name, bases, attrs):
        if name != "CServiceBase":
            #动态为该类添加一个cal_price方法
            #attrs['TestFunc'] = TestFunc
            cls = type.__new__(metacls, name, bases, attrs)
            g_ServiceCls[attrs["m_Name"]] = cls
            return cls
        return type.__new__(metacls, name, bases, attrs)

class CServiceBase(metaclass = ServiceMeta):
    
    m_Name = "UnkonwService"

    def Init(self):
        self.OnInit()

    # 所有服务都继承于这个基类，初始化时会调用OnInit,尽量别重写Init
    # 如果服务之间有依赖，建议不要在Init时就调用，用定时器延后一下
    def OnInit(self):
        pass

def GetService(sName):
    return g_ServiceInstance.get(sName, None)

def Init():
    for sName, cls in g_ServiceCls.items():
        g_ServiceInstance[sName] = cls()

    for sName, ins in g_ServiceInstance.items():
        ins.Init()
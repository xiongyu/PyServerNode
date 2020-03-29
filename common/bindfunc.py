#encoding: utf-8

class CFuncBinder:

    m_WhiteList = ()
    m_CBFuncs = None

    def On(self, sKey, oCBFunc):
        if self.m_WhiteList and not sKey in self.m_WhiteList:
            raise Exception("Unkonw key %s to bind"%(str(sKey)))
        if None == self.m_CBFuncs:
            self.m_CBFuncs = {}
        self.m_CBFuncs[sKey] = oCBFunc

    def Call(self, sKey, *args):
        if not sKey in self.m_CBFuncs:
            return
        self.m_CBFuncs[sKey](*args)
            

class CFunction:

    def __init__(self, oFunc, *args, **params):
        self.m_Func = oFunc
        self.m_Args = args
        self.m_Params = params

    def __call__(self):
        if not self.m_Func:
            return
        self.m_Func(*self.m_Args, **self.m_Params)

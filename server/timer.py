#encoding: utf-8

import time, bisect

class CTimerManager:

    def __init__(self):
        self.m_Timers = []
        self.m_Mapping = {}

    def GetMTime(self):
        return int(round(time.time() * 1000))

    def Schedule(self, oCBFunc, msec: int, sFlag: str):
        oTimer = CTimer(msec, oCBFunc, sFlag)
        self.AddTimer(oTimer)

    def AddTimer(self, oTimer):
        if oTimer.m_Flag in self.m_Mapping:
            raise Exception("'%s' timer is already exist!"%(oTimer.m_Flag))
        index = bisect.bisect(self.m_Timers, oTimer)
        self.m_Timers.insert(index, oTimer)
        self.m_Mapping[oTimer.m_Flag] = oTimer

    def RemoveTimer(self, sFlag):
        if not sFlag in self.m_Mapping:
            return
        oTimer = self.m_Mapping[sFlag]
        del self.m_Mapping[sFlag]
        self.m_Timers.remove(oTimer)

    def Frame(self):
        oTimeoutList = []
        iMsec = self.GetMTime()
        for oTimer in self.m_Timers:
            if iMsec < oTimer.m_Time:
                break
            oTimeoutList.append(oTimer)
        
        for oTimer in oTimeoutList:
            self.RemoveTimer(oTimer.m_Flag)
            if oTimer.m_CBFunc:
               oTimer.m_CBFunc()

    def Exit(self):
        pass

if not "g_TimerManager" in globals():
    g_TimerManager = CTimerManager()

def Frame():
    g_TimerManager.Frame()

def Schedule(oCBFunc, msec: int, sFlag: str):
    g_TimerManager.Schedule(oCBFunc, msec, sFlag)

def Unschedule(sFlag):
    g_TimerManager.RemoveTimer(sFlag)

class CTimer:

    def __init__(self, msec, oCBFunc, sFlag):
        self.m_CBFunc = oCBFunc
        self.m_Flag = sFlag
        self.m_Time = int(round(time.time() * 1000)) + msec

    # 大于
    def __gt__(self, oTimer):
        if not isinstance(oTimer, CTimer):
            raise TypeError("'>' not supported between instances of 'CTimer' and '%s'"%(type(oTimer)))
        if self.m_Time > oTimer.m_Time:
            return True
        return False

    # 等于
    def __eq__(self, oTimer):
        if not isinstance(oTimer, CTimer):
            raise TypeError("'=' not supported between instances of 'CTimer' and '%s'"%(type(oTimer)))
        if self.m_Time == oTimer.m_Time:
            return True
        return False

    # 大于等于
    def __ge__(self, oTimer):
        if not isinstance(oTimer, CTimer):
            raise TypeError("'<' not supported between instances of 'CTimer' and '%s'"%(type(oTimer)))
        if self.m_Time == oTimer.m_Time:
            return True
        return self.m_Time > oTimer.m_Time or self.m_Time == oTimer.m_Time

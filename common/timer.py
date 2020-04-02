#encoding: utf-8

import bisect
import time

class CTimeManager:

    def __init__(self):
        self.m_TimeDifference = 0
        self.m_Millisecond = 0

    def SetTimeDifference(self, iMillisecond):
        self.m_TimeDifference = iMillisecond

    # 返回时间时要检查下，如果对时， 发现时间快了，要继续当前时间直到超越
    def GetMillisecond(self):
        iMillisecond = int(round(time.time() * 1000))\
             + self.m_TimeDifference
        if self.m_Millisecond >= iMillisecond:
            return self.m_Millisecond
        self.m_Millisecond = iMillisecond
        return iMillisecond

    def GetSecond(self):
        iMillisecond = self.GetMillisecond()
        return int(iMillisecond / 1000.0)
if not 'g_TimeManager' in globals():
    g_TimeManager = CTimeManager()

class CTimerManager:

    def __init__(self):
        self.m_Timers = []
        self.m_Mapping = {}

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
        iMsec = GetMillisecond()
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


class CTimer:

    def __init__(self, msec, oCBFunc, sFlag):
        self.m_CBFunc = oCBFunc
        self.m_Flag = sFlag
        self.m_Time = GetMillisecond() + msec

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


def Frame():
    g_TimerManager.Frame()

def Schedule(oCBFunc, msec: int, sFlag: str):
    g_TimerManager.Schedule(oCBFunc, msec, sFlag)

def Unschedule(sFlag):
    g_TimerManager.RemoveTimer(sFlag)

def GetMillisecond():
    return g_TimeManager.GetMillisecond()

def GetShortMillisecond():
    iMillisecond = GetMillisecond()
    iShortMsecond = iMillisecond - (int(iMillisecond / 1000.0) * 1000)
    return iShortMsecond

def GetSecond():
    return g_TimeManager.GetSecond()

def SetTimeDifference(iMillisecond):
    g_TimeManager.SetTimeDifference(iMillisecond)

def MillisecondSleep(iMillisecond):
    time.sleep(iMillisecond / 1000.0)
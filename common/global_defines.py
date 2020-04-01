#encoding: utf-8

import time

def GetMillisecond():
    a = time.time()
    b = int((a*1000) / 100000000) * 100000000
    c = a * 1000
    d = int(c - b)
    return d

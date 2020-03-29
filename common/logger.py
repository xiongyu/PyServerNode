#encoding: utf-8

import logging

class CLogger:

    def __init__(self):
        logging.basicConfig(level = logging.INFO,format = '[%(asctime)s] %(levelname)s - %(message)s')
        self.m_Logger = logging.getLogger("Log")

    def Info(self, sText):
        self.m_Logger.info(sText)

    def Debug(self, sText):
        self.m_Logger.debug(sText)

    def Warning(self, sText):
        self.m_Logger.warning(sText)


def Init():
    global g_Logger
    if "g_Logger" in globals():
        return
    g_Logger = CLogger()

def Info(sText):
    g_Logger.Info(sText)

def Debug(sText):
    g_Logger.Debug(sText)

def Warning(sText):
    g_Logger.Warning(sText)
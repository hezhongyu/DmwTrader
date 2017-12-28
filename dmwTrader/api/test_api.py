# -*- coding: utf-8 -*-

# @Time    : 2017/12/28 11:23
# @Author  : Zhongyu
# @File    : test_api.py

from dmwTrader.api.ctp.CTPMdApi import CTPMdApi
from dmwTrader.api.ctp.ctpsetting import *
from threading import Lock
import dmwTrader.logger
logger = dmwTrader.logger.getLogger("CTP")


class TestMdApi(object):

    def __init__(self):
        self.__identifiers = ['au1802', 'ag1802']
        self.__ticksDf = {}
        self.__lock = Lock()

    def login(self):
        ctpMdApi = CTPMdApi(self.__identifiers, self.__ticksDf, self.__lock, logger)
        ctpMdApi.login(CTPAPI_MdAddress, CTPAPI_UserID, CTPAPI_Password, CTPAPI_BrokerID)
        ctpMdApi.subscribe(self.__identifiers[0])


if __name__ == '__main__':
    mdapi = TestMdApi()
    mdapi.login()

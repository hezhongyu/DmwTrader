# -*- coding: utf-8 -*-

"""
@author: zhongyu

api模块测试
"""

import time

from dmwTrader.api2.ctp.ctpsetting import *
from dmwTrader.api2.ctp.CTPMdApi import CTPMdApi

import dmwTrader.logger
logger = dmwTrader.logger.getLogger("CTP")
from threading import Lock


def test():
    brokerID = CTPAPI_BrokerID
    userID = CTPAPI_UserID
    password = CTPAPI_Password
    tdAddress = CTPAPI_TdAddress
    mdAddress = CTPAPI_mdAddress

    exchangeID = b'SHFE'
    instrumentID = b'rb1801'
    instruments = ['rb1801']

    ticksDf = {}
    lock = Lock()
    ctpMdApi = CTPMdApi(instruments, ticksDf, lock, logger)
    ctpMdApi.login(CTPAPI_mdAddress, CTPAPI_UserID, CTPAPI_Password, CTPAPI_BrokerID)

    while True:
        if input('enter q exit:') == 'q':
            break
    time.sleep(1.0)
    print('退订行情:', ctpMdApi.UnSubMarketData([instrumentID]))
    # print('账号登出', trader.Logout())
    print('账号登出', ctpMdApi.Logout())


if __name__ == "__main__":
    print('adsf')
    test()

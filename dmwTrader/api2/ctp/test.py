# -*- coding: utf-8 -*-

"""
@author: zhongyu

api模块测试
"""

import time

from dmwTrader.api2.ctp.ctp_setting import *
from dmwTrader.api2.ctp.CTPMdApi import CTPMdApi


def test():
    print('asdf')
    brokerID = CTPAPI_BrokerID
    userID = CTPAPI_UserID
    password = CTPAPI_Password
    tdAddress = CTPAPI_TdAddress
    mdAddress = CTPAPI_mdAddress

    exchangeID = b'SHFE'
    instrumentID = b'rb1801'
    # trader = PyCTP_Trader.CreateFtdcTraderApi(b'_tmp_t_')
    market = CTPMdApi.CreateFtdcMdApi(b'_tmp_m_')

    # print('连接前置', trader.Connect(tdAddress))
    print('连接前置', market.Connect(mdAddress))
    # print('账号登陆', trader.Login(brokerID, userID, password))
    print('账号登陆', market.Login(brokerID, userID, password))
    # print('投资者代码', trader.setInvestorID(userID))

    # time.sleep(1.0)
    # print('查询交易所', trader.QryExchange())
    # time.sleep(1.0)
    # print('查询投资者', trader.QryInvestor())
    # time.sleep(1.0)
    # print('查询资金账户', trader.QryTradingAccount())
    # time.sleep(1.0)
    # print('查询合约', trader.QryInstrument(ExchangeID, InstrumentID))
    # time.sleep(1.0)
    # print('合约手续费率', trader.QryInstrumentCommissionRate(InstrumentID))
    # time.sleep(1.0)
    # print('合约保证金率', trader.QryInstrumentMarginRate(InstrumentID))
    # time.sleep(1.0)
    # print('投资者持仓', trader.QryInvestorPosition())
    # time.sleep(1.0)
    # print('查询行情', trader.QryDepthMarketData(InstrumentID))
    # time.sleep(1.0)
    print('订阅行情:', market.SubMarketData([instrumentID]))

    while True:
        if input('enter q exit:') == 'q':
            break
    time.sleep(1.0)
    print('退订行情:', market.UnSubMarketData([instrumentID]))
    # print('账号登出', trader.Logout())
    print('账号登出', market.Logout())


if __name__ == "__main__":
    print('adsf')
    test()

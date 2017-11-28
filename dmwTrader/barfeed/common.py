# -*- coding: utf-8 -*-

"""
.. modulefrom:: pyalgotrade
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>

revised by Zhongyu
"""


def sanitize_ohlc(open_, high, low, close):
    if low > open_:
        low = open_
    if low > close:
        low = close
    if high < open_:
        high = open_
    if high < close:
        high = close
    return open_, high, low, close

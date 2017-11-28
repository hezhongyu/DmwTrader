# -*- coding: utf-8 -*-

"""
.. modulefrom:: pyalgotrade
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>

revised by Zhongyu
"""

from dmwTrader import technical
from dmwTrader import utils


class RatioEventWindow(technical.EventWindow):
    def __init__(self):
        super(RatioEventWindow, self).__init__(2)

    def getValue(self):
        ret = None
        if self.windowFull():
            prev = self.getValues()[0]
            actual = self.getValues()[-1]
            ret = utils.get_change_percentage(actual, prev)
        return ret


# Calculates the ratio between a value and the previous one.
# The ratio can't be calculated if a previous value is 0.
class Ratio(technical.EventBasedFilter):
    def __init__(self, dataSeries, maxLen=None):
        super(Ratio, self).__init__(dataSeries, RatioEventWindow(), maxLen)

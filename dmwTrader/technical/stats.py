# -*- coding: utf-8 -*-

"""
.. modulefrom:: pyalgotrade
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>

revised by Zhongyu
"""

from DmwTrader import technical


class StdDevEventWindow(technical.EventWindow):
    def __init__(self, period, ddof):
        assert(period > 0)
        super(StdDevEventWindow, self).__init__(period)
        self.__ddof = ddof

    def getValue(self):
        ret = None
        if self.windowFull():
            ret = self.getValues().std(ddof=self.__ddof)
        return ret


class StdDev(technical.EventBasedFilter):
    """Standard deviation filter.

    :param dataSeries: The DataSeries instance being filtered.
    :type dataSeries: :class:`pyalgotrade.dataseries.DataSeries`.
    :param period: The number of values to use to calculate the Standard deviation.
    :type period: int.
    :param ddof: Delta degrees of freedom.
    :type ddof: int.
    :param maxLen: The maximum number of values to hold.
        Once a bounded length is full, when new items are added, a corresponding number of items are discarded from the
        opposite end. If None then dataseries.DEFAULT_MAX_LEN is used.
    :type maxLen: int.
    """

    def __init__(self, dataSeries, period, ddof=0, maxLen=None):
        super(StdDev, self).__init__(dataSeries, StdDevEventWindow(period, ddof), maxLen)


class ZScoreEventWindow(technical.EventWindow):
    def __init__(self, period, ddof):
        assert(period > 1)
        super(ZScoreEventWindow, self).__init__(period)
        self.__ddof = ddof

    def getValue(self):
        ret = None
        if self.windowFull():
            values = self.getValues()
            lastValue = values[-1]
            mean = values.mean()
            std = values.std(ddof=self.__ddof)
            ret = (lastValue - mean) / float(std)
        return ret


class ZScore(technical.EventBasedFilter):
    """Z-Score filter.

    :param dataSeries: The DataSeries instance being filtered.
    :type dataSeries: :class:`pyalgotrade.dataseries.DataSeries`.
    :param period: The number of values to use to calculate the Z-Score.
    :type period: int.
    :param ddof: Delta degrees of freedom to use for the standard deviation.
    :type ddof: int.
    :param maxLen: The maximum number of values to hold.
        Once a bounded length is full, when new items are added, a corresponding number of items are discarded from the
        opposite end. If None then dataseries.DEFAULT_MAX_LEN is used.
    :type maxLen: int.
    """

    def __init__(self, dataSeries, period, ddof=0, maxLen=None):
        super(ZScore, self).__init__(dataSeries, ZScoreEventWindow(period, ddof), maxLen)

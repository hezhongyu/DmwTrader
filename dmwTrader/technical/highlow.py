# -*- coding: utf-8 -*-

"""
.. modulefrom:: pyalgotrade
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>

revised by Zhongyu
"""

from dmwTrader import technical


class HighLowEventWindow(technical.EventWindow):
    def __init__(self, windowSize, useMin):
        super(HighLowEventWindow, self).__init__(windowSize)
        self.__useMin = useMin

    def getValue(self):
        ret = None
        if self.windowFull():
            values = self.getValues()
            if self.__useMin:
                ret = values.min()
            else:
                ret = values.max()
        return ret


class High(technical.EventBasedFilter):
    """This filter calculates the highest value.

    :param dataSeries: The DataSeries instance being filtered.
    :type dataSeries: :class:`pyalgotrade.dataseries.DataSeries`.
    :param period: The number of values to use to calculate the highest value.
    :type period: int.
    :param maxLen: The maximum number of values to hold.
        Once a bounded length is full, when new items are added, a corresponding number of items are discarded from the
        opposite end. If None then dataseries.DEFAULT_MAX_LEN is used.
    :type maxLen: int.
    """

    def __init__(self, dataSeries, period, maxLen=None):
        super(High, self).__init__(dataSeries, HighLowEventWindow(period, False), maxLen)


class Low(technical.EventBasedFilter):
    """This filter calculates the lowest value.

    :param dataSeries: The DataSeries instance being filtered.
    :type dataSeries: :class:`pyalgotrade.dataseries.DataSeries`.
    :param period: The number of values to use to calculate the lowest value.
    :type period: int.
    :param maxLen: The maximum number of values to hold.
        Once a bounded length is full, when new items are added, a corresponding number of items are discarded from the
        opposite end. If None then dataseries.DEFAULT_MAX_LEN is used.
    :type maxLen: int.
    """

    def __init__(self, dataSeries, period, maxLen=None):
        super(Low, self).__init__(dataSeries, HighLowEventWindow(period, True), maxLen)

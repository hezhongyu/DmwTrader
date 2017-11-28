# -*- coding: utf-8 -*-

"""
.. modulefrom:: pyalgotrade
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>

revised by Zhongyu
"""

from dmwTrader import technical


class ROCEventWindow(technical.EventWindow):
    def __init__(self, windowSize):
        super(ROCEventWindow, self).__init__(windowSize)

    def getValue(self):
        ret = None
        if self.windowFull():
            prev = self.getValues()[0]
            actual = self.getValues()[-1]
            if actual is not None and prev is not None:
                diff = float(actual - prev)
                if diff == 0:
                    ret = float(0)
                elif prev != 0:
                    ret = diff / prev
        return ret


class RateOfChange(technical.EventBasedFilter):
    """Rate of change filter as described in http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:rate_of_change_roc_and_momentum.

    :param dataSeries: The DataSeries instance being filtered.
    :type dataSeries: :class:`pyalgotrade.dataseries.DataSeries`.
    :param valuesAgo: The number of values back that a given value will compare to. Must be > 0.
    :type valuesAgo: int.
    :param maxLen: The maximum number of values to hold.
        Once a bounded length is full, when new items are added, a corresponding number of items are discarded from the
        opposite end. If None then dataseries.DEFAULT_MAX_LEN is used.
    :type maxLen: int.
    """

    def __init__(self, dataSeries, valuesAgo, maxLen=None):
        assert(valuesAgo > 0)
        super(RateOfChange, self).__init__(dataSeries, ROCEventWindow(valuesAgo + 1), maxLen)

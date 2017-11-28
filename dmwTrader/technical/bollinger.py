# -*- coding: utf-8 -*-

"""
.. modulefrom:: pyalgotrade
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>

revised by Zhongyu
"""

from DmwTrader import dataseries
from DmwTrader.technical import ma
from DmwTrader.technical import stats


class BollingerBands(object):
    """Bollinger Bands filter as described in http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:bollinger_bands.

    :param dataSeries: The DataSeries instance being filtered.
    :type dataSeries: :class:`pyalgotrade.dataseries.DataSeries`.
    :param period: The number of values to use in the calculation. Must be > 1.
    :type period: int.
    :param numStdDev: The number of standard deviations to use for the upper and lower bands.
    :type numStdDev: int.
    :param maxLen: The maximum number of values to hold.
        Once a bounded length is full, when new items are added, a corresponding number of items are discarded from the
        opposite end. If None then dataseries.DEFAULT_MAX_LEN is used.
    :type maxLen: int.
    """

    def __init__(self, dataSeries, period, numStdDev, maxLen=None):
        self.__sma = ma.SMA(dataSeries, period, maxLen=maxLen)
        self.__stdDev = stats.StdDev(dataSeries, period, maxLen=maxLen)
        self.__upperBand = dataseries.SequenceDataSeries(maxLen)
        self.__lowerBand = dataseries.SequenceDataSeries(maxLen)
        self.__numStdDev = numStdDev
        # It is important to subscribe after sma and stddev since we'll use those values.
        dataSeries.getNewValueEvent().subscribe(self.__onNewValue)

    def __onNewValue(self, dataSeries, dateTime, value):
        upperValue = None
        lowerValue = None

        if value is not None:
            sma = self.__sma[-1]
            if sma is not None:
                stdDev = self.__stdDev[-1]
                upperValue = sma + stdDev * self.__numStdDev
                lowerValue = sma + stdDev * self.__numStdDev * -1

        self.__upperBand.appendWithDateTime(dateTime, upperValue)
        self.__lowerBand.appendWithDateTime(dateTime, lowerValue)

    def getUpperBand(self):
        """
        Returns the upper band as a :class:`pyalgotrade.dataseries.DataSeries`.
        """
        return self.__upperBand

    def getMiddleBand(self):
        """
        Returns the middle band as a :class:`pyalgotrade.dataseries.DataSeries`.
        """
        return self.__sma

    def getLowerBand(self):
        """
        Returns the lower band as a :class:`pyalgotrade.dataseries.DataSeries`.
        """
        return self.__lowerBand

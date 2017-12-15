# -*- coding: utf-8 -*-

"""
.. modulefrom:: pyalgotrade
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>

revised by Zhongyu
"""

from dmwTrader.technical import ma
from dmwTrader import dataseries


class MACD(dataseries.SequenceDataSeries):
    """Moving Average Convergence-Divergence indicator as described in http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:moving_average_convergence_divergence_macd.

    :param dataSeries: The DataSeries instance being filtered.
    :type dataSeries: :class:`pyalgotrade.dataseries.DataSeries`.
    :param fastEMA: The number of values to use to calculate the fast EMA.
    :type fastEMA: int.
    :param slowEMA: The number of values to use to calculate the slow EMA.
    :type slowEMA: int.
    :param signalEMA: The number of values to use to calculate the signal EMA.
    :type signalEMA: int.
    :param maxLen: The maximum number of values to hold.
        Once a bounded length is full, when new items are added, a corresponding number of items are discarded from the
        opposite end. If None then dataseries.DEFAULT_MAX_LEN is used.
    :type maxLen: int.
    """
    def __init__(self, dataSeries, fastEMA=12, slowEMA=26, signalEMA=9, maxLen=None):
        assert(fastEMA > 0)
        assert(slowEMA > 0)
        assert(fastEMA < slowEMA)
        assert(signalEMA > 0)

        super(MACD, self).__init__(maxLen)

        # We need to skip some values when calculating the fast EMA in order for both EMA
        # to calculate their first values at the same time.
        # I'M FORCING THIS BEHAVIOUR ONLY TO MAKE THIS FITLER MATCH TA-Lib MACD VALUES.
        self.__fastEMASkip = slowEMA - fastEMA

        self.__fastEMAWindow = ma.EMAEventWindow(fastEMA)
        self.__slowEMAWindow = ma.EMAEventWindow(slowEMA)
        self.__signalEMAWindow = ma.EMAEventWindow(signalEMA)
        self.__signal = dataseries.SequenceDataSeries(maxLen)
        self.__histogram = dataseries.SequenceDataSeries(maxLen)
        dataSeries.getNewValueEvent().subscribe(self.__onNewValue)

    def getSignal(self):
        """Returns a :class:`pyalgotrade.dataseries.DataSeries` with the EMA over the MACD."""
        return self.__signal

    def getHistogram(self):
        """Returns a :class:`pyalgotrade.dataseries.DataSeries` with the histogram (the difference between the MACD and the Signal)."""
        return self.__histogram

    def __onNewValue(self, dataSeries, dateTime, value):
        diff = None
        macdValue = None
        signalValue = None
        histogramValue = None

        # We need to skip some values when calculating the fast EMA in order for both EMA
        # to calculate their first values at the same time.
        # I'M FORCING THIS BEHAVIOUR ONLY TO MAKE THIS FITLER MATCH TA-Lib MACD VALUES.
        self.__slowEMAWindow.onNewValue(dateTime, value)
        if self.__fastEMASkip > 0:
            self.__fastEMASkip -= 1
        else:
            self.__fastEMAWindow.onNewValue(dateTime, value)
            if self.__fastEMAWindow.windowFull():
                diff = self.__fastEMAWindow.getValue() - self.__slowEMAWindow.getValue()

        # Make the first MACD value available as soon as the first signal value is available.
        # I'M FORCING THIS BEHAVIOUR ONLY TO MAKE THIS FITLER MATCH TA-Lib MACD VALUES.
        self.__signalEMAWindow.onNewValue(dateTime, diff)
        if self.__signalEMAWindow.windowFull():
            macdValue = diff
            signalValue = self.__signalEMAWindow.getValue()
            # histogramValue = macdValue - signalValue
            histogramValue = 2*(macdValue - signalValue)

        self.appendWithDateTime(dateTime, macdValue)
        self.__signal.appendWithDateTime(dateTime, signalValue)
        self.__histogram.appendWithDateTime(dateTime, histogramValue)

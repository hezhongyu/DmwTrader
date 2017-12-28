# -*- coding: utf-8 -*-

"""
.. modulefrom:: pyalgotrade
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>
.. modified by: Zhongyu
"""


class Database(object):
    def addBars(self, bars, frequency):
        for instrument in bars.getInstruments():
            bar = bars.getBar(instrument)
            self.addBar(instrument, bar, frequency)

    def addBarsFromFeed(self, feed):
        for dateTime, bars in feed:
            if bars:
                self.addBars(bars, feed.getFrequency())

    def addBar(self, instrument, bar, frequency):
        raise NotImplementedError()

    def getBars(self, instrument, frequency, timezone=None, fromDateTime=None, toDateTime=None):
        raise NotImplementedError()

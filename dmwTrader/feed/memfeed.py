# -*- coding: utf-8 -*-

"""
.. modulefrom:: pyalgotrade
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>

revised by Zhongyu
"""

from DmwTrader import feed
from DmwTrader import dataseries


class MemFeed(feed.BaseFeed):
    def __init__(self, maxLen=None):
        super(MemFeed, self).__init__(maxLen)

        self.__values = []
        self.__nextIdx = 0

    def reset(self):
        self.__nextIdx = 0
        feed.BaseFeed.reset(self)

    def start(self):
        super(MemFeed, self).start()
        # Now that all the data is in place, sort it to dispatch it in order.
        self.__values.sort(key=lambda x: x[0])

    def stop(self):
        pass

    def join(self):
        pass

    def eof(self):
        if self.__nextIdx < len(self.__values):
            return False
        else:
            return True

    def peekDateTime(self):
        ret = None
        if self.__nextIdx < len(self.__values):
            ret = self.__values[self.__nextIdx][0]
        return ret

    def createDataSeries(self, key, maxLen):
        return dataseries.SequenceDataSeries(maxLen)

    def getNextValues(self):
        ret = (None, None)
        if self.__nextIdx < len(self.__values):
            ret = self.__values[self.__nextIdx]
            self.__nextIdx += 1
        return ret

    # Add values to the feed. values should be a sequence of tuples. The tuples should have two elements:
    # 1: datetime.datetime.
    # 2: dictionary or dict-like object.
    def addValues(self, values):
        # Register a dataseries for each item.
        for key in values[0][1].keys():
            self.registerDataSeries(key)

        self.__values.extend(values)

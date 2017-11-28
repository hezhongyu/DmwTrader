# -*- coding: utf-8 -*-

"""
.. modulefrom:: pyalgotrade
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>

revised by Zhongyu
"""

from DmwTrader import barfeed
from DmwTrader import bar
from DmwTrader import utils


# A non real-time BarFeed responsible for:
# - Holding bars in memory.
# - Aligning them with respect to time.
#
# Subclasses should:
# - Forward the call to start() if they override it.

class BarFeed(barfeed.BaseBarFeed):
    def __init__(self, frequency, maxLen=None):
        super(BarFeed, self).__init__(frequency, maxLen)

        self.__bars = {}
        self.__nextPos = {}
        self.__started = False
        self.__currDateTime = None

    def reset(self):
        self.__nextPos = {}
        for instrument in self.__bars.keys():
            self.__nextPos.setdefault(instrument, 0)
        self.__currDateTime = None
        super(BarFeed, self).reset()

    def getCurrentDateTime(self):
        return self.__currDateTime

    def start(self):
        super(BarFeed, self).start()
        self.__started = True

    def stop(self):
        pass

    def join(self):
        pass

    def addBarsFromSequence(self, instrument, bars):
        if self.__started:
            raise Exception("Can't add more bars once you started consuming bars")

        self.__bars.setdefault(instrument, [])
        self.__nextPos.setdefault(instrument, 0)

        # Add and sort the bars
        self.__bars[instrument].extend(bars)
        # py2 to 3 修改
        # barCmp = lambda x, y: cmp(x.getDateTime(), y.getDateTime())
        # self.__bars[instrument].sort(barCmp)
        self.__bars[instrument].sort(key=lambda x: x.getDateTime())

        self.registerInstrument(instrument)

    def eof(self):
        ret = True
        # Check if there is at least one more bar to return.
        for instrument, bars in self.__bars.items():
            nextPos = self.__nextPos[instrument]
            if nextPos < len(bars):
                ret = False
                break
        return ret

    def peekDateTime(self):
        ret = None

        for instrument, bars in self.__bars.items():
            nextPos = self.__nextPos[instrument]
            if nextPos < len(bars):
                ret = utils.safe_min(ret, bars[nextPos].getDateTime())
        return ret

    def getNextBars(self):
        # All bars must have the same datetime. We will return all the ones with the smallest datetime.
        smallestDateTime = self.peekDateTime()

        if smallestDateTime is None:
            return None

        # Make a second pass to get all the bars that had the smallest datetime.
        ret = {}
        for instrument, bars in self.__bars.items():
            nextPos = self.__nextPos[instrument]
            if nextPos < len(bars) and bars[nextPos].getDateTime() == smallestDateTime:
                ret[instrument] = bars[nextPos]
                self.__nextPos[instrument] += 1

        if self.__currDateTime == smallestDateTime:
            raise Exception("Duplicate bars found for %s on %s" % (ret.keys(), smallestDateTime))

        self.__currDateTime = smallestDateTime
        return bar.Bars(ret)

    def loadAll(self):
        for dateTime, bars in self:
            pass
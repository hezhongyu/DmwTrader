#coding:utf-8

"""
.. modulefrom:: vnpy & potato
.. moduleauthor:: ZackZK <silajoin@sina.com>
.. modifyauthor:: Zhongyu
"""

import queue

import pytz

from dmwTrader.api.ctp.CTPMdApi import CTPMdApi
from dmwTrader.api.ctp.ctpsetting import *

from dmwTrader.barfeed import bar
from dmwTrader import barfeed
from dmwTrader import resamplebase
from dmwTrader.utils import dt
from dmwTrader.xignite.barfeed import PollingThread, utcnow

from threading import Lock

from pandas import DataFrame

import dmwTrader.logger
logger = dmwTrader.logger.getLogger("CTP")


def to_market_datetime(dateTime):
    timezone = pytz.timezone('Asia/Shanghai')
    return dt.localize(dateTime, timezone)


class GetBarThread(PollingThread):
    # Events
    ON_BARS = 1

    def __init__(self, queue, identifiers, frequency):
        super(GetBarThread, self).__init__()

        self.__queue = queue
        self.__identifiers = identifiers
        self.__frequency = frequency
        self.__nextBarStart = None
        self.__nextBarClose = None
        self._ticksDf = {}
        self.__lock = Lock()

        for identifier in self.__identifiers:
            self._ticksDf[identifier] = DataFrame(columns=['time', 'price', 'volume', 'amount'])

        self._ctpMdApi = CTPMdApi(self.__identifiers, self._ticksDf, self.__lock, logger)
        self._ctpMdApi.login(CTPAPI_MdAddress, CTPAPI_UserID, CTPAPI_Password, CTPAPI_BrokerID)
        self.__updateNextBarClose()

    def __updateNextBarClose(self):
        self.__nextBarStart = resamplebase.build_range(utcnow(), self.__frequency).getBeginning()
        self.__nextBarClose = resamplebase.build_range(utcnow(), self.__frequency).getEnding()

    def getNextCallDateTime(self):
        return self.__nextBarClose

    def doCall(self):
        startDateTime = to_market_datetime(self.__nextBarStart)
        endDateTime = to_market_datetime(self.__nextBarClose)
        self.__updateNextBarClose()
        barDict = dict()

        for identifier in self.__identifiers:
            try:
                period_bar = self._build_bar(identifier, startDateTime, endDateTime)
                if period_bar:
                    barDict[identifier] = period_bar

            except Exception as e:
                logger.error(e)

        if len(barDict):
            bars = bar.Bars(barDict)
            self.__queue.put((GetBarThread.ON_BARS, bars))

    def _build_bar(self, identifier, start, end):

        df = self._ticksDf[identifier]

        ticks_slice = df.ix[(df.time < end.strftime("%H:%M:%S")) &
                            (df.time >= start.strftime("%H:%M:%S"))]

        if not ticks_slice.empty:
            open_ = ticks_slice.price.get_values()[0]
            high = max(ticks_slice.price)
            low = min(ticks_slice.price)
            close = ticks_slice.price.get_values()[-1]
            volume = sum(ticks_slice.volume)
            amount = sum(ticks_slice.amount)

            return bar.BasicBar(to_market_datetime(start), open_, high, low, close, volume,
                                amount, self.__frequency, {})
        else:
            return None


class CTPLiveFeed(barfeed.BaseBarFeed):
    QUEUE_TIMEOUT = 0.01

    def __init__(self, identifiers, frequency):
        super(CTPLiveFeed, self).__init__(frequency)
        if not isinstance(identifiers, list):
            raise Exception("identifiers must be a list")

        self.__identifiers = identifiers
        self.__queue = queue.Queue()
        self._thread = GetBarThread(self.__queue, identifiers, frequency)
        for instrument in identifiers:
            self.registerInstrument(instrument)

    ######################################################################
    # observer.Subject interface

    def start(self):
        if self._thread.is_alive():
            raise Exception("Already strated")

        # Start the thread that runs the client.
        self._thread.start()

    def stop(self):
        self._thread.stop()

    def join(self):
        if self._thread.is_alive():
            self._thread.join()

    def eof(self):
        return self._thread.stopped()

    def peekDateTime(self):
        return None

    ######################################################################
    # barfeed.BaseBarFeed interface

    def getCurrentDateTime(self):
        return utcnow()

    def barsHaveAdjClose(self):
        return False

    def getNextBars(self):
        ret = None
        try:
            eventType, eventData = self.__queue.get(True, CTPLiveFeed.QUEUE_TIMEOUT)
            if eventType == GetBarThread.ON_BARS:
                ret = eventData
            else:
                logger.error("Invalid event received: %s - %s" % (eventType, eventData))
        except queue.Empty:
            pass
        return ret
        
        
def test_feed():
    feed = CTPLiveFeed(['au1802', 'ag1802'], 30)
    feed.start()
    while True:
        bars = feed.getNextBars()
        if bars:
            b = bars.getBar('au1802')
            if b:
                print('__________________au__________________')
                print('time', b.getDateTime(), 'open:',b.getOpen(),  'high:', b.getHigh(), ' low: ', b.getLow(), \
                    'close: ', b.getClose(), 'volume:', b.getVolume(), 'amount:', b.getAmount())
            b = bars.getBar('ag1802')
            if b:
                print('__________________ag__________________')
                print('time', b.getDateTime(), 'open:',b.getOpen(),  'high:', b.getHigh(), ' low: ', b.getLow(), \
                    'close: ', b.getClose(), 'volume:', b.getVolume(), 'amount:', b.getAmount())


if __name__ == '__main__':
    test_feed()
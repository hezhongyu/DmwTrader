# -*- coding: utf-8 -*-

from dmwTrader import strategy
from dmwTrader.barfeed import tbfeed
from dmwTrader.technical import ma, macd


class myStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument):
        super(myStrategy, self).__init__(feed, 100000)
        self.__position = None
        self.__instrument = instrument
        self.__sma5 = ma.SMA(feed[instrument].getPriceDataSeries(), 5)
        self.__sma30 = ma.SMA(feed[instrument].getPriceDataSeries(), 30)
        self.__macd = macd.MACD(feed[instrument].getPriceDataSeries(), 12, 26, 9)

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info("BUY at $%.2f" % (execInfo.getPrice()))

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info("SELL at $%.2f" % (execInfo.getPrice()))
        self.__position = None

    def onBars(self, bars):
        # Wait for enough bars to be available to calculate a SMA.
        if self.__sma5[-1] is None or self.__sma30[-1] is None:
            return

        bar = bars[self.__instrument]
        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if self.__sma5[-1] >= self.__sma30[-1]:
                # Enter a buy market order for 10 shares. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, 10, True)
        # Check if we have to exit the position.
        elif self.__sma5[-1] < self.__sma30[-1] and not self.__position.exitActive():
            self.__position.exitMarket()


def run_strategy():
    feed = tbfeed.Feed()
    feed.addBarsFromCSV("IF", "../data/IF主力连续.csv")

    stra = myStrategy(feed, "IF")
    stra.run()
    print("Final portfolio value: $%.2f" % stra.getBroker().getEquity())

run_strategy()
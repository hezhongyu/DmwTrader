# -*- coding: utf-8 -*-

import datetime
from dmwTrader import strategy
from dmwTrader.barfeed import tbfeed
from dmwTrader.technical import macd


class myStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument):
        super(myStrategy, self).__init__(feed, 100000)
        self.__position = None
        self.__instrument = instrument
        self.__macd = macd.MACD(feed[instrument].getPriceDataSeries())


    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info("BUY at $%.2f" % (execInfo.getPrice()))

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info("SELL at $%.2f" % (execInfo.getPrice()))
        self.__position = None

    def onBars(self, bars):
        bar = bars[self.__instrument]
        # If a position was not opened, check if we should enter a long position.
        if self.__macd[-1] is None:
            return

        time = bar.getDateTime()
        if time >= datetime.datetime(2017, 9, 1) and time <= datetime.datetime(2017, 9, 2):
            print(time)
            print("macd:" + str(self.__macd.getHistogram()[-1]))
        if self.__position is None:
            if self.__macd.getHistogram()[-1] > 0:
                # Enter a buy market order for 10 shares. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, 10, True)
        # Check if we have to exit the position.
        elif self.__macd.getHistogram()[-1] < 0 and not self.__position.exitActive():
            self.__position.exitMarket()


def run_strategy():
    feed = tbfeed.Feed()
    feed.addBarsFromCSV("IF", "../data/IF主力连续.csv")

    stra = myStrategy(feed, "IF")
    stra.run()
    print("Final portfolio value: $%.2f" % stra.getBroker().getEquity())

run_strategy()
# -*- coding: utf-8 -*-

"""
.. modulefrom:: pyalgotrade and pyalgotrade-cn
.. moduleauthor:: Gabriel Martin Becedillas Ruiz <gabriel.becedillas@gmail.com>
.. modified by: James Ge(james.ge@gmail.com)
.. second modified by: Zhongyu
"""

import time
import queue
from datetime import datetime
from dmwTrader import broker
from dmwTrader.logger import getLogger
from dmwTrader.api.ctp import CTPTdApi
from components.database.mongo import *
from components.celery.tasks import *
from components.celery.tasksmgmt import *

logger = getLogger('CTP_broker')

class FutureTraits(broker.InstrumentTraits):
    def roundQuantity(self, quantity):
        return round(quantity, 2)

    def getCommission(self, instrument_id):
        return 0


class LiveBroker(broker.Broker):
    """A CTP live broker.

    .. note::
        * Only limit orders are supported.
        * Orders are automatically set as **goodTillCanceled=True** and  **allOrNone=False**.
        * BUY_TO_COVER orders are mapped to BUY orders.
        * SELL_SHORT orders are mapped to SELL orders.
        * API access permissions should include:

          * Account balance
          * send order
          * Cancel order
    """

    QUEUE_TIMEOUT = 0.01

    ##TODO: need a margin value dict to calculate if there is enough cash for orders
    def __init__(self, userid):
        broker.Broker.__init__(self)
        self.__userid = userid
        self.__stop = False
        self.__cash_available = 0
        self.__margin = 0
        self.__cash_frozen = 0

        self.__positions = {}
        self.__activeOrders = {}
        self.__TradeDetailDB = mongo_db(collection = "trade_detail")
        self.__AccountInfoDB = mongo_db(collection = "account_info")
        self.__StrategyInfoDB = mongo_db(collection = "strategy_info")
        #self.__CyclThread = Thread(target=self.refreshInfo)

    def login(self, timeout=10):
        account_info = mongo_db('ctp_account')
        userid = self.__userid
        if userid is None:
                raise Exception('userid not found')

        address = "tcp://" + str(account_info.read({"userid":userid})['address']) + ":" + str(account_info.read({"userid":userid})['port'])
        password = str(account_info.read({"userid":userid})['password'])
        brokerid = str(account_info.read({"userid":userid})['brokerid'])

        self.__msg_queue = queue.Queue()
        self.__api = CTPTdApi.CTPTdApi(self.__msg_queue)
        self.__api.connect(userid, password, brokerid, address)

        ##check if login successed
        t1 = time.time()
        while True:
            #print api.loginStatus
            if self.__api.loginStatus:
                logger.info('login successful')
                break

            elif time.time() - t1 >= timeout:
                logger.info('login timeout')
                break

        # Store the last trade id since we'll start processing new ones only.
        old_messages = []
        while self.__msg_queue.qsize() > 0:
            old_messages.append(self.__queue.get())
            logger.info("%d msg found before starting broker" % (self.__lastTradeId))


    def _registerOrder(self, order):
        assert(order.getId() not in self.__activeOrders)
        assert(order.getId() is not None)
        self.__activeOrders[order.getId()] = order

    def _unregisterOrder(self, order):
        assert(order.getId() in self.__activeOrders)
        assert(order.getId() is not None)
        del self.__activeOrders[order.getId()]

    def refreshInfo(self):
        pass

    def refreshAccountBalance(self, msg_dict):
        """Refreshes cash and account balance."""
        # logger.info("updating account balance.")
        # Cash
        doc = {'dyn_right': msg_dict['balance'],
               'cash_frozen': msg_dict['cash_frozen'],
               'cash_avalible': msg_dict['cash_available'],
               'asset': msg_dict['margin']},

        self.__AccountInfoDB.update({'aaccount_id':self.__userid}, doc, upsert=True)

    def refreshStrategInfo(self, strategy_info_dict):
        """Refreshes Strategy info"""
        doc = {'position_profit': strategy_info_dict['close_profit'],  #持仓盈亏
               'strategy_profit': None,
               'position_lot': strategy_info_dict['position']}

        self.__StrategyInfoDB.update({'strategy_id':find_strategy(get_task_id())}, doc, upsert=True)


    def _onUserTrades(self, msg_dict):
        print("_onUserTrades")
        order = self.__activeOrders.get(msg_dict['order_id'])
        if order is not None:
            commision = self.getInstrumentTraits().getCommission(msg_dict['instrument_id'])
            fill_price = msg_dict['price']
            volume = msg_dict['volume']
            datetime = msg_dict['datetime']

            # Update the order.
            orderExecutionInfo = broker.OrderExecutionInfo(fill_price, abs(volume), commision, datetime)
            order.addExecutionInfo(orderExecutionInfo)
            if not order.isActive():
                self._unregisterOrder(order)
            # Notify that the order was updated.
            if order.isFilled():
                eventType = broker.OrderEvent.Type.FILLED
            else:
                eventType = broker.OrderEvent.Type.PARTIALLY_FILLED
            self.notifyOrderEvent(broker.OrderEvent(order, eventType, orderExecutionInfo))

            print(msg_dict)
            self.__TradeDetailDB.update({'strategy_id':find_strategy(get_task_id())}, msg_dict, upsert=True)

            # Update cash and shares.
            self.__api.qryAccount()

            # Update position.
            self.__api.qryPosition()

        else:
            logger.info("Trade %d refered to order %d that is not active" % (int(msg_dict['trade_id']), int(msg_dict['order_id'])))


    def _onOrderAction(self, msg_dict):
        order = self.__activeOrders.get(msg_dict['order_id'])
        if msg_dict['action'] == 'canceled':
            self._unregisterOrder(order)
            order.switchState(broker.Order.State.CANCELED)

            # Notify that the order was canceled.
            self.notifyOrderEvent(broker.OrderEvent(order, broker.OrderEvent.Type.CANCELED, "User requested cancellation"))

            # Update cash and shares.
            self.__api.qryAccount()

            # Update position.
            self.__api.qryPosition()


    # BEGIN observer.Subject interface
    def start(self):
        #self.refreshAccountBalance()
        #self.refreshOpenOrders()
        self.login()
        pass

    def stop(self):
        self.__stop = True
        logger.info("Shutting down trade monitor.")
        #self.__tradeMonitor.stop()

    def join(self):
        pass

    def eof(self):
        return self.__stop

    def dispatch(self):
        # Switch orders from SUBMITTED to ACCEPTED.
        ordersToProcess = self.__activeOrders.values()
        for order in ordersToProcess:
            if order.isSubmitted():
                order.switchState(broker.Order.State.ACCEPTED)
                self.notifyOrderEvent(broker.OrderEvent(order, broker.OrderEvent.Type.ACCEPTED, None))

        # Dispatch events from the trade monitor.
        while self.__msg_queue.qsize() > 0:
            msg = self.__msg_queue.get(True, LiveBroker.QUEUE_TIMEOUT)

            if msg['event_type'] == CTPTdApi.EventType.ON_TRADE:
                self._onUserTrades(msg)
            elif msg['event_type'] == CTPTdApi.EventType.ON_QUERY_ACCOUNT:
                self.refreshAccountBalance(msg)
            elif msg['event_type'] == CTPTdApi.EventType.ON_ORDER_ACTION:
                self._onOrderAction(msg)
            elif msg['event_type'] == CTPTdApi.EventType.ON_QUERY_POSITION:
                self.refreshStrategInfo(msg)
            else:
                pass


    def peekDateTime(self):
        # Return None since this is a realtime subject.
        return None

    # END observer.Subject interface

    # BEGIN broker.Broker interface

    def getShares(self, instrument_id):
        return self.__positions[instrument_id]


    def getCash(self, includeShort=True):
        return self.__cash_available


    def getInstrument(self, instrument):
        return self.__positions.get(instrument, 0)


    def getPositions(self):
        return self.__positions


    def getActiveOrders(self, instrument=None):
        return self.__activeOrders.values()


    def getInstrumentTraits(self):
        return FutureTraits()


    def submitOrder(self, order):
        if order.isInitial():
            # Override user settings based on Bitstamp limitations.
            order.setAllOrNone(False)
            order.setGoodTillCanceled(True)

            order_ref = self.__api.sendOrder(order.getInstrument(), order.getAction(),\
                                     order.getLimitPrice(), int(order.getQuantity()))
            order.setSubmitted(order_ref, datetime.now())
            self._registerOrder(order)
            # Switch from INITIAL -> SUBMITTED
            # IMPORTANT: Do not emit an event for this switch because when using the position interface
            # the order is not yet mapped to the position and Position.onOrderUpdated will get called.
            order.switchState(broker.Order.State.SUBMITTED)
        else:
            raise Exception("The order was already processed")


    def createMarketOrder(self, action, instrument, quantity, onClose=False):
        raise Exception("Market orders are not supported")


    def createLimitOrder(self, action, instrument, limitPrice, quantity):
        instrumentTraits = self.getInstrumentTraits()
        limitPrice = round(limitPrice, 2)
        quantity = instrumentTraits.roundQuantity(quantity)
        return broker.LimitOrder(action, instrument, limitPrice, quantity, instrumentTraits)


    def createStopOrder(self, action, instrument, stopPrice, quantity):
        raise Exception("Stop orders are not supported")


    def createStopLimitOrder(self, action, instrument, stopPrice, limitPrice, quantity):
        raise Exception("Stop limit orders are not supported")


    def cancelOrder(self, order):
        activeOrder = self.__activeOrders.get(order.getId())
        if activeOrder is None:
            raise Exception("The order is not active anymore")
        if activeOrder.isFilled():
            raise Exception("Can't cancel order that has already been filled")


        self.__api.cancelOrder(order.getInstrument(), str(order.getId()))


    def queryPosition(self, order):
        self.__api.qryPosition()


    def queryAccount(self):
        self.__api.qryAccount()


    # END broker.Broker interface



if __name__ == '__main__':
    pass
    #test_limit_order()
    #test_cancel_order()

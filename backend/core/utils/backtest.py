from datetime import datetime, time
import backtrader as bt
import matplotlib.pyplot as plt
import argparse
import collections
import datetime
import quantstats

from core.utils import load_data_db


class MLIndicator(bt.Strategy):
    # list of parameters which are configurable for the strategy
    params = dict(
        pfast=5,  # period for the fast moving average
        pslow=15   # period for the slow moving average
    )

    def __init__(self):
        self.idx = 0 
        self.signal = self.data.signal

    def log(self, txt, dt=None):
        # Logging function for the strategy.  'txt' is the statement and 'dt' can be used to specify a specific datetime
        dt = dt or self.datas[0].datetime.date(0)
        print('{0},{1}'.format(dt.isoformat(), txt))
 
    def notify_order(self, order):
        # 1. If order is submitted/accepted, do nothing
        if order.status in [order.Submitted, order.Accepted]:
            return
        # 2. If order is buy/sell executed, report price executed
        if order.status in [order.Completed]:
            if order.isbuy():
                # self.log('BUY EXECUTED , SIZE {0:8.2f}, Price: {0:8.2f}, Cost: {1:8.2f}, Comm: {2:8.2f}'.format(
                #     order.size, 
                #     order.executed.price,
                #     order.executed.value,
                #     order.executed.comm))
 
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                # self.log('SELL EXECUTED, SIZE {0:8.2f}, Cost: {1:8.2f}, Comm{2:8.2f}'.format(
                #     order.size,
                #     order.executed.price,
                #     order.executed.value,
                #     order.executed.comm))
                pass
            self.bar_executed = len(self)  # when was trade executed
        # 3. If order is canceled/margin/rejected, report order canceled
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        else:
          self.log('Other')
        self.order = None
 
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
 
        self.log('OPERATION PROFIT,  GROSS {0:8.2f}, NET {1:8.2f}'.format(
            trade.pnl, trade.pnlcomm))

    def next(self):
        price = self.datas[0].close[-1]
        self.idx += 1
        if self.order:  # check if order is pending, if so, then break out
            return
        # if not self.position: 
        #   # Compute number of shares we can buy 
        #   value = self.broker.getvalue()
        #   size = int(value/(price*1.01))
        #   self.buy(size=size, exectype=bt.Order.Market)
        signal = self.signal[0]
        if signal < 0.5 and  self.position: 
            self.close(size=self.position.size)

        if signal > 0.5:  # if fast crosses slow to the upside
            if not self.position and not self.order:
              print("Buying", self.datas[0].datetime.date(0))
              value = self.broker.cash
              print(value, price)
              size = int(value/(price*1.1)) 
              print(size)
              self.buy(size=size, exectype=bt.Order.Market)  # enter long


    def stop(self):
      self.close(size=self.position.size)


def backtest_strategy(stock, res, strategy, start_date=None, end_date=None):
    load_data_db(stock=stock, res=res)
    # Load Strategy Model 
    cerebro = bt.Cerebro()
    cerebro.addstrategy(SmaCross)

    data0 = bt.feeds.GenericCSVData(
        dataname="fin.csv",
        nullvalue=0.0,
        dtformat=('%Y-%m-%d %H:%M:%S'),
        timeframe=bt.TimeFrame.Minutes)
    cerebro.broker.setcash(100000)

    cerebro.adddata(data0)
    cerebro.addanalyzer(bt.analyzers.PyFolio)
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)



    res = cerebro.run()
    strat = res[0]
    pyfoliozer = strat.analyzers.getbyname('pyfolio')
    returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()

    returns.index = returns.index.astype('datetime64[ns]')
    quantstats.reports.full(returns)


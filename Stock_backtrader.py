#------------------------
#
# NAME:		Stock_backtrader.py
#
# CREATED: 	11.26.2021 - dserke
#
# EDITS:	11.26.2021, implemented first two strategies from:
#			https://analyzingalpha.com/backtrader-backtesting-trading-strategies
#			The third (Conners RSI) is more complex and requires creation importation 
#			of an equities database.
#               12.11.2021, implemented all of:
#               	https://www.backtrader.com/docu/quickstart/quickstart/
#
#
#
#
#------------------------

#------------------------
# import libraries
#------------------------
import pandas
import requests
import backtrader       as     bt
import yfinance         as     yf
import sqlalchemy
from   datetime         import datetime
import pandas           as     pd
import matplotlib
from   matplotlib       import warnings
from   matplotlib.dates import (HOURS_PER_DAY, MIN_PER_HOUR, SEC_PER_MIN,
                              MONTHS_PER_YEAR, DAYS_PER_WEEK,
                              SEC_PER_HOUR, SEC_PER_DAY,
                              num2date, rrulewrapper, YearLocator,
                              MicrosecondLocator)
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import datetime                                # For datetime objects
import os.path                                 # To manage paths
import sys                                     # To find out the script name (in argv[0])
import warnings
warnings.filterwarnings('ignore')

#------------------------
# define constants
#------------------------
# ... money values
value_start_usd = 100000.00
comm_usd        =     0.001
# ... stock values
#ticker          = 'AAPL'
#ticker          = 'TSLA'
ticker          = 'BTC-USD'
share_tranche    =  1
# ... date values
yyyymmdd_start  = '2013-01-01'
yyyymmdd_end    = '2020-10-30'

#------------------------
# 4. Create the strategy
#------------------------
class SmaCross(bt.SignalStrategy):

    # 4a. Initiation
    def __init__(self): 
      
        # 4b. Pre-Processing 
        sma1, sma2 = bt.ind.SMA(period=10), bt.ind.SMA(period=20)
        crossover  = bt.ind.CrossOver(sma1, sma2)
        self.signal_add(bt.SIGNAL_LONG, crossover)

    ## 4c. Processing
    #def next(self):  
    #    if self.sma > self.data.close:
    #        # Do something
    #        pass

    #    # 4d. Post-processing
    #    elif self.sma < self.data.close: 
    #        # Do something else
    #        pass

class DonchianChannels(bt.Indicator):
    '''
    Params Note:
      - `lookback` (default: -1)
        If `-1`, the bars to consider will start 1 bar in the past and the
        current high/low may break through the channel.
        If `0`, the current prices will be considered for the Donchian
        Channel. This means that the price will **NEVER** break through the
        upper/lower channel bands.
    ''' 
    
    alias     = ('DCH', 'DonchianChannel',)
    lines     = ('dcm', 'dch', 'dcl',)        # dc middle, dc high, dc low
    params    = dict(period=20, lookback=-1)  # consider current bar or not
    plotinfo  = dict(subplot=False)           # plot along with data
    plotlines = dict(
        dcm=dict(ls='--'),                    # dashed line
        dch=dict(_samecolor=True),            # use same color as prev line (dcm)
        dcl=dict(_samecolor=True),            # use same color as prev line (dch)
    )
    
    def __init__(self):
        hi, lo     = self.data.high, self.data.low
        if self.p.lookback:  # move backwards as needed
            hi, lo = hi(self.p.lookback), lo(self.p.lookback)
        self.l.dch = bt.ind.Highest(hi, period=self.p.period)
        self.l.dcl = bt.ind.Lowest(lo, period=self.p.period)
        self.l.dcm = (self.l.dch + self.l.dcl) / 2.0  # avg of the above
  
class MyStrategy(bt.Strategy):
    params = (('printlog', 'TRUE'), 
              ('exitbars',      5), 
              ('size',         10))
    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        if self.params.printlog or doprint:
            dt             = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))
    def __init__(self):
        self.myind     = DonchianChannels()
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        # Keep track of pending orders
        self.order     = None  
        self.buyprice  = None
        self.buycomm   = None
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return
        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Size: %.3f, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (self.params.size,
		     order.executed.price,
                     order.executed.value,
                     order.executed.comm))
                self.buyprice = order.executed.price
                self.buycomm  = order.executed.comm 
            else: # Sell
                self.log('SELL EXECUTED, Size: %.3f, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (self.params.size,
                          order.executed.price,
                          order.executed.value,
                          order.executed.comm))
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        # Write down: no pending order
        self.order = None     
    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))       
    def next(self):
        # log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])
        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return
        # Check if we are in the market....
        # ... ANSWER is Not yet ...
        if not self.position:
            # BUY, if statement is true...
            if self.data[0] > self.myind.dch[0]:
                # BUY, with default params
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
        # ... ANSWER is yes ...
        else:
            # SELL, if statement is true...
            #if len(self) >= (self.bar_executed + self.params.exitbars):
            if self.data[0] < self.myind.dcl[0]:
                # SELL, with default params
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.sell()

if __name__ == '__main__':
    #------------------------
    # 1. Initialize the engine
    #------------------------
    cerebro = bt.Cerebro()   
    #------------------------
    # 2. Configure the broker
    #------------------------
    #cerebro.addstrategy(SmaCross)
    cerebro.addstrategy(MyStrategy)
    cerebro.broker.setcash(value_start_usd)
    cerebro.broker.setcommission(commission = comm_usd)    
    #------------------------
    # 3. Add the data
    #------------------------
    # ... pick one of these load methods
    # ...... import YF pandas DF into BT format
    data                       = bt.feeds.PandasData(dataname=yf.download(ticker, yyyymmdd_start, yyyymmdd_end))
    data.plotinfo.plotlog      = 'True'
    data.plotinfo.plotylimited = 'FALSE'
    # ...... import YF datafeed into BT format
    #data = bt.feeds.YahooFinanceData(dataname   = 'AAPL',
    #                                 fromdate   = datetime(2017, 1, 1),
    #                                 todate     = datetime(2020, 12, 31))
    #data = bt.feeds.YahooFinanceCSVData(dataname = 'yahoo_finance_aapl.csv')   
    cerebro.adddata(data)  
    # Add a FixedSize sizer according to the stake
    cerebro.addsizer(bt.sizers.FixedSize, stake = share_tranche)
    #------------------------
    # 5. Analyze the performance
    #------------------------
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    #------------------------
    # 6. Plot the performance
    #------------------------
    cerebro.plot(iplot = False)
    #cerebro.plot()

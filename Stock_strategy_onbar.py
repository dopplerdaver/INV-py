#------------------------------------------------------
#
# NAME: 	Stock_strategy_onbar.py
#
# PURPOSE:	strategy plotter
#		1. Declaring a new strategy. There is only one method that has to be defined, onBars, which is called for every bar in the feed.
#		2. Loading the feed from a CSV file or dataframe
#		3. Running the strategy with the bars supplied by the feed.
#
# CREATED:	11.12.2021 - dserke
#
# SOURCE:	http://gbeced.github.io/pyalgotrade/docs/v0.20/html/tutorial.html
#
#------------------------------------------------------

#------------------------------------------------------
# IMPORT LIBRARIES
#------------------------------------------------------
from pyalgotrade import strategy
from pyalgotrade.barfeed import quandlfeed

class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument):
        super(MyStrategy, self).__init__(feed)
        self.__instrument = instrument

    def onBars(self, bars):
        bar = bars[self.__instrument]
        self.info(bar.getClose())

# Load the bar feed from the CSV file
feed = quandlfeed.Feed()
feed.addBarsFromCSV("orcl", "WIKI-ORCL-2000-quandl.csv")

# Evaluate the strategy with the feed's bars.
myStrategy = MyStrategy(feed, "orcl")
myStrategy.run()
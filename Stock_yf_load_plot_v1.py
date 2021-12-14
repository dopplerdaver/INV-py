 
##################################################
#
# Name: stock_yf_load_plot_v1.py
#
# Purpose: 
#          
# Created: 11.8.2021 - dserke, https://towardsdatascience.com/the-simplest-way-to-create-an-interactive-candlestick-chart-in-python-ee9c1cde50d8
# Edited:  
#
# Notes: sample script also added to GIT with these commands
#        git add mysci.py
#        git commit -m "Comment"
#        git log --oneline
#
################################################

# import libraries
import numpy    as np
import pandas   as pd
import yfinance as yf
import warnings

import cufflinks as cf
import plotly.graph_objects as go
from plotly.offline import iplot, init_notebook_mode
import matplotlib.pyplot as plt
import statsmodels.api as sm

# settings for offline mode
cf.go_offline()
init_notebook_mode()

# define desired ticker
#TICKER = "AAPL"
TICKER = "BTC-USD"

# download OHLC data for predefined ticker
df = yf.download(TICKER, 
                 start="2021-01-01", 
                 end  ="2021-11-12")

# plot as a line
# plot as a line, but not visible
# run metrics on the line
# add trend lines

# plot ticker chart with other metrics
qf = cf.QuantFig(df, title=(str(TICKER)+" price in 2021"), name=TICKER)
qf.add_shapes(hline=66800)
qf.iplot()

# add metrics
qf.add_sma([10, 50], width=2, color=['blue', 'red'])
qf.add_rsi(periods=14, color='green')
qf.add_bollinger_bands(periods=20, boll_std=2 ,colors=['orange','grey'], fill=True)
qf.add_volume()
qf.add_macd()

# change plot dimensions
plt.rcParams['figure.figsize'] = [12, 8]

# make plot of qf visible
qf.iplot()
#------------------------
#
# NAME:		Google_trends_scraper.py
#
# CREATED: 	01.09.2022 - dserke
#
# EDITS:	
#
# SOURCE:	https://github.com/GeneralMills/pytrends#historical-hourly-interest
#		https://lazarinastoy.com/the-ultimate-guide-to-pytrends-google-trends-api-with-python/
#
# NOTES:	1. Search term and topics are two different things
# 		2. keyword length limited to 100 characters
#               3. max number of kw values at one time is 5
#
#------------------------

#------------------------
# import libraries
#------------------------
import pandas                  as     pd
import yfinance                as     yf
import numpy                   as     np
import joblib
from   sklearn.model_selection import train_test_split, RandomizedSearchCV
from   sklearn.metrics         import accuracy_score, f1_score, recall_score, precision_score
from   sklearn.neural_network  import MLPClassifier
from   xgboost                 import XGBClassifier
import seaborn                 as     sns; sns.set()
import matplotlib.pyplot       as     plt

import sys
sys.path.append('..')
from   src.features.build_features import *

#------------------------
# define constants
#------------------------

#------------------------
# define functions
#------------------------
def stock_score(y_pred):
    """
    Returns the annual return of the predictions made by the algorithm,
    and the position history of the algorithm (used for plots).
    """
    ticker_df    = yf.download('DJIA', start='2004-04-09', end='2020-06-26')
    ticker_df['pct_change'] = 1 + ticker_df.Close.pct_change()
    ticker_df    = ticker_df[1:]
    ticker_train = ticker_df[:int(len(ticker_df) * 0.8)]
    ticker_test  = ticker_df[int((len(ticker_df)) * 0.8):]
    if len(y_pred) == len(ticker_train):
        stock = ticker_train
    elif len(y_pred) == len(ticker_test):
        stock = ticker_test
    else:
        raise IndexError(f'Not the length of test or train. Wrong series? {len(y_pred)}')
    position     = 100
    history      = []  
    i            = 0
    while i < len(y_pred):
        if y_pred[i] == 1:
            position *= stock['pct_change'][i]
        else:
            position /= stock['pct_change'][i]

        history.append(position)
        i += 1

    ann_return = ((1+((position - 100) / 100)) ** (1 / (len(y_pred)/365)) - 1) * 100
    return ann_return, history

#------------------------
# data load
#------------------------
djia         = yf.download('DJIA', start='2004-01-01', end='2020-06-26')
search       = pd.read_csv('../data/raw/daily/stock_market.csv')
df           = pd.DataFrame()

df['target'] = target_binary(djia.Close)[1:].astype(int)
#------------------------
# data manipulation
#------------------------
# feature selection
# ... Many features are made, which are all lagged for 3-10 days (it starts at 3, because the data is available after three days, thus it prevents future leakage). 
# ... Then the 50 most correlating (with the target) features are selected and are used for the machine learning algorithm.
# ... Underlying computation can be found in src/features/build_features.py.


#------------------------
# plotting
#------------------------

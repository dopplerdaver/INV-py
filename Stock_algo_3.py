#------------------------------------------------------
#
# NAME: 	Stock_algo_3.py
#
# PURPOSE:	Quantitative value strategy
#
# CREATED:	11.12.2021 - dserke
#
# SOURCE:	https://github.com/nickmccullum/algorithmic-trading-python/blob/master/finished_files/003_quantitative_value_strategy.ipynb
#
#------------------------------------------------------

#------------------------------------------------------
# IMPORT LIBRARIES
#------------------------------------------------------
import numpy as np      #The Numpy numerical computing library
import pandas as pd     #The Pandas data science library
import requests         #The requests library for HTTP requests in Python
import xlsxwriter       #The XlsxWriter libarary for 
import math             #The Python math module
from scipy import stats #The SciPy stats module

# define API token
IEX_CLOUD_API_TOKEN = 'Tpk_059b97af715d417d9f49f50b51b1c448'

#------------------------------------------------------
# LOAD INPUT DATA
#------------------------------------------------------
# ... Import List of Stocks
stocks              = pd.read_csv('/d1/serke/projects/python_tutorial/data/sp_500_stocks.csv')

# ... First API call
symbol              = 'AAPL'
api_url             = f'https://sandbox.iexapis.com/stable/stock/{symbol}/stats?token={IEX_CLOUD_API_TOKEN}'
data                = requests.get(api_url).json()
data

# ... parse API call
data['year1ChangePercent']

# define list chunking function
#   Function sourced from: 
#     https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
   
symbol_groups = list(chunks(stocks['Ticker'], 100))
symbol_strings = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
#     print(symbol_strings[i])
        
#------------------------------------------------------
# MANIPULATE INPUT DATA
#------------------------------------------------------
# ... Adding Stocks Data to Pandas DataFrame
# ...... one-year momentum (oym)
#oym_columns         = ['Ticker', 'Price','One-Year Price Return', 'Number Of Shares to Buy']
#oym_dataframe       = pd.DataFrame(columns = oym_columns)
# ...... high-quality momentum (hqm)
hqm_columns         = [
                       'Ticker', 
                       'Price', 
                       'Number of Shares to Buy', 
                       'One-Year Price Return', 
                       'One-Year Return Percentile',
                       'Six-Month Price Return',
                       'Six-Month Return Percentile',
                       'Three-Month Price Return',
                       'Three-Month Return Percentile',
                       'One-Month Price Return',
                       'One-Month Return Percentile',
                       'HQM Score'
                      ]
hqm_dataframe       = pd.DataFrame(columns = hqm_columns)
# ... replace None values with 0s
convert_none        = lambda x : 0 if x is None else x

for symbol_string in symbol_strings:
#    print(symbol_strings)
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=stats,quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
    data               = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        #oym_dataframe  = oym_dataframe.append(
        #                                pd.Series([symbol, 
        #                                           data[symbol]['quote']['latestPrice'], 
        #                                           data[symbol]['stats']['year1ChangePercent'], 
        #                                          'N/A'], 
        #                                          index = oym_columns), 
        #                                ignore_index = True)
        hqm_dataframe = hqm_dataframe.append(
                                        pd.Series([symbol, 
                                                   data[symbol]['quote']['latestPrice'],
                                                   'N/A',
                                                   convert_none(data[symbol]['stats']['year1ChangePercent']),
                                                   'N/A',
                                                   convert_none(data[symbol]['stats']['month6ChangePercent']),
                                                   'N/A',
                                                   convert_none(data[symbol]['stats']['month3ChangePercent']),
                                                   'N/A',
                                                   convert_none(data[symbol]['stats']['month1ChangePercent']),
                                                   'N/A',
                                                   'N/A'
                                                   ], 
                                                  index = hqm_columns), 
                                        ignore_index = True)
#oym_dataframe
#hqm_dataframe.columns

#------------------------------------------------
# ALGORITHM APPLICATION
#------------------------------------------------
# ... Calculating Momentum Percentiles
time_periods = [
                'One-Year',
                'Six-Month',
                'Three-Month',
                'One-Month'
                ]
for row in hqm_dataframe.index:
    for time_period in time_periods:
        hqm_dataframe.loc[row, f'{time_period} Return Percentile'] = stats.percentileofscore(hqm_dataframe[f'{time_period} Price Return'], hqm_dataframe.loc[row, f'{time_period} Price Return'])/100
# ...Print each percentile score to make sure it was calculated properly
for time_period in time_periods:
    print(hqm_dataframe[f'{time_period} Return Percentile'])
# ...Print the entire DataFrame    
hqm_dataframe

# ... Calculating the HQM Score
for row in hqm_dataframe.index:
    momentum_percentiles = []
    for time_period in time_periods:
        momentum_percentiles.append(hqm_dataframe.loc[row, f'{time_period} Return Percentile'])
    hqm_dataframe.loc[row, 'HQM Score'] = mean(momentum_percentiles)

# SORT ALGORITHM OUTPUT
# ... Identify 20 highest momentum stocks
hqm_dataframe.sort_values(by = 'HQM Score', ascending = False, inplace = True)
hqm_dataframe = hqm_dataframe[:21]
hqm_dataframe.reset_index(drop = True, inplace = True)
hqm_dataframe
#oym_dataframe.sort_values('One-Year Price Return', ascending = False, inplace = True)
#oym_dataframe = final_dataframe[:51]
#oym_dataframe.reset_index(drop = True, inplace = True)
#oym_dataframe

#------------------------------------------------
# Calculating the Number of Shares to Buy
#------------------------------------------------
# ... accept user input
def portfolio_input():
    global portfolio_size
    portfolio_size = input("Enter the value of your portfolio:")

    try:
        val = float(portfolio_size)
    except ValueError:
        print("That's not a number! \n Try again:")
        portfolio_size = input("Enter the value of your portfolio:")

portfolio_input()
print(portfolio_size)

# ... calculate number of shares to buy
# ...... for equal fractions
position_size    = float(portfolio_size) / len(hqm_dataframe.index)
for i in range(0, len(hqm_dataframe['Ticker'])):
    hqm_dataframe.loc[i, 'Number of Shares to Buy'] = math.floor(position_size / hqm_dataframe['Price'][i])
hqm_dataframe

#------------------------------------------------
# OUTPUT DATA: Formatting Our Excel Output
#------------------------------------------------
# ... Initializing our XlsxWriter Object
writer           = pd.ExcelWriter('momentum_strategy.xlsx', engine='xlsxwriter')
hqm_dataframe.to_excel(writer, sheet_name='Momentum Strategy', index = False)

# ... creating format for .xlsx file
background_color = '#0a0a23'
font_color       = '#ffffff'
string_template    = writer.book.add_format(
        {
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )
dollar_template = writer.book.add_format(
        {
            'num_format':'$0.00',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )
integer_template = writer.book.add_format(
        {
            'num_format':'0',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )
percent_template = writer.book.add_format(
        {
            'num_format':'0.0%',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

# ... Apply the format to the .xlsx file columns
column_formats = { 
                    'A': ['Ticker', string_template],
                    'B': ['Price', dollar_template],
                    'C': ['Number of Shares to Buy', integer_template],
                    'D': ['One-Year Price Return', percent_template],
                    'E': ['One-Year Return Percentile', percent_template],
                    'F': ['Six-Month Price Return', percent_template],
                    'G': ['Six-Month Return Percentile', percent_template],
                    'H': ['Three-Month Price Return', percent_template],
                    'I': ['Three-Month Return Percentile', percent_template],
                    'J': ['One-Month Price Return', percent_template],
                    'K': ['One-Month Return Percentile', percent_template],
                    'L': ['HQM Score', integer_template]
                    }
for column in column_formats.keys():
    writer.sheets['Momentum Strategy'].set_column(f'{column}:{column}', 20, column_formats[column][1])
    writer.sheets['Momentum Strategy'].write(f'{column}1', column_formats[column][0], string_format)
    
# Save excel output     
writer.save()
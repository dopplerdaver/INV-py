#------------------------------------------------------
#
# NAME: 	Stock_algo_1.py
#
# CREATED:	11.12.2021 - dserke
#
# SOURCE:	https://github.com/nickmccullum/algorithmic-trading-python/blob/master/finished_files/001_equal_weight_S%26P_500.ipynb
#
#------------------------------------------------------

#-----------------------------------------
# import libraries
#-----------------------------------------
import numpy as np #The Numpy numerical computing library
import pandas as pd #The Pandas data science library
import requests #The requests library for HTTP requests in Python
#import xlsxwriter #The XlsxWriter libarary for 
import math #The Python math module
from secrets import IEX_CLOUD_API_TOKEN

# define API token
IEX_CLOUD_API_TOKEN = 'Tpk_059b97af715d417d9f49f50b51b1c448'

# Import List of Stocks
stocks              = pd.read_csv('/d1/serke/projects/python_tutorial/data/sp_500_stocks.csv')

#
symbol              = 'AAPL'
api_url             = f'https://sandbox.iexapis.com/stable/stock/{symbol}/quote?token={IEX_CLOUD_API_TOKEN}'
data                = requests.get(api_url).json()
data

# parse API call
data['latestPrice']
data['marketCap']

# Adding Stocks Data to Pandas DataFrame
my_columns          = ['Ticker', 'Price','Market Capitalization', 'Number Of Shares to Buy']
final_dataframe     = pd.DataFrame(columns = my_columns)

#-----------------------------------------
# define list chunking function
#-----------------------------------------
#   Function sourced from: 
#     https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
       
#-----------------------------------------       
# Loop Through Tickers List of Stocks Using Batch API Calls 
#-----------------------------------------
symbol_groups       = list(chunks(stocks['Ticker'], 100))
symbol_strings      = []
for i in range(0, len(symbol_groups)):
    symbol_strings.append(','.join(symbol_groups[i]))
#     print(symbol_strings[i])

final_dataframe = pd.DataFrame(columns = my_columns)

for symbol_string in symbol_strings:
#     print(symbol_strings)
    batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote&symbols={symbol_string}&token={IEX_CLOUD_API_TOKEN}'
    data = requests.get(batch_api_call_url).json()
    for symbol in symbol_string.split(','):
        final_dataframe = final_dataframe.append(
                                        pd.Series([symbol, 
                                                   data[symbol]['quote']['latestPrice'], 
                                                   data[symbol]['quote']['marketCap'], 
                                                   'N/A'], 
                                                  index = my_columns), 
                                        ignore_index = True)
final_dataframe

#-----------------------------------------
# Calculating the Number of Shares to Buy
#-----------------------------------------
portfolio_size = input("Enter the value of your portfolio:")
try:
    val            = float(portfolio_size)
except ValueError:
    print("That's not a number! \n Try again:")
    portfolio_size = input("Enter the value of your portfolio:")
    position_size  = float(portfolio_size) / len(final_dataframe.index)
for i in range(0, len(final_dataframe['Ticker'])-1):
    final_dataframe.loc[i, 'Number Of Shares to Buy'] = math.floor(position_size / final_dataframe['Price'][i])
final_dataframe

#-----------------------------------------
# Formatting Our Excel Output
#-----------------------------------------
# ... Initializing our XlsxWriter Object
writer = pd.ExcelWriter('recommended_trades.xlsx', engine='xlsxwriter')
final_dataframe.to_excel(writer, sheet_name='Recommended Trades', index = False)

# ... creating format for .xlsx file
background_color = '#0a0a23'
font_color       = '#ffffff'
string_format    = writer.book.add_format(
        {
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )
dollar_format = writer.book.add_format(
        {
            'num_format':'$0.00',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )
integer_format = writer.book.add_format(
        {
            'num_format':'0',
            'font_color': font_color,
            'bg_color': background_color,
            'border': 1
        }
    )

# ... Apply the format to the .xlsx file columns
column_formats = { 
                    'A': ['Ticker', string_format],
                    'B': ['Price', dollar_format],
                    'C': ['Market Capitalization', dollar_format],
                    'D': ['Number of Shares to Buy', integer_format]
                    }
for column in column_formats.keys():
    writer.sheets['Recommended Trades'].set_column(f'{column}:{column}', 20, column_formats[column][1])
    writer.sheets['Recommended Trades'].write(f'{column}1', column_formats[column][0], string_format)

#-----------------------------------------  
# Save excel output    
#-----------------------------------------
writer.save()
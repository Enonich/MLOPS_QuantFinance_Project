import pandas as pd
#import pandas_datareader as pdr
import yfinance as yf
from datetime import date

#symbols = ['GBPUSD=X', 'JPY=X', 'AAPL']
# symbols = ['AAPL', 'EURUSD=X', 'GBPUSD=X', 'JPY=X']
symbols = ['SPY']
start_date = '2023-03-10-09-30-00' 
end_date   = '2023-05-10'
SD = date(2023, 3, 20)
ED = date(2023, 5, 10)
#interval = (end_date-start_date).days
 
def get_stock_data(symbol):
    data = yf.download(symbol, period='60d', interval='5m')
    return data

def store_data():    
    data = get_stock_data(symbol)
    data.reset_index(inplace=True)
    data.rename(columns={'index': 'Date'}, inplace=True)
    filename = f'{symbol}_5m.csv'
    #data.to_csv(filename, encoding='utf-8-sig', index=False)
    print(data)


for symbol in symbols:
    store_data()
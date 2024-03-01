import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# DAILY RETURN(5MIN RETURN)
def calculate_daily_return(data):
    daily_return = data['Adj Close'].pct_change() * 100
    data.loc[:, 'Daily_Return'] = daily_return
    #data.to_csv(f'./Data/{symbol}/Daily_Return.csv')
    data = data.drop(columns=['High', 'Low', 'Close', 'Adj Close'])
    return data
    
# SIMPLE MOVING AVERAGE
def calculate_sma(data, window=20):    
    sma = data['Adj Close'].rolling(window=window, min_periods=1).mean()
    data.loc[:, 'Simple_Moving_Avg'] = sma
    #data.to_csv(f'./Data/{symbol}/SMA.csv')
    data = data.drop(columns=['High', 'Low', 'Close', 'Adj Close'])
    return data
    
# BOLLINGER BANDS
def calculate_bollinger_bands(data, window=20, std=2):
     
    #calculate the rolling standard deviation
    rolling_std = data['Adj Close'].rolling(window=window, min_periods=1).std()
    #Get the rolling mean from the simple moving average function(sma==rolling mean)
    rolling_mean = data['Adj Close'].rolling(window=window, min_periods=1).mean()
    #Calculate the upper and the lower Bollinger Bands
    upper_band = rolling_mean + rolling_std * std
    lower_band = rolling_mean - rolling_std * std
    #Rename columns and save 
    data.loc[:, 'Upper_Band'] = upper_band
    data.loc[:, 'Lower_Band'] = lower_band
    #data.to_csv(f'./Data/{symbol}/BB.csv')
    data = data.drop(columns=['High', 'Low', 'Close', 'Adj Close'])
    return data
    
# MOVING AVERAGE CONVERGENCE DIVERGENCE
def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
     
    #calculate Short-term amd Long-Term Exponential Moving-Weighted Average(EMA) 
    short_ema = data['Adj Close'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['Adj Close'].ewm(span=long_window, adjust = False).mean()   
    #calculate the differential MACD Line
    macd_line = short_ema - long_ema    
    #Calculate the signal Line; EMA of the MACD line
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()    
    #calculate the MACD Histogram; MACD and Signal Line Differential
    macd_histogram = macd_line - signal_line
    # Rename and Save columns
    data.loc[:, 'MACD_Line'] = macd_line
    data.loc[:, 'Signal_Line'] = signal_line
    data.loc[:, 'MACD_Histogram'] = macd_histogram
    #data.to_csv(f'./Data/{symbol}/MACD.csv') 
    data = data.drop(columns=['High', 'Low', 'Close', 'Adj Close'])
    return data 
    
    
# AVERAGE TRUE RANGE (TRUE RANGE AND AVERAGE TRUE RANGE FUNCTIONS) 
def calculate_true_range(data):
     
    high = data['High']
    low = data['Low']
    prev_close = data['Close'].shift(1)
    true_range = pd.DataFrame(data={'high_low':high-low, 'high_close':abs(high-prev_close), 'low_close':abs(low-prev_close)})
    return true_range.max(axis=1)

def average_true_range(data, period=14):
     
    true_range = calculate_true_range(data)
    atr = true_range.rolling(window=period).mean()
    # Rename and Save Column
    data.loc[:, 'ATR'] = atr
    #atr['ATR'] = atr
    #data.to_csv(f'./Data/{symbol}/ATR.csv', columns=( 'Adj Close', 'ATR'))
    data = data.drop(columns=['High', 'Low', 'Close', 'Adj Close'])
    return data
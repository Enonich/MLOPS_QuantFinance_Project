import pickle
import joblib as jb
from flask import Flask, request, jsonify
import pandas as pd
import yfinance as yf
from feature_engineering import calculate_bollinger_bands, calculate_daily_return, calculate_macd, calculate_sma, average_true_range

    

def read_data(symbol):
    data = yf.download(symbol, period='60d', interval='5m')
    return data

def preprocess(stock):
    # Get the data from the read_data function 
    df = read_data(stock['Symbol'])

    # Feature Engineering
    atr_data = average_true_range(df)
    macd_data = calculate_macd(df)  
    dr_data = calculate_daily_return(df)
    bb_data = calculate_bollinger_bands(df)
    sma_data = calculate_sma(df)
    train_sets = sma_data
    
    # Drop null values and some columns
    data = df.dropna()
    features = data.drop(['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'], axis=1)
    return features



def predict(stock):
    model = jb.load("Linear_Reg.pkl")
    
    features = preprocess(stock)
    
    pred = model.predict(features)
    final_pred = float(pred[-1])
    return round(final_pred, 5)


app = Flask('Stock-Prediction')

@app.route('/predict', methods=['POST'])
def predict_endpoint():
    stock = request.get_json()
    
    pred = predict(stock)
    
    result = {
        'price': pred
    }    
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)
    
import pickle
import joblib as jb
from flask import Flask, request, jsonify
import pandas as pd
import yfinance as yf
from feature_engineering import calculate_bollinger_bands, calculate_daily_return, calculate_macd, calculate_sma, average_true_range
import mlflow
from mlflow.tracking import MlflowClient
import os



# Set MLFLOW_TRACKING_URI environment variable to 
# local MLFlow server URI
os.environ['MLFLOW_TRACKING_URI'] = 'http://127.0.0.1:5000'
client = MlflowClient()

model_name = 'stock_predictor'
model_version = 2

    

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

    features = preprocess(stock)

    model = mlflow.pyfunc.load_model(model_uri=f"models:/{model_name}/{model_version}")
    pred = model.predict(features)
    final_pred = float(pred[-1])
    return round(final_pred, 5)



app = Flask('Stock-Prediction')

@app.route('/predict', methods=['POST'])
def predict_endpoint():
    stock = request.get_json()
    
    pred = predict(stock)
    
    result = {
        "price": pred, 
        "model_version": model_version
    }    
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)
    
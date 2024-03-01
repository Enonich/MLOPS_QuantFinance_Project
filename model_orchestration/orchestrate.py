import pathlib
import pickle
import pandas as pd
import numpy as np
import sklearn
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error
import mlflow
from prefect import flow, task
from prefect.artifacts import create_markdown_artifact
from datetime import date
from feature_engineering import calculate_bollinger_bands, calculate_daily_return, calculate_macd, calculate_sma, average_true_range


@task(retries=3, retry_delay_seconds=2)
def read_dataframe(filename: str) -> pd.DataFrame:
    
    """Read data into DataFrame"""
    df = pd.read_csv(filename, index_col='Datetime')
    
    #Feature Engineering 
    atr_data = average_true_range(df)
    macd_data = calculate_macd(df)  
    dr_data = calculate_daily_return(df)
    bb_data = calculate_bollinger_bands(df)
    sma_data = calculate_sma(df)
    train_sets = sma_data
    
    df = df.drop(['Open', 'High', 'Low', 'Close'], axis=1)
    return df

@task
def preprocess(df_train, df_val):
    train_data = df_train.dropna()
    val_data  = df_val.dropna()
    X_train = train_data.drop(['Adj Close', 'Volume'], axis=1)
    y_train = train_data[['Adj Close']]
    
    X_test = val_data.drop(['Adj Close', 'Volume'], axis=1)
    y_test = val_data[['Adj Close']]
    
    # Dropping The Last Row of the x_test and the first row of the y_test
    X_test = X_test.drop(X_test.index[-1])
    y_test = y_test.drop(y_test.index[0])
    return X_train, y_train, X_test, y_test



@task(log_prints=True)
def train_model(
    X_train, y_train, 
    X_test, y_test) -> None:
    
    
    with mlflow.start_run():
    
        # logging parameters
        mlflow.log_param("polynomial degree", 1)
        mlflow.log_param("alpha", 0.1)
    
        degree = 1
        alpha = 0.1  # Regularization strength
        ridge_model = make_pipeline(PolynomialFeatures(degree=degree), StandardScaler(), Ridge(alpha=alpha))
        ridge_model.fit(X_train, y_train)
    
        # MAKE PREDICTIONS AND CHECK THE VARIANCE AND BIAS VALUES
        train_pred = ridge_model.predict(X_train)
        test_pred = ridge_model.predict(X_test)
        mlflow.set_tag('model', 'RidgeRegressor')
    
        train_mse = mean_squared_error(y_train, train_pred, squared=False)
        test_mse = mean_squared_error(y_test, test_pred, squared=False)
        train_r2 = r2_score(y_train, train_pred)
        test_r2 = r2_score(y_test, test_pred)
    
        mlflow.log_metric("rmse", test_mse)
        mlflow.log_metric("r2", test_r2)
        
        # Print the metric scores
        print(f"Test RMSE: {test_mse:.4f}")
        print(f"Test R^2 Score: {test_r2:.4f}")
        
        pathlib.Path("models").mkdir(exist_ok=True)
        
        mlflow.sklearn.log_model(ridge_model, 'models')
        
        markdown__rmse_report = f"""# RMSE Report

        ## Summary

        Asset Price Prediction Report 

        ## RMSE Ridge Model

        | Region    | RMSE |
        |:----------|-------:|
        | {date.today()} | {test_mse:.2f} |
        """

        create_markdown_artifact(
            key="quant-price-model-report", markdown=markdown__rmse_report
        )

    return None


@flow
def main_flow(
    train_path = "../Data/EURUSD=X_5m.csv",
    val_path   = "../Data/AAPL_5m.csv"    
    ) -> None:
    """The main training pipeline""" 
    
    
    # MLflow settings
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("stock_pred_exp")
    
    
    # Load
    df_train = read_dataframe(train_path)
    df_val = read_dataframe(val_path)

    # Transform
    X_train, y_train, X_val, y_val, = preprocess(df_train, df_val)

    # Train
    train_model(X_train, y_train, X_val, y_val)


if __name__ == "__main__":
    main_flow()

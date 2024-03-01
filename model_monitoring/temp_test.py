import datetime
import time
import random
import logging 
import uuid
import pytz
import pandas as pd
import io
import psycopg
import joblib
from feature_engineering import calculate_bollinger_bands, calculate_daily_return, calculate_macd, calculate_sma, average_true_range

from prefect import task, flow

from evidently.report import Report
from evidently import ColumnMapping
from evidently.metrics import ColumnDriftMetric, DatasetDriftMetric, DatasetMissingValuesMetric

# logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

# SEND_TIMEOUT = 10
# rand = random.Random()

# create_table_statement = """
# drop table if exists dummy_metrics;
# create table dummy_metrics(
# 	timestamp timestamp,
# 	prediction_drift float,
# 	num_drifted_columns integer,
# 	share_missing_values float
# )
# """



reference_data = pd.read_csv('data/reference.csv')

with open('model/lin_reg.bin', 'rb') as f_in:
	model = joblib.load(f_in)

raw_data = pd.read_csv('data/AAPL.csv', index_col='Datetime')
y_rd = raw_data['Adj Close']
# applying feature engineering
atr_data = average_true_range(raw_data)
macd_data = calculate_macd(raw_data)
dr_data = calculate_daily_return(raw_data)
bb_data = calculate_bollinger_bands(raw_data)
sma_data = calculate_sma(raw_data)
features = sma_data

# data preprocessing
rd_features = features.dropna()
rd_features = rd_features.drop(['Open', 'Volume'], axis=1)

rd_features = pd.merge(rd_features, y_rd, on='Datetime')

target_feature = rd_features[['Adj Close']]
input_features = rd_features.drop(['Adj Close'], axis=1)
print(input_features.head(2))
print(target_feature.head(2))
print(rd_features)
input_features = input_features.drop(input_features.index[-1])
current_data = pd.merge(input_features, target_feature, on='Datetime')

target_feature = target_feature.drop(target_feature.index[0])

print(input_features.shape, target_feature.shape)
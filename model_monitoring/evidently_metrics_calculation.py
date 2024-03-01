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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

SEND_TIMEOUT = 10
rand = random.Random()

create_table_statement = """
drop table if exists dummy_metrics;
create table dummy_metrics(
	timestamp timestamp,
	prediction_drift float,
	num_drifted_columns integer,
	share_missing_values float
)
"""

reference_data = pd.read_csv('data/reference.csv')

with open('model/lin_reg.bin', 'rb') as f_in:
	model = joblib.load(f_in)

raw_data = pd.read_csv('data/SPY.csv', index_col='Datetime')
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
input_features = input_features.drop(input_features.index[-1])

# merge input and target features for data drift report
current_data = pd.merge(input_features, target_feature, on='Datetime')

target_feature = target_feature.drop(target_feature.index[0])
current_data = current_data.reset_index(drop=True)
print(current_data)

# Defining the features for drifting report
num_features = ['ATR', 'MACD_Line', 'Signal_Line', 'MACD_Histogram', 'Daily_Return'
       'Upper_Band', 'Lower_Band', 'Simple_Moving_Avg']

target = 'Adj Close'

column_mapping = ColumnMapping(
    prediction='prediction',
    numerical_features=num_features,
    categorical_features=None,
    target=target
)

report = Report(metrics = [
    ColumnDriftMetric(column_name='prediction'),
    DatasetDriftMetric(),
    DatasetMissingValuesMetric()
])

@task
def prep_db():
	with psycopg.connect("host=localhost port=5432 user=postgres password=example", autocommit=True) as conn:
		res = conn.execute("SELECT 1 FROM pg_database WHERE datname='test'")
		if len(res.fetchall()) == 0:
			conn.execute("create database test;")
		with psycopg.connect("host=localhost port=5432 dbname=test user=postgres password=example") as conn:
			conn.execute(create_table_statement)

@task
def calculate_metrics_postgresql(curr, i):
    current_time = datetime.datetime.now()  # Get the current timestamp
    timestamp = current_time + datetime.timedelta(seconds=i)  # Add timedelta to the current timestamp

    current_data['prediction'] = model.predict(input_features)

    report.run(reference_data=reference_data, current_data=current_data, column_mapping=column_mapping)

    result = report.as_dict()

    prediction_drift = result['metrics'][0]['result']['drift_score']
    num_drifted_columns = result['metrics'][1]['result']['number_of_drifted_columns']
    share_missing_values = result['metrics'][2]['result']['current']['share_of_missing_values']

    curr.execute(
        "insert into dummy_metrics(timestamp, prediction_drift, num_drifted_columns, share_missing_values) values (%s, %s, %s, %s)",
        (timestamp, prediction_drift, num_drifted_columns, share_missing_values)
    )


@flow
def batch_monitoring_backfill():
	prep_db()
	last_send = datetime.datetime.now() - datetime.timedelta(seconds=10)
	with psycopg.connect("host=localhost port=5432 dbname=test user=postgres password=example", autocommit=True) as conn:
		for i in range(0, 12):
			with conn.cursor() as curr:
				calculate_metrics_postgresql(curr, i)

			new_send = datetime.datetime.now()
			seconds_elapsed = (new_send - last_send).total_seconds()
			if seconds_elapsed < SEND_TIMEOUT:
				time.sleep(SEND_TIMEOUT - seconds_elapsed)
			while last_send < new_send:
				last_send = last_send + datetime.timedelta(seconds=10)
			logging.info("data sent")

if __name__ == '__main__':
	batch_monitoring_backfill()

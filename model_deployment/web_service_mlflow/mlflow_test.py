import os
import mlflow
from mlflow.tracking import MlflowClient 

# Set MLFLOW_TRACKING_URI environment variable to your local MLFlow server URI
os.environ['MLFLOW_TRACKING_URI'] = 'http://127.0.0.1:5000'

# Define your MLFlow run ID
# RUN_ID = '15c269a13c0740279839814804315ad5'

# Initialize MLFlow client
client = MlflowClient()


experiments = client.search_experiments()

# from mlflow.entities import ViewType
# runs = client.search_runs(
#     experiment_ids = '1',
#     filter_string = "",
#     run_view_type = ViewType.ACTIVE_ONLY,
#     max_results = 5, 
#     order_by = ["metrics.rmse ASC"]
# )


# for run in runs:
#     print(f"run id: {run.info.run_id}, rmse: {run.data.metrics['rmse']:.4f}")   

# # # Load your logged model
# logged_model = f'runs/{RUN_ID}/model'

model_name = 'stock_predictor'
model_version = 2

model = mlflow.pyfunc.load_model(model_uri=f"models:/{model_name}/{model_version}")
print("\n ", model)

print(model()
# print(model)
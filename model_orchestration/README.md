# Model Orchestration
This section of the repo is about using a workflow management system (prefect) designed for orchestrating complex data workflows. 
Prefect provides a framewrok for building, scheduling, monitoring and debugging data workflows in python.


### Same virtual environment created for the model tracking can be used here (with a few more installations).
** conda create -n model-orch python==3.11.4
where 'model-orch' is the name of the conda environment

* Activate your virtual enviroment


# Check this image for your prefect deployment
![alt text](Activity-create-run-deployment.png)

## Running the Prefect server. (terminal command) 
** prefect server start 

### Deploying on Prefect
prefect deploy 3.4/orchestrate.py:main_flow -n quantpred -p quantpool

### Starting the worker
prefect worker start -p quantpred

* Run the orchestrate_spy.py and the orchestrate.py
python orchestrate_spy.py
python orchestrate.py
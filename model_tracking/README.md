# Model Tracking
This section of the repo is about managing the end-to-end machine learning lifecycle. 
Tasks here include experiment tracking, reproducibility, model packaging and deployment



## Environment Dependencies and Installments
* Required python version
    python == 3.11.4
scikit-learn == 1.3.2
mlflow == 2.9.2



### Creates a conda virtual environment with the above packages
** conda create -n my_env python==3.11.4



### Pip install dependencies all (found at the root directory)
** pip install -r requirements.txt


## Running the mlflow ui/server using sqlite(terminal command) 
** mlflow ui --backend-store-uri sqlite:///mlruns.db
** mlflow server --backend-store-uri sqlite:///mlruns.db
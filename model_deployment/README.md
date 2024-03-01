# Model Deployment
web-service deployment


## Environment Dependencies and Installments
python == 3.11.4
scikit-learn == 1.3.2
mlflow == 2.9.2

gunicorn


#### Create and install pipenv with:
** pipenv install scikit-learn==1.3.2 flask --python=3.11.4
** pipenv install gunicorn

activate with:
** pipenv shell

## Running with gunicorn instead of flask
gunicorn --bind=0.0.0.0:9696 predict:app  (run in terminal)


## Building and Running with Docker

```bash
docker build -t stock-prediction-service:v1 .
```

```bash
docker run -it --rm -p 9696:9696  stock-prediction-service:v1
```

### run this command to run the package in the docker container
```bash
python test.py
